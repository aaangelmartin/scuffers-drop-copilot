# 🚀 Deploy Guide — Scuffers Drop Co-Pilot

Tienes 3 caminos de menos a más permanente. Para el hackathon, **opción A** es la más rápida.

---

## 🟢 Opción A — ngrok (la más rápida, ~3 min)

Te da una URL pública temporal. Perfecto para la demo en directo.

### 1. Configurar ngrok (sólo la primera vez)
```bash
# Si no tienes cuenta:
open https://dashboard.ngrok.com/signup
# Coge tu authtoken de:
open https://dashboard.ngrok.com/get-started/your-authtoken

ngrok config add-authtoken TU_TOKEN_AQUI
```

### 2. Lanzar la web app + tunel
```bash
# Terminal 1: lanza la web app
cd "/Users/aaangel/Desktop/Hackathon UDIA x Scuffers"
source venv/bin/activate
PORT=8080 python3 webapp.py

# Terminal 2: lanza ngrok
ngrok http 8080
```

Verás algo como:
```
Forwarding   https://abcd-1234.ngrok-free.app -> http://localhost:8080
```

### 3. Actualiza la URL pública
```bash
# Edita .env y añade:
PUBLIC_URL=https://abcd-1234.ngrok-free.app

# Re-lanza la web app (ctrl+c y de nuevo PORT=8080 python3 webapp.py)
```

### 4. Prueba desde el móvil
- Abre `https://abcd-1234.ngrok-free.app` en el navegador del móvil → ves el dashboard
- Pulsa cualquier botón **EXECUTE** → se ejecuta y notifica a Telegram, Discord, Slack
- Vuelve a Telegram → el bot ya tendrá los mensajes con links que ahora apuntan a la URL pública

---

## 🟡 Opción B — Cloudflare Tunnel (sin auth, ~5 min)

Si no quieres crear cuenta de ngrok:

```bash
brew install cloudflared
# Lanza la web app en otra terminal primero
cloudflared tunnel --url http://localhost:8080
```

Te da una URL `https://*.trycloudflare.com` sin necesidad de auth. Igualmente:
- Pega esa URL en `PUBLIC_URL` de `.env`
- Re-lanza la web app

---

## 🔵 Opción C — Render free tier (URL permanente, ~15 min)

Para tener una URL que viva más allá del hackathon:

### 1. Crear repo de GitHub
```bash
cd "/Users/aaangel/Desktop/Hackathon UDIA x Scuffers"
git init
git add .
git commit -m "feat: scuffers drop co-pilot"
gh repo create scuffers-drop-copilot --public --source=. --push
```

### 2. Deploy a Render
1. Abre https://render.com → Sign up con GitHub
2. **New** → **Blueprint** → conecta tu repo `scuffers-drop-copilot`
3. Render detecta `render.yaml` automáticamente
4. Configura las env vars (Telegram, Gemini, etc) — copia desde tu `.env`
5. **Apply** y espera 3 min
6. Obtienes URL: `https://scuffers-drop-copilot.onrender.com`

### 3. Actualiza el `PUBLIC_URL`
- En Render Dashboard → Settings → Environment → `PUBLIC_URL` = tu URL de Render
- Redeploy

> **Nota:** El plan free de Render duerme tras 15 min sin tráfico. Tarda ~30s en despertar la primera petición.

---

## 🟣 Opción D — Fly.io (también gratis, ~10 min)

```bash
brew install flyctl
fly auth signup
fly launch          # detecta Dockerfile, sigue el wizard
fly secrets set TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... GEMINI_API_KEY=...
fly deploy
```

URL: `https://scuffers-drop-copilot.fly.dev`

---

## 📲 Después de desplegar

### 1. Actualiza n8n con la URL pública
Edita `.env`:
```
PUBLIC_URL=https://tu-deploy.com
```

Y reconstruye los workflows:
```bash
python3 scripts/build_n8n.py
```

Esto hace que los botones de Telegram apunten a la URL pública.

### 2. Lanza la demo
```bash
python3 demo_run.py --skip-engine
```

Ahora desde Telegram en cualquier móvil:
- Recibirás Health Score + Counterfactual + 10 acciones
- Cada acción tiene un link **▶️ EXECUTE THIS ACTION** que abre tu dashboard público
- Click → ejecuta → notifica de vuelta a Telegram + Discord + Slack
- Todo desde el móvil, sin tocar el ordenador

### 3. Comparte con Javi y Jaime
Sólo necesitan:
- El URL del dashboard (`https://...`) para ver en su navegador del móvil
- Estar añadidos al canal de Telegram para recibir las acciones
- Tap en EXECUTE en el botón / link → todo se ejecuta y todo el equipo se entera

---

## 🔌 Endpoints disponibles en la web app

| Path | Método | Para qué |
|---|---|---|
| `/` | GET | Dashboard mobile-first |
| `/healthz` | GET | Health check (deploy) |
| `/api/data` | GET | JSON de actions + sim + health |
| `/api/run` | GET/POST | Re-ejecuta el motor |
| `/webhook/drop-copilot-run` | POST | Trigger desde n8n con payload |
| `/webhook/execute-action?type=X&id=Y` | GET | Ejecuta acción + notifica todos los canales |
| `/executions` | GET | Log de ejecuciones (JSON) |

---

## ⚠️ Variables de entorno en cloud

Asegúrate de configurar en tu plataforma:

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
DISCORD_WEBHOOK_URL=...        (opcional)
SLACK_WEBHOOK_URL=...          (opcional)
PUBLIC_URL=https://tu-deploy.com
PORT=8080                       (algunos hosts lo setean automáticamente)
```

---

## 🆘 Troubleshooting

- **Render se duerme**: cambia a plan starter ($7/mes) o usa cron-ping para mantenerlo vivo
- **Telegram no recibe**: verifica `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en env vars del cloud
- **Botones no funcionan**: verifica que `PUBLIC_URL` esté seteado y sea HTTPS
- **No data**: corre `/api/run` desde el navegador para regenerar los JSONs en el servidor
