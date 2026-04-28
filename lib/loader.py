"""Carga robusta de CSVs. Tolerante a columnas faltantes y valores sucios."""
import os, csv
from datetime import datetime
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "candidate_csvs")


def _coerce_num(v: Any, default=None):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _coerce_int(v: Any, default=0):
    n = _coerce_num(v, None)
    return int(n) if n is not None else default


def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("true", "1", "yes", "si", "sí")


def _coerce_dt(v: Any):
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:
        return None


def _read(path: str):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_all(data_dir=DATA_DIR):
    """Devuelve dict con todas las tablas casteadas y normalizadas."""
    out = {}

    # inventory
    out["inventory"] = []
    for r in _read(os.path.join(data_dir, "inventory.csv")):
        out["inventory"].append({
            "sku": r.get("sku", "").strip(),
            "product_name": r.get("product_name", "").strip(),
            "category": r.get("category", "").strip(),
            "size": r.get("size", "").strip(),
            "unit_price": _coerce_num(r.get("unit_price"), 0.0),
            "warehouse_stock": _coerce_int(r.get("warehouse_stock")),
            "available": _coerce_int(r.get("inventory_available_units")),
            "reserved": _coerce_int(r.get("inventory_reserved_units")),
            "incoming": _coerce_int(r.get("inventory_incoming_units")),
            "incoming_eta": _coerce_dt(r.get("inventory_incoming_eta")),
            "sell_through_rate": _coerce_num(r.get("sell_through_rate_last_hour"), 0),
            "page_views": _coerce_int(r.get("product_page_views_last_hour")),
            "conversion_rate": _coerce_num(r.get("conversion_rate_last_hour"), 0),
        })

    # customers
    out["customers"] = []
    for r in _read(os.path.join(data_dir, "customers.csv")):
        out["customers"].append({
            "customer_id": r.get("customer_id", "").strip(),
            "segment": r.get("customer_segment", "").strip(),
            "ltv": _coerce_num(r.get("customer_lifetime_value"), 0.0),
            "orders_count": _coerce_int(r.get("customer_orders_count")),
            "returns_count": _coerce_int(r.get("customer_returns_count")),
            "is_vip": _coerce_bool(r.get("is_vip")),
            "preferred_city": r.get("preferred_city", "").strip(),
            "email_opt_in": _coerce_bool(r.get("email_opt_in")),
        })

    # orders
    out["orders"] = []
    for r in _read(os.path.join(data_dir, "orders.csv")):
        out["orders"].append({
            "order_id": r.get("order_id", "").strip(),
            "customer_id": r.get("customer_id", "").strip(),
            "created_at": _coerce_dt(r.get("created_at")),
            "status": r.get("order_status", "").strip(),
            "sku": r.get("sku", "").strip(),
            "quantity": _coerce_int(r.get("quantity"), 1),
            "value": _coerce_num(r.get("order_value"), 0.0),
            "shipping_city": r.get("shipping_city", "").strip(),
            "shipping_country": r.get("shipping_country", "").strip(),
            "shipping_method": r.get("shipping_method", "").strip(),
            "customer_segment": r.get("customer_segment", "").strip(),
            "campaign_source": r.get("campaign_source", "").strip(),
        })

    # order_items (opcional)
    out["order_items"] = []
    for r in _read(os.path.join(data_dir, "order_items.csv")):
        out["order_items"].append({
            "order_id": r.get("order_id", "").strip(),
            "sku": r.get("sku", "").strip(),
            "quantity": _coerce_int(r.get("quantity"), 1),
            "unit_price": _coerce_num(r.get("unit_price"), 0.0),
        })

    # campaigns
    out["campaigns"] = []
    for r in _read(os.path.join(data_dir, "campaigns.csv")):
        out["campaigns"].append({
            "campaign_id": r.get("campaign_id", "").strip(),
            "source": r.get("campaign_source", "").strip(),
            "status": r.get("status", "").strip(),
            "target_sku": r.get("target_sku", "").strip(),
            "target_city": r.get("target_city", "").strip(),
            "intensity": r.get("campaign_intensity", "").strip(),
            "budget_spent": _coerce_num(r.get("budget_spent"), 0.0),
            "traffic_growth": _coerce_num(r.get("traffic_growth"), 0.0),
            "conversion_rate": _coerce_num(r.get("conversion_rate"), 0.0),
            "started_at": _coerce_dt(r.get("started_at")),
        })

    # tickets
    out["tickets"] = []
    for r in _read(os.path.join(data_dir, "support_tickets.csv")):
        out["tickets"].append({
            "ticket_id": r.get("ticket_id", "").strip(),
            "order_id": r.get("order_id", "").strip(),
            "customer_id": r.get("customer_id", "").strip(),
            "created_at": _coerce_dt(r.get("created_at")),
            "channel": r.get("channel", "").strip(),
            "message": r.get("support_ticket_message", "").strip(),
            "urgency": r.get("support_ticket_urgency", "").strip().lower(),
            "sentiment": r.get("support_ticket_sentiment", "").strip().lower(),
        })

    return out


def build_indexes(data: dict):
    """Crea diccionarios de lookup para uso rápido."""
    idx = {}
    idx["inv_by_sku"] = {x["sku"]: x for x in data["inventory"]}
    idx["cust_by_id"] = {x["customer_id"]: x for x in data["customers"]}
    idx["camp_by_sku"] = {}
    for c in data["campaigns"]:
        idx["camp_by_sku"].setdefault(c["target_sku"], []).append(c)
    idx["orders_by_sku"] = {}
    idx["orders_by_cust"] = {}
    for o in data["orders"]:
        idx["orders_by_sku"].setdefault(o["sku"], []).append(o)
        idx["orders_by_cust"].setdefault(o["customer_id"], []).append(o)
    idx["tickets_by_cust"] = {}
    idx["tickets_by_order"] = {}
    for t in data["tickets"]:
        idx["tickets_by_cust"].setdefault(t["customer_id"], []).append(t)
        if t["order_id"]:
            idx["tickets_by_order"].setdefault(t["order_id"], []).append(t)
    return idx


if __name__ == "__main__":
    d = load_all()
    print(f"inventory: {len(d['inventory'])}, customers: {len(d['customers'])}, orders: {len(d['orders'])}, tickets: {len(d['tickets'])}, campaigns: {len(d['campaigns'])}")
