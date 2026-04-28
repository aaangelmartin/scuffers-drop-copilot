"""Cliente para la Shipping Status API de Scuffers.

Endpoint: GET https://lkuutmnykcnbfmbpopcu.functions.supabase.co/api/shipping-status/{order_id}
Header obligatorio: X-Candidate-Id: SCF-2026-XXXX

Diseño:
  - Cache en disco (out/_shipping_cache.json) para no martillar la API
  - Manejo robusto de errores (404, timeout, JSON inválido, campos faltantes)
  - Devuelve siempre un dict (con `_error` si algo falló) para que el resto del pipeline no rompa
  - TTL de cache: 600s (10 min) — suficiente para una demo, evita rate limits
  - Solo consulta los pedidos RELEVANTES (no los 180): solo los que tienen un riesgo asociado o son VIP
"""
import os, json, time, urllib.request, urllib.error

API_BASE = "https://lkuutmnykcnbfmbpopcu.functions.supabase.co/api/shipping-status"
CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "out", "_shipping_cache.json")
CACHE_TTL = 600  # segundos

# Status que requieren ATENCIÓN urgente
ALERT_STATUSES = {"delayed", "exception", "lost", "returned_to_sender"}
SAFE_STATUSES = {"delivered", "out_for_delivery"}

# Razones de retraso prioritarias (más graves primero)
SEVERE_REASONS = {"customs_hold", "lost", "address_validation_error"}


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        return json.load(open(CACHE_FILE))
    except Exception:
        return {}


def _save_cache(c):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(c, f)


