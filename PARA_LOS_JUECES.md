# 🎯 Para los jueces · cómo probar Scuffers Drop Co-Pilot

> Léete esto justo antes de la demo. 30 segundos.

---

## 📲 Cómo accedéis al sistema

### 1. Web app (móvil o desktop)
**https://walmart-outage-frolic.ngrok-free.dev**

> ⚠ **La primera vez** ngrok muestra una pantalla de "abuse warning". Pulsa **Visit Site** una sola vez. A partir de ahí entras directo. Esto es un límite del plan gratuito de ngrok, no afecta a la funcionalidad.

Pasos:
1. Abre la URL → pantalla de **login**
2. Pon tu nombre y elige rol (**Manager** ve todo)
3. Ya estás dentro del panel — **funciona en móvil y desktop**

### 2. Discord (server público que el equipo creó)
Únete al server con el invite que os pasarán. Ahí veréis:
- 📌 Un **panel pinneado** con el resumen del drop (se actualiza solo)
- 10 **cards individuales** con cada acción
- Cada card lleva un botón **"→ Ejecutar esta acción"** que dispara la acción real

### 3. Telegram (privado del founder)
El bot envía al chat privado del founder · puedes verlo en pantalla compartida durante la demo.

---

## 🎮 Qué probar (en orden)

| # | Prueba | Qué deberías ver |
|---|---|---|
| 1 | Abre el dashboard en el móvil | Logo Scuffers + login Spanish |
| 2 | Entra como **Manager** | Ves todas las 10 acciones |
| 3 | Mira el **Health Score** (69/100) y los KPIs | "€7.775 en riesgo" — todo en castellano |
| 4 | Comprueba el **banner amarillo "Shipping API conectada"** | "50 pedidos · 10 incidencias" — la nueva API del reto está consumida en vivo |
| 5 | Pulsa **filtros**: "logística", "marketing", "VIPs", "mías" | Las cards se filtran instantáneamente |
| 6 | Pulsa **↻ re-analizar** (header) | El motor recalcula con shipping API en directo |
| 7 | Toca **→ Ejecutar** en cualquier acción | Se abre página de confirmación verde · acción registrada |
| 8 | **Vuelve al dashboard** | El KPI "€ ya salvados" sube en TIEMPO REAL · esa acción ya no aparece · entra la siguiente del pool de candidatos |
| 9 | Mira **Discord** | El panel pinneado se ha **EDITADO** (no duplicado) — actualiza el contador · llega un mensaje "✅ Acción ejecutada" |
| 10 | Mira **Telegram** | Idem · panel pinneado actualizado |
| 11 | Sal y vuelve a entrar como **Logística** | Las acciones de marketing aparecen bloqueadas en gris |

---

## 🔍 Lo que es 100% funcional (no mocks)

✅ **Health Score 69/100**: calculado en vivo desde 22 SKUs + 180 pedidos + 120 clientes + 18 tickets + 5 campañas + 50 envíos consultados a API
✅ **Top 10 dinámico**: al ejecutar una acción, entra automáticamente la siguiente del pool de 67 candidatos
✅ **KPIs LIVE**: € en riesgo, € salvados, VIPs protegidos, plan ejecutado — actualizan en tiempo real
✅ **Reloj** del header: actualiza cada segundo
✅ **Auto-refresh**: el dashboard detecta cambios cada 6 segundos
✅ **Shipping API**: integrada con candidate_id `1498`, 50 llamadas reales, 10 problemáticos detectados
✅ **Telegram bot**: 12 mensajes en español natural por demo
✅ **Discord webhook**: panel pinneado que se EDITA + 10 acciones individuales
✅ **Slack webhook**: listo (falta solo URL en `.env`)
✅ **Botones EJECUTAR**: actualizan state.json, notifican Telegram + Discord, edit panel pinneado, refresh dashboard
✅ **Login dummy con roles**: Manager / Logística / Atención / Marketing / Operaciones — cada uno ve y ejecuta solo lo suyo
✅ **Filtros**: por owner, por VIP, por "lo mío"
✅ **Re-analizar**: relanza el motor entero (incluyendo Shipping API)

---

## 🧠 Para el pitch

**"Imaginad las 16:00 de un drop. El equipo abre esto en su móvil:**

1. **Health Score 69/100 — Atención.** Una sola cifra. No 47 alertas.
2. **€7.775 en riesgo. Si ejecutáis las 10 acciones, recuperáis €6.906 y protegéis a 2 VIPs.** No es un dashboard, es un plan de batalla con ROI calculado.
3. **Cada acción tiene un botón EJECUTAR**. El operador toca, se notifica al equipo entero (Discord + Telegram + Slack), el panel se actualiza solo.
4. **Cuando Scuffers añadió la API de envíos en vivo durante el reto**, el sistema la absorbió en 30 segundos y reordenó las acciones. Pedidos con `delay_risk: 0.8` subieron al top 10 sin que tocáramos código.
5. **Y todo en castellano natural, sin código a la vista, optimizado para móvil**. El equipo de operaciones lo usa sin saber qué es un SKU."

---

## 🔥 La frase de cierre

**"Esto no es una alerta. Es una decisión ejecutada en 1 click. Lo difícil ya no es decidir — lo difícil es resistir las ganas de comprar más cápsulas."**
