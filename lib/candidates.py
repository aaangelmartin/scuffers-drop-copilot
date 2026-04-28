"""Generador de candidatos de acción.

Cada candidato es un dict con:
  action_type, target_id, owner, score (0-100), confidence (0-1),
  euros_at_risk, euros_recoverable, vips_affected, evidence (dict con datos brutos)

Pipeline luego: dedupe + ranquear + Gemini enriquece + emit top 10.
"""
from typing import List, Dict
from datetime import datetime, timezone

# Pesos de las 4 lentes
W = {"logistics": 0.40, "customer_care": 0.25, "marketing": 0.20, "operations": 0.15}

# Multiplicadores de "executability"
EXEC_FACTOR = {
    "pause_campaign": 0.90,
    "prevent_oversell": 0.85,
    "prioritize_order": 0.75,
    "contact_customer": 0.70,
    "escalate_ticket": 0.80,
    "manual_review_order": 0.60,
    "restock_alert": 0.65,
    "redirect_campaign_budget": 0.55,
}

REFUND_OVERHEAD = 12.0   # coste fijo por refund (envío + soporte + procesamiento)
VIP_CHURN_LTV_FACTOR = 0.20  # si un VIP rompe, asumimos riesgo de perder 20% de su LTV


def _now():
    return datetime.now(timezone.utc)


def _eur(x):
    return round(float(x), 2)


# ---------------------------------------------------------------- detectors

def detect_oversell_risks(data, idx) -> List[Dict]:
    """Lente 1: Logistics — SKUs donde available - reserved < 0 con orders pendientes."""
    out = []
    for sku, inv in idx["inv_by_sku"].items():
        gap = inv["available"] - inv["reserved"]
        orders = idx["orders_by_sku"].get(sku, [])
        pending = [o for o in orders if o["status"] in ("paid", "processing", "packed", "payment_review")]
        if gap >= 0 and inv["available"] >= len(pending):
            continue  # no hay riesgo
        units_short = max(0, len(pending) - max(0, inv["available"]))
        if units_short == 0:
            continue
        # ¿hay incoming a tiempo?
        has_quick_restock = (
            inv["incoming"] >= units_short
            and inv["incoming_eta"]
            and (inv["incoming_eta"] - _now()).total_seconds() < 24 * 3600
        )
        # cuántos VIPs afectados
        affected_vips = []
        for o in pending:
            c = idx["cust_by_id"].get(o["customer_id"])
            if c and c["is_vip"]:
                affected_vips.append(c)
        # euros en riesgo
        unit_price = inv["unit_price"] or (sum(o["value"] for o in pending) / max(1, len(pending)))
        eur_risk = units_short * (unit_price + REFUND_OVERHEAD)
        eur_risk += sum(c["ltv"] * VIP_CHURN_LTV_FACTOR for c in affected_vips)
        # score 0-100: cuanto mayor el gap relativo, peor
        gap_ratio = units_short / max(1, len(pending))
        score = min(100, 60 + 40 * gap_ratio)
        if has_quick_restock:
            score *= 0.6  # menos urgente si llega reposición pronto
        confidence = 0.95 if inv["available"] >= 0 and inv["reserved"] >= 0 else 0.70
        out.append({
            "action_type": "prevent_oversell",
            "target_id": sku,
            "owner": "logistics",
            "score": score,
            "confidence": confidence,
            "euros_at_risk": _eur(eur_risk),
            "euros_recoverable": _eur(eur_risk * confidence * EXEC_FACTOR["prevent_oversell"]),
            "vips_affected": len(affected_vips),
            "evidence": {
                "sku": sku,
                "product_name": inv["product_name"],
                "available": inv["available"],
                "reserved": inv["reserved"],
                "incoming": inv["incoming"],
                "incoming_eta": inv["incoming_eta"].isoformat() if inv["incoming_eta"] else None,
                "pending_orders": len(pending),
                "units_short": units_short,
                "vips_in_pending": [c["customer_id"] for c in affected_vips],
                "has_quick_restock": has_quick_restock,
                "unit_price": inv["unit_price"],
            },
        })
    return out


