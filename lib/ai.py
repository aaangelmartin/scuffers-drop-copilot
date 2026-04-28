"""Wrapper Gemini con cache y fallback a templates si la API falla.

Funciones expuestas:
  - enrich_action(candidate) -> añade title, reason, expected_impact, pre_built_message
  - counterfactual_narrative(simulation) -> párrafo ejecutivo
"""
import os, json, hashlib, time
import urllib.request, urllib.error

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "out", "_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"


def _cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()[:16]


def _gemini(prompt: str, max_tokens=400, temperature=0.7) -> "str | None":
    """Llama a Gemini con cache. Devuelve None si falla."""
    if not GEMINI_API_KEY:
        return None
    key = _cache_key(prompt)
    cache_path = os.path.join(CACHE_DIR, f"{key}.txt")
    if os.path.exists(cache_path):
        return open(cache_path).read()

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "thinkingConfig": {"thinkingBudget": 0},  # 2.5-flash: desactivar thinking interno
        },
    }).encode()
    req = urllib.request.Request(
        GEMINI_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if text:
                    with open(cache_path, "w") as f:
                        f.write(text)
                    return text
                return None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 + attempt * 3)
                continue
            return None
        except Exception:
            return None
    return None


# ----------------------------------------------------------- ENRICH ACTION

ACTION_TEMPLATES = {
    "pause_campaign": {
        "title": "Pausar campaña {target_id} antes de oversell masivo",
        "expected_impact": "Evita oversells y protege presupuesto malgastado en SKU sin stock.",
    },
    "prevent_oversell": {
        "title": "Bloquear venta de {target_id} para evitar refunds",
        "expected_impact": "Evita devoluciones masivas y protege experiencia de cliente.",
    },
    "prioritize_order": {
        "title": "Priorizar envío del pedido {target_id}",
        "expected_impact": "Acelera entrega de cliente clave / VIP y reduce ticket entrante.",
    },
    "contact_customer": {
        "title": "Contactar proactivamente a {target_id}",
        "expected_impact": "Reduce churn de cliente alto-LTV mediante comunicación proactiva.",
    },
    "escalate_ticket": {
        "title": "Escalar ticket {target_id} a revisión humana urgente",
        "expected_impact": "Resolución rápida de incidencia con sentimiento negativo.",
    },
    "manual_review_order": {
        "title": "Revisar manualmente el pedido {target_id}",
        "expected_impact": "Detecta fraude/ruido antes de envío.",
    },
    "restock_alert": {
        "title": "Solicitar reposición urgente de {target_id}",
        "expected_impact": "Recupera capacidad de venta antes de que la demanda se enfríe.",
    },
    "redirect_campaign_budget": {
        "title": "Redirigir presupuesto de {target_id} a SKU con stock disponible",
        "expected_impact": "Convierte presupuesto mal asignado en venta efectiva.",
    },
}


def _fallback_action(c: dict) -> dict:
    tmpl = ACTION_TEMPLATES.get(c["action_type"], {"title": "Acción {target_id}", "expected_impact": "Reduce riesgo operativo."})
    return {
        "title": tmpl["title"].format(target_id=c["target_id"]),
        "reason": _build_reason_from_evidence(c),
        "expected_impact": tmpl["expected_impact"],
        "pre_built_message": _default_message(c),
    }


