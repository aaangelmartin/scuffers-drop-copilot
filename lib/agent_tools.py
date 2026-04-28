"""Tools que el agente IA conversacional puede invocar.

Cada tool es una función pura que consulta el state actual y devuelve
un dict con `text` (respuesta humana) y opcionalmente `extra` (datos).

El agente (Gemini) decide qué tool llamar a partir del mensaje del usuario.
"""
import os, json, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out")


def _load_actions():
    try:
        return json.load(open(os.path.join(OUT_DIR, "actions.json")))
    except Exception:
        return None


def _load_state():
    try:
        return json.load(open(os.path.join(OUT_DIR, "state.json")))
    except Exception:
        return {"executed_actions": []}


def _load_health():
    try:
        return json.load(open(os.path.join(OUT_DIR, "health_score.json")))
    except Exception:
        return {}


def _load_sim():
    try:
        return json.load(open(os.path.join(OUT_DIR, "simulation.json")))
    except Exception:
        return {}


def _eur(n):
    try:
        return f"€{float(n):,.0f}".replace(",", ".")
    except Exception:
        return f"€{n}"


# ============================================================ TOOLS

def query_health() -> dict:
    a = _load_actions(); h = _load_health(); sim = _load_sim()
    if not a or not h:
        return {"text": "Aún no hay datos. Lanza el motor con re_analyze."}
    s = a["summary"]
    state = _load_state()
    done = len(state.get("executed_actions", []))
    text = (
        f"📊 Drop a {h.get('score','?')}/100 · {h.get('verdict','?')}.\n"
        f"💰 {_eur(s.get('euros_at_risk_total',0))} en riesgo · {_eur(s.get('euros_recoverable_total',0))} recuperables.\n"
        f"🛡️ {s.get('vips_protected_total',0)} VIPs por proteger.\n"
        f"📋 {done}/{len(a['actions'])} acciones ejecutadas.\n\n"
        f"Plan en marcha · si lo ejecutas todo salvas {_eur(sim.get('delta',{}).get('euros_saved',0))}."
    )
    return {"text": text}


def query_actions() -> dict:
    a = _load_actions()
    if not a:
        return {"text": "Aún no hay acciones priorizadas."}
    state = _load_state()
    executed = set(state.get("executed_actions", []))
    lines = []
    for x in a["actions"]:
        key = f"{x['action_type']}:{x['target_id']}"
        prefix = "✅" if key in executed else f"#{x['rank']}"
        target = x.get("target_label") or x["target_id"]
        action = x.get("action_label") or x["action_type"]
        lines.append(f"{prefix} {action} · {target} · {_eur(x['euros_recoverable'])} recuperables")
    return {"text": "🎯 Plan top 10:\n\n" + "\n".join(lines)}


def query_action(rank: int) -> dict:
    a = _load_actions()
    if not a: return {"text": "No hay acciones cargadas."}
    try:
        rank = int(rank)
    except Exception:
        return {"text": "Necesito un número (1-10)."}
    found = next((x for x in a["actions"] if x["rank"] == rank), None)
    if not found:
        return {"text": f"No encuentro la acción #{rank}."}
    target = found.get("target_label") or found["target_id"]
    text = (
        f"🔍 Acción #{rank} · {found.get('action_label')}\n"
        f"📦 {target}\n"
        f"👤 {found.get('owner_label')} · confianza {found.get('confidence_word')}\n\n"
        f"💸 {_eur(found['euros_at_risk'])} en riesgo → 💰 {_eur(found['euros_recoverable'])} recuperables\n"
    )
    if found.get("vips_affected"):
        text += f"🛡️ {found['vips_affected']} VIP(s) afectado(s)\n"
    if found.get("shipping_info") and found["shipping_info"].get("human"):
        text += f"🚚 {found['shipping_info']['human']}\n"
    text += f"\n📝 {found.get('reason','')}\n\n✅ Resultado esperado: {found.get('expected_impact','')}"
    if found.get("pre_built_message"):
        text += f"\n\n💬 Mensaje listo para cliente:\n«{found['pre_built_message']}»"
    return {"text": text, "extra": {"action_type": found["action_type"], "target_id": found["target_id"]}}


