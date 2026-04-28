# 📦 SUBMISSION · Scuffers Drop Co-Pilot

> Datos listos para COPY-PASTE en el formulario `/SUBMIT`. Deadline 20:30.

---

## 👤 Identificado
- Ángel Martín Domínguez · #SCF-2026-1498
- Email: martindominguez.angel@gmail.com

---

# 📝 CAMPOS DEL FORMULARIO (copy-paste)

---

## 🔵 Resumen ejecutivo · OBLIGATORIO

```
Scuffers Drop Co-Pilot es un Control Tower mobile-first que durante un drop de alta demanda prioriza las 10 acciones críticas que el equipo de operaciones debe ejecutar AHORA, las cuantifica en € y permite dispararlas desde el móvil con un solo tap o por lenguaje natural en Telegram.

El motor carga 6 CSVs (orders, customers, inventory, support_tickets, campaigns, order_items), consulta en vivo la nueva Shipping Status API (50 pedidos relevantes, no los 180 — para no martillar), aplica un scoring determinista sobre 5 lentes (Logística 40% · Atención 25% · Marketing 20% · Operaciones 15% · Shipping API en vivo) y enriquece cada acción con Gemini para escribir títulos humanos, justificaciones, mensajes pre-redactados al cliente y narrativa counterfactual.

La salida combina los campos exigidos por el reto con extensiones útiles: € en riesgo, € recuperables, VIPs afectados, mensaje listo para enviar al cliente, data_source (scoring vs scoring+shipping_api), shipping_info y target_label humanizado.

La interfaz es una web responsive con login dummy de 5 roles, sticky subnav, reloj realtime, KPIs que actualizan en vivo al ejecutar acciones (€ ya salvados sube, € en riesgo baja, top 10 dinámico que rellena con el siguiente del pool de 67 candidatos), feed de envíos en tiempo real, chat widget conversacional y botones que mutan state.json y notifican Telegram + Discord (3 canales: ops/logs/soporte) + Slack en paralelo.

División de canales · Discord = ver (panel pinneado que se EDITA al ejecutar) · Telegram = actuar (bot conversacional con Gemini que entiende "ejecuta la 1" o "qué pasa con los envíos" y dispara acciones reales).

Diferenciadores clave: Drop Health Score como KPI ejecutivo único (1 cifra 0-100), Counterfactual Twin que cuantifica "sin actuar -€3.375 vs con plan -€169 = €3.206 salvados", detección de oportunidades (no solo riesgos: redirigir presupuesto de campaña rota a SKU con stock muerto), endpoint /api/evaluate con 22 self-checks que pasan auto-validación para el evaluador IA, y EVALUATION_REPORT.md auto-generado mapeando cada criterio del reto a evidencia concreta.

Construido íntegramente con Claude Code en 95 minutos.
```

---

## 🔵 Enfoque / arquitectura · OPCIONAL

