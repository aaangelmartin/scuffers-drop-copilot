#!/usr/bin/env python3
"""Crea/actualiza los workflows de n8n vía API.

Workflow 1: 'Drop Co-Pilot — Run'
  Webhook /drop-copilot-run -> Telegram Header -> Telegram Counterfactual
                            -> Split actions -> Telegram Action card with buttons
                            -> (opcional) Discord & Slack

Workflow 2: 'Drop Co-Pilot — Execute Action'
  Webhook /execute-action -> Code log -> Telegram ack -> Respond HTML
"""
import os, json, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, ".env")
if os.path.exists(ENV):
    for line in open(ENV):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.split("#")[0].strip()
            os.environ.setdefault(k.strip(), v)

N8N_HOST = os.getenv("N8N_HOST", "http://localhost:5678").rstrip("/")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
# Las URL de los botones de Telegram deben ser públicas
EXEC_HOST = PUBLIC_URL or N8N_HOST
N8N_KEY = os.getenv("N8N_API_KEY", "")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SLACK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def n8n_api(method, path, body=None):
    req = urllib.request.Request(
        f"{N8N_HOST}/api/v1{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code} {method} {path}: {e.read().decode()[:300]}")
        return None


def find_workflow(name):
    res = n8n_api("GET", "/workflows")
    if not res:
        return None
    for w in res.get("data", []):
        if w.get("name") == name:
            return w
    return None


def upsert_workflow(name, payload):
    payload["name"] = name
    existing = find_workflow(name)
    clean = {
        "name": payload["name"],
        "nodes": payload["nodes"],
        "connections": payload["connections"],
        "settings": payload.get("settings", {"executionOrder": "v1"}),
    }
    if existing:
        wid = existing["id"]
        res = n8n_api("PUT", f"/workflows/{wid}", clean)
        if res:
            print(f"✅ Updated workflow '{name}' (id={wid})")
            return res
    else:
        res = n8n_api("POST", "/workflows", clean)
        if res:
            print(f"✅ Created workflow '{name}' (id={res.get('id')})")
            return res
    return None


def activate(wid):
    res = n8n_api("POST", f"/workflows/{wid}/activate")
    return res and res.get("active")