def execute_action(rank=None, action_type=None, target_id=None, public_url=""):
    """Llama al endpoint REAL del webapp para ejecutar la acción."""
    a = _load_actions()
    if not a:
        return {"text": "No hay acciones cargadas."}

    found = None
    if rank is not None:
        try:
            rank = int(rank)
        except Exception:
            pass
        found = next((x for x in a["actions"] if x["rank"] == rank), None)
    if not found and action_type and target_id:
        found = next((x for x in a["actions"] if x["action_type"] == action_type and x["target_id"] == target_id), None)
    if not found:
        return {"text": "No encuentro esa acción. Dime un número del 1 al 10."}

    state = _load_state()
    key = f"{found['action_type']}:{found['target_id']}"
    if key in set(state.get("executed_actions", [])):
        return {"text": f"⚠️ La acción #{found['rank']} ya estaba ejecutada antes."}

    base = (public_url or os.getenv("PUBLIC_URL") or "http://localhost:8080").rstrip("/")
    url = f"{base}/webhook/execute-action?type={urllib.parse.quote(found['action_type'])}&id={urllib.parse.quote(found['target_id'])}&rank={found['rank']}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TelegramAgent/1.0"})
        urllib.request.urlopen(req, timeout=15).read()
    except Exception as e:
        return {"text": f"❌ Error ejecutando: {e}"}

    target = found.get("target_label") or found["target_id"]
    text = (
        f"✅ HECHO · {found.get('action_label')} · {target}\n\n"
        f"💰 Acabas de salvar {_eur(found['euros_recoverable'])}"
    )
    if found.get("vips_affected"):
        text += f" y proteger {found['vips_affected']} VIP(s)"
    text += f".\nEl equipo ya ha sido avisado por todos los canales."
    return {"text": text}


def query_vips() -> dict:
    a = _load_actions()
    if not a: return {"text": "Sin datos."}
    vips = [x for x in a["actions"] if x.get("vips_affected", 0) > 0]
    if not vips:
        return {"text": "🛡️ No hay VIPs en peligro ahora mismo."}
    lines = []
    for x in vips:
        target = x.get("target_label") or x["target_id"]
        lines.append(f"• #{x['rank']} · {target} · {_eur(x['euros_recoverable'])} recuperables")
    return {"text": f"🛡️ {len(vips)} VIPs en peligro:\n\n" + "\n".join(lines)}


def query_shipping() -> dict:
    cache_path = os.path.join(OUT_DIR, "_shipping_cache.json")
    if not os.path.exists(cache_path):
        return {"text": "🚚 Shipping API aún no consultada. Lanza re_analyze."}
    try:
        cache = json.load(open(cache_path))
    except Exception:
        return {"text": "Error leyendo cache."}
    from lib.shipping_api import is_problematic, severity_score, humanize_shipping
    issues = []
    for oid, s in cache.items():
        if not is_problematic(s): continue
        issues.append((severity_score(s), oid, humanize_shipping(s), s))
    issues.sort(reverse=True)
    if not issues:
        return {"text": f"🚚 Consultados {len(cache)} pedidos · ninguna incidencia."}
    lines = [f"🚚 {len(cache)} pedidos consultados · {len(issues)} con incidencias:\n"]
    for sev, oid, human, s in issues[:8]:
        lines.append(f"• {oid} · {human}")
    return {"text": "\n".join(lines)}


def re_analyze(public_url="") -> dict:
    base = (public_url or os.getenv("PUBLIC_URL") or "http://localhost:8080").rstrip("/")
    try:
        req = urllib.request.Request(f"{base}/api/run", method="POST", headers={"User-Agent": "TelegramAgent/1.0"})
        urllib.request.urlopen(req, timeout=240).read()
        return {"text": "✅ He relanzado el motor con los datos actuales (incluida la Shipping API)."}
    except Exception as e:
        return {"text": f"❌ Error al re-analizar: {e}"}


# ============================================================ DISPATCHER

