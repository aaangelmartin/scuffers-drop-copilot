"""Counterfactual Twin: simula 'sin actuar' vs 'ejecutar plan'."""

REFUND_OVERHEAD = 12.0
VIP_CHURN_FACTOR = 0.20
NON_VIP_CHURN_FACTOR = 0.05


def simulate_do_nothing(data, idx) -> dict:
    """Calcula pérdidas si no se ejecuta ninguna acción."""
    oversells = 0
    euros_lost = 0.0
    vips_hurt = set()
    affected_orders = []
    for sku, inv in idx["inv_by_sku"].items():
        pending = [o for o in idx["orders_by_sku"].get(sku, []) if o["status"] in ("paid", "processing", "packed", "payment_review")]
        units_short = max(0, len(pending) - max(0, inv["available"]))
        if units_short == 0:
            continue
        # ordenar pending por LTV descendente — los VIPs caen primero (peor caso)
        # asumimos que los oversells son los últimos `units_short` (peor caso ordenando por created_at)
        pending_sorted = sorted(pending, key=lambda o: o["created_at"] or 0)
        oversold = pending_sorted[-units_short:]
        oversells += units_short
        for o in oversold:
            unit_price = inv["unit_price"] or o["value"]
            euros_lost += unit_price + REFUND_OVERHEAD
            c = idx["cust_by_id"].get(o["customer_id"])
            if c:
                if c["is_vip"]:
                    vips_hurt.add(c["customer_id"])
                    euros_lost += c["ltv"] * VIP_CHURN_FACTOR
                elif c["ltv"] >= 500:
                    euros_lost += c["ltv"] * NON_VIP_CHURN_FACTOR
            affected_orders.append(o["order_id"])

    # añadir tickets sin atender que generan churn
    for t in data["tickets"]:
        if t["urgency"] in ("urgent", "high") and t["sentiment"] == "negative":
            c = idx["cust_by_id"].get(t["customer_id"])
            if c and c["is_vip"]:
                vips_hurt.add(c["customer_id"])
                euros_lost += c["ltv"] * VIP_CHURN_FACTOR * 0.5  # mitad si es solo ticket sin oversell

    return {
        "oversells": oversells,
        "euros_lost": round(euros_lost, 2),
        "vips_hurt": len(vips_hurt),
        "vips_hurt_ids": list(vips_hurt),
        "affected_orders": affected_orders,
        "brand_risk": "high" if oversells > 10 or len(vips_hurt) >= 2 else ("medium" if oversells > 3 else "low"),
    }


def simulate_with_plan(do_nothing: dict, top_actions: list) -> dict:
    """Aplica las acciones del plan al baseline 'do_nothing'."""
    oversells_avoided = 0
    euros_recovered = 0.0
    vips_protected = set()

    for a in top_actions:
        at = a["action_type"]
        ev = a.get("evidence", {})
        # Cada acción "neutraliza" parte del riesgo según su recoverable y tipo
        if at == "pause_campaign":
            oversells_avoided += int(ev.get("units_short", 0)) * a["confidence"]
            euros_recovered += a["euros_recoverable"]
        elif at == "prevent_oversell":
            oversells_avoided += int(ev.get("units_short", 0)) * a["confidence"] * 0.85
            euros_recovered += a["euros_recoverable"]
            for v in ev.get("vips_in_pending", []):
                vips_protected.add(v)
        elif at == "contact_customer":
            cust_id = ev.get("customer_id")
            if cust_id:
                vips_protected.add(cust_id)
            euros_recovered += a["euros_recoverable"] * 0.7
        elif at == "prioritize_order":
            cust_id = ev.get("customer_id")
            if cust_id:
                vips_protected.add(cust_id)
            euros_recovered += a["euros_recoverable"]
        elif at == "escalate_ticket":
            cust_id = ev.get("customer_id")
            if cust_id and ev.get("is_vip"):
                vips_protected.add(cust_id)
            euros_recovered += a["euros_recoverable"]
        elif at == "redirect_campaign_budget":
            euros_recovered += a["euros_recoverable"] * 0.5
        # restock_alert y manual_review tienen impacto modesto
        else:
            euros_recovered += a["euros_recoverable"] * 0.3

    # Cap: no podemos recuperar más de lo perdido
    euros_recovered = min(euros_recovered, do_nothing["euros_lost"] * 0.95)
    oversells_avoided = min(round(oversells_avoided), do_nothing["oversells"])
    vips_protected_count = min(len(vips_protected), do_nothing["vips_hurt"])

    return {
        "oversells": max(0, do_nothing["oversells"] - oversells_avoided),
        "euros_lost": round(do_nothing["euros_lost"] - euros_recovered, 2),
        "vips_hurt": max(0, do_nothing["vips_hurt"] - vips_protected_count),
        "oversells_avoided": oversells_avoided,
        "euros_recovered": round(euros_recovered, 2),
        "vips_protected": vips_protected_count,
        "brand_risk": "low" if do_nothing["brand_risk"] != "high" or vips_protected_count >= do_nothing["vips_hurt"] else "medium",
    }


