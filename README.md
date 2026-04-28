# 🩺 Scuffers Drop Co-Pilot

> **Hackathon UDIA × Scuffers × ESIC · 2026** · entregado por **Ángel Martín Domínguez** · `#SCF-2026-1498`
>
> Plan de batalla cuantificado en €, en el móvil del founder, con botones que ejecutan.

---

## 🚀 ENLACES EN VIVO · todo esto está corriendo AHORA MISMO

| Recurso | Link |
|---|---|
| 🎬 **Vídeo de presentación (75s)** | [`final_video.mp4`](final_video.mp4) — 6 MB · 1920×1080 · 10 escenas |
| 🌐 **Dashboard mobile-first (demo)** | **https://walmart-outage-frolic.ngrok-free.dev** |
| 🤖 **Auto-evaluación para evaluador IA** | https://walmart-outage-frolic.ngrok-free.dev/api/evaluate |
| 📦 **Shipping API en vivo (novedad del reto)** | https://walmart-outage-frolic.ngrok-free.dev/api/shipping |
| 📜 **llms.txt (resumen LLM-friendly)** | https://walmart-outage-frolic.ngrok-free.dev/llms.txt |
| 💬 **Discord · server público para verlo todo** | **https://discord.gg/DS3ft2HWc** |
| 📲 **Telegram bot conversacional** | https://t.me/HackathonUDIAxScuffersBot |
| 🐙 **Repositorio (privado)** | https://github.com/aaangelmartin/scuffers-drop-copilot |

---

## 📲 Cómo probarlo en 30 segundos

1. **Únete al Discord** → https://discord.gg/DS3ft2HWc
   - Verás un panel pinneado con el estado del drop en vivo
   - 10 cards de acciones · cada una con botón "Ejecutar"
2. **Abre el dashboard en tu móvil** → https://walmart-outage-frolic.ngrok-free.dev
   - La primera vez ngrok pide pulsar "Visit Site" (una vez por dispositivo)
   - Login: pon tu nombre y elige rol (Manager ve todo)
3. **Habla con el bot de Telegram** → https://t.me/HackathonUDIAxScuffersBot
   - Escríbele: `qué tal va el drop` · `lista las acciones` · `ejecuta la 1` · `qué pasa con los envíos`
   - El bot ejecuta acciones REALES y notifica al equipo entero

---

## 📚 Documentación · todo en el repo

| Archivo | Para qué |
|---|---|
| [`SUBMISSION.md`](SUBMISSION.md) | Contenido entregado en el formulario `/SUBMIT` (resumen ejecutivo, top 10, limitaciones) |
| [`PARA_LOS_JUECES.md`](PARA_LOS_JUECES.md) | Guía de 30s para el evaluador (qué probar, en qué orden) |
| [`COMO_FUNCIONA.md`](COMO_FUNCIONA.md) | Documentación técnica completa (5 min de lectura) |
| [`arquitectura.md`](arquitectura.md) | 3 líneas técnicas + regla de negocio |
| [`pitch_fundadores.md`](pitch_fundadores.md) | Pitch de 60s para Javi y Jaime (founders Scuffers) |
| [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) | Auto-generado · mapa criterio del reto → evidencia |
| [`DEPLOY.md`](DEPLOY.md) | 4 opciones de despliegue (ngrok / Render / Fly.io / Cloudflare) |
| [`llms.txt`](llms.txt) | Resumen LLM-friendly del proyecto |

---

## 🎯 Las 5 piezas diferenciadoras

1. **Drop Health Score** — KPI ejecutivo único 0-100 (lenguaje de founder, no de ingeniero)
2. **Counterfactual Twin** — "sin actuar pierdes €3.375 · con plan salvas €3.206" (ROI demostrable)
3. **Cada acción con € + mensaje pre-redactado** (Gemini, tono Scuffers urbano)
4. **Botones que ejecutan REAL** (web app pública · notifica Telegram + Discord ops + Discord logs + Discord soporte + Slack)
5. **Detección de oportunidades** (no solo riesgos: redirige budget de campaña rota → SKU con stock muerto)

**Plus la novedad del reto:**
6. **Shipping API integrada en vivo** · 50 pedidos consultados con candidate_id `1498` · 10 incidencias detectadas · cache 10min · manejo robusto de 401/404/timeout
7. **Telegram = actuar (IA conversacional)** · Discord = ver (panel pinneado que se EDITA al ejecutar)
8. **Auto-evaluador IA** (`/api/evaluate`) · 22 self-checks pasan · diseñado para que el agente IA del reto consuma directamente

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