TOOL_REGISTRY = {
    "query_health": query_health,
    "query_actions": query_actions,
    "query_action": query_action,
    "execute_action": execute_action,
    "query_vips": query_vips,
    "query_shipping": query_shipping,
    "re_analyze": re_analyze,
}


SYSTEM_PROMPT = """Eres el asistente de operaciones de Scuffers durante un drop de streetwear.
Hablas en castellano natural, directo, sin jerga técnica ni anglicismos innecesarios.

Tienes acceso a estas tools (funciones que ejecutan acciones reales):

- query_health: estado del drop (puntuación, dinero en riesgo, VIPs)
- query_actions: lista las 10 acciones priorizadas
- query_action(rank): detalle de la acción #rank (1-10)
- execute_action(rank): EJECUTA la acción #rank (real, notifica equipo, suma a contador)
- query_vips: clientes VIP en peligro
- query_shipping: incidencias logísticas en vivo (Shipping API)
- re_analyze: relanza el motor entero (puede tardar 1-2 min)
- chat: SOLO conversa, sin tool

REGLAS DE ORO:
1. Cuando el usuario te pide "ejecuta la X" o "haz la X", usa execute_action con rank=X. NO pidas confirmación.
2. Cuando dice "qué tal", "cómo va", "estado" → query_health.
3. Cuando dice "lista", "cuáles", "qué hay" → query_actions.
4. Cuando dice "envíos", "pedidos", "logística" → query_shipping.
5. Cuando dice "VIPs", "clientes importantes" → query_vips.
6. Cuando dice "re-analiza", "actualiza", "vuelve a calcular" → re_analyze.
7. Si el usuario solo saluda o no pide nada concreto, usa chat.

FORMATO DE RESPUESTA (obligatorio):
Devuelve SOLO un objeto JSON sin markdown, así:
{"tool": "<nombre>", "params": {...}, "reply": "<frase corta de confirmación>"}

Ejemplos:
Usuario: "qué tal va el drop"
{"tool":"query_health","params":{},"reply":"Te miro el estado..."}

Usuario: "ejecuta la 3"
{"tool":"execute_action","params":{"rank":3},"reply":"Ejecutando la #3..."}

Usuario: "cuéntame de la acción 5"
{"tool":"query_action","params":{"rank":5},"reply":"Te miro la #5..."}

Usuario: "qué pasa con los envíos"
{"tool":"query_shipping","params":{},"reply":"Voy a revisar la API de envíos..."}

Usuario: "hola"
{"tool":"chat","params":{},"reply":"¡Hola! Soy tu asistente para gestionar el drop. Puedes preguntarme cómo va, ver acciones, o decirme 'ejecuta la X' para que dispare una acción real. ¿Qué necesitas?"}
"""


