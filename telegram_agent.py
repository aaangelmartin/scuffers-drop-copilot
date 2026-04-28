"""Worker que escucha mensajes en Telegram y los enruta al asistente IA.

Polling sobre getUpdates → Gemini decide tool → ejecuta vía /api/agent → responde.

Lanzar: PORT=8080 python3 telegram_agent.py
       (o desde start.sh con `agent` flag)
"""
import os, json, time, urllib.request, urllib.parse, urllib.error
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

ENV_PATH = os.path.join(ROOT, ".env")
if os.path.exists(ENV_PATH):
    for line in open(ENV_PATH):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.split("#")[0].strip()
            os.environ.setdefault(k.strip(), v)

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/") or "http://localhost:8080"

OFFSET_FILE = os.path.join(ROOT, "out", "_telegram_offset.json")


def get_offset():
    try:
        return json.load(open(OFFSET_FILE)).get("offset", 0)
    except Exception:
        return 0


def save_offset(o):
    os.makedirs(os.path.dirname(OFFSET_FILE), exist_ok=True)
    json.dump({"offset": o}, open(OFFSET_FILE, "w"))


def send_message(chat_id, text):
    body = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text[:4000],
        "parse_mode": "HTML", "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"send error: {e}")


def get_updates(offset):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates?offset={offset}&timeout=20"
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.URLError:
        return None
    except Exception as e:
        print(f"getUpdates error: {e}")
        return None


def call_agent(message_text):
    """Llama al endpoint del webapp (más fiable que importar el módulo aquí)."""
    body = json.dumps({"message": message_text}).encode()
    req = urllib.request.Request(
        f"{PUBLIC_URL}/api/agent",
        data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "text": f"Error: {e}"}


def main():
    if not TG_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    print(f"🤖 Telegram Agent · escuchando en {PUBLIC_URL}/api/agent")
    print(f"   chat permitido: {TG_CHAT or 'cualquiera'}")
    offset = get_offset()
    while True:
        try:
            data = get_updates(offset)
            if not data or not data.get("ok"):
                time.sleep(2); continue
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)
                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue
                chat_id = str(msg.get("chat", {}).get("id", ""))
                # Si tenemos TELEGRAM_CHAT_ID configurado, solo aceptamos ese chat
                if TG_CHAT and chat_id != str(TG_CHAT):
                    print(f"  · ignorando chat {chat_id}")
                    continue
                text = msg.get("text", "").strip()
                if not text:
                    continue
                if text.startswith("/start"):
                    send_message(chat_id, "👋 Soy tu asistente del drop. Pregúntame cómo va, dime <i>'ejecuta la 1'</i>, <i>'cuéntame de la acción 5'</i>, <i>'qué pasa con los envíos'</i>...")
                    continue
                print(f"  📩 {text[:80]}")
                # tipo de "estoy escribiendo"
                try:
                    typing = urllib.parse.urlencode({"chat_id": chat_id, "action": "typing"}).encode()
                    urllib.request.urlopen(urllib.request.Request(
                        f"https://api.telegram.org/bot{TG_TOKEN}/sendChatAction",
                        data=typing, headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=5)
                except Exception:
                    pass
                # llamar agent
                resp = call_agent(text)
                reply = resp.get("text", "Sin respuesta del asistente.")
                send_message(chat_id, reply)
        except KeyboardInterrupt:
            print("\nbye"); return
        except Exception as e:
            print(f"loop error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
