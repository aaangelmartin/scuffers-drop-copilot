# 🎯 TUS TAREAS — SOLO LO QUE FALTA

> Lo automático ya está hecho. Solo queda lo que requiere tu login/email/tarjeta.

---

## ✅ YA COMPLETADO POR MÍ

- [x] Estructura de carpetas (`data/`, `scripts/`, `assets/`)
- [x] `.env` plantilla creada
- [x] `.gitignore` configurado
- [x] Mocks generados: `mock_stock.csv`, `mock_pedidos.json`, `mock_tickets.json`
- [x] Script `verify_setup.py` listo
- [x] **Docker funcionando** (verificado)
- [x] **n8n corriendo en http://localhost:5678** (container `n8n` activo)
- [x] **ngrok instalado** (`/opt/homebrew/bin/ngrok` v3.39.0)
- [x] **Python venv creado** con anthropic, openai, requests, pandas, dotenv, flask
- [x] Node v25 disponible (fallback)

---

## 🔴 LO QUE TIENES QUE HACER TÚ AHORA (15 min)

### 1. Abrir n8n y crear cuenta owner (1 min)
- [ ] Abre **http://localhost:5678** en el navegador
- [ ] Crea tu cuenta (email + password) — **apúntalos aquí**:
  - Email: ____________________
  - Pass:  ____________________

### 2. Anthropic API Key (2 min) — *CRÍTICO*
- [ ] https://console.anthropic.com/ → Settings → API Keys → **Create Key**
- [ ] Nombre: `hackathon-scuffers`
- [ ] Pega en `.env` → línea `ANTHROPIC_API_KEY=`
- [ ] Verifica saldo > 5€ en Settings → Billing

### 3. ngrok authtoken (2 min)
- [ ] Crea cuenta gratis: https://dashboard.ngrok.com/signup
- [ ] Copia tu token de: https://dashboard.ngrok.com/get-started/your-authtoken
- [ ] Ejecuta en terminal:
  ```bash
  ngrok config add-authtoken TU_TOKEN_AQUI
  ```

### 4. Telegram Bot (3 min) — *CANAL DEMO VISUAL*
- [ ] Telegram → busca **@BotFather** → `/newbot`
- [ ] Nombre: `Scuffers Hackathon Bot`
- [ ] Username: `scuffers_hack_<lo_que_sea>_bot`
- [ ] Pega el TOKEN en `.env` → `TELEGRAM_BOT_TOKEN=`
- [ ] Escribe `/start` a tu propio bot desde tu cuenta personal
- [ ] Abre `https://api.telegram.org/bot<TU_TOKEN>/getUpdates` en el navegador
- [ ] Busca `"chat":{"id":NUMERO}` → pega ese número en `.env` → `TELEGRAM_CHAT_ID=`

### 5. Shopify Dev Store (4 min) — *PROBABLE STACK*
- [ ] https://partners.shopify.com/signup
- [ ] Stores → **Add store** → Development store → tema "Dawn"
- [ ] Apps → **Develop apps** → Create an app → `hackathon-scuffers`
- [ ] Configure Admin API scopes: marca `read/write_products`, `read/write_orders`, `read/write_inventory`, `read/write_customers`
- [ ] Install app → copia **Admin API access token** (`shpat_...`) → `.env` → `SHOPIFY_ACCESS_TOKEN=`
- [ ] Pega también dominio (`tu-tienda.myshopify.com`) → `.env` → `SHOPIFY_STORE_DOMAIN=`
- [ ] Sube 3-4 productos demo (hoodies con tallas)

### 6. Airtable (2 min) — *MOCK DB VISUAL*
- [ ] https://airtable.com → login con Google
- [ ] Create base vacía → `Scuffers Hackathon`
- [ ] https://airtable.com/create/tokens → Create token → scopes: `data.records:read/write`, `schema.bases:read` → access la base creada
- [ ] Pega token → `.env` → `AIRTABLE_TOKEN=`
- [ ] Pega Base ID → `.env` → `AIRTABLE_BASE_ID=`

### 7. OpenAI (opcional backup, 1 min)
- [ ] https://platform.openai.com/api-keys → Create secret key
- [ ] `.env` → `OPENAI_API_KEY=`

---

## 🧪 VERIFICACIÓN

Cuando rellenes `.env`, ejecuta:
```bash
cd "/Users/aaangel/Desktop/Hackathon UDIA x Scuffers"
source venv/bin/activate
python3 scripts/verify_setup.py
```

---

## 📋 ESTADO ACTUAL

```
✅ Docker, n8n, ngrok, Python venv     → TODO CORRIENDO
🔴 Cuenta n8n local                     → Falta crear (1 min)
🔴 ANTHROPIC_API_KEY                    → Falta (CRÍTICO)
🔴 TELEGRAM_BOT_TOKEN + CHAT_ID         → Falta
🟡 SHOPIFY_ACCESS_TOKEN + DOMAIN        → Falta (probable uso)
🟡 AIRTABLE_TOKEN + BASE_ID             → Falta (probable uso)
🟢 OPENAI_API_KEY                       → Opcional
🟢 ngrok authtoken                      → Lo necesitarás solo si el reto pide webhook público
```

---

## 🚨 SI ALGO FALLA

| Si falla… | Plan B inmediato |
|---|---|
| n8n local | Reinicia: `docker restart n8n` |
| Docker | Plan B Node: `npx n8n` |
| Shopify | Mocks ya creados en `data/mock_pedidos.json` |
| Airtable | Google Sheets (n8n tiene OAuth nativo) |
| Anthropic | OpenAI como swap directo |

---

**Cuando llegue el reto a las 18:15 → pégamelo y arranco Fase 2 inmediatamente.**
