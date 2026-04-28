# Pitch — Drop Co-Pilot · 60 segundos para Javi y Jaime

> Tono: directo, urbano, datos. Cero jerga técnica. Cada frase con cifra.

---

## 🎯 Bullet 1 — El € que estáis a punto de perder (15 seg)
> **"Sin actuar en las próximas 2 horas, este drop os va a costar €3,375 en refunds y vais a quemar a 2 VIPs (LTV €4k cada uno). En total, €5,660 por la borda."**

*Datos en pantalla del Counterfactual Twin: tabla "Sin actuar vs. Ejecutando plan".*

---

## 🛡️ Bullet 2 — El plan ya está cargado (25 seg)
> **"Os he priorizado las 10 cosas que tenéis que hacer AHORA — no 47, ni 200: 10. Cada una lleva el € que salvaréis, el cliente concreto al que afecta y un mensaje listo para enviarle. Si pulsáis 'Execute' en Telegram, se dispara: la campaña de TikTok que está reventando el HOODIE-BLK-M se pausa, los pedidos del VIP CUS-2033 (LTV €2,119) se priorizan, y el ticket urgente del que ya está cabreado se escala a humano. Salváis €3,206 y protegéis al 100% de los VIPs en riesgo."**

*Mostrar acción #1 en Telegram con botones, pulsar Execute en directo.*

---

## 🚀 Bullet 3 — Lo que esto es a partir de hoy (20 seg)
> **"Esto no es un dashboard. Es un Co-Pilot. Cada drop futuro arranca con un Health Score, una simulación cuantificada y un plan de batalla en Telegram en 60 segundos. Vuestro equipo ops gana ~4 horas por drop, deja de apagar fuegos y se dedica a lo que importa: producto, comunidad y márgenes. Y para vosotros: un número, un plan, y un botón. Lo difícil ya no es decidir — lo difícil es resistir las ganas de comprar más cápsulas."**

*Cierre con el Drop Health Score "47 → 78 con plan ejecutado".*

---

## 🎬 Demo flow (90 seg total)

| Segundo | Acción | Pantalla |
|---|---|---|
| 0–10 | "Imaginad que son las 16:00 de un drop. Esto es lo que ven nuestros founders." | Dashboard Streamlit, Health Score visible |
| 10–25 | Mostrar Counterfactual Twin | Sección "Sin actuar vs. Plan" |
| 25–40 | Saltar a Telegram (proyectar móvil), mostrar Health + 3 primeras acciones | Telegram bot del jurado |
| 40–55 | Pulsar **Execute** en acción #1 (CMP-778 TikTok) | Aparece ack en Telegram + página HTML "Action executed" |
| 55–75 | Volver al pitch: "salváis €3,206 y 2 VIPs sin tocar una hoja de cálculo" | Pitch + dashboard |
| 75–90 | "Y mañana, en cada drop futuro, este Co-Pilot está esperando. Decisión clara, plan, botón." | Cierre |

---

## 📌 Frases de respaldo si preguntan

- **"¿Cómo justificáis esos números?"** → "Cada acción tiene una `evidence` JSON con los datos brutos del CSV — disponible para auditoría. Top 1 (CMP-778) cubre 12 pedidos pendientes, 2 unidades disponibles, TikTok very_high. Multiplicado por unit_price + refund_overhead + LTV en riesgo."
- **"¿Y si la IA se equivoca?"** → "El motor es determinista por reglas; Gemini solo redacta el lenguaje humano. Si Gemini cae, el sistema sigue funcionando con templates. Cada acción tiene `confidence` numérica."
- **"¿Y la integración real con Shopify?"** → "El botón Execute dispara un webhook en n8n. Hoy registra y notifica. Conectar a Shopify Admin API son 5 minutos: solo cambiar el endpoint en el switch de n8n."
- **"¿Cuánto le ahorraría esto al equipo?"** → "El equipo de ops dedica ~4 horas/drop revisando Excel y respondiendo tickets duplicados. Esto se carga el 70% de eso. Y previene oversells que rompen la marca."

---

## 🔥 Por qué ganamos

| El resto de equipos van a presentar | Nosotros presentamos |
|---|---|
| Top 10 de "riesgos detectados" | Plan de batalla con € y plan de ataque |
| Score técnico de IA | Drop Health Score (KPI ejecutivo único) |
| "Aquí podríamos automatizar" | Botones que ya ejecutan en Telegram |
| Análisis estático en pantalla | Notificación que aterriza en el móvil |
| Lista descriptiva | Counterfactual: cuánto € salváis vs. perdéis |
