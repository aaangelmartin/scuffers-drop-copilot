"""Traducciones human-readable. Convierte SKUs/códigos a etiquetas para personas no-técnicas."""

ACTION_LABELS = {
    "pause_campaign": "Pausar campaña",
    "prevent_oversell": "Bloquear venta",
    "prioritize_order": "Priorizar pedido",
    "contact_customer": "Contactar cliente",
    "escalate_ticket": "Escalar a humano",
    "manual_review_order": "Revisar pedido manualmente",
    "restock_alert": "Pedir reposición",
    "redirect_campaign_budget": "Redirigir presupuesto",
}

ACTION_VERBS_DONE = {
    "pause_campaign": "Has pausado la campaña",
    "prevent_oversell": "Has bloqueado la venta de",
    "prioritize_order": "Has priorizado el pedido",
    "contact_customer": "Has contactado al cliente",
    "escalate_ticket": "Has escalado el ticket",
    "manual_review_order": "Has marcado para revisión el pedido",
    "restock_alert": "Has pedido reposición de",
    "redirect_campaign_budget": "Has redirigido el presupuesto de",
}

OWNER_LABELS = {
    "logistics": "Logística",
    "customer_care": "Atención al Cliente",
    "marketing": "Marketing",
    "operations": "Operaciones",
}

VERDICT_LABELS = {"HEALTHY": "Todo bien", "WARNING": "Atención", "CRITICAL": "Crítico"}

COMPONENT_LABELS = {
    "stock_health": "Inventario",
    "customer_health": "Clientes",
    "pipeline_health": "Pedidos",
    "campaign_health": "Campañas",
}

BRAND_RISK_LABELS = {"low": "bajo", "medium": "medio", "high": "alto"}

URGENCY_LABELS = {"urgent": "urgente", "high": "alta", "medium": "media", "low": "baja"}


def confidence_word(c) -> str:
    try:
        c = float(c)
    except Exception:
        return "media"
    if c >= 0.85: return "alta"
    if c >= 0.65: return "media"
    return "baja"


def fmt_eur(n) -> str:
    """Formato europeo: 1.234,56 €"""
    try:
        n = float(n)
    except Exception:
        return "€0"
    s = f"{n:,.0f}".replace(",", ".")
    return f"€{s}"


def friendly_target(target_id: str, idx: dict) -> str:
    """Traduce un código a etiqueta humana usando los índices cargados."""
    if not target_id:
        return ""
    tid = target_id.strip()

    # SKU (HOODIE-BLK-M, TEE-WHT-S, etc.)
    inv = idx.get("inv_by_sku", {}).get(tid)
    if inv:
        product = inv.get("product_name", "")
        size = inv.get("size", "")
        if product and size:
            return f"{product} · talla {size}"
        return product or tid

    # Campaña
    if tid.startswith("CMP-"):
        for camps in idx.get("camp_by_sku", {}).values():
            for c in camps:
                if c.get("campaign_id") == tid:
                    src = (c.get("source") or "").capitalize()
                    city = c.get("target_city", "")
                    target_sku = c.get("target_sku", "")
                    sku_label = friendly_target(target_sku, idx) if target_sku else ""
                    parts = [f"Campaña {src}" if src else "Campaña"]
                    if city: parts.append(city)
                    if sku_label: parts.append(sku_label)
                    return " · ".join(parts)
        return f"Campaña {tid}"

    # Cliente
    if tid.startswith("CUS-"):
        c = idx.get("cust_by_id", {}).get(tid)
        if c:
            label_parts = []
            if c.get("is_vip"): label_parts.append("Cliente VIP")
            else: label_parts.append("Cliente")
            if c.get("preferred_city"): label_parts.append(c["preferred_city"])
            if c.get("ltv"): label_parts.append(f"LTV {fmt_eur(c['ltv'])}")
            return " · ".join(label_parts)
        return f"Cliente {tid}"

    # Ticket
    if tid.startswith("TCK-"):
        return f"Ticket #{tid.replace('TCK-','')}"

    # Pedido
    if tid.startswith("ORD-"):
        return f"Pedido #{tid.replace('ORD-','')}"

    return tid


def action_state_key(action_type: str, target_id: str) -> str:
    return f"{action_type}:{target_id}"
