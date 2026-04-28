# Arquitectura — Scuffers Drop Co-Pilot

## Cómo viajan los datos (3 líneas)
1. **Ingesta:** `control_tower.py` carga los 6 CSVs de `data/candidate_csvs/` con un loader tolerante a datos sucios + consulta la **Shipping API en vivo** (`lib/shipping_api.py`) solo para pedidos relevantes (≤50 llamadas) con cache 10min y manejo robusto de 401/404/timeout.
2. **Decisión:** un motor de scoring de 4 lentes (Logistics 40% / Customer Care 25% / Marketing 20% / Operations 15%) + 1 lente shipping enriquece ~63 candidatos, Gemini redacta el lenguaje humano y emite un Top 10 con € en riesgo, € recuperables, mensaje listo para cliente y `data_source` indicando si la decisión usa shipping API.
3. **Acción:** la web app Flask sirve dashboard mobile-first con branding Scuffers oficial; los botones EJECUTAR disparan un webhook que actualiza `state.json` (mutación real), notifica Telegram + Discord + Slack en paralelo, y el dashboard refleja el cambio en 8s.

## Regla de negocio principal
**El sistema solo recomienda acciones que (a) reduzcan demostrablemente € perdidos en las próximas 2 horas o (b) protejan a un VIP/cliente de alto LTV de una experiencia rota.** Cada acción lleva su justificación cuantitativa (`euros_at_risk`, `vips_affected`, `confidence`) y su reverso (`expected_impact`). Top 10 con balanceo entre owners para que ningún área quede ciega.

## Stack
- **Python 3.9+** (motor) — pandas para CSVs, requests para Gemini/Telegram/Shopify
- **Gemini 2.5-flash** (lenguaje de los `reason`/`title`/`pre_built_message` y narrativa)
- **n8n** (orquestación visible en pantalla, webhook executor)
- **Telegram Bot** (interfaz táctil con botones Execute/Skip)
- **Streamlit** (dashboard para pantalla compartida durante el pitch)
- **Discord/Slack webhooks** (fan-out opcional según configuración)