```
ARQUITECTURA

6 CSVs → control_tower.py (motor Python, ~250 LOC)
            ├─ lib/loader.py          carga robusta CSV (try/except por celda, casts seguros, schema-tolerant)
            ├─ lib/shipping_api.py    cliente Shipping API con cache TTL 10min y manejo de 401/404/timeout/JSON inválido
            ├─ lib/candidates.py      8 detectores en 5 lentes → ~67 candidatos
            ├─ ranking                top 10 con score ponderado + balanceo de owners (≤4 por lente)
            ├─ lib/simulator.py       Counterfactual Twin (con/sin plan)
            ├─ lib/ai.py              Gemini 2.5-flash con cache + fallback determinista
            └─ lib/humanize.py        traducción SKU/CMP/CUS/TCK/ORD → etiqueta humana ("HOODIE-BLK-M" → "Black Hoodie · talla M")
            → out/actions.json + simulation.json + health_score.json + EVALUATION_REPORT.md

webapp.py (Flask single-file, ~1000 LOC con HTML+CSS+JS embebido)
   ├─ Dashboard mobile-first con branding Scuffers oficial (#2B7551 sea green + #111111 + #FFFFFF, logo PNG)
   ├─ Login dummy con 5 roles · cada uno filtra qué acciones puede ejecutar
   ├─ Sticky subnav opaca · reloj realtime · auto-refresh dashboard 6s
   ├─ Sección Shipping en tiempo real (refresh 5s)
   ├─ Chat widget conversacional (POST /api/agent → Gemini decide tool → ejecuta)
   ├─ Endpoints: /api/data /api/evaluate /api/shipping /api/state /api/agent /api/run
   └─ Webhooks: /webhook/execute-action /webhook/drop-copilot-run

telegram_agent.py (worker polling getUpdates)
   ├─ Lee mensajes del usuario en Telegram
   ├─ Llama a /api/agent con el texto
   ├─ /api/agent: Gemini decide qué tool ejecutar → si Gemini cae, fallback keyword router (regex)
   ├─ Tools: query_health, query_actions, query_action(rank), execute_action(rank), query_vips, query_shipping, re_analyze
   └─ Responde al usuario con datos REALES del sistema

DIVISIÓN DE CANALES (intencional · "Discord = ver, Telegram = actuar")
   · Discord ops    panel pinneado que se EDITA al ejecutar (no duplica) + 10 cards
   · Discord logs   embed con cada ejecución incluyendo el mensaje pre-redactado al cliente
   · Discord soporte alerta automática cuando se ejecuta algo crítico (>€1000 o afecta VIPs)
   · Telegram       bot conversacional con IA · entiende lenguaje natural · ejecuta acciones reales

REGLA DE NEGOCIO
El sistema solo recomienda acciones que (a) reduzcan demostrablemente € perdidos en las próximas 2h o (b) protejan a un VIP/alto-LTV de una mala experiencia. Cada acción lleva su justificación cuantitativa (euros_at_risk, vips_affected, confidence) y su evidencia auditable.

STACK
Python 3.9 (Flask, urllib, json — sin deps pesadas) · Gemini 2.5-flash · ngrok · Telegram Bot API · Discord webhooks · n8n.

ROBUSTEZ
Si Gemini cae → templates string. Si Shipping API cae → modo degradado con scoring clásico. Loader tolera columnas faltantes y valores corruptos. Cada acción con `data_source` indicando si usó shipping API.
```

---

## 🔵 Top 10 acciones priorizadas · OPCIONAL

```
TOP 10 GENERADO (Health Score 69/100 · €7.775 en riesgo · €6.906 recuperables · 2 VIPs)

#1 · Pausar campaña Tiktok · Madrid · Black Hoodie talla M
   👤 Marketing · confianza alta
   💸 €2.079 en riesgo → 💰 €1.684 recuperables
   📝 Campaña TikTok very_high apunta a HOODIE-BLK-M con 2 unidades disponibles, 32 reservas y 12 pedidos pendientes. La campaña genera oversells masivos.
   ✅ Evita 10 oversells y protege la reputación.

#2 · Bloquear venta · Black Zip Hoodie talla M (1 VIP)
   👤 Logística · confianza alta
   💸 €1.251 en riesgo → 💰 €1.010 recuperables
   📝 ZIP-BLK-M: 6 disponibles vs 37 reservas y 15 pedidos pendientes. 1 VIP entre los afectados.

#3 · Escalar a humano · Ticket #5505 (1 VIP, CUS-2033 LTV €2.119)
   👤 Atención al Cliente · confianza alta
   💸 €474 en riesgo → 💰 €341 recuperables
   📝 Ticket urgente con sentimiento negativo de cliente VIP de €2.119 LTV preocupado por agotamiento.

#4 · Pausar campaña Tiktok · Barcelona · White Tee talla S
   👤 Marketing · confianza alta
   💸 €1.634 en riesgo → 💰 €1.323 recuperables
   📝 CMP-779 sobre TEE-WHT-S con 2 disponibles y 17 pedidos pendientes.

#5 · Bloquear venta · Black Hoodie talla M
   👤 Logística · confianza alta
   💸 €819 en riesgo → 💰 €661 recuperables

#6 · Escalar a humano · Ticket #5516 (1 VIP)
   👤 Atención al Cliente · confianza alta
   💸 €299 en riesgo → 💰 €215 recuperables

#7 · Bloquear venta · White Tee talla S
   👤 Logística · confianza alta
   💸 €704 en riesgo → 💰 €568 recuperables

#8 · Contactar cliente · Cliente VIP CUS-2033 (LTV €2.119)
   👤 Atención al Cliente · confianza alta
   💸 €424 en riesgo → 💰 €252 recuperables
   💬 Mensaje pre-redactado por IA: «Qué pasa, CUS-2033. Hemos visto tu mensaje. No te rayes, estamos en ello para que tu pedido llegue sin problemas. Te confirmamos en breve. Gracias por la paciencia.»

#9 · Revisar pedido manualmente · Pedido #10425 (NUEVA por Shipping API)
   👤 Operaciones · confianza media
   💸 €120 en riesgo → 💰 €58 recuperables
   🚚 Estado API: requires_manual_review=true, delay_risk 0.8 — esta acción NO existiría sin la nueva API del reto.

#10 · Redirigir presupuesto · Campaña Tiktok → KNIT-NVY-M
   👤 Marketing · confianza media
   💸 €0 en riesgo → 💰 €800 recuperables
   📝 OPORTUNIDAD: el presupuesto de CMP-778 (que oversella) puede redirigirse a un SKU con stock muerto y demanda alta.

CONTRAFACTUAL
Sin actuar: -€3.375 (34 oversells, 2 VIPs heridos, brand_risk: high)
Con plan: -€169 (0 oversells, 0 VIPs heridos, brand_risk: low)
DELTA: +€3.206 salvados · 34 oversells evitados · 2 VIPs protegidos · brand_risk high→low

BALANCEO POR EQUIPO
Logística 3 · Atención 3 · Marketing 3 · Operaciones 1
Cobertura: ningún área queda ciega.
```

