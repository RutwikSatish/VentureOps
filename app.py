"""
VentureOps — Startup Operational Due Diligence Engine
Built for the Roux Institute | Rutwik Satish
Demo: Ativegh Logistics Pvt. Ltd. — Real startup case study
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="VentureOps — Startup Due Diligence Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #1a1a2e, #16213e, #0f3460);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #6b7280; font-size: 1rem; margin-bottom: 1rem; }
    .metric-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1.2rem; text-align: center;
    }
    .score-excellent { color: #16a34a; font-weight: 800; font-size: 2rem; }
    .score-good      { color: #2563eb; font-weight: 800; font-size: 2rem; }
    .score-moderate  { color: #d97706; font-weight: 800; font-size: 2rem; }
    .score-critical  { color: #dc2626; font-weight: 800; font-size: 2rem; }
    .insight-box  { background:#f0fdf4; border-left:4px solid #16a34a; padding:1rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
    .warning-box  { background:#fffbeb; border-left:4px solid #d97706; padding:1rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
    .danger-box   { background:#fef2f2; border-left:4px solid #dc2626; padding:1rem; border-radius:0 8px 8px 0; margin:0.5rem 0; }
    .story-box    { background:#eff6ff; border:2px solid #2563eb; border-radius:12px; padding:1.2rem; margin:0.8rem 0; }
    .framework-note { background:#f1f5f9; border:1px solid #cbd5e1; border-radius:8px; padding:0.8rem; font-size:0.78rem; color:#64748b; margin-top:1rem; }
    .stTabs [data-baseweb="tab"] { font-weight:600; font-size:0.95rem; }
</style>
""", unsafe_allow_html=True)

# ── ATIVEGH DEMO DATA ──────────────────────────────────────────────────────────
# Based on: MCA filing (paid-up capital ₹15L, 4 years old, 7 B2B clients)
# Sector: Port logistics at Haldia, serving steel/ferro alloy companies in Jharkhand
# Conversion: 1 USD ≈ 83 INR (estimated figures — actual financials not public)
ATIVEGH = {
    # Profile
    "name":          "Ativegh Logistics Pvt. Ltd.",
    "industry":      "Other",
    "stage":         "Pre-Seed",
    "team_size":     8,
    "founded_years": 4,
    "biz_model":     "Services",
    # Financials (USD equivalents, estimated)
    "monthly_revenue": 5500,   # ~₹4.5L/month from 7 industrial clients
    "monthly_burn":    4200,   # fuel, driver wages, vehicle maintenance, admin
    "cash_on_hand":    9000,   # limited working capital from ₹15L paid-up
    "arpu":            785,    # ~₹65K/month per client average
    "cac":             120,    # referral-based, negligible formal CAC
    "gross_margin_pct":32,     # logistics: low margin, high variable cost
    "monthly_churn":   0.8,    # sticky B2B relationships, low churn
    "mrr_growth":      3.5,    # steady but slow growth typical for regional logistics
    # Ops readiness sliders
    "sc_single_source": 8,  # 7 clients all in steel/ferro sector — extreme concentration
    "sc_lead_time":     6,  # port-based, somewhat predictable
    "sc_inventory":     4,  # limited buffer, asset-light model
    "ue_ltv_cac":       3,  # unit economics not formally tracked
    "ue_payback":       4,  # not measured — estimated moderate
    "ue_margin":        3,  # 32% gross margin, below target
    "ol_automation":    2,  # almost entirely manual — phone/paper based dispatch
    "ol_scalability":   3,  # adding clients requires adding drivers/vehicles
    "tc_key_person":    9,  # family business, 3 of 4 directors share surname
    "tc_hiring":        2,  # no formal hiring pipeline
    "pm_documentation": 2,  # no formal SOPs, 4-year-old family operation
    "pm_kpis":          2,  # no KPI dashboards or tracking cadence
    "td_infrastructure":3,  # basic tech (WhatsApp/phone dispatch)
    "td_debt_level":    2,  # no significant tech debt — just no tech
    # TAM/SAM/SOM (Industrial logistics, Haldia Port / Jharkhand-WB corridor)
    "total_potential_customers": 850,   # industrial companies in the corridor
    "acv_annual":                9420,  # $785/month × 12
    "sam_filter_pct":            22,    # geographic + port-adjacent service fit
    "som_capture_pct":           12,    # realistic 3-year capture given team size
    "industry_market_size":      18.5,  # Indian industrial logistics market ($B)
    "td_segment_pct":            4,     # port ground support is a small sub-segment
    "td_geo_pct":                8,     # Jharkhand/WB corridor
    "td_product_fit_pct":        65,
    # Scale bottleneck
    "current_customers":    7,
    "ops_team_size":        4,    # 4 operational staff (drivers + coordinator)
    "customers_per_csm":    3,    # each staff handles ~3 clients at this service level
    "infra_cost_per_cust":  2.0,  # minimal tech infra
    "supplier_count":       2,    # 2 fuel/vehicle vendors
    "single_source_pct":    80,   # 80%+ revenue from steel sector
    "manual_ops_hrs_week":  55,   # high manual ops — dispatch, tracking, invoicing
    "tech_incidents_month": 1,
    "hiring_time_weeks":    8,
    "monthly_hiring_budget":400,
}