def fetch_shipping(order_id: str, candidate_id: str = None, use_cache=True) -> dict:
    """Devuelve el dict de shipping para un order_id.
    Si la API falla o el candidate_id falta, devuelve {'_error': '...', 'order_id': order_id}."""
    if not candidate_id:
        candidate_id = os.getenv("SCUFFERS_CANDIDATE_ID", "")
    candidate_id = (candidate_id or "").strip().lstrip("#")
    if not candidate_id:
        return {"order_id": order_id, "_error": "missing_candidate_id"}

    # Cache check
    cache = _load_cache() if use_cache else {}
    cached = cache.get(order_id)
    if cached and (time.time() - cached.get("_cached_at", 0) < CACHE_TTL):
        return cached

    url = f"{API_BASE}/{order_id}"
    req = urllib.request.Request(url, headers={
        "X-Candidate-Id": candidate_id,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            data["_cached_at"] = time.time()
            data["_error"] = None
            cache[order_id] = data
            _save_cache(cache)
            return data
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        result = {"order_id": order_id, "_error": f"http_{e.code}", "_body": body}
        if e.code == 404:
            cache[order_id] = {**result, "_cached_at": time.time()}
            _save_cache(cache)
        return result
    except Exception as e:
        return {"order_id": order_id, "_error": f"exception:{type(e).__name__}"}


def is_problematic(s: dict) -> bool:
    """¿Este envío necesita atención?"""
    if not s or s.get("_error"):
        return False
    status = (s.get("shipping_status") or "").lower()
    if status in ALERT_STATUSES:
        return True
    if (s.get("delay_risk") or 0) >= 0.5:
        return True
    if s.get("requires_manual_review"):
        return True
    return False


def severity_score(s: dict) -> int:
    """0-100 basado en el shipping. Mayor = peor."""
    if not s or s.get("_error"):
        return 0
    status = (s.get("shipping_status") or "").lower()
    score = 0
    if status == "lost": score += 90
    elif status == "exception": score += 75
    elif status == "delayed": score += 60
    elif status == "returned_to_sender": score += 65
    elif status in SAFE_STATUSES: score = max(0, score - 20)
    delay_risk = s.get("delay_risk") or 0
    score += int(delay_risk * 40)
    if s.get("requires_manual_review"):
        score += 20
    reason = (s.get("delay_reason") or "").lower()
    if reason in SEVERE_REASONS:
        score += 15
    delivery_attempts = s.get("delivery_attempts") or 0
    if delivery_attempts >= 2:
        score += 10
    return min(100, score)


def fetch_relevant_orders(orders, idx, candidate_id=None, max_calls=50) -> dict:
    """Decide qué pedidos consultar y devuelve dict {order_id: shipping_data}.
    Estrategia: solo consultamos los pedidos que ya identificamos como problemáticos
    (oversell-risk, VIPs, tickets abiertos, payment_review) hasta `max_calls` para no saturar."""
    relevant_ids = set()

    # 1. Pedidos con ticket abierto
    for tickets in idx.get("tickets_by_order", {}).keys():
        if tickets:
            relevant_ids.add(tickets)

    # 2. Pedidos de VIPs activos
    vips = {c["customer_id"] for c in idx.get("cust_by_id", {}).values() if c.get("is_vip")}
    for o in orders:
        if o["customer_id"] in vips and o["status"] in ("paid", "processing", "packed", "payment_review"):
            relevant_ids.add(o["order_id"])

    # 3. Pedidos en SKUs con stock crítico
    for sku, inv in idx.get("inv_by_sku", {}).items():
        if inv.get("available", 0) <= 5:
            for o in idx.get("orders_by_sku", {}).get(sku, []):
                if o["status"] in ("paid", "processing", "packed", "payment_review"):
                    relevant_ids.add(o["order_id"])

    # 4. Pedidos en payment_review
    for o in orders:
        if o.get("status") == "payment_review":
            relevant_ids.add(o["order_id"])

    # Limitar para no martillar
    relevant_ids = list(relevant_ids)[:max_calls]
    print(f"   📦 Consultando shipping para {len(relevant_ids)} pedidos relevantes...")

    out = {}
    for oid in relevant_ids:
        s = fetch_shipping(oid, candidate_id)
        out[oid] = s
    # Stats
    ok = sum(1 for s in out.values() if not s.get("_error"))
    err = len(out) - ok
    problematic = sum(1 for s in out.values() if is_problematic(s))
    print(f"   📊 Shipping: {ok} OK, {err} errores, {problematic} problemáticos")
    return out


# ==================== Helpers para humanizar shipping data

SHIPPING_STATUS_ES = {
    "label_created": "Etiqueta creada",
    "picked_up": "Recogido",
    "in_transit": "En tránsito",
    "at_sorting_center": "En centro de clasificación",
    "out_for_delivery": "Saliendo para entrega",
    "delivered": "Entregado",
    "delayed": "Retrasado",
    "exception": "Incidencia",
    "lost": "Perdido",
    "returned_to_sender": "Devuelto al remitente",
}

DELAY_REASON_ES = {
    "high_volume": "Alto volumen",
    "carrier_capacity_issue": "Problema de capacidad del transportista",
    "address_validation_error": "Error de dirección",
    "weather_disruption": "Disrupción climática",
    "warehouse_delay": "Retraso en almacén",
    "customs_hold": "Retención en aduanas",
    "unknown": "Causa desconocida",
}


def humanize_shipping(s: dict) -> str:
    """Genera una frase corta human-friendly del estado del envío."""
    if not s or s.get("_error"):
        return ""
    status = SHIPPING_STATUS_ES.get(s.get("shipping_status", ""), s.get("shipping_status", ""))
    risk = s.get("delay_risk") or 0
    reason = DELAY_REASON_ES.get((s.get("delay_reason") or "").lower(), "")
    eta = s.get("estimated_delivery_date", "")
    parts = [f"📦 {status}"] if status else []
    if risk >= 0.3:
        parts.append(f"⏰ riesgo retraso {int(risk*100)}%")
    if reason and risk >= 0.3:
        parts.append(f"motivo: {reason.lower()}")
    if eta:
        parts.append(f"ETA {eta}")
    if s.get("requires_manual_review"):
        parts.append("⚠️ revisión manual requerida")
    return " · ".join(parts)


if __name__ == "__main__":
    # Smoke test
    cid = os.getenv("SCUFFERS_CANDIDATE_ID", "")
    if not cid:
        print("⚠️  SCUFFERS_CANDIDATE_ID no configurado en .env")
    else:
        r = fetch_shipping("ORD-10492", cid, use_cache=False)
        print(json.dumps(r, indent=2))
        print(humanize_shipping(r))