def detect_campaign_mismatch(data, idx) -> List[Dict]:
    """Lente 3: Marketing — campañas pegando a SKUs rotos."""
    out = []
    intensity_score = {"very_high": 100, "high": 75, "medium": 45, "low": 20}
    for c in data["campaigns"]:
        if c["status"] != "active":
            continue
        inv = idx["inv_by_sku"].get(c["target_sku"])
        if not inv:
            continue
        gap = inv["available"] - inv["reserved"]
        if gap >= 5:  # hay margen, ok
            continue
        # presión = intensity * traffic_growth
        i_score = intensity_score.get(c["intensity"], 30)
        # severidad por stock
        stock_severity = max(0, min(100, 100 * (1 - inv["available"] / max(1, inv["reserved"]))))
        score = min(100, 0.6 * i_score + 0.4 * stock_severity)
        confidence = 0.90
        # euros en riesgo: budget_spent + oversells potenciales
        pending = [o for o in idx["orders_by_sku"].get(c["target_sku"], []) if o["status"] in ("paid", "processing", "packed")]
        units_short = max(0, len(pending) - max(0, inv["available"]))
        eur_risk = c["budget_spent"] * 0.3 + units_short * (inv["unit_price"] + REFUND_OVERHEAD)
        out.append({
            "action_type": "pause_campaign",
            "target_id": c["campaign_id"],
            "owner": "marketing",
            "score": score,
            "confidence": confidence,
            "euros_at_risk": _eur(eur_risk),
            "euros_recoverable": _eur(eur_risk * confidence * EXEC_FACTOR["pause_campaign"]),
            "vips_affected": 0,
            "evidence": {
                "campaign_id": c["campaign_id"],
                "source": c["source"],
                "target_sku": c["target_sku"],
                "target_city": c["target_city"],
                "intensity": c["intensity"],
                "available": inv["available"],
                "reserved": inv["reserved"],
                "pending_orders": len(pending),
                "units_short": units_short,
                "budget_spent": c["budget_spent"],
                "traffic_growth": c["traffic_growth"],
            },
        })
    return out


def detect_vip_at_risk(data, idx) -> List[Dict]:
    """Lente 2: Customer Care — VIPs/alto LTV con ticket o pedido en SKU roto."""
    out = []
    for c in data["customers"]:
        risk_signals = []
        eur_risk = 0
        # ticket abierto?
        tickets = idx["tickets_by_cust"].get(c["customer_id"], [])
        if tickets:
            risk_signals.append("open_ticket")
            for t in tickets:
                if t["urgency"] in ("urgent", "high"):
                    risk_signals.append(f"urgency_{t['urgency']}")
                if t["sentiment"] == "negative":
                    risk_signals.append("negative_sentiment")
        # pedido en SKU roto?
        orders = idx["orders_by_cust"].get(c["customer_id"], [])
        broken_orders = []
        for o in orders:
            inv = idx["inv_by_sku"].get(o["sku"])
            if inv and inv["available"] < 1 and o["status"] in ("paid", "processing", "packed"):
                broken_orders.append(o)
                eur_risk += (inv["unit_price"] or o["value"]) + REFUND_OVERHEAD
        if broken_orders:
            risk_signals.append(f"broken_orders={len(broken_orders)}")

        is_high_value = c["is_vip"] or c["ltv"] >= 500
        if not is_high_value or not risk_signals:
            continue

        # score
        base = 50
        if c["is_vip"]:
            base += 25
        if "negative_sentiment" in risk_signals:
            base += 15
        if any("urgency_" in s for s in risk_signals):
            base += 10
        if broken_orders:
            base += 10
        score = min(100, base)

        eur_risk += c["ltv"] * VIP_CHURN_LTV_FACTOR if c["is_vip"] else c["ltv"] * 0.10
        confidence = 0.85
        out.append({
            "action_type": "contact_customer" if not broken_orders else "prioritize_order",
            "target_id": c["customer_id"] if not broken_orders else broken_orders[0]["order_id"],
            "owner": "customer_care",
            "score": score,
            "confidence": confidence,
            "euros_at_risk": _eur(eur_risk),
            "euros_recoverable": _eur(eur_risk * confidence * EXEC_FACTOR["contact_customer"]),
            "vips_affected": 1 if c["is_vip"] else 0,
            "evidence": {
                "customer_id": c["customer_id"],
                "is_vip": c["is_vip"],
                "ltv": c["ltv"],
                "segment": c["segment"],
                "preferred_city": c["preferred_city"],
                "risk_signals": risk_signals,
                "broken_order_ids": [o["order_id"] for o in broken_orders],
                "tickets": [{"id": t["ticket_id"], "urgency": t["urgency"], "sentiment": t["sentiment"], "msg": t["message"]} for t in tickets],
            },
        })
    return out