def _build_reason_from_evidence(c: dict) -> str:
    """Si Gemini falla, construimos un reason determinista decente desde la evidence."""
    e = c.get("evidence", {})
    at = c["action_type"]
    if at == "pause_campaign":
        return (f"Campaña {e.get('source','?')} con intensidad {e.get('intensity','?')} apuntando a {e.get('target_sku','?')} "
                f"en {e.get('target_city','?')}. Stock disponible: {e.get('available',0)} vs reservas {e.get('reserved',0)}. "
                f"{e.get('pending_orders',0)} pedidos pendientes y {e.get('units_short',0)} unidades cortas.")
    if at == "prevent_oversell":
        return (f"SKU {e.get('sku','?')} ({e.get('product_name','?')}): {e.get('available',0)} disponibles vs {e.get('reserved',0)} reservas "
                f"y {e.get('pending_orders',0)} pedidos pendientes. {e.get('units_short',0)} unidades cortas. "
                f"VIPs entre afectados: {len(e.get('vips_in_pending', []))}.")
    if at == "contact_customer":
        return (f"Cliente {e.get('customer_id','?')} (LTV €{e.get('ltv',0):.0f}, segmento {e.get('segment','?')}). "
                f"Señales de riesgo: {', '.join(e.get('risk_signals', []))}. "
                f"Pedidos rotos: {len(e.get('broken_order_ids', []))}.")
    if at == "escalate_ticket":
        return (f"Ticket {e.get('ticket_id','?')} canal {e.get('channel','?')}: urgencia {e.get('urgency','?')}, "
                f"sentimiento {e.get('sentiment','?')}. VIP={e.get('is_vip',False)}, LTV €{e.get('ltv',0):.0f}. "
                f"Mensaje: \"{e.get('message','')[:120]}\"")
    if at == "manual_review_order":
        return (f"Pedido {e.get('order_id','?')} flags {','.join(e.get('flags',[]))}. "
                f"Cliente con {e.get('customer_returns_count',0)} devoluciones previas. Valor €{e.get('value',0)}.")
    if at == "restock_alert":
        return (f"SKU {e.get('sku','?')}: {e.get('available',0)} unidades, {e.get('page_views',0)} vistas/h, "
                f"sell_through {e.get('sell_through_rate',0):.2f}, sin reposición programada.")
    if at == "redirect_campaign_budget":
        return (f"Campaña {e.get('campaign_id','?')} apunta a {e.get('current_target','?')} (stock {e.get('current_target_available',0)}). "
                f"Sugerencia: redirigir a {e.get('suggested_target','?')} ({e.get('suggested_target_available',0)} unidades, "
                f"{e.get('suggested_target_views',0)} vistas/h).")
    return f"Score {c['score']:.0f}, riesgo €{c.get('euros_at_risk',0):.0f}."


def _default_message(c: dict) -> str:
    e = c.get("evidence", {})
    at = c["action_type"]
    if at == "contact_customer":
        return ("Hola, gracias por confiar en Scuffers ⚡. Hemos detectado un problema con tu pedido y "
                "queremos resolverlo antes de que te enteres. Te tendremos actualizado en las próximas 2h.")
    if at == "prioritize_order":
        return "Tu pedido ha sido priorizado en el almacén. Saldrá hoy. Gracias por la paciencia 🖤"
    if at == "escalate_ticket":
        return f"Hola, hemos escalado tu consulta a un humano que va a darte respuesta en menos de 30 min."
    return ""


def enrich_action(c: dict, idx=None) -> dict:
    """Pide a Gemini que rellene title, reason, expected_impact, pre_built_message.
    Si falla, usa fallback determinista."""
    fallback = _fallback_action(c)
    e = c.get("evidence", {})

    prompt = f"""Eres un Director de Operaciones de Scuffers (marca de streetwear premium española) durante un drop de alta demanda.
Genera SOLO un JSON válido (sin markdown) con estas claves: title, reason, expected_impact, pre_built_message.

- title: máximo 80 caracteres, imperativo, claro, accionable
- reason: 2-3 frases con números concretos del problema, justificando POR QUÉ esto es prioritario AHORA
- expected_impact: 1-2 frases con el resultado esperado (€, oversells evitados, VIPs protegidos)
- pre_built_message: mensaje LISTO para enviar al cliente afectado, tono Scuffers (urbano, directo, sin emojis abusivos, español natural). Si la acción no afecta a un cliente específico, devuelve "" (string vacío)

ACCIÓN: {c['action_type']}
TARGET: {c['target_id']}
DATOS:
{json.dumps(e, ensure_ascii=False, default=str, indent=2)}

CONTEXTO ECONÓMICO:
- Euros en riesgo: €{c['euros_at_risk']}
- Euros recuperables: €{c['euros_recoverable']}
- VIPs afectados: {c['vips_affected']}
- Score: {c['score']:.0f}/100
- Confianza: {c['confidence']:.2f}

Responde SOLO el JSON, sin texto adicional."""

    text = _gemini(prompt, max_tokens=600, temperature=0.4)
    if not text:
        return fallback
    # limpiar markdown si lo añade
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1])
    text = text.strip()
    try:
        parsed = json.loads(text)
        return {
            "title": parsed.get("title") or fallback["title"],
            "reason": parsed.get("reason") or fallback["reason"],
            "expected_impact": parsed.get("expected_impact") or fallback["expected_impact"],
            "pre_built_message": parsed.get("pre_built_message", fallback["pre_built_message"]),
        }
    except Exception:
        return fallback