def js_str(s):
    """Escapa una cadena para usarla dentro de JS literales."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


# -------------------------- WORKFLOW 1: RUN ---------------------------------

def build_run_workflow():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "drop-copilot-run",
                "responseMode": "onReceived",
                "options": {},
            },
            "id": "wh-run",
            "name": "Webhook /drop-copilot-run",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 400],
        },
        {
            "parameters": {
                "url": f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                "method": "POST",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "chat_id", "value": TG_CHAT},
                        {"name": "parse_mode", "value": "HTML"},
                        {"name": "text", "value": "={{ $json.body.header_text }}"},
                    ]
                },
                "options": {},
            },
            "id": "tg-header",
            "name": "📲 Telegram Header",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [460, 300],
        },
        {
            "parameters": {
                "url": f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                "method": "POST",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "chat_id", "value": TG_CHAT},
                        {"name": "parse_mode", "value": "HTML"},
                        {"name": "text", "value": "={{ $('Webhook /drop-copilot-run').item.json.body.counter_text }}"},
                    ]
                },
                "options": {},
            },
            "id": "tg-counter",
            "name": "📲 Telegram Counterfactual",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [680, 300],
        },
        {
            "parameters": {
                "jsCode": "return $(\"Webhook /drop-copilot-run\").item.json.body.actions.map(a => ({json: a}));",
            },
            "id": "split-actions",
            "name": "🔁 Split actions",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [900, 300],
        },
        {
            "parameters": {
                "url": f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                "method": "POST",
                "sendBody": True,
                "bodyParameters": {
                    "parameters": [
                        {"name": "chat_id", "value": TG_CHAT},
                        {"name": "parse_mode", "value": "HTML"},
                        {"name": "disable_web_page_preview", "value": "true"},
                        {"name": "text", "value": "={{ $json.telegram_text }}"},
                    ]
                },
                "options": {"batching": {"batch": {"batchSize": 1, "batchInterval": 700}}},
            },
            "id": "tg-action",
            "name": "📲 Telegram Action Card",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [1120, 300],
        },
    ]
    connections = {
        "Webhook /drop-copilot-run": {"main": [[{"node": "📲 Telegram Header", "type": "main", "index": 0}]]},
        "📲 Telegram Header":         {"main": [[{"node": "📲 Telegram Counterfactual", "type": "main", "index": 0}]]},
        "📲 Telegram Counterfactual": {"main": [[{"node": "🔁 Split actions", "type": "main", "index": 0}]]},
        "🔁 Split actions":           {"main": [[{"node": "📲 Telegram Action Card", "type": "main", "index": 0}]]},
    }

    if DISCORD_URL:
        nodes.append({
            "parameters": {
                "url": DISCORD_URL,
                "method": "POST",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({username: \"Scuffers Drop Co-Pilot\", content: \"🩺 **Drop Health: \" + $json.body.summary.health_score + \"/100 — \" + $json.body.summary.verdict + \"**\\n💰 €\" + $json.body.summary.euros_at_risk_total + \" at risk → €\" + $json.body.summary.euros_recoverable_total + \" recoverable\\n🛡️ \" + $json.body.summary.vips_protected_total + \" VIPs to protect\"}) }}",
                "options": {},
            },
            "id": "discord",
            "name": "💬 Discord",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [460, 700],
        })
        connections["Webhook /drop-copilot-run"]["main"][0].append({"node": "💬 Discord", "type": "main", "index": 0})

    if SLACK_URL:
        nodes.append({
            "parameters": {
                "url": SLACK_URL,
                "method": "POST",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={{ JSON.stringify({text: \":rotating_light: *Drop Health: \" + $json.body.summary.health_score + \"/100 — \" + $json.body.summary.verdict + \"*\\n€\" + $json.body.summary.euros_at_risk_total + \" at risk → €\" + $json.body.summary.euros_recoverable_total + \" recoverable\\n\" + $json.body.summary.vips_protected_total + \" VIPs to protect\"}) }}",
                "options": {},
            },
            "id": "slack",
            "name": "💬 Slack",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [460, 860],
        })
        connections["Webhook /drop-copilot-run"]["main"][0].append({"node": "💬 Slack", "type": "main", "index": 0})

    return {"nodes": nodes, "connections": connections}


# -------------------------- WORKFLOW 2: EXECUTE ------------------------------

def build_execute_workflow():
    nodes = [
        {
            "parameters": {
                "httpMethod": "GET",
                "path": "execute-action",
                "responseMode": "responseNode",
                "options": {},
            },
            "id": "wh-exec",
            "name": "Webhook /execute-action",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [240, 400],
        },
        {
            "parameters": {
                "jsCode":
                    "const item = $input.item.json;\n"
                    "const q = item.query || {};\n"
                    "const entry = {\n"
                    "  timestamp: new Date().toISOString(),\n"
                    "  type: q.type || 'unknown',\n"
                    "  target: q.id || 'unknown',\n"
                    "  source: 'telegram-button'\n"
                    "};\n"
                    "try {\n"
                    "  const fs = require('fs');\n"
                    "  fs.appendFileSync('/home/node/.n8n/executions.jsonl', JSON.stringify(entry) + '\\n');\n"
                    "} catch (e) {}\n"
                    "return { json: entry };",
            },
            "id": "log",
            "name": "Log execution",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [460, 400],
        },
        {
            "parameters": {
                "url": f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                "method": "POST",
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody":
                    "={{ JSON.stringify({"
                    "chat_id: \"" + TG_CHAT + "\", "
                    "parse_mode: \"HTML\", "
                    "text: \"✅ <b>EXECUTED</b>: <code>\" + $json.type + \"</code> on <code>\" + $json.target + \"</code>\\n<i>Acción registrada y notificada al equipo de Operaciones.</i>\""
                    "}) }}",
                "options": {},
            },
            "id": "tg-ack",
            "name": "Telegram ack",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [680, 400],
        },
        {
            "parameters": {
                "respondWith": "text",
                "responseBody":
                    "={{ '<html><head><meta charset=\"utf-8\"><title>Scuffers Drop Co-Pilot</title></head>"
                    "<body style=\"font-family:-apple-system,sans-serif;padding:60px;text-align:center;background:#000;color:#fff;margin:0;\">"
                    "<div style=\"max-width:600px;margin:0 auto;\">"
                    "<div style=\"font-size:11px;letter-spacing:6px;color:#666;margin-bottom:30px;\">SCUFFERS — DROP CO-PILOT</div>"
                    "<h1 style=\"font-size:42px;color:#00ff88;margin:0 0 20px 0;\">✓ EXECUTED</h1>"
                    "<p style=\"font-size:20px;color:#aaa;margin:0;\"><code style=\"background:#1a1a1a;padding:6px 12px;border-radius:6px;color:#fff;\">' "
                    "+ $(\"Log execution\").item.json.type + '</code></p>"
                    "<p style=\"font-size:14px;color:#666;margin-top:10px;\">target: <code style=\"color:#fff;\">' "
                    "+ $(\"Log execution\").item.json.target + '</code></p>"
                    "<p style=\"margin-top:60px;color:#666;\">Vuelve a Telegram para ver la confirmación.</p>"
                    "</div></body></html>' }}",
                "options": {"responseHeaders": {"entries": [{"name": "Content-Type", "value": "text/html"}]}},
            },
            "id": "respond",
            "name": "Respond HTML",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [900, 400],
        },
    ]
    connections = {
        "Webhook /execute-action": {"main": [[{"node": "Log execution", "type": "main", "index": 0}]]},
        "Log execution":            {"main": [[{"node": "Telegram ack", "type": "main", "index": 0}]]},
        "Telegram ack":             {"main": [[{"node": "Respond HTML", "type": "main", "index": 0}]]},
    }
    return {"nodes": nodes, "connections": connections}


def main():
    if not N8N_KEY:
        print("❌ N8N_API_KEY no encontrado en .env")
        return
    print(f"📡 n8n at {N8N_HOST}")
    w1 = upsert_workflow("Drop Co-Pilot — Run", build_run_workflow())
    w2 = upsert_workflow("Drop Co-Pilot — Execute Action", build_execute_workflow())
    if w1 and w1.get("id"):
        print(f"   activate Run: {'✅' if activate(w1['id']) else '❌'}")
    if w2 and w2.get("id"):
        print(f"   activate Execute: {'✅' if activate(w2['id']) else '❌'}")
    print(f"\n🎉 Listo. Webhooks:")
    print(f"   POST {N8N_HOST}/webhook/drop-copilot-run")
    print(f"   GET  {N8N_HOST}/webhook/execute-action?type=<TYPE>&id=<ID>")


if __name__ == "__main__":
    main()