def detect_urgent_tickets(data, idx) -> List[Dict]:
    """Lente 2 bis: tickets urgent + negative que no estén ya cubiertos."""
    out = []
    for t in data["tickets"]:
        if t["urgency"] not in ("urgent", "high") and t["sentiment"] != "negative":
            continue
        c = idx["cust_by_id"].get(t["customer_id"]) or {"is_vip": False, "ltv": 0, "segment": ""}
        score = 50
        if t["urgency"] == "urgent":
            score += 30
        elif t["urgency"] == "high":
            score += 20
        if t["sentiment"] == "negative":
            score += 15
        if c.get("is_vip"):
            score += 15
        elif c.get("ltv", 0) >= 500:
            score += 8
        score = min(100, score)
        eur_risk = 50 + (c.get("ltv", 0) * VIP_CHURN_LTV_FACTOR if c.get("is_vip") else 0)
        out.append({
            "action_type": "escalate_ticket",
            "target_id": t["ticket_id"],
            "owner": "customer_care",
            "score": score,
            "confidence": 0.9,
            "euros_at_risk": _eur(eur_risk),
            "euros_recoverable": _eur(eur_risk * 0.9 * EXEC_FACTOR["escalate_ticket"]),
            "vips_affected": 1 if c.get("is_vip") else 0,
            "evidence": {
                "ticket_id": t["ticket_id"],
                "order_id": t["order_id"],
                "customer_id": t["customer_id"],
                "is_vip": c.get("is_vip", False),
                "ltv": c.get("ltv", 0),
                "channel": t["channel"],
                "urgency": t["urgency"],
                "sentiment": t["sentiment"],
                "message": t["message"],
            },
        })
    return out


def detect_manual_review(data, idx) -> List[Dict]:
    """Lente 4: Operations — pedidos sospechosos."""
    out = []
    for o in data["orders"]:
        flags = []
        c = idx["cust_by_id"].get(o["customer_id"]) or {}
        if o["quantity"] >= 4:
            flags.append("qty_high")
        if c.get("returns_count", 0) >= 3:
            flags.append("high_returns")
        if o["status"] == "payment_review":
            flags.append("payment_review")
        if o["value"] >= 200:
            flags.append("high_value")
        if not flags:
            continue
        score = 40 + 15 * len(flags)
        score = min(100, score)
        out.append({
            "action_type": "manual_review_order",
            "target_id": o["order_id"],
            "owner": "operations",
            "score": score,
            "confidence": 0.7,
            "euros_at_risk": _eur(o["value"]),
            "euros_recoverable": _eur(o["value"] * 0.7 * EXEC_FACTOR["manual_review_order"]),
            "vips_affected": 1 if c.get("is_vip") else 0,
            "evidence": {
                "order_id": o["order_id"],
                "customer_id": o["customer_id"],
                "sku": o["sku"],
                "value": o["value"],
                "quantity": o["quantity"],
                "status": o["status"],
                "flags": flags,
                "customer_returns_count": c.get("returns_count", 0),
            },
        })
    return out


def detect_opportunities(data, idx) -> List[Dict]:
    """Bonus: oportunidades — SKUs con stock muerto y conversión baja, redirigir budget."""
    out = []
    # Localizar SKUs con stock alto + reservas bajas + page_views relativamente bajos
    dead_stock = []
    for sku, inv in idx["inv_by_sku"].items():
        if inv["available"] >= 30 and inv["reserved"] <= 5 and inv["sell_through_rate"] < 0.25:
            dead_stock.append(inv)
    if not dead_stock:
        return out
    # Buscar campañas activas pegando a SKUs rotos: ese budget se podría mover
    for c in data["campaigns"]:
        if c["status"] != "active":
            continue
        inv_target = idx["inv_by_sku"].get(c["target_sku"])
        if not inv_target:
            continue
        if inv_target["available"] - inv_target["reserved"] >= 0:
            continue  # campaña ok, no oversell
        # Hay match: redirigir budget a un dead_stock con perfil similar
        candidate = max(dead_stock, key=lambda x: x["page_views"])
        # cap oportunidad: % del budget mal-empleado
        eur_opportunity = min(800, c["budget_spent"] * 0.4)
        out.append({
            "action_type": "redirect_campaign_budget",
            "target_id": c["campaign_id"],
            "owner": "marketing",
            "score": 70,
            "confidence": 0.65,
            "euros_at_risk": 0,
            "euros_recoverable": _eur(eur_opportunity),
            "vips_affected": 0,
            "evidence": {
                "campaign_id": c["campaign_id"],
                "current_target": c["target_sku"],
                "current_target_available": inv_target["available"],
                "suggested_target": candidate["sku"],
                "suggested_target_available": candidate["available"],
                "suggested_target_views": candidate["page_views"],
                "budget_spent": c["budget_spent"],
                "is_opportunity": True,
            },
        })
    return out


