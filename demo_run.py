#!/usr/bin/env python3
"""Lanza la demo end-to-end:
1. Ejecuta control_tower.py (motor)
2. POSTea el payload combinado al webhook de n8n
3. n8n hace fan-out a Telegram + Discord/Slack si están configurados
"""
import os, json, subprocess, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# .env
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
# Si tenemos URL pública, usamos la web app (que también notifica Discord/Slack)
# Si no, usamos n8n local
if PUBLIC_URL:
    WEBHOOK = f"{PUBLIC_URL}/webhook/drop-copilot-run"
else:
    WEBHOOK = f"{N8N_HOST}/webhook/drop-copilot-run"


def run_engine():
    print("▶️  Ejecutando control_tower.py...")
    r = subprocess.run([os.path.join(ROOT, "venv/bin/python3"), "control_tower.py"], cwd=ROOT)
    if r.returncode != 0:
        print("❌ Engine falló")
        sys.exit(1)


def load_outputs():
    actions = json.load(open(os.path.join(ROOT, "out/actions.json")))
    sim = json.load(open(os.path.join(ROOT, "out/simulation.json")))
    health = json.load(open(os.path.join(ROOT, "out/health_score.json")))

    # Pre-formateamos los textos para Telegram en Python (más simple que expresiones n8n)
    s = actions["summary"]
    header_text = (
        f"🩺 <b>Drop Health: {s['health_score']}/100 — {s['verdict']}</b>\n\n"
        f"💰 <b>€{s['euros_at_risk_total']:.0f}</b> at risk\n"
        f"💵 <b>€{s['euros_recoverable_total']:.0f}</b> recoverable\n"
        f"🛡️ <b>{s['vips_protected_total']}</b> VIPs to protect\n\n"
        f"<i>{health.get('narrative', '')}</i>\n\n"
        f"<i>Top {len(actions['actions'])} acciones inbound...</i>"
    )

    dn = sim["do_nothing"]
    ep = sim["execute_plan"]
    dl = sim["delta"]
    counter_text = (
        "🔮 <b>Counterfactual Twin</b>\n\n"
        f"<b>Sin actuar:</b> -€{dn['euros_lost']:.0f} ({dn['oversells']} oversells, {dn['vips_hurt']} VIPs heridos)\n\n"
        f"<b>Ejecutando plan:</b> -€{ep['euros_lost']:.0f} ({ep['oversells']} oversells, {ep['vips_hurt']} VIPs heridos)\n\n"
        f"<b>💎 Salvas €{dl['euros_saved']:.0f} y {dl['vips_protected']} VIPs</b>\n\n"
        f"<i>{sim.get('narrative', '')}</i>"
    )

    # Pre-formateamos cada acción en español natural, sin código visible
    public = os.getenv("PUBLIC_URL", "").rstrip("/")
    n8n_host = public or os.getenv("N8N_HOST", "http://localhost:5678").rstrip("/")
    import urllib.parse
    sys.path.insert(0, ROOT)
    from lib.humanize import ACTION_LABELS, OWNER_LABELS, fmt_eur

    formatted_actions = []
    for a in actions["actions"]:
        exec_url = f"{n8n_host}/webhook/execute-action?type={urllib.parse.quote(a['action_type'])}&id={urllib.parse.quote(a['target_id'])}&rank={a['rank']}"
        target_label = a.get("target_label") or a["target_id"]
        action_label = a.get("action_label") or ACTION_LABELS.get(a["action_type"], a["action_type"])
        owner_label = a.get("owner_label") or OWNER_LABELS.get(a["owner"], a["owner"])
        conf_word = a.get("confidence_word", "media")

        text = (
            f"<b>#{a['rank']} · {a['title']}</b>\n\n"
            f"📦 <b>{target_label}</b>\n"
            f"🏷 {action_label} · {owner_label} · confianza {conf_word}\n"
        )
        if a.get("shipping_info") and a["shipping_info"].get("human"):
            text += f"🚚 <i>{a['shipping_info']['human']}</i>\n"
        text += (
            f"\n💸 <b>{fmt_eur(a['euros_at_risk'])}</b> en riesgo → 💰 <b>{fmt_eur(a['euros_recoverable'])}</b> recuperables"
        )
        if a.get("vips_affected"):
            text += f"\n🛡️ {a['vips_affected']} VIP(s) afectado(s)"
        text += f"\n\n📝 <i>{a['reason']}</i>"
        text += f"\n\n✅ <b>Resultado esperado:</b> {a['expected_impact']}"
        if a.get("pre_built_message"):
            text += f"\n\n💬 <b>Mensaje listo para enviar al cliente:</b>\n<i>« {a['pre_built_message']} »</i>"
        text += f"\n\n▶️ <a href=\"{exec_url}\">EJECUTAR ESTA ACCIÓN</a>"
        formatted_actions.append({**a, "telegram_text": text, "exec_url": exec_url})

    return {
        "summary": s,
        "actions": formatted_actions,
        "simulation": sim,
        "health_narrative": health.get("narrative", ""),
        "header_text": header_text,
        "counter_text": counter_text,
        "generated_at": actions["generated_at"],
    }


def post_to_n8n(payload):
    print(f"📡 POST {WEBHOOK}")
    body = json.dumps(payload).encode()
    req = urllib.request.Request(WEBHOOK, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"   ✅ n8n: {r.status} {r.read()[:200].decode()}")
    except urllib.error.HTTPError as e:
        print(f"   ❌ n8n {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        print(f"   ❌ {e}")


def main():
    if "--skip-engine" not in sys.argv:
        run_engine()
    payload = load_outputs()
    print(f"📦 Payload: {len(payload['actions'])} acciones, health={payload['summary']['health_score']}, salvas €{payload['simulation']['delta']['euros_saved']}")
    post_to_n8n(payload)
    print("\n🎉 Demo lanzada. Revisa Telegram.")


if __name__ == "__main__":
    main()