# ----------------------------------------------------------- COUNTERFACTUAL

def counterfactual_narrative(sim: dict) -> str:
    """Genera el párrafo ejecutivo del Counterfactual Twin."""
    fallback = (f"Sin actuar en los próximos 120 min, Scuffers perdería €{sim['do_nothing']['euros_lost']:.0f} "
                f"({sim['do_nothing']['oversells']} oversells y {sim['do_nothing']['vips_hurt']} VIPs heridos). "
                f"Ejecutando este plan, la pérdida cae a €{sim['execute_plan']['euros_lost']:.0f}: "
                f"se salvan €{sim['delta']['euros_saved']:.0f} y se protege al "
                f"{sim['delta']['vips_protected']*100/max(1,sim['do_nothing']['vips_hurt']):.0f}% de los VIPs en riesgo.")
    if not GEMINI_API_KEY:
        return fallback

    prompt = f"""Eres consultor estratégico de operaciones para Scuffers durante un drop de streetwear.
Escribe UN ÚNICO párrafo ejecutivo (máximo 4 líneas, máximo 90 palabras) que se leerá a los fundadores Javi y Jaime.

Habla en tono directo, urbano pero serio, sin emojis. Compara escenario "no actuar" vs "ejecutar plan", destaca el delta en € salvados y VIPs protegidos. Termina con una frase que les invite a accionar.

DATOS:
- Sin actuar: {sim['do_nothing']['oversells']} oversells, €{sim['do_nothing']['euros_lost']:.0f} perdidos, {sim['do_nothing']['vips_hurt']} VIPs heridos
- Ejecutando plan: {sim['execute_plan']['oversells']} oversells, €{sim['execute_plan']['euros_lost']:.0f} perdidos, {sim['execute_plan']['vips_hurt']} VIPs heridos
- Delta: €{sim['delta']['euros_saved']:.0f} salvados, {sim['delta']['vips_protected']} VIPs protegidos
"""
    text = _gemini(prompt, max_tokens=300, temperature=0.5)
    return text or fallback


_COMPONENT_ES = {
    "stock_health": "el inventario",
    "customer_health": "los clientes",
    "pipeline_health": "los pedidos",
    "campaign_health": "las campañas",
}
_VERDICT_ES = {"HEALTHY": "está saludable", "WARNING": "necesita atención", "CRITICAL": "está en estado crítico"}


def health_score_narrative(score: int, components: dict, top_action) -> str:
    """1 frase humana, 100% en castellano, sin jerga técnica."""
    verdict = "CRITICAL" if score < 50 else ("WARNING" if score < 75 else "HEALTHY")
    weakest_key = min(components, key=components.get)
    weakest_es = _COMPONENT_ES.get(weakest_key, weakest_key)
    verdict_es = _VERDICT_ES.get(verdict, verdict.lower())
    fallback = f"El drop {verdict_es}: la puntuación está en {score} sobre 100. La parte más débil ahora mismo es {weakest_es}, hay que actuar primero ahí."
    if not GEMINI_API_KEY:
        return fallback
    prompt = f"""Escribe en castellano UNA sola frase corta (máx 25 palabras) que resuma el estado de un drop de streetwear.

Datos:
- Puntuación de salud: {score}/100
- Verdict: {verdict_es}
- Parte más débil: {weakest_es} ({components[weakest_key]} sobre 100)
- Próxima acción recomendada: {top_action.get('title','sin acción') if top_action else 'sin acción'}

Reglas:
- Tono natural, sencillo, directo
- Cero jerga técnica, cero anglicismos, cero códigos
- No uses palabras como 'health', 'score', 'WARNING', 'CRITICAL'
- Devuelve solo la frase, sin comillas."""
    text = _gemini(prompt, max_tokens=120, temperature=0.4)
    return text or fallback
