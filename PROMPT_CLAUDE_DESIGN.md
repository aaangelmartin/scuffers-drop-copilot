# PROMPT — Diseña el dashboard "Scuffers Drop Co-Pilot"

Copia y pega este prompt entero en Claude Design / Cursor / cualquier agente de frontend.

---

## CONTEXTO DEL PROYECTO

Estoy compitiendo en el **Hackathon UDIA × Scuffers × ESIC 2026**. Mi proyecto se llama **"Scuffers Drop Co-Pilot"**: un Control Tower operativo para que la marca Scuffers (streetwear premium española) gestione drops de alta demanda en tiempo real, priorizando 10 acciones cuantificadas en € que protegen margen, comunidad y marca.

El dashboard es una **demo en pantalla compartida** que voy a presentar a los fundadores Javi y Jaime junto con un pitch hablado de 60 segundos. Después de la demo del dashboard, salto al móvil para enseñar el bot de Telegram. El dashboard debe ser **espectacular visualmente, instantáneamente comprensible para alguien sin conocimiento técnico** (founders, jurado, equipo de operaciones), y reflejar la estética **Scuffers**.

## QUIÉN ES SCUFFERS (BRAND IDENTITY)

- Marca de streetwear premium española
- Vive de los "drops" (lanzamientos de stock limitado), del "hype" y de una comunidad muy fiel
- Estética: minimalismo brutal, hiper-cuidada, deportiva-urbana
- Paleta: **negro absoluto (#000), blanco off-white, gris carbón (#1a1a1a, #2a2a2a), acentos crema (#f5e8d3) y rojo deportivo (#ff3333)** para alertas. Verde fluor (#00ff88) reservado SOLO para "executed/recovered".
- Tipografía: sans-serif geométrica condensada (estilo Helvetica Neue, Inter Tight, Suisse, o Space Grotesk). MAYÚSCULAS para titulares, mucho letter-spacing.
- Fotografía: high-contrast, blanco y negro, modelos serios
- Influencias: Off-White™ con tags ["like this"], Yeezy Season minimalismo, Acne Studios tipografía, Fear of God spacing, Daily Paper streetwear español
- NO emojis decorativos abusivos, NO colores festivos, NO degradados arcoiris
- SÍ: numeración técnica con leading zeros (01/, 02/, 03/), comillas tipográficas tag-style, divisores horizontales finos, montones de aire

## STACK TÉCNICO (NO NEGOCIABLE)

- **Streamlit** (Python). El archivo se llama `dashboard.py` y se lanza con `streamlit run dashboard.py`.
- Puedo usar `st.markdown(html, unsafe_allow_html=True)` para meter HTML/CSS custom — y debes hacerlo masivamente.
- Puedo usar `st.components.v1.html` para componentes custom si es necesario.
- Puedo importar `plotly` para gráficos.
- NO puedo usar React/Vue/Tailwind como tal — pero SÍ puedo embeber CSS y HTML completo via `st.markdown(unsafe_allow_html=True)`.
- El dashboard lee 3 archivos JSON ya generados (estructura abajo).

## DATOS QUE TIENES QUE PINTAR

Tres archivos JSON en `out/`:

### `out/health_score.json`
```json
{
  "score": 69,
  "verdict": "WARNING",   // CRITICAL | WARNING | HEALTHY
  "components": {
    "stock_health": 86,
    "customer_health": 75,
    "pipeline_health": 80,
    "campaign_health": 25
  },
  "weights": {"stock_health": 0.30, "customer_health": 0.30, "pipeline_health": 0.20, "campaign_health": 0.20},
  "narrative": "Drop Health Score: 69/100 [WARNING]. Atención inmediata requerida en campaign_health."
}
```

### `out/simulation.json`
```json
{
  "do_nothing": {
    "oversells": 34,
    "euros_lost": 3375,
    "vips_hurt": 2,
    "vips_hurt_ids": ["CUS-2033", "CUS-2004"],
    "brand_risk": "high"
  },
  "execute_plan": {
    "oversells": 0,
    "euros_lost": 169,
    "vips_hurt": 0,
    "oversells_avoided": 34,
    "euros_recovered": 3206,
    "vips_protected": 2,
    "brand_risk": "low"
  },
  "delta": {
    "euros_saved": 3206,
    "oversells_avoided": 34,
    "vips_protected": 2,
    "brand_risk_reduction": "high → low"
  },
  "narrative": "Sin actuar en los próximos 120 min, Scuffers perdería €3375 (34 oversells y 2 VIPs heridos)..."
}
```

### `out/actions.json`
```json
{
  "generated_at": "2026-04-28T18:53:00",
  "summary": {
    "health_score": 69,
    "verdict": "WARNING",
    "euros_at_risk_total": 7763,
    "euros_recoverable_total": 6889,
    "vips_protected_total": 2
  },
  "actions": [
    {
      "rank": 1,
      "action_type": "pause_campaign",   // pause_campaign | prevent_oversell | prioritize_order | contact_customer | escalate_ticket | manual_review_order | restock_alert | redirect_campaign_budget
      "target_id": "CMP-778",
      "title": "PAUSA INMEDIATA: Campaña TikTok CMP-778 para HOODIE-BLK-M en Madrid",
      "reason": "La campaña CMP-778 está generando un 3.8x de tráfico y ha gastado 4200€, pero solo quedan 2 unidades disponibles del HOODIE-BLK-M, con 32 reservadas y 12 pedidos pendientes...",
      "expected_impact": "Evitaremos aproximadamente 2079€ en potenciales reembolsos...",
      "confidence": 0.9,
      "owner": "marketing",   // logistics | customer_care | marketing | operations
      "automation_possible": true,
      "euros_at_risk": 2079,
      "euros_recoverable": 1684,
      "vips_affected": 0,
      "pre_built_message": "Hola, gracias por confiar en Scuffers...",  // mensaje listo para enviar al cliente
      "automation_endpoint": "http://localhost:5678/webhook/execute-action",
      "execution_payload": {"action_type": "pause_campaign", "target_id": "CMP-778", "rank": 1},
      "score": 97.5,
      "evidence": {
        "campaign_id": "CMP-778",
        "source": "tiktok",
        "target_sku": "HOODIE-BLK-M",
        "target_city": "Madrid",
        "intensity": "very_high",
        "available": 2,
        "reserved": 32,
        "pending_orders": 12,
        "units_short": 10,
        "budget_spent": 4200
      }
    }
    // ... 9 más
  ]
}
```

## SECCIONES DEL DASHBOARD (en este orden)

### 0. HEADER de marca (top fixed)
- A la izquierda: logo "SCUFFERS" en mayúsculas tracking-out + tag "DROP CO-PILOT" más pequeño
- A la derecha: timestamp del último análisis ("ANÁLISIS · 18:54 UTC · DROP-04")
- Debajo del header: navegación tag-style: `[ HEALTH ] [ COUNTERFACTUAL ] [ ACTIONS ] [ VIP SHIELD ] [ EXECUTIONS ]` (anchors)
- Línea horizontal blanca/2px que separa header del body

### 1. DROP HEALTH SCORE (hero section)
- Centrado, dominante. El score (69) en tipografía gigantesca (entre 180px y 240px), peso black/extrabold, gradient sutil de blanco a gris.
- Debajo: el verdict ("WARNING") en MAYÚSCULAS rojo/amarillo según severity, con pequeño badge.
- A la derecha del score (en row): un **arco de progreso semi-circular** estilo speedometer (puedes hacerlo con SVG embebido) que va de 0 a 100. Color del arco según verdict.
- Debajo del bloque hero: 4 mini-cards con los componentes (stock_health, customer_health, pipeline_health, campaign_health), cada una con su número y un mini-bar progress bar. Mostrar peso ("30% weight") debajo.
- El de campaign_health (que está en 25 - mal) debe destacar visualmente como el más urgente.
- Debajo: el `narrative` en cursiva y color gris claro.

### 2. COUNTERFACTUAL TWIN (la sección más importante del pitch)
- Título grande: `02 / COUNTERFACTUAL TWIN — ¿QUÉ PASA SI NO ACTUAMOS?`
- Layout: dos cards grandes lado a lado, separadas por un divisor vertical o por el delta en medio.
- **CARD IZQUIERDA: SIN ACTUAR**
  - Borde rojo, fondo casi negro
  - Big number: `-€3,375` en rojo
  - Sub-data: 34 oversells / 2 VIPs heridos / brand_risk: HIGH
  - Pequeña ilustración o icono: ⚠️ minimal
- **CARD DERECHA: EJECUTANDO PLAN**
  - Borde verde sutil, fondo casi negro
  - Big number: `-€169` en blanco
  - Sub-data: 0 oversells / 0 VIPs heridos / brand_risk: LOW
- **EN MEDIO o ARRIBA**: el DELTA en una pill grande:
  - `€3,206 SAVED` en verde fluor con tipografía gigante
  - "+34 OVERSELLS AVOIDED · 2 VIPS PROTECTED · BRAND RISK: HIGH → LOW"
- Debajo: la `narrative` en cursiva grande, citada como un quote (con las comillas tipográficas)

### 3. THE PLAYBOOK — 10 ACTIONS
- Título: `03 / THE PLAYBOOK · 10 ACCIONES PRIORIZADAS`
- Cada acción es una **card** estilo "spec card" de drop:
  - Top-left: número grande con leading zero `01/`
  - Top-right: pill con `action_type` + pill con `owner` (color por owner: logistics=rojo, customer_care=naranja-crema, marketing=violeta o blanco, operations=azul muted)
  - Title en MAYÚSCULAS, peso bold, bien grande (24-32px)
  - Línea de info técnica monospace: `SKU/ID: CMP-778 · OWNER: MARKETING · CONFIDENCE: 0.90`
  - **Money block** prominente: `€2,079 AT RISK → €1,684 RECOVERABLE` (la flecha tiene énfasis)
  - Si vips_affected > 0: badge `🛡️ {N} VIP SHIELD` en cream/dorado
  - `reason` en cursiva con borde izquierdo (blockquote style)
  - `expected_impact` con icono check
  - Si hay `pre_built_message`: una caja diferenciada con etiqueta "MESSAGE READY TO SEND →" y el mensaje en serif diferente o monospace, dando feel de "documento generado"
  - **Botón EXECUTE** estilo CTA streetwear: rectangular, fondo verde fluor o crema, texto NEGRO en MAYÚSCULAS bold, sin border-radius o muy poco, con efecto hover
  - Botón secundario más sutil "VIEW EVIDENCE" que despliega el JSON `evidence` en formato code block monospace
- Las cards deben tener separación generosa, hover sutil (slight border glow), y la #1 debe destacar (tal vez ribbon "TOP PRIORITY" o size up)
- **Owner color coding** consistente con un mini-leyenda al inicio de la sección

### 4. VIP SHIELD
- Título: `04 / VIP SHIELD — CLIENTES PROTEGIDOS`
- Solo aparecen las acciones donde `vips_affected > 0`
- Layout más íntimo: lista de "perfiles" de VIP (nombre customer_id, LTV, ciudad, riesgo). 
- Cada VIP card muestra: avatar placeholder con iniciales, customer_id, LTV badge, segment badge, qué acción los protege, y mensaje pre-redactado
- Vibe: como una página "Members" de un club privado

### 5. EXECUTIONS LOG (footer dinámico)
- Título: `05 / EXECUTIONS LOG`
- Tabla minimalista de las acciones que ya se ejecutaron (lee `out/executions.jsonl` si existe, formato: `{timestamp, type, target, source}`)
- Si está vacío, muestra "No executions yet — click EXECUTE on any action above"

### 6. FOOTER
- Pequeño, gris muted: `SCUFFERS × UDIA × ESIC HACKATHON 2026 · BUILT IN 95 MINUTES · DROP-04`
- Eslogan tag-style: `"PROTECTING THE DROP, ONE DECISION AT A TIME."`

## DETALLES VISUALES OBLIGATORIOS

- **Fondo**: negro absoluto (#0a0a0a) en TODA la app. NO el gris claro de Streamlit por defecto.
- **Tipografía cuerpo**: 'Space Grotesk', 'Inter Tight', o fallback sans-serif geométrica
- **Numbers**: peso 800-900 en todos los KPIs grandes, tabular-nums para que cuadren
- **Detalles de marca**:
  - Pequeñas líneas horizontales 1px blancas separando secciones
  - Numeración `01/`, `02/`, etc. al inicio de cada sección
  - Algunas labels en mayúsculas con letter-spacing ~3-5px
  - Comillas tipográficas distintas (« » o "smart quotes") en las narrativas
  - El símbolo `→` MUY usado para dirección de cambio
- **Animations sutiles**: entrada de cards con ligero fade-up via CSS keyframes (sin librerías JS pesadas)
- **Loading**: si los JSON no existen, muestra una pantalla de "AWAITING DATA" con instrucciones de cómo correr el motor
- **Responsive**: que se vea bien proyectado en una pantalla 1920x1080 (es para presentación, no móvil)

## INTERACCIONES

1. Click en el botón **EXECUTE** de cualquier acción → abre `automation_endpoint?type={action_type}&id={target_id}` en una nueva pestaña (ya está cableado a n8n y devuelve una página HTML de confirmación)
2. Click en **VIEW EVIDENCE** → expande/colapsa el JSON `evidence` con sintaxis highlight
3. Auto-refresh: cada 10s relee los JSONs por si el motor se ha re-ejecutado (usa `st.cache_data(ttl=10)`)

## QUE NO HAGAS

- No metas iconos abusivos (1-2 emojis máximo por sección, integrados con sentido)
- No uses `st.metric()` con su look default — los KPIs son hechos a mano con HTML/CSS
- No tabs ni sidebars de Streamlit — single-page, scroll vertical
- No uses la paleta de Streamlit por defecto (azules) en absoluto
- No metas explicaciones del producto ni "about us" — el dashboard es para alguien que ya está dentro de la situación

## INSPIRACIÓN VISUAL DE REFERENCIA

- Off-White™ product cards (las pestañas con `"PRODUCT"`, `"COLOR"`, etc.)
- Página de Yeezy Season releases
- Linear.app (oscuro, datos densos, tipografía contundente)
- Bloomberg Terminal (densidad de info pero monoespaciada)
- Acne Studios website (tipografía huge, blanco/negro, mucho aire)
- Vercel dashboard (oscuro, gradientes sutiles, monospace)
- The Browser Company (Arc) — micro-interactions

## ENTREGABLE

Un único archivo `dashboard.py` con todo el HTML/CSS embebido que:
1. Sea **plug & play**: `streamlit run dashboard.py` y funciona
2. Lea los 3 JSON de `out/`
3. Tenga TODO el styling custom (no use defaults de Streamlit)
4. Sea **visualmente impactante** desde el primer pixel
5. Funcione en pantalla 1920x1080 proyectada
6. Quepa la lógica completa en ~400-600 líneas

Comenta el código por secciones (`# SECTION 1: HEADER`, etc.) para que pueda iterar.