def keyword_route(user_message: str) -> dict:
    """Fallback determinista por keywords cuando Gemini cae (rate limit, etc).
    Devuelve mismo formato {tool, params, reply} que Gemini."""
    m = (user_message or "").lower().strip()
    import re

    # ejecutar / hacer / dispara
    exec_match = re.search(r"(?:ejecut|dispar|haz|hacer|lanz|corr|activ).*?(\d+)", m)
    if exec_match:
        rank = int(exec_match.group(1))
        return {"tool": "execute_action", "params": {"rank": rank}, "reply": f"Vale, ejecuto la #{rank}..."}
    if any(w in m for w in ["ejecuta la", "haz la", "dispara la", "lanza la"]):
        # genérico sin número
        nums = re.findall(r"\d+", m)
        if nums:
            return {"tool": "execute_action", "params": {"rank": int(nums[0])}, "reply": f"Ejecutando la #{nums[0]}..."}

    # detalle de acción
    detail_match = re.search(r"(?:cuént|detall|dime|info|sobre).*?(\d+)", m)
    if detail_match:
        return {"tool": "query_action", "params": {"rank": int(detail_match.group(1))}, "reply": ""}
    nums_only = re.findall(r"\baccion\w*\s*(\d+)\b|\bla\s*(\d+)\b|^\s*#?(\d+)\s*$", m)
    if nums_only and not exec_match:
        n = next((int(x) for grp in nums_only for x in grp if x), None)
        if n: return {"tool": "query_action", "params": {"rank": n}, "reply": ""}

    # envíos / shipping
    if any(w in m for w in ["envío", "envio", "envíos", "envios", "shipping", "logíst", "logist", "incidencia", "retraso"]):
        return {"tool": "query_shipping", "params": {}, "reply": "Reviso la API de envíos..."}

    # vips
    if any(w in m for w in ["vip", "client important", "client clave"]):
        return {"tool": "query_vips", "params": {}, "reply": ""}

    # re-analizar
    if any(w in m for w in ["re-analiza", "reanaliza", "actualiza", "vuelve a calcular", "recalcula", "rerun"]):
        return {"tool": "re_analyze", "params": {}, "reply": "Relanzando el motor..."}

    # listar acciones
    if any(w in m for w in ["lista", "listar", "cuáles", "cuales", "qué hay", "que hay", "muéstrame", "muestrame", "acciones", "plan", "qué tengo", "que tengo"]):
        return {"tool": "query_actions", "params": {}, "reply": ""}

    # estado / health
    if any(w in m for w in ["qué tal", "que tal", "cómo va", "como va", "estado", "salud", "score", "drop", "resumen", "cómo está", "como esta", "hola", "buenas"]):
        return {"tool": "query_health", "params": {}, "reply": ""}

    # fallback chat
    return {
        "tool": "chat",
        "params": {},
        "reply": (
            "Soy tu copiloto del drop. Puedes pedirme cosas como:\n"
            "• 'qué tal va el drop' → estado general\n"
            "• 'lista las acciones' → top 10\n"
            "• 'cuéntame de la 5' → detalle acción #5\n"
            "• 'ejecuta la 1' → DISPARA la acción real\n"
            "• 'qué pasa con los envíos' → incidencias logísticas\n"
            "• 'los VIPs' → clientes en peligro\n"
            "• 're-analiza' → relanza el motor"
        ),
    }


def run_agent(user_message: str, public_url: str = "") -> dict:
    """Orquestador: usuario → Gemini (con fallback keyword) → ejecuta tool → respuesta."""
    from lib.ai import _gemini

    prompt = SYSTEM_PROMPT + f"\n\n--- MENSAJE DEL USUARIO ---\n{user_message}\n\nResponde solo con el JSON."
    raw = _gemini(prompt, max_tokens=300, temperature=0.2)
    if raw:
        # Parse Gemini response
        txt = raw.strip()
        if txt.startswith("```"):
            txt = "\n".join(line for line in txt.split("\n") if not line.startswith("```"))
        try:
            decision = json.loads(txt)
        except Exception:
            import re
            m = re.search(r"\{[\s\S]*\}", txt)
            if m:
                try:
                    decision = json.loads(m.group(0))
                except Exception:
                    decision = keyword_route(user_message)
            else:
                decision = keyword_route(user_message)
    else:
        # FALLBACK: Gemini caído o rate-limited → keyword routing
        decision = keyword_route(user_message)

    tool_name = decision.get("tool", "chat")
    params = decision.get("params", {}) or {}
    reply = decision.get("reply", "")

    if tool_name == "chat":
        return {"text": reply, "tool": "chat"}

    fn = TOOL_REGISTRY.get(tool_name)
    if not fn:
        return {"text": f"No reconozco esa intención ({tool_name}).", "tool": "unknown"}

    # Inyectar public_url si lo necesita
    import inspect
    sig = inspect.signature(fn)
    if "public_url" in sig.parameters:
        params["public_url"] = public_url

    try:
        result = fn(**params)
    except TypeError as e:
        return {"text": f"Parámetros incorrectos: {e}", "tool": tool_name}
    except Exception as e:
        return {"text": f"Error en {tool_name}: {e}", "tool": tool_name}

    full_text = (reply + "\n\n" + result.get("text", "")).strip() if reply else result.get("text", "")
    return {"text": full_text, "tool": tool_name, "extra": result.get("extra")}