def detect_shipping_issues(data, idx, shipping_data: dict) -> List[Dict]:
    """NUEVA lente (Shipping API): pedidos con incidencias logísticas reales."""
    out = []
    if not shipping_data:
        return out
    from lib.shipping_api import is_problematic, severity_score, SHIPPING_STATUS_ES, DELAY_REASON_ES

    for order_id, s in shipping_data.items():
        if not is_problematic(s):
            continue
        sev = severity_score(s)
        if sev < 30:
            continue

        # Encuentra la order
        order = next((o for o in data["orders"] if o["order_id"] == order_id), None)
        if not order:
            continue
        cust = idx["cust_by_id"].get(order["customer_id"]) or {}
        is_vip = cust.get("is_vip", False)
        ltv = cust.get("ltv", 0)

        status = (s.get("shipping_status") or "").lower()
        reason = (s.get("delay_reason") or "").lower()
        delay_risk = s.get("delay_risk") or 0

        # Decidir tipo de acción
        if status == "lost":
            action_type = "contact_customer"
            owner = "customer_care"
            score_base = 95
        elif status in ("exception", "returned_to_sender"):
            action_type = "manual_review_order"
            owner = "operations"
            score_base = 80
        elif s.get("requires_manual_review"):
            action_type = "manual_review_order"
            owner = "operations"
            score_base = 70
        elif status == "delayed" or delay_risk >= 0.5:
            action_type = "contact_customer" if is_vip or ltv >= 500 else "prioritize_order"
            owner = "customer_care" if is_vip else "logistics"
            score_base = 60
        else:
            continue

        # Boost si VIP
        if is_vip:
            score_base += 10
        score = min(100, score_base + sev // 4)

        # Euros en riesgo
        eur_risk = order["value"] + REFUND_OVERHEAD
        if is_vip:
            eur_risk += ltv * VIP_CHURN_LTV_FACTOR

        confidence = 0.92 if not s.get("_error") else 0.5

        out.append({
            "action_type": action_type,
            "target_id": order_id,
            "owner": owner,
            "score": score,
            "confidence": confidence,
            "euros_at_risk": _eur(eur_risk),
            "euros_recoverable": _eur(eur_risk * confidence * EXEC_FACTOR.get(action_type, 0.6)),
            "vips_affected": 1 if is_vip else 0,
            "evidence": {
                "order_id": order_id,
                "customer_id": order["customer_id"],
                "is_vip": is_vip,
                "ltv": ltv,
                "shipping_status": status,
                "delay_risk": delay_risk,
                "delay_reason": reason,
                "estimated_delivery_date": s.get("estimated_delivery_date"),
                "requires_manual_review": s.get("requires_manual_review", False),
                "delivery_attempts": s.get("delivery_attempts", 0),
                "shipping_severity": sev,
                "data_source": "shipping_api",  # marcador de origen
            },
        })
    return out


def detect_restock(data, idx) -> List[Dict]:
    """Lente 1 bis: alertas de reposición para SKUs con alta demanda."""
    out = []
    for sku, inv in idx["inv_by_sku"].items():
        if inv["available"] >= 10:
            continue
        if inv["incoming"] > 0:
            continue  # ya hay reposición
        # alta demanda?
        if inv["sell_through_rate"] < 0.4 and inv["page_views"] < 2000:
            continue
        score = 50 + 30 * inv["sell_through_rate"]
        score = min(100, score)
        # cap conservador: 1 hora de demanda al precio unitario, máximo €500
        eur_potential = min(500, inv["page_views"] * inv["conversion_rate"] * inv["unit_price"] * 0.05)
        out.append({
            "action_type": "restock_alert",
            "target_id": sku,
            "owner": "logistics",
            "score": score,
            "confidence": 0.7,
            "euros_at_risk": 0,
            "euros_recoverable": _eur(eur_potential),
            "vips_affected": 0,
            "evidence": {
                "sku": sku,
                "product_name": inv["product_name"],
                "available": inv["available"],
                "page_views": inv["page_views"],
                "sell_through_rate": inv["sell_through_rate"],
                "incoming": inv["incoming"],
            },
        })
    return out


# ---------------------------------------------------------------- pipeline

def build_all_candidates(data, idx, shipping_data=None) -> List[Dict]:
    cands = []
    cands += detect_oversell_risks(data, idx)
    cands += detect_campaign_mismatch(data, idx)
    cands += detect_vip_at_risk(data, idx)
    cands += detect_urgent_tickets(data, idx)
    cands += detect_manual_review(data, idx)
    cands += detect_opportunities(data, idx)
    cands += detect_restock(data, idx)
    if shipping_data:
        cands += detect_shipping_issues(data, idx, shipping_data)
    return cands


def rank_top10(candidates: List[Dict]) -> List[Dict]:
    """Aplica balanceo entre owners y devuelve top 10."""
    import math
    for c in candidates:
        # Final score = severity * confidence + euros + vips
        eur_boost = math.sqrt(max(1, c["euros_recoverable"])) * 1.5
        vip_boost = c["vips_affected"] * 12
        c["_final"] = c["score"] * (0.5 + 0.5 * c["confidence"]) + eur_boost + vip_boost
    candidates.sort(key=lambda x: x["_final"], reverse=True)

    # dedupe por (action_type, target_id)
    seen = set()
    deduped = []
    for c in candidates:
        k = (c["action_type"], c["target_id"])
        if k in seen:
            continue
        seen.add(k)
        deduped.append(c)

    # balanceo: máximo 4 por owner
    out, owner_count = [], {}
    for c in deduped:
        ow = c["owner"]
        if owner_count.get(ow, 0) >= 4:
            continue
        out.append(c)
        owner_count[ow] = owner_count.get(ow, 0) + 1
        if len(out) >= 10:
            break

    # forzar al menos 1 redirect_campaign_budget (oportunidad) si existe en deduped
    has_opportunity = any(c["action_type"] == "redirect_campaign_budget" for c in out)
    if not has_opportunity:
        opps = [c for c in deduped if c["action_type"] == "redirect_campaign_budget"]
        if opps:
            # quitamos el de menor _final del top y metemos la oportunidad
            out.sort(key=lambda x: x["_final"], reverse=True)
            out = out[:9] + [opps[0]]

    # forzar al menos 1 manual_review_order si existe (operations no quede ciego)
    has_manual = any(c["action_type"] == "manual_review_order" for c in out)
    if not has_manual and len(out) >= 10:
        manuals = [c for c in deduped if c["action_type"] == "manual_review_order"]
        if manuals:
            # quitamos el de menor _final que no sea oportunidad y metemos el manual
            out.sort(key=lambda x: x["_final"], reverse=True)
            removable = [c for c in out if c["action_type"] != "redirect_campaign_budget"]
            if removable:
                worst = removable[-1]
                out.remove(worst)
                out.append(manuals[0])

    # reordenar por _final descendente
    out.sort(key=lambda x: x["_final"], reverse=True)

    # asignar rank final
    for i, c in enumerate(out):
        c["rank"] = i + 1
    return out


if __name__ == "__main__":
    from lib.loader import load_all, build_indexes
    data = load_all()
    idx = build_indexes(data)
    cands = build_all_candidates(data, idx)
    print(f"Total candidatos: {len(cands)}")
    top = rank_top10(cands)
    for c in top:
        print(f"#{c['rank']} [{c['owner']:13s}] {c['action_type']:25s} {c['target_id']:18s} score={c['score']:.0f} eur_risk=€{c['euros_at_risk']:.0f} eur_rec=€{c['euros_recoverable']:.0f} vips={c['vips_affected']}")