def compute_simulation(data, idx, top_actions: list) -> dict:
    do_nothing = simulate_do_nothing(data, idx)
    plan = simulate_with_plan(do_nothing, top_actions)
    delta = {
        "euros_saved": round(do_nothing["euros_lost"] - plan["euros_lost"], 2),
        "oversells_avoided": do_nothing["oversells"] - plan["oversells"],
        "vips_protected": do_nothing["vips_hurt"] - plan["vips_hurt"],
        "brand_risk_reduction": f"{do_nothing['brand_risk']} → {plan['brand_risk']}",
    }
    return {"do_nothing": do_nothing, "execute_plan": plan, "delta": delta}


def compute_health_score(data, idx, do_nothing: dict) -> dict:
    """Calcula Health Score 0-100 y desglose por componentes."""
    # Componentes (cada uno 0-100, mayor = mejor)
    # 1. Stock health: % de SKUs sin oversell
    skus_total = len(idx["inv_by_sku"])
    skus_critical = 0
    for sku, inv in idx["inv_by_sku"].items():
        pending = [o for o in idx["orders_by_sku"].get(sku, []) if o["status"] in ("paid", "processing", "packed")]
        if max(0, len(pending) - max(0, inv["available"])) > 0:
            skus_critical += 1
    stock_health = round(100 * (1 - skus_critical / max(1, skus_total)))

    # 2. Customer health: % de VIPs sin riesgo
    vips_total = sum(1 for c in data["customers"] if c["is_vip"])
    customer_health = round(100 * (1 - do_nothing["vips_hurt"] / max(1, vips_total)))

    # 3. Pipeline health: % de pedidos sin riesgo de oversell
    orders_total = len([o for o in data["orders"] if o["status"] in ("paid", "processing", "packed")])
    pipeline_health = round(100 * (1 - len(do_nothing["affected_orders"]) / max(1, orders_total)))

    # 4. Campaign alignment: % de campañas activas que NO apuntan a SKU roto
    active_campaigns = [c for c in data["campaigns"] if c["status"] == "active"]
    bad_campaigns = 0
    for c in active_campaigns:
        inv = idx["inv_by_sku"].get(c["target_sku"])
        if inv and inv["available"] - inv["reserved"] < 0:
            bad_campaigns += 1
    campaign_health = round(100 * (1 - bad_campaigns / max(1, len(active_campaigns))))

    components = {
        "stock_health": stock_health,
        "customer_health": customer_health,
        "pipeline_health": pipeline_health,
        "campaign_health": campaign_health,
    }
    # Score = media ponderada
    weights = {"stock_health": 0.30, "customer_health": 0.30, "pipeline_health": 0.20, "campaign_health": 0.20}
    score = round(sum(components[k] * w for k, w in weights.items()))
    if score < 50:
        verdict = "CRITICAL"
    elif score < 75:
        verdict = "WARNING"
    else:
        verdict = "HEALTHY"
    return {
        "score": score,
        "verdict": verdict,
        "components": components,
        "weights": weights,
    }
