"""Scuffers Drop Co-Pilot — Dashboard ejecutivo.
Run: streamlit run dashboard.py
"""
import os, json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scuffers Drop Co-Pilot", page_icon="🩺", layout="wide")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")


@st.cache_data(ttl=5)
def load_data():
    actions = json.load(open(os.path.join(OUT, "actions.json")))
    sim = json.load(open(os.path.join(OUT, "simulation.json")))
    health = json.load(open(os.path.join(OUT, "health_score.json")))
    return actions, sim, health


# ---- CSS dark Scuffers vibe
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #fafafa; }
    h1, h2, h3, h4 { color: #fafafa !important; }
    .metric-big {
        font-size: 88px; font-weight: 900; line-height: 1;
        background: linear-gradient(180deg, #fff 0%, #888 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .verdict-CRITICAL { color: #ff3333; }
    .verdict-WARNING  { color: #ffaa00; }
    .verdict-HEALTHY  { color: #00cc66; }
    .action-card {
        background: #181818; padding: 20px; border-radius: 12px; margin-bottom: 12px;
        border-left: 4px solid #ff3333;
    }
    .action-card.logistics { border-left-color: #ff3333; }
    .action-card.customer_care { border-left-color: #ff9933; }
    .action-card.marketing { border-left-color: #cc66ff; }
    .action-card.operations { border-left-color: #66ccff; }
    .pill { display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 12px; background: #2a2a2a; color: #aaa; margin-right: 6px; }
    .euros { font-size: 22px; font-weight: bold; color: #00cc66; }
    .euros-risk { color: #ff5555; }
</style>
""", unsafe_allow_html=True)

st.title("🩺 Scuffers Drop Co-Pilot")
st.caption("Control Tower operativo — protege margen, comunidad y marca durante el drop")

try:
    actions_data, sim, health = load_data()
except FileNotFoundError:
    st.error("⚠️  Aún no hay output. Ejecuta `python3 control_tower.py`.")
    st.stop()

# ----------------------------------------------------------- HEADER
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    score = health["score"]
    verdict = health["verdict"]
    st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <div style="font-size:14px; letter-spacing:3px; color:#888;">DROP HEALTH SCORE</div>
        <div class="metric-big verdict-{verdict}">{score}</div>
        <div style="font-size:18px; font-weight:bold;" class="verdict-{verdict}">— {verdict} —</div>
        <div style="font-size:13px; color:#aaa; margin-top:10px;">{health.get('narrative','')}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.metric("💸 At risk", f"€{actions_data['summary']['euros_at_risk_total']:,.0f}",
              delta=f"-€{sim['do_nothing']['euros_lost']:,.0f} sin actuar", delta_color="inverse")
with col3:
    st.metric("💰 Recoverable", f"€{actions_data['summary']['euros_recoverable_total']:,.0f}",
              delta=f"+€{sim['delta']['euros_saved']:,.0f} con plan")

# Health components
st.markdown("### Componentes del Health Score")
c1, c2, c3, c4 = st.columns(4)
comps = health["components"]
c1.metric("📦 Stock", f"{comps['stock_health']}/100")
c2.metric("👤 Customer", f"{comps['customer_health']}/100")
c3.metric("🚚 Pipeline", f"{comps['pipeline_health']}/100")
c4.metric("📣 Campaign", f"{comps['campaign_health']}/100")

st.divider()

# ----------------------------------------------------------- COUNTERFACTUAL
st.markdown("## 🔮 Counterfactual Twin")
st.markdown(f"*{sim.get('narrative','')}*")

cf1, cf2, cf3 = st.columns(3)
with cf1:
    st.markdown("#### ❌ Sin actuar")
    st.markdown(f"**€{sim['do_nothing']['euros_lost']:,.0f}** perdidos")
    st.markdown(f"**{sim['do_nothing']['oversells']}** oversells")
    st.markdown(f"**{sim['do_nothing']['vips_hurt']}** VIPs heridos")
    st.markdown(f"Brand risk: `{sim['do_nothing']['brand_risk']}`")
with cf2:
    st.markdown("#### ✅ Ejecutando plan")
    st.markdown(f"**€{sim['execute_plan']['euros_lost']:,.0f}** perdidos")
    st.markdown(f"**{sim['execute_plan']['oversells']}** oversells")
    st.markdown(f"**{sim['execute_plan']['vips_hurt']}** VIPs heridos")
    st.markdown(f"Brand risk: `{sim['execute_plan']['brand_risk']}`")
with cf3:
    st.markdown("#### 💎 Delta (lo que ganas)")
    st.markdown(f"<span class='euros'>+€{sim['delta']['euros_saved']:,.0f}</span> salvados", unsafe_allow_html=True)
    st.markdown(f"**{sim['delta']['oversells_avoided']}** oversells evitados")
    st.markdown(f"**{sim['delta']['vips_protected']}** VIPs protegidos")
    st.markdown(f"Brand: {sim['delta']['brand_risk_reduction']}")

st.divider()

# ----------------------------------------------------------- ACTIONS
st.markdown(f"## 🎯 Top {len(actions_data['actions'])} acciones priorizadas")

for a in actions_data["actions"]:
    owner_class = a["owner"]
    eur_risk = a["euros_at_risk"]
    eur_rec = a["euros_recoverable"]

    with st.container():
        st.markdown(f"""
        <div class="action-card {owner_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <span style="font-size:14px; color:#888;">#{a['rank']}</span>
                    <span class="pill">{a['action_type']}</span>
                    <span class="pill">👤 {a['owner']}</span>
                    <span class="pill">target: <code>{a['target_id']}</code></span>
                    <span class="pill">conf: {a['confidence']}</span>
                </div>
                <div style="text-align:right;">
                    <div class="euros euros-risk">€{eur_risk:,.0f}</div>
                    <div style="font-size:12px;color:#888;">at risk</div>
                </div>
            </div>
            <h3 style="margin-top:10px;">{a['title']}</h3>
            <p style="color:#bbb;"><b>Por qué:</b> {a['reason']}</p>
            <p style="color:#bbb;"><b>Impact:</b> {a['expected_impact']}</p>
            {f'<p style="background:#222;padding:12px;border-radius:6px;color:#ddd;font-style:italic;">💬 {a["pre_built_message"]}</p>' if a.get('pre_built_message') else ''}
            <div style="margin-top:10px;">
                <span class="euros">€{eur_rec:,.0f} recoverable</span>
                {f'<span style="color:#ff9933;margin-left:20px;">🛡️ {a["vips_affected"]} VIP(s)</span>' if a.get('vips_affected') else ''}
                <a href="{a['automation_endpoint']}?type={a['action_type']}&id={a['target_id']}" target="_blank"
                   style="float:right; background:#00cc66; color:#000; padding:8px 18px; border-radius:6px; text-decoration:none; font-weight:bold;">
                    ▶️ EXECUTE
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------------- VIP SHIELD
vips = [a for a in actions_data["actions"] if a.get("vips_affected", 0) > 0]
if vips:
    st.markdown("## 🛡️ VIP Shield")
    st.caption(f"{len(vips)} acciones protegen directamente a VIPs")
    df = pd.DataFrame([{
        "#": a["rank"],
        "Action": a["action_type"],
        "Target": a["target_id"],
        "Reason": a["title"],
        "VIPs": a["vips_affected"],
        "€ recoverable": f"€{a['euros_recoverable']:,.0f}",
    } for a in vips])
    st.dataframe(df, hide_index=True, use_container_width=True)

# ----------------------------------------------------------- FOOTER
st.divider()
st.caption(f"Generated at {actions_data.get('generated_at','?')} · Scuffers × UDIA × ESIC Hackathon 2026")