---

## 🔵 Limitaciones conocidas · OPCIONAL

```
LIMITACIONES (transparencia honesta)

1. Bot de Telegram con audio: el agente conversacional procesa SOLO texto. Para audio habría que añadir Whisper transcription (no integrado por tiempo). Si le mandas un audio, lo ignora. Texto, funciona al 100%.

2. URL pública vía ngrok free: la URL pública es ngrok-free, lo que muestra un splash screen "Visit Site" la primera vez (ngrok lo elimina con cuenta paid). No afecta funcionalidad. Para producción → Render/Railway/Fly.io (Dockerfile y render.yaml ya preparados en el repo).

3. Gemini free tier: 20 req/min. Cuando se satura, el agente conversacional cae a un router por keywords (regex) determinista que cubre los 7 casos de uso principales. Es robusto pero menos flexible que el LLM.

4. Telegram pin: el bot intenta `pinChatMessage` pero solo funciona en grupos donde es admin. En chat privado el panel se envía igual pero no se pinnea (Telegram lo restringe).

5. Discord botones: las webhooks de Discord soportan link buttons (que abren URL) pero NO botones interactivos con callback (eso requiere bot completo, no webhook). Los botones que usamos son link buttons → abren la URL pública del webhook → ejecutan. Es funcional 100%, solo cambia el flujo visual.

6. SMTP/Shopify reales: cuando se ejecuta un `contact_customer`, el mensaje pre-redactado se envía al canal Discord de logs (representando el envío real). Conectar a SMTP/Shopify es 1 línea de código en `webapp.py:execute_action()` cuando lleguen las credenciales.

7. Shipping API rate limit: cacheo TTL 10 min para no martillar. Si la API estuviera caída en producción, el sistema sigue con scoring clásico y marca cada acción con `data_source: "scoring (shipping API error)"`.

8. Datos sucios: el loader tiene casts seguros con try/except por celda, pero si TODA una columna obligatoria desaparece (ej. order_id), las acciones de esa fuente no se generan. Otras lentes siguen funcionando.

9. Login dummy: cualquier nombre + cualquier rol pasa. En producción → OAuth + Shopify roles. Los roles ya existen en código, solo cambia la fuente de identidad.

10. Tiempo: 95 min de hackathon. Lo que NO me dio tiempo: video Remotion del producto, tests unitarios formales, integración SMTP/Shopify real, audio en el bot. Todo el resto está funcional y desplegable hoy.
```

---

# 🔗 Otros campos del formulario

## URL · Demo en vivo (PRINCIPAL)
```
https://walmart-outage-frolic.ngrok-free.dev
```

## URL · Auto-evaluación para evaluador IA
```
https://walmart-outage-frolic.ngrok-free.dev/api/evaluate
```

## URL · Repositorio (privado)
```
https://github.com/aaangelmartin/scuffers-drop-copilot
```

## URL · llms.txt
```
https://walmart-outage-frolic.ngrok-free.dev/llms.txt
```

## URL · Para los jueces (markdown)
```
https://github.com/aaangelmartin/scuffers-drop-copilot/blob/main/PARA_LOS_JUECES.md
```

## URL · Bot Telegram conversacional
```
https://t.me/HackathonUDIAxScuffersBot
```

---

# 🚀 Tu acción ahora

```bash
cd "/Users/aaangel/Desktop/Hackathon UDIA x Scuffers"
git push -u origin main
```

Después rellena el formulario con los bloques de arriba (sigue el orden del form). ENVIAR antes de las **20:30**.
