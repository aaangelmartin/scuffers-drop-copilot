# 🩺 Scuffers Drop Co-Pilot

> Hackathon UDIA × Scuffers × ESIC · 2026
> **Plan de batalla cuantificado en €, en el móvil del founder, con botones que ejecutan.**

Una **web app mobile-first** + bot de Telegram + integraciones Discord/Slack que permite a un equipo de operaciones gestionar un drop de alta demanda **desde cualquier móvil** sin tocar el ordenador.

---

## 🎯 Las 5 piezas diferenciadoras

1. **Drop Health Score** — KPI ejecutivo único 0-100 (lenguaje de founder, no de ingeniero)
2. **Counterfactual Twin** — "sin actuar pierdes €X · con plan salvas €Y" (ROI demostrable)
3. **Cada acción con € + mensaje pre-redactado** (Gemini, tono Scuffers urbano)
4. **Botones que ejecutan REAL** (web app pública, notifica Telegram + Discord + Slack)
5. **Detección de oportunidades** (no solo riesgos: redirige budget de campaña rota → SKU con stock muerto)

---

## 🚀 Demo en 3 niveles

### Nivel 1 — Solo motor + n8n local (sin URL pública)
```bash
source venv/bin/activate
python3 control_tower.py        # genera out/*.json
python3 demo_run.py --skip-engine   # POST a n8n → fan-out Telegram
```

### Nivel 2 — Web app local + Telegram (móvil propio)
```bash
./start.sh                       # arranca webapp en :8080
# Abre http://localhost:8080 en tu navegador
```

### Nivel 3 — URL pública (cualquier móvil del equipo)
```bash
./start.sh full                  # webapp + ngrok + demo a Telegram
# Comparte la URL ngrok con tu equipo. Listo.
```

Ver **[DEPLOY.md](DEPLOY.md)** para opciones permanentes (Render, Railway, Fly.io, Cloudflare Tunnel).

---

## 📂 Estructura

```
.
├── webapp.py                 # 🌐 Web app Flask mobile-first (DASHBOARD + EJECUCIÓN)
├── control_tower.py          # 🧠 Motor: carga, scorea, enriquece, simula
├── demo_run.py               # 🎬 Lanza la demo (POST a webhook)
├── start.sh                  # ⚡ Arranque all-in-one (web + tunnel + demo)
├── dashboard.py              # 📊 Streamlit dashboard (alternativo, para pantalla compartida)
├── arquitectura.md           # 📐 3 líneas + regla de negocio
├── pitch_fundadores.md       # 🎤 Pitch 60s para Javi y Jaime
├── DEPLOY.md                 # 🚀 4 opciones de despliegue
├── PROMPT_CLAUDE_DESIGN.md   # 🎨 Prompt para rediseñar el dashboard
├── lib/
│   ├── loader.py             # Carga CSV robusta (datos sucios)
│   ├── candidates.py         # 7 detectores + ranking top 10
│   ├── simulator.py          # Counterfactual Twin
│   └── ai.py                 # Gemini wrapper (titles, reasons, mensajes)
├── scripts/
│   ├── build_n8n.py          # Crea/actualiza workflows n8n vía API
│   └── verify_setup.py       # Health check pre-vuelo
├── data/candidate_csvs/      # Datos del reto (orders, customers, inventory…)
├── out/
│   ├── actions.json          # Top 10 acciones (formato del reto + extensiones)
│   ├── simulation.json       # Counterfactual numérico + narrativa Gemini
│   ├── health_score.json     # Drop Health Score y componentes
│   └── executions.jsonl      # Log de acciones ejecutadas (1 por línea)
├── requirements.txt          # Para deploy
├── Procfile                  # Para Render/Railway
├── render.yaml               # One-click deploy a Render
└── Dockerfile                # Para Fly.io / cualquier container host
```

---

## 🌐 Endpoints de la web app

| Path | Método | Para qué |
|---|---|---|
| `/` | GET | Dashboard mobile-first (HTML completo) |
| `/api/data` | GET | JSON de actions + sim + health |
| `/api/run` | GET/POST | Re-ejecuta el motor (control_tower.py) |
| `/webhook/drop-copilot-run` | POST | Trigger desde n8n (recibe payload, fan-out) |
| `/webhook/execute-action?type=X&id=Y` | GET | Ejecuta acción + notifica todos los canales |
| `/executions` | GET | Log JSON de ejecuciones |
| `/healthz` | GET | Health check |

---

## 🎮 Cómo usarlo desde el móvil (flujo del founder)

1. **Recibes notificación en Telegram**: `🩺 Drop Health: 69/100 — WARNING`
2. **Counterfactual Twin** llega justo después: `Sin actuar perdéis €3,375. Con plan salváis €3,206.`
3. **10 acciones aterrizan en el chat** con € en riesgo, € recuperables, mensaje listo y link **▶️ EXECUTE**
4. **Pulsas EXECUTE** → se abre página de confirmación + se notifica al equipo (todos los canales)
5. **Vuelves al chat** → ves el ack de ejecución
6. (Opcional) Abres el **dashboard** en el navegador del móvil para ver Health Score visual + tabla VIP Shield

Todo desde el móvil. Cero ordenador.

---

## 🧠 Stack

| Capa | Tech | Por qué |
|---|---|---|
| Motor | Python 3.9+ (loader + 7 detectores + ranking) | Determinista, auditable |
| IA | Gemini 2.5-flash | Lenguaje humano para reasons/messages, fallback a templates |
| Web app | Flask single-file | Plug & play, mobile-first, deployable cualquier sitio |
| Orquestación | n8n (visible en demo) | Mostrar el "control tower" en pantalla |
| Bot | Telegram Bot API | Universal, sin app extra |
| Fan-out | Discord + Slack webhooks | Reaching all teams |

---

## 📊 Cifras clave de esta corrida

- 22 SKUs, 180 pedidos, 120 clientes, 18 tickets, 5 campañas
- **8 VIPs** detectados (LTV combinado €11k+)
- **Drop Health Score: 69/100 (WARNING)**
- **€3,375 perdidos sin actuar**, **€169 con plan** → **€3,206 salvados (95% mitigation)**
- **2 VIPs heridos sin actuar → 0 con plan**
- 10 acciones priorizadas con € y mensajes listos

Top 3 acciones (generadas por la IA):
1. **PAUSA INMEDIATA**: Campaña TikTok CMP-778 → HOODIE-BLK-M Madrid (€1,684 recoverable)
2. **Bloquear venta** ZIP-BLK-M (€1,010 recoverable, 1 VIP)
3. **Escalar ticket** TCK-5505 urgente VIP CUS-2033 (LTV €2,119)

---

## 🛡️ Robustez

- Loader tolera columnas faltantes y valores corruptos
- Si Gemini falla → templates deterministas
- Si Shopify/SMTP no configurados → modo mock con logs
- 7 detectores independientes (un detector roto no rompe el resto)
- `confidence` numérica por acción (auditable)
- Fallback HTTP: si web app cae, n8n sigue notificando Telegram

---

## ✅ Verificación

```bash
python3 scripts/verify_setup.py
```

---

## 👥 Equipo

Construido en 95 minutos durante el Hackathon Scuffers × UDIA × ESIC 2026.