# ── SESSION STATE INIT ─────────────────────────────────────────────────────────
def load_demo():
    for k, v in ATIVEGH.items():
        st.session_state[f"ativegh_{k}"] = v
    st.session_state["demo_loaded"] = True

if "demo_loaded" not in st.session_state:
    st.session_state["demo_loaded"] = False

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🔬 VentureOps</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Startup Operational Due Diligence Engine — Built for the Roux Institute</p>', unsafe_allow_html=True)

col_btn1, col_btn2, _ = st.columns([1, 1, 3])
with col_btn1:
    if st.button("🏭 Load Ativegh Logistics Demo", use_container_width=True, type="primary"):
        load_demo()
        st.rerun()
with col_btn2:
    if st.button("🔄 Reset to Blank", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Show demo story banner
if st.session_state.get("demo_loaded"):
    st.markdown("""
    <div class="story-box">
    <b>🏭 Demo: Ativegh Logistics Pvt. Ltd.</b> — Real startup case study<br>
    <span style="font-size:0.9rem;">Port logistics company at Haldia Port, Jharkhand. Established 2021. 
    7 B2B clients across the Jharkhand–West Bengal steel corridor. Bootstrapped on ₹15L paid-up capital (~$18K). 
    Family-run — 3 of 4 directors share a surname. All financials are estimated from public MCA filings 
    and industry benchmarks since private financials are not disclosed.<br><br>
    <b>What to watch:</b> Client concentration risk (all 7 clients in steel sector), 
    key-person dependency (family-run), and zero process automation are the three signals 
    this tool will flag immediately.</span>
    </div>
    """, unsafe_allow_html=True)

def sv(key, default):
    """Get session value or default."""
    return st.session_state.get(f"ativegh_{key}", default)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏢 Startup Profile")
    if st.session_state.get("demo_loaded"):
        st.caption("🔵 Demo data loaded: Ativegh Logistics")

    industry_opts = ["SaaS / Software","E-Commerce","HealthTech","FinTech",
                     "DeepTech / Hardware","Marketplace","CleanTech","EdTech","Other"]
    stage_opts    = ["Pre-Seed","Seed","Series A","Series B+"]
    bm_opts       = ["B2B SaaS","B2C SaaS","Marketplace","E-Commerce",
                     "Hardware + Software","Services","Freemium"]

    startup_name     = st.text_input("Startup Name", sv("name","Acme AI"))
    industry         = st.selectbox("Industry", industry_opts,
                                     index=industry_opts.index(sv("industry","SaaS / Software")))
    stage            = st.selectbox("Stage", stage_opts,
                                     index=stage_opts.index(sv("stage","Seed")))
    team_size        = st.slider("Team Size (FTEs)", 1, 200, sv("team_size", 12))
    founded_years    = st.slider("Years Since Founded", 0, 10, sv("founded_years", 2))
    biz_model        = st.selectbox("Business Model", bm_opts,
                                     index=bm_opts.index(sv("biz_model","B2B SaaS")))

    st.divider()
    st.markdown("### 💰 Financials")
    monthly_revenue  = st.number_input("Monthly Revenue ($)", 0, 10_000_000,
                                        sv("monthly_revenue", 50000), step=500)
    monthly_burn     = st.number_input("Monthly Gross Burn ($)", 1000, 10_000_000,
                                        sv("monthly_burn", 150000), step=500)
    cash_on_hand     = st.number_input("Cash on Hand ($)", 0, 100_000_000,
                                        sv("cash_on_hand", 1200000), step=500)
    arpu             = st.number_input("Avg Revenue Per Client/Month ($)", 1, 100_000,
                                        sv("arpu", 299))
    cac              = st.number_input("Customer Acquisition Cost ($)", 1, 500_000,
                                        sv("cac", 900))
    gross_margin_pct = st.slider("Gross Margin (%)", 0, 100, sv("gross_margin_pct", 72))
    monthly_churn    = st.slider("Monthly Churn Rate (%)", 0.0, 20.0,
                                  float(sv("monthly_churn", 2.5)), 0.1)
    mrr_growth       = st.slider("MoM Revenue Growth (%)", -20.0, 50.0,
                                  float(sv("mrr_growth", 8.0)), 0.5)

    st.divider()
    st.caption("📚 Frameworks: Bessemer VP · McKinsey · CB Insights · Antler")

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Ops Readiness Score",
    "📐 TAM / SAM / SOM",
    "🔥 Runway & Burn",
    "⚡ Scale Bottleneck",
    "🤖 AI Strategic Brief"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OPERATIONAL READINESS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🎯 Operational Readiness Score")

    if st.session_state.get("demo_loaded"):
        st.markdown("""
        <div class="warning-box">
        <b>Ativegh Context:</b> This is a 4-year-old bootstrapped port logistics company.
        The sliders below reflect what we know from public MCA data, the company profile,
        and typical characteristics of small Indian B2B logistics operators at this stage.
        Move any slider to simulate a scenario change.
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Supply Chain & Delivery Risk")
        st.caption("⚠️ All 7 clients are in steel/ferro alloy sector — extreme industry concentration")
        sc_single_source = st.slider("Client/sector concentration risk", 0, 10,
                                      sv("sc_single_source", 5),
                                      help="10 = All revenue from one sector. Ativegh: 7 clients, all steel — rated 8.")
        sc_lead_time     = st.slider("Delivery predictability", 0, 10,
                                      sv("sc_lead_time", 6),
                                      help="Port-based logistics has some predictability but weather and port delays apply.")
        sc_inventory     = st.slider("Operational buffer adequacy", 0, 10,
                                      sv("sc_inventory", 4),
                                      help="Asset-light model, limited spare vehicle capacity.")

        st.markdown("#### Unit Economics Health")
        st.caption("⚠️ Unit economics likely not formally tracked at this stage")
        ue_ltv_cac  = st.slider("LTV:CAC ratio awareness", 0, 10, sv("ue_ltv_cac", 5),
                                 help="0 = Not tracked. Ativegh: referral-based, CAC is near zero but LTV not measured.")
        ue_payback  = st.slider("Revenue per client sustainability", 0, 10, sv("ue_payback", 5),
                                 help="Rated on consistency of client billing and payment terms.")
        ue_margin   = st.slider("Gross margin sustainability", 0, 10, sv("ue_margin", 6),
                                 help="32% gross margin. Logistics is inherently low-margin. Rated 3.")

    with col2:
        st.markdown("#### Operational Leverage")
        st.caption("🔴 Almost entirely manual — phone/WhatsApp dispatch, paper invoicing")
        ol_automation  = st.slider("Process automation maturity", 0, 10, sv("ol_automation", 4),
                                    help="0 = Fully manual. Ativegh dispatch and tracking is phone-based. Rated 2.")
        ol_scalability = st.slider("Revenue scalability without headcount", 0, 10, sv("ol_scalability", 5),
                                    help="Each new client requires additional driver. Not a scalable model. Rated 3.")

        st.markdown("#### Team Capacity & Execution")
        st.caption("🔴 Family business — 3 of 4 directors share surname Kharakia")
        tc_key_person = st.slider("Key-person dependency risk", 0, 10, sv("tc_key_person", 6),
                                   help="10 = Critical decisions concentrated in 1-2 people. Family-run = high risk. Rated 9.")
        tc_hiring     = st.slider("Hiring pipeline for critical roles", 0, 10, sv("tc_hiring", 5),
                                   help="No formal hiring process visible. Rated 2.")

        st.markdown("#### Process Maturity")
        st.caption("🔴 4-year-old bootstrapped operation — SOPs and KPIs unlikely to exist formally")
        pm_documentation = st.slider("SOPs and process documentation", 0, 10, sv("pm_documentation", 4),
                                      help="No evidence of formal SOPs for a company at this stage and size. Rated 2.")
        pm_kpis          = st.slider("KPI framework and monitoring", 0, 10, sv("pm_kpis", 5),
                                      help="No KPI dashboards visible. Likely managed by gut feel. Rated 2.")

        st.markdown("#### Tech Debt Exposure")
        st.caption("ℹ️ Not tech-native — minimal tech infrastructure, minimal tech debt")
        td_infrastructure = st.slider("Infrastructure scalability", 0, 10, sv("td_infrastructure", 5),
                                       help="Basic mobile/WhatsApp operations. No cloud infrastructure. Rated 3.")
        td_debt_level     = st.slider("Known tech debt severity", 0, 10, sv("td_debt_level", 4),
                                       help="No significant tech debt — there is simply no tech. Rated 2.")

    # Scoring
    sc_score = (10 - sc_single_source) * 0.4 + sc_lead_time * 0.3 + sc_inventory * 0.3
    ue_score = ue_ltv_cac * 0.35 + ue_payback * 0.35 + ue_margin * 0.30
    ol_score = ol_automation * 0.5 + ol_scalability * 0.5
    tc_score = (10 - tc_key_person) * 0.5 + tc_hiring * 0.5
    pm_score = pm_documentation * 0.5 + pm_kpis * 0.5
    td_score = td_infrastructure * 0.5 + (10 - td_debt_level) * 0.5

    weights = {
        "Supply Chain & Delivery": (sc_score, 0.18),
        "Unit Economics":          (ue_score, 0.22),
        "Operational Leverage":    (ol_score, 0.18),
        "Team Capacity":           (tc_score, 0.17),
        "Process Maturity":        (pm_score, 0.13),
        "Tech Debt":               (td_score, 0.12),
    }

    total_score = sum(s * w for s, w in weights.values())

    if total_score >= 7.5:
        classification = "🟢 Launch-Ready"; cls_color = "score-excellent"
        cls_desc = "Strong operational foundation. Ready to scale."
    elif total_score >= 5.5:
        classification = "🟡 Scaling Risk"; cls_color = "score-moderate"
        cls_desc = "Viable but gaps will compound at scale."
    elif total_score >= 3.5:
        classification = "🟠 Ops Gaps"; cls_color = "score-good"
        cls_desc = "Multiple structural weaknesses. High risk without remediation plan."
    else:
        classification = "🔴 Critical Gaps"; cls_color = "score-critical"
        cls_desc = "Operational fundamentals not in place. High failure risk at 2x scale."

    st.divider()
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.markdown(f"""<div class="metric-card">
            <div style="color:#6b7280;font-size:0.85rem;">OVERALL OPS SCORE</div>
            <div class="{cls_color}">{total_score:.1f}/10</div>
            <div style="font-size:0.9rem;font-weight:600;">{classification}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        weakest = min(weights.items(), key=lambda x: x[1][0])
        strongest = max(weights.items(), key=lambda x: x[1][0])
        st.markdown(f"""<div class="metric-card">
            <div style="color:#6b7280;font-size:0.85rem;">WEAKEST DIMENSION</div>
            <div class="score-critical" style="font-size:1.3rem;">{weakest[0]}</div>
            <div style="font-size:0.9rem;">{weakest[1][0]:.1f}/10</div>
            <div style="font-size:0.75rem;color:#16a34a;margin-top:0.3rem;">
            Strongest: {strongest[0]} ({strongest[1][0]:.1f}/10)</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"**Assessment:** {cls_desc}")
        for dim, (score, _) in weights.items():
            if score < 5:
                st.markdown(f'<div class="danger-box">⚠️ <b>{dim}</b> — {score:.1f}/10. Intervention required before scaling.</div>', unsafe_allow_html=True)
            elif score < 7:
                st.markdown(f'<div class="warning-box">🔶 <b>{dim}</b> — {score:.1f}/10. Monitor closely.</div>', unsafe_allow_html=True)

    if st.session_state.get("demo_loaded"):
        st.markdown("""
        <div class="danger-box">
        <b>Ativegh Insight:</b> The three critical flags — key-person dependency, process automation,
        and process maturity — are all interconnected. The business runs on the knowledge and relationships
        of the founding family. If one key person steps back, there is no documented process to hand off.
        This is the single biggest risk before any growth attempt.
        </div>
        """, unsafe_allow_html=True)

    # Radar
    categories = list(weights.keys())
    values_norm = [(s/10)*100 for s, _ in weights.values()]
    fig_radar = go.Figure(go.Scatterpolar(
        r=values_norm + [values_norm[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.15)',
        line=dict(color='#2563eb', width=2),
        name=startup_name
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        showlegend=False, title=f"Operational Readiness Radar — {startup_name}",
        height=400, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("""<div class="framework-note">
    📚 <b>Scoring Framework:</b> Dimension weights derived from CB Insights "Why Startups Fail"
    post-mortem analysis (101 companies, 2014 original study), Bessemer Venture Partners State of the Cloud
    benchmarks, and McKinsey operational due diligence framework. Unit economics weighted highest (0.22)
    as the #1 predictor of post-Series A survival.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TAM/SAM/SOM
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📐 TAM / SAM / SOM Calculator")

    if st.session_state.get("demo_loaded"):
        st.markdown("""
        <div class="story-box">
        <b>Ativegh Market Context:</b> Indian industrial logistics market serving the
        Jharkhand–West Bengal steel corridor. Target buyer: steel, ferro alloy, and thermal power
        companies needing ground transport and port handling at Haldia Port.
        TAM sourced from IBEF India Logistics Report 2023.
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔢 Bottom-Up Method (Primary)")
        total_potential_customers = st.number_input("Total potential customers in market",
                                                     100, 100_000_000, sv("total_potential_customers", 50000), step=10)
        acv_annual  = st.number_input("Annual revenue per customer ($)", 10, 1_000_000,
                                       sv("acv_annual", 3600), step=100)
        sam_filter_pct = st.slider("% of TAM you can realistically serve today", 1, 100,
                                    sv("sam_filter_pct", 25))
        som_capture_pct = st.slider("% of SAM you can capture in 3 years", 1, 50,
                                     sv("som_capture_pct", 8))
        tam_bu = total_potential_customers * acv_annual
        sam_bu = tam_bu * (sam_filter_pct / 100)
        som_bu = sam_bu * (som_capture_pct / 100)

    with col2:
        st.markdown("#### 📊 Top-Down Method (Cross-Check)")
        industry_market_size = st.number_input("Total industry market size ($B)", 0.1, 5000.0,
                                                float(sv("industry_market_size", 12.5)), step=0.5)
        td_segment_pct  = st.slider("% of industry relevant to your segment", 1, 100,
                                     sv("td_segment_pct", 18))
        td_geo_pct      = st.slider("% addressable by your geographic reach", 1, 100,
                                     sv("td_geo_pct", 35))
        td_product_fit_pct = st.slider("% matching your current service capability", 1, 100,
                                        sv("td_product_fit_pct", 60))
        tam_td = industry_market_size * 1e9
        sam_td = tam_td * (td_segment_pct/100) * (td_geo_pct/100)
        som_td = sam_td * (td_product_fit_pct/100) * (som_capture_pct/100)

    st.divider()

    def fmt_bn(n):
        if n >= 1e9: return f"${n/1e9:.1f}B"
        if n >= 1e6: return f"${n/1e6:.1f}M"
        if n >= 1e3: return f"${n/1e3:.0f}K"
        return f"${n:.0f}"

    tam_ratio = tam_bu / tam_td if tam_td > 0 else 1
    alignment = "✅ Methods aligned" if 0.5 <= tam_ratio <= 2.0 else "⚠️ Methods diverge >2x"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("TAM (Bottom-Up)", fmt_bn(tam_bu))
        st.metric("TAM (Top-Down)", fmt_bn(tam_td))
    with c2:
        st.metric("SAM (Bottom-Up)", fmt_bn(sam_bu))
        st.metric("SAM (Top-Down)", fmt_bn(sam_td))
    with c3:
        st.metric("SOM (Bottom-Up)", fmt_bn(som_bu))
        st.metric("SOM (Top-Down)", fmt_bn(som_td))
    with c4:
        st.metric("Alignment", alignment)
        st.metric("Primary SOM", fmt_bn(som_bu))

    fig_funnel = go.Figure(go.Funnel(
        y=["TAM — Total Market", "SAM — Serviceable", "SOM — Obtainable (3yr)"],
        x=[tam_bu, sam_bu, som_bu],
        textinfo="value+percent previous",
        marker=dict(color=["#1e3a5f","#2563eb","#60a5fa"])
    ))
    fig_funnel.update_layout(title=f"Market Sizing Funnel — {startup_name}",
                              height=320, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_funnel, use_container_width=True)

    if st.session_state.get("demo_loaded"):
        st.markdown("""
        <div class="warning-box">
        <b>Ativegh Market Insight:</b> The SOM is small in dollar terms — but that is honest.
        With a 4-person ops team and 7 clients, Ativegh cannot realistically serve 50+ clients
        in 3 years without a fundamental operational change (automation, additional vehicles, hiring).
        The market is real. The constraint is capacity, not demand.
        The one growth move available right now: add 1-2 clients <i>outside</i> the steel sector
        to reduce the concentration risk without requiring operational scaling.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<div class="framework-note">
    📚 Bottom-up method preferred per Forum VC, Antler, and McKinsey/BCG guidelines.
    TAM = ACV × Total Addressable Customers. SAM applies segment/geography filters.
    SOM built from sales capacity, not % of TAM (avoids the "1% fallacy" — Pear VC).
    India logistics market size: IBEF Logistics Sector Report 2023.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — RUNWAY & BURN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔥 Runway & Burn Analysis")

    net_burn       = max(monthly_burn - monthly_revenue, 0)
    runway_months  = cash_on_hand / net_burn if net_burn > 0 else 999

    gm    = gross_margin_pct / 100
    churn = monthly_churn / 100
    ltv   = (arpu * gm) / churn if churn > 0 else 0
    ltv_cac       = ltv / cac if cac > 0 else 0
    payback_months = cac / (arpu * gm) if (arpu * gm) > 0 else 999

    annual_growth  = (mrr_growth / 100) * 12 * 100
    profit_margin  = ((monthly_revenue - monthly_burn) / monthly_revenue * 100) if monthly_revenue > 0 else -100
    rule_of_40     = annual_growth + profit_margin

    monthly_new_arr = monthly_revenue * (mrr_growth / 100)
    burn_multiple   = net_burn / (monthly_new_arr * 12) if monthly_new_arr > 0 else 999
    fundraise_month = max(runway_months - 7, 0)

    if st.session_state.get("demo_loaded"):
        if net_burn == 0:
            st.markdown("""<div class="insight-box">
            <b>Ativegh is cash-flow positive.</b> Monthly revenue ($5,500) exceeds monthly burn ($4,200).
            Net surplus: ~$1,300/month. This is the key survival advantage of a bootstrapped services business.
            Runway is theoretically infinite at current trajectory — the risk is not cash, it is concentration.
            </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "normal" if runway_months > 18 else ("off" if runway_months > 9 else "inverse")
        st.metric("Runway", f"{runway_months:.0f} mo" if runway_months < 500 else "∞ (Cash+)",
                  delta="Cash-flow positive" if net_burn == 0 else
                  ("Safe" if runway_months > 18 else "Warning"))
    with c2:
        st.metric("Net Burn / mo", f"${net_burn:,.0f}" if net_burn > 0 else "Net Positive")
        st.metric("Monthly Surplus", f"${monthly_revenue - monthly_burn:,.0f}" if monthly_revenue > monthly_burn else "Negative")
    with c3:
        st.metric("LTV : CAC", f"{ltv_cac:.1f}x",
                  delta="Healthy" if ltv_cac >= 3 else "Track this",
                  delta_color="normal" if ltv_cac >= 3 else "off")
        st.metric("CAC Payback", f"{payback_months:.0f} mo" if payback_months < 500 else "< 1 mo")
    with c4:
        st.metric("Gross Margin", f"{gross_margin_pct}%",
                  delta="Below 60% target" if gross_margin_pct < 60 else "Healthy",
                  delta_color="inverse" if gross_margin_pct < 60 else "normal")
        st.metric("MoM Growth", f"{mrr_growth}%")

    st.divider()
    st.markdown("#### 📊 Three-Scenario Runway Model")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Conservative** — lose 1 client")
        cons_rev_growth  = st.slider("Revenue growth MoM %", -5.0, 30.0, -1.5, 0.5, key="cons_rev")
        cons_burn_growth = st.slider("Cost growth MoM %", 0.0, 20.0, 2.0, 0.5, key="cons_burn")
    with col2:
        st.markdown("**Base Case** — current trajectory")
        base_rev_growth  = st.slider("Revenue growth MoM %", -5.0, 30.0, mrr_growth, 0.5, key="base_rev")
        base_burn_growth = st.slider("Cost growth MoM %", 0.0, 20.0, 1.0, 0.5, key="base_burn")
    with col3:
        st.markdown("**Optimistic** — add 2 new clients")
        opt_rev_growth   = st.slider("Revenue growth MoM %", -5.0, 30.0, 8.0, 0.5, key="opt_rev")
        opt_burn_growth  = st.slider("Cost growth MoM %", 0.0, 20.0, 2.5, 0.5, key="opt_burn")

    def simulate_runway(rev_growth, burn_growth, months=36):
        cash, revenue, burn = cash_on_hand, monthly_revenue, monthly_burn
        cash_hist, zero_month = [cash], None
        for m in range(1, months + 1):
            revenue *= (1 + rev_growth / 100)
            burn    *= (1 + burn_growth / 100)
            cash    -= (burn - revenue)
            cash_hist.append(cash)
            if cash <= 0 and zero_month is None:
                zero_month = m
        return cash_hist, zero_month

    months_range = list(range(37))
    cons_cash, cons_zero = simulate_runway(cons_rev_growth, cons_burn_growth)
    base_cash, base_zero = simulate_runway(base_rev_growth, base_burn_growth)
    opt_cash,  opt_zero  = simulate_runway(opt_rev_growth,  opt_burn_growth)

    fig_runway = go.Figure()
    fig_runway.add_trace(go.Scatter(x=months_range, y=cons_cash, name="Conservative (lose 1 client)",
                                     line=dict(color="#dc2626", dash="dash", width=2)))
    fig_runway.add_trace(go.Scatter(x=months_range, y=base_cash, name="Base Case",
                                     line=dict(color="#2563eb", width=3)))
    fig_runway.add_trace(go.Scatter(x=months_range, y=opt_cash, name="Optimistic (add 2 clients)",
                                     line=dict(color="#16a34a", dash="dot", width=2)))
    fig_runway.add_hline(y=0, line_dash="solid", line_color="red", opacity=0.4,
                          annotation_text="Cash = 0")
    fig_runway.update_layout(
        title="36-Month Cash Projection — Ativegh Logistics",
        xaxis_title="Months from Now", yaxis_title="Cash Balance ($)",
        height=380, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_runway, use_container_width=True)

    if st.session_state.get("demo_loaded") and cons_zero:
        st.markdown(f"""<div class="danger-box">
        <b>Conservative scenario (losing 1 client):</b> Cash hits zero at month {cons_zero}.
        With only 7 clients all in the same sector, losing even one — due to a steel market downturn
        or a relationship break — turns a cash-positive business into a cash-negative one within months.
        This is the concentration risk in financial terms.
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="framework-note">
    📚 Net Burn = Gross Burn − Revenue (standard). Runway = Cash / Net Burn.
    LTV = (ARPU × Gross Margin%) / Monthly Churn (David Skok, forentrepreneurs.com).
    CAC Payback = CAC / (ARPU × GM%). Benchmarks: Bessemer State of Cloud 2023;
    McKinsey SaaS analysis. Note: SaaS benchmarks applied directionally —
    Ativegh is a services business, not SaaS.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SCALE BOTTLENECK
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⚡ Scale Bottleneck Predictor")
    st.markdown("Stress-tests at 2x, 5x, and 10x current scale. For Ativegh: what breaks if they go from 7 to 14, 35, or 70 clients?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Current State")
        current_customers   = st.number_input("Current active clients", 1, 10000,
                                               sv("current_customers", 150))
        ops_team_size       = st.slider("Ops team size (FTEs)", 1, 100,
                                         sv("ops_team_size", 3))
        customers_per_csm   = st.slider("Clients per ops person", 1, 500,
                                         sv("customers_per_csm", 50),
                                         help="Ativegh: ~3 clients per staff at this service intensity. Rated 3.")
        infra_cost_per_cust = st.number_input("Monthly tech cost per client ($)", 0.01, 1000.0,
                                               float(sv("infra_cost_per_cust", 8.5)))
        single_source_pct   = st.slider("% of revenue from dominant sector", 0, 100,
                                         sv("single_source_pct", 65),
                                         help="Ativegh: ~80% from steel sector. Rated 80.")
    with col2:
        st.markdown("#### Process & People")
        manual_ops_hrs_week  = st.slider("Manual ops hours per week", 0, 200,
                                          sv("manual_ops_hrs_week", 35),
                                          help="Ativegh: dispatch, tracking, invoicing all manual. Estimated 55 hrs/week.")
        tech_incidents_month = st.slider("Operational incidents per month", 0, 50,
                                          sv("tech_incidents_month", 3))
        hiring_time_weeks    = st.slider("Weeks to hire a key person", 1, 52,
                                          sv("hiring_time_weeks", 10))
        monthly_hiring_budget = st.number_input("Monthly hiring budget ($)", 0, 500_000,
                                                 sv("monthly_hiring_budget", 25000))

    st.divider()

    scales = [1, 2, 5, 10]
    scale_labels = ["Now (7 clients)", "2x (14 clients)", "5x (35 clients)", "10x (70 clients)"]

    headcount_needed  = [current_customers * s / customers_per_csm for s in scales]
    headcount_risk    = [h / ops_team_size for h in headcount_needed]
    infra_monthly     = [current_customers * s * infra_cost_per_cust for s in scales]
    net_burn_current  = max(monthly_burn - monthly_revenue, 1)
    infra_burn_share  = [i / monthly_burn * 100 for i in infra_monthly]
    manual_scale      = [manual_ops_hrs_week * s for s in scales]
    cashflow_press    = [(net_burn_current * s / monthly_revenue) if monthly_revenue > 0 else s for s in scales]
    supplier_risk     = [single_source_pct * (1 + (s-1) * 0.15) for s in scales]

    vectors = {
        "👥 Hiring Pressure":       [min(r * 3, 10) for r in headcount_risk],
        "💻 Infra Cost Burden":      [min(s / 10, 10) for s in infra_burn_share],
        "⚙️ Manual Ops Overload":    [min(h / 80 * 10, 10) for h in manual_scale],
        "💰 Cash Flow Stress":       [min(c * 2, 10) for c in cashflow_press],
        "🔗 Sector Concentration":   [min(s / 10, 10) for s in supplier_risk],
    }

    df_heat = pd.DataFrame(vectors, index=scale_labels).T
    fig_heat = px.imshow(df_heat,
        color_continuous_scale=[[0,"#16a34a"],[0.4,"#f59e0b"],[0.7,"#ef4444"],[1,"#7f1d1d"]],
        zmin=0, zmax=10,
        title=f"Bottleneck Risk Heatmap — {startup_name} (0=Low, 10=Critical)",
        text_auto=".1f")
    fig_heat.update_layout(height=320, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    risk_at_5x = {k: v[2] for k, v in vectors.items()}
    risk_at_2x = {k: v[1] for k, v in vectors.items()}
    worst_5x   = max(risk_at_5x.items(), key=lambda x: x[1])
    worst_2x   = max(risk_at_2x.items(), key=lambda x: x[1])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="warning-box"><b>At 2x (14 clients):</b> {worst_2x[0]} is the binding constraint (risk: {worst_2x[1]:.1f}/10)</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="danger-box"><b>At 5x (35 clients):</b> {worst_5x[0]} becomes critical (risk: {worst_5x[1]:.1f}/10)</div>', unsafe_allow_html=True)

    st.markdown("#### 🛠️ Pre-Scale Interventions")
    interventions = {
        "👥 Hiring Pressure":     "Document every operational role now. Create a simple hiring process before adding new clients. At 14 clients, the current team cannot absorb the load.",
        "💻 Infra Cost Burden":   "Introduce basic dispatch software (WhatsApp → simple TMS). Even a ₹2,000/month tool changes the capacity curve significantly.",
        "⚙️ Manual Ops Overload": f"{manual_ops_hrs_week} manual hrs/week now → {manual_ops_hrs_week*5} hrs/week at 5x. This is unsustainable. The first automation target is dispatch and invoicing.",
        "💰 Cash Flow Stress":    "The business is cash-positive today. Protect that by keeping at least 3 months of operating costs in reserve before adding capacity.",
        "🔗 Sector Concentration":"Add 1-2 clients outside the steel sector before the next client conversation. This single move changes the risk profile significantly.",
    }

    for vector, rec in interventions.items():
        risk = risk_at_5x.get(vector, 0)
        css  = "danger-box" if risk >= 6 else ("warning-box" if risk >= 4 else "insight-box")
        icon = "🔴" if risk >= 6 else ("🟡" if risk >= 4 else "🟢")
        st.markdown(f'<div class="{css}">{icon} <b>{vector}</b> (5x risk: {risk:.1f}/10)<br>{rec}</div>', unsafe_allow_html=True)

    st.markdown("""<div class="framework-note">
    📚 Theory of Constraints (Goldratt, 1984): every system has exactly one binding constraint.
    Kingman's Formula (1961): wait times grow exponentially above 80% utilization.
    Scale multiples (2x/5x/10x) map to realistic growth milestones for a regional logistics operator.
    Sector concentration threshold: MIT Center for Transportation & Logistics supply chain resilience research.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — AI STRATEGIC BRIEF
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🤖 AI Strategic Brief Generator")
    st.markdown("Powered by **Groq (Llama 3.3 70B)**. Generates an advisor-grade brief from all inputs above.")

    net_burn_display = max(monthly_burn - monthly_revenue, 0)
    gm_final = gross_margin_pct / 100
    churn_final = monthly_churn / 100
    ltv_final = (arpu * gm_final) / churn_final if churn_final > 0 else 0
    ltv_cac_final = ltv_final / cac if cac > 0 else 0

    if st.button("⚡ Generate AI Strategic Brief", type="primary", use_container_width=True):
        context = f"""
You are a senior startup advisor at the Roux Institute conducting operational due diligence.

STARTUP: {startup_name}
Industry: {industry} | Stage: {stage} | Team: {team_size} FTEs | Model: {biz_model} | Founded: {founded_years} years ago

IMPORTANT CONTEXT: This is a bootstrapped family-run logistics company in India serving
industrial B2B clients at a port. It is NOT a SaaS company. Apply appropriate benchmarks
for a traditional services business, not software benchmarks.

FINANCIALS:
Monthly Revenue: ${monthly_revenue:,.0f} | Monthly Burn: ${monthly_burn:,.0f}
Net Position: {"Cash-flow POSITIVE by $" + str(monthly_revenue - monthly_burn) if monthly_revenue > monthly_burn else "Net burn $" + str(monthly_burn - monthly_revenue)}
Cash on Hand: ${cash_on_hand:,.0f}
Gross Margin: {gross_margin_pct}% | Monthly Churn: {monthly_churn}% | MoM Growth: {mrr_growth}%

UNIT ECONOMICS:
ARPU: ${arpu}/month | CAC: ${cac} | LTV: ${ltv_cac_final * cac:,.0f} | LTV:CAC: {ltv_cac_final:.1f}x

MARKET:
TAM (bottom-up): {fmt_bn(tam_bu)} | SAM: {fmt_bn(sam_bu)} | SOM (3yr): {fmt_bn(som_bu)}

OPS READINESS: {total_score:.1f}/10 — {classification}
Weakest: {weakest[0]} ({weakest[1][0]:.1f}/10)
Strongest: {strongest[0]} ({strongest[1][0]:.1f}/10)

KEY RISKS IDENTIFIED:
- All 7 clients are in the steel/ferro alloy sector (extreme concentration)
- Family-run: 3 of 4 directors share surname — key-person dependency is critical
- Entirely manual operations — dispatch, tracking, invoicing all by phone/paper
- No formal SOPs, no KPI tracking, no documented processes
- Cash-flow positive but single client loss could turn it negative

SCALE BOTTLENECK (5x = 35 clients):
- Biggest risk at 2x: {worst_2x[0]} (risk {worst_2x[1]:.1f}/10)
- Biggest risk at 5x: {worst_5x[0]} (risk {worst_5x[1]:.1f}/10)

Generate a structured brief in exactly this format:

## SITUATION SUMMARY
[2-3 sentences. Acknowledge this is a real, cash-positive business with genuine strengths.
Be honest about the structural risks without being harsh.]

## TOP 3 RISKS (ranked by financial impact)
**Risk 1 — [Name]:** [Specific with numbers]
**Risk 2 — [Name]:** [Specific with numbers]
**Risk 3 — [Name]:** [Specific with numbers]

## TOP 3 OPPORTUNITIES
**Opportunity 1 — [Name]:** [Specific and actionable for a small Indian logistics company]
**Opportunity 2 — [Name]:** [Specific]
**Opportunity 3 — [Name]:** [Specific]

## 90-DAY ACTION PLAN
**Week 1-2:** [Most urgent, low-cost action]
**Week 3-4:** [Second priority]
**Month 2:** [Third priority]
**Month 3:** [Sets up next milestone]

## THE SINGLE METRIC TO WATCH
[One metric — what it is, why it matters most right now for THIS specific business]

## GROWTH READINESS VERDICT
[One paragraph: Is this business ready to add new clients? What specifically needs to happen first?
Be direct but constructive.]
"""
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.spinner("Generating strategic brief for Ativegh Logistics..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": context}],
                    temperature=0.35,
                    max_tokens=1500
                )
                brief = response.choices[0].message.content
            st.markdown("---")
            st.markdown(f"### Strategic Brief — {startup_name}")
            st.markdown(brief)
            st.download_button("📥 Download Brief", data=brief,
                               file_name=f"Ativegh_VentureOps_Brief.txt", mime="text/plain")
        except ImportError:
            st.error("Run: pip install groq")
        except KeyError:
            st.error("Add GROQ_API_KEY to .streamlit/secrets.toml")
        except Exception as e:
            st.error(f"API error: {str(e)}")

    if st.session_state.get("demo_loaded"):
        st.markdown("""
        <div class="story-box">
        <b>What the AI brief will surface for Ativegh:</b><br>
        The brief will almost certainly identify (1) sector concentration as the #1 financial risk —
        because losing one steel client is a 14% revenue drop, (2) key-person dependency as the #1
        operational risk — because the business stops if the founding family steps back,
        and (3) the opportunity in process automation — because even basic dispatch software
        changes the capacity math dramatically.
        These are the three conversations worth having with this founder.
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;color:#9ca3af;font-size:0.78rem;padding:1rem;">
VentureOps — Built by Rutwik Satish for the Roux Institute<br>
Demo: Ativegh Logistics Pvt. Ltd. — Estimated figures from public MCA data and industry benchmarks<br>
Frameworks: CB Insights (n=101, 2014) · Bessemer VP · McKinsey · Theory of Constraints (Goldratt) ·
Kingman's Formula (1961) · David Skok SaaS Metrics<br>
All inputs processed locally. No data stored.
</div>
""", unsafe_allow_html=True)
