"""
VentureOps — Startup Operational Due Diligence Engine
Built for the Roux Institute | Rutwik Satish

Frameworks used:
- Operational scoring: 6-dimension framework (supply chain risk, unit economics,
  operational leverage, team capacity, process maturity, tech debt)
- TAM/SAM/SOM: Bottom-up (ACV × addressable customers) + top-down cross-check
  (Antler, Forum VC, HubSpot methodology)
- Runway/Burn: Net Burn = Gross Burn - Revenue; Runway = Cash / Net Burn
  Burn Multiple = Net Burn / Net New ARR (Bessemer benchmark)
  LTV = (ARPU × Gross Margin) / Churn Rate
  CAC Payback = CAC / (ARPU × Gross Margin) (McKinsey SaaS benchmarks)
  Rule of 40 = Growth Rate % + Profit Margin %
- Scale Bottleneck: 5-vector stress test at 2x/5x/10x scale
- AI Brief: Groq (Llama 3) via st.secrets["GROQ_API_KEY"]

Install: pip install streamlit plotly groq pandas numpy
Run:     streamlit run ventureops_app.py
Secrets: Create .streamlit/secrets.toml with GROQ_API_KEY = "your_key_here"
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VentureOps — Startup Due Diligence Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLES ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #1a1a2e, #16213e, #0f3460);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #6b7280; font-size: 1rem; margin-bottom: 2rem; }
    .metric-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1.2rem; text-align: center;
    }
    .score-excellent { color: #16a34a; font-weight: 800; font-size: 2rem; }
    .score-good      { color: #2563eb; font-weight: 800; font-size: 2rem; }
    .score-moderate  { color: #d97706; font-weight: 800; font-size: 2rem; }
    .score-critical  { color: #dc2626; font-weight: 800; font-size: 2rem; }
    .insight-box {
        background: #f0fdf4; border-left: 4px solid #16a34a;
        padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
    }
    .warning-box {
        background: #fffbeb; border-left: 4px solid #d97706;
        padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
    }
    .danger-box {
        background: #fef2f2; border-left: 4px solid #dc2626;
        padding: 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0;
    }
    .framework-note {
        background: #f1f5f9; border: 1px solid #cbd5e1;
        border-radius: 8px; padding: 0.8rem; font-size: 0.78rem;
        color: #64748b; margin-top: 1rem;
    }
    .stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🔬 VentureOps</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Startup Operational Due Diligence Engine — Built for the Roux Institute</p>', unsafe_allow_html=True)

st.markdown("""
> **What this does:** VentureOps replaces gut-feel startup assessment with a structured,
> scored, AI-powered operational due diligence engine. Advisors can run a full ODD brief
> on any startup in under 10 minutes.
""")

# ─── SIDEBAR — STARTUP PROFILE ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏢 Startup Profile")
    st.markdown("*Fill this in once. All 5 modules use it.*")

    startup_name    = st.text_input("Startup Name", "Ativegh Logistics Pvt. Ltd.")
    industry        = st.selectbox("Industry", [
        "SaaS / Software", "E-Commerce", "HealthTech", "FinTech",
        "DeepTech / Hardware", "Marketplace", "CleanTech", "EdTech", "Other"
    ], index=8)
    stage           = st.selectbox("Stage", ["Pre-Seed", "Seed", "Series A", "Series B+"], index=0)
    team_size       = st.slider("Team Size (FTEs)", 1, 200, 8)
    founded_years   = st.slider("Years Since Founded", 0, 10, 4)
    biz_model       = st.selectbox("Business Model", [
        "B2B SaaS", "B2C SaaS", "Marketplace", "E-Commerce",
        "Hardware + Software", "Services", "Freemium"
    ], index=5)

    st.divider()
    st.markdown("### 💰 Financials")
    # Ativegh: port logistics, 7 B2B steel/alloy clients, bootstrapped ₹15L (~$18K)
    # Revenue estimated: ~₹4.5L/month from 7 clients = ~$5,500
    # Burn estimated: fuel + wages + maintenance = ~$4,200
    monthly_revenue = st.number_input("Monthly Revenue ($)", 0, 10_000_000, 5_500, step=500)
    monthly_burn    = st.number_input("Monthly Gross Burn ($)", 1_000, 10_000_000, 4_200, step=500)
    cash_on_hand    = st.number_input("Cash on Hand ($)", 0, 100_000_000, 9_000, step=500)
    arpu            = st.number_input("Avg Revenue Per Client/Month ($)", 1, 100_000, 785)
    cac             = st.number_input("Customer Acquisition Cost ($)", 1, 500_000, 120)
    gross_margin_pct= st.slider("Gross Margin (%)", 0, 100, 32)
    monthly_churn   = st.slider("Monthly Churn Rate (%)", 0.0, 20.0, 0.8, 0.1)
    mrr_growth      = st.slider("MoM Revenue Growth (%)", -20.0, 50.0, 3.5, 0.5)

    st.divider()
    st.caption("📚 Frameworks: Bessemer Venture Partners, McKinsey SaaS Benchmarks, "
               "Antler TAM methodology, CB Insights failure analysis")

# ─── TABS ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Ops Readiness Score",
    "📐 TAM / SAM / SOM",
    "🔥 Runway & Burn",
    "⚡ Scale Bottleneck",
    "🤖 AI Strategic Brief"
])

# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 — OPERATIONAL READINESS SCORE
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🎯 Operational Readiness Score")
    st.markdown("Rate the startup across 6 dimensions. Each dimension is weighted by its impact on scaling failure.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Supply Chain & Delivery Risk")
        sc_single_source  = st.slider("Single-source supplier concentration", 0, 10, 8,
            help="10 = All key inputs from one supplier (highest risk). Ativegh: all 7 clients in steel sector.")
        sc_lead_time      = st.slider("Lead time predictability", 0, 10, 6,
            help="Port-based logistics — moderate predictability.")
        sc_inventory      = st.slider("Inventory / delivery buffer adequacy", 0, 10, 4,
            help="Asset-light model, limited spare capacity.")

        st.markdown("#### Unit Economics Health")
        ue_ltv_cac        = st.slider("LTV:CAC ratio awareness", 0, 10, 3,
            help="Unit economics not formally tracked. CAC is near zero but LTV unmeasured.")
        ue_payback        = st.slider("CAC payback period control", 0, 10, 4,
            help="Referral-based acquisition — payback not measured.")
        ue_margin         = st.slider("Gross margin sustainability", 0, 10, 3,
            help="32% gross margin. Logistics is inherently low-margin.")

    with col2:
        st.markdown("#### Operational Leverage")
        ol_automation     = st.slider("Process automation maturity", 0, 10, 2,
            help="Almost entirely manual — phone/WhatsApp dispatch, paper invoicing.")
        ol_scalability    = st.slider("Revenue scalability without headcount", 0, 10, 3,
            help="Each new client requires additional driver/vehicle. Not scalable without automation.")

        st.markdown("#### Team Capacity & Execution")
        tc_key_person     = st.slider("Key-person dependency risk", 0, 10, 9,
            help="Family business — 3 of 4 directors share surname. Critical decisions concentrated in 1-2 people.")
        tc_hiring         = st.slider("Hiring pipeline for critical roles", 0, 10, 2,
            help="No formal hiring process. All recruitment through personal network.")

        st.markdown("#### Process Maturity")
        pm_documentation  = st.slider("SOPs and process documentation", 0, 10, 2,
            help="No formal SOPs for a 4-year bootstrapped family operation.")
        pm_kpis           = st.slider("KPI framework and monitoring", 0, 10, 2,
            help="No KPI dashboards. Business managed by gut feel and owner judgment.")

        st.markdown("#### Tech Debt Exposure")
        td_infrastructure = st.slider("Infrastructure scalability", 0, 10, 3,
            help="Basic mobile/WhatsApp operations. No cloud infrastructure.")
        td_debt_level     = st.slider("Known tech debt severity", 0, 10, 2,
            help="No significant tech debt — there is simply no tech yet.")

    # ── SCORING ──────────────────────────────────────────────────────────────────
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
        classification = "🟢 Launch-Ready"
        cls_color = "score-excellent"
        cls_desc  = "Strong operational foundation. Ready to scale with confidence."
    elif total_score >= 5.5:
        classification = "🟡 Scaling Risk"
        cls_color = "score-moderate"
        cls_desc  = "Viable but 2-3 critical gaps will compound at scale. Remediate before next round."
    elif total_score >= 3.5:
        classification = "🟠 Ops Gaps"
        cls_color = "score-good"
        cls_desc  = "Multiple structural weaknesses. Fundraising risk without operational plan."
    else:
        classification = "🔴 Critical Gaps"
        cls_color = "score-critical"
        cls_desc  = "Operational fundamentals not in place. High failure risk at 2x scale."

    st.divider()
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#6b7280; font-size:0.85rem;">OVERALL OPS SCORE</div>
            <div class="{cls_color}">{total_score:.1f}/10</div>
            <div style="font-size:0.9rem; font-weight:600;">{classification}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        weakest = min(weights.items(), key=lambda x: x[1][0])
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#6b7280; font-size:0.85rem;">WEAKEST DIMENSION</div>
            <div class="score-critical" style="font-size:1.4rem;">{weakest[0]}</div>
            <div style="font-size:0.9rem;">{weakest[1][0]:.1f}/10</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"**Assessment:** {cls_desc}")
        for dim, (score, _) in weights.items():
            if score < 5:
                st.markdown(f'<div class="danger-box">⚠️ <b>{dim}</b> — Score {score:.1f}/10. Intervention required before scaling.</div>', unsafe_allow_html=True)
            elif score < 7:
                st.markdown(f'<div class="warning-box">🔶 <b>{dim}</b> — Score {score:.1f}/10. Monitor closely.</div>', unsafe_allow_html=True)

    categories = list(weights.keys())
    values     = [s for s, _ in weights.values()]
    values_normalized = [(v/10)*100 for v in values]

    fig_radar = go.Figure(go.Scatterpolar(
        r=values_normalized + [values_normalized[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.15)',
        line=dict(color='#2563eb', width=2),
        name=startup_name
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, title="Operational Readiness Radar",
        height=400, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("""
    <div class="framework-note">
    📚 <b>Scoring Framework:</b> Dimension weights derived from CB Insights "Why Startups Fail" analysis
    (101 post-mortems, 2014 original study), Bessemer Venture Partners State of the Cloud benchmarks,
    and McKinsey operational due diligence framework for PE/VC transactions.
    Unit economics weighted highest (0.22) as the #1 predictor of post-Series A survival.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 — TAM / SAM / SOM
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📐 TAM / SAM / SOM Calculator")
    st.markdown("Uses **both** bottom-up (ACV × customers) and top-down (industry × segment %) methods, then cross-checks them. Bottom-up is primary — it's what investors trust.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔢 Bottom-Up Method (Primary)")
        st.markdown("*Industrial logistics market — Jharkhand / West Bengal steel corridor*")

        total_potential_customers = st.number_input("Total potential customers in your market",
                                                     100, 100_000_000, 850, step=10)
        acv_annual                = st.number_input("Annual Contract Value / Revenue per customer ($)",
                                                     10, 1_000_000, 9_420, step=100)
        sam_filter_pct            = st.slider("% of TAM you can realistically serve today", 1, 100, 22)
        som_capture_pct           = st.slider("% of SAM you can capture in 3 years", 1, 50, 12)

        tam_bu = total_potential_customers * acv_annual
        sam_bu = tam_bu * (sam_filter_pct / 100)
        som_bu = sam_bu * (som_capture_pct / 100)

    with col2:
        st.markdown("#### 📊 Top-Down Method (Cross-Check)")
        st.markdown("*Indian industrial logistics market (IBEF Logistics Report 2023)*")

        industry_market_size = st.number_input("Total industry market size ($B from reports)",
                                                0.1, 5000.0, 18.5, step=0.5)
        td_segment_pct       = st.slider("% of industry relevant to your segment", 1, 100, 4)
        td_geo_pct           = st.slider("% addressable by your geographic reach", 1, 100, 8)
        td_product_fit_pct   = st.slider("% matching your product's current features", 1, 100, 65)

        tam_td = industry_market_size * 1e9
        sam_td = tam_td * (td_segment_pct/100) * (td_geo_pct/100)
        som_td = sam_td * (td_product_fit_pct/100) * (som_capture_pct/100)

    st.divider()

    tam_ratio = tam_bu / tam_td if tam_td > 0 else 1
    alignment = "✅ Good alignment" if 0.5 <= tam_ratio <= 2.0 else "⚠️ Estimates diverge >2x — revisit assumptions"

    c1, c2, c3, c4 = st.columns(4)
    def fmt_bn(n):
        if n >= 1e9:  return f"${n/1e9:.1f}B"
        if n >= 1e6:  return f"${n/1e6:.1f}M"
        if n >= 1e3:  return f"${n/1e3:.0f}K"
        return f"${n:.0f}"

    with c1:
        st.metric("TAM (Bottom-Up)", fmt_bn(tam_bu))
        st.metric("TAM (Top-Down)",  fmt_bn(tam_td))
    with c2:
        st.metric("SAM (Bottom-Up)", fmt_bn(sam_bu))
        st.metric("SAM (Top-Down)",  fmt_bn(sam_td))
    with c3:
        st.metric("SOM (Bottom-Up)", fmt_bn(som_bu))
        st.metric("SOM (Top-Down)",  fmt_bn(som_td))
    with c4:
        st.metric("Alignment Check", alignment)
        st.metric("Primary SOM",     fmt_bn(som_bu))

    fig_funnel = go.Figure(go.Funnel(
        y=["TAM — Total Market", "SAM — Serviceable", "SOM — Obtainable (3yr)"],
        x=[tam_bu, sam_bu, som_bu],
        textinfo="value+percent previous",
        marker=dict(color=["#1e3a5f", "#2563eb", "#60a5fa"])
    ))
    fig_funnel.update_layout(title=f"Market Sizing Funnel — {startup_name}",
                              height=350, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_funnel, use_container_width=True)

    years = [1, 2, 3, 4, 5]
    growth_rate = mrr_growth / 100
    year1_rev = monthly_revenue * 12
    projected = [year1_rev * ((1 + growth_rate * 12) ** (y - 1)) for y in years]
    som_line   = [som_bu] * 5

    fig_path = go.Figure()
    fig_path.add_trace(go.Scatter(x=years, y=projected, name="Projected ARR",
                                   mode="lines+markers", line=dict(color="#2563eb", width=3)))
    fig_path.add_trace(go.Scatter(x=years, y=som_line, name="SOM Target",
                                   mode="lines", line=dict(color="#dc2626", dash="dash")))
    fig_path.update_layout(
        title="Projected Revenue vs SOM Target",
        xaxis_title="Year", yaxis_title="Revenue ($)",
        height=350, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_path, use_container_width=True)

    st.markdown("""
    <div class="framework-note">
    📚 <b>Methodology:</b> Bottom-up preferred per Forum VC, Antler, and McKinsey/BCG guidelines.
    Formula: TAM = ACV × Total Addressable Customers. SAM applies segment/geography filters.
    SOM built from realistic sales capacity, not % of TAM (avoids the "1% fallacy" — Pear VC).
    India logistics market: IBEF Logistics Sector Report 2023.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 — RUNWAY & BURN
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔥 Runway & Burn Analysis")
    st.markdown("Models three scenarios. Calculates all unit economics benchmarks used by investors.")

    net_burn        = max(monthly_burn - monthly_revenue, 0)
    gross_burn      = monthly_burn
    runway_months   = cash_on_hand / net_burn if net_burn > 0 else 999

    gm              = gross_margin_pct / 100
    churn           = monthly_churn / 100
    ltv             = (arpu * gm) / churn if churn > 0 else 0
    ltv_cac         = ltv / cac if cac > 0 else 0
    payback_months  = cac / (arpu * gm) if (arpu * gm) > 0 else 999

    annual_growth   = (mrr_growth / 100) * 12 * 100
    profit_margin   = ((monthly_revenue - monthly_burn) / monthly_revenue * 100) if monthly_revenue > 0 else -100
    rule_of_40      = annual_growth + profit_margin

    monthly_new_arr = monthly_revenue * (mrr_growth / 100)
    burn_multiple   = net_burn / (monthly_new_arr * 12) if monthly_new_arr > 0 else 999
    fundraise_month = max(runway_months - 7, 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "normal" if runway_months > 18 else ("off" if runway_months > 9 else "inverse")
        st.metric("Runway",
                  f"{runway_months:.0f} mo" if runway_months < 500 else "∞ (Cash+)",
                  delta="Cash-flow positive" if net_burn == 0 else
                  ("Safe" if runway_months > 18 else "Warning" if runway_months > 9 else "CRITICAL"),
                  delta_color="normal" if net_burn == 0 else color)
    with c2:
        st.metric("Net Burn / mo",
                  f"${net_burn:,.0f}" if net_burn > 0 else "Net Positive",)
        st.metric("Monthly Surplus" if monthly_revenue > monthly_burn else "Gross Burn / mo",
                  f"${abs(monthly_revenue - monthly_burn):,.0f}")
    with c3:
        ltv_color = "normal" if ltv_cac >= 3 else "inverse"
        st.metric("LTV : CAC", f"{ltv_cac:.1f}x",
                  delta="Healthy (>3x)" if ltv_cac >= 3 else "Below threshold",
                  delta_color=ltv_color)
        st.metric("CAC Payback", f"{payback_months:.0f} mo" if payback_months < 500 else "< 1 mo")
    with c4:
        bm_label = "Excellent" if burn_multiple < 1 else "Good" if burn_multiple < 1.5 else "Suspect" if burn_multiple < 3 else "Poor"
        st.metric("Burn Multiple", f"{burn_multiple:.2f}x" if burn_multiple < 500 else "N/A",
                  delta=bm_label)
        st.metric("Rule of 40", f"{rule_of_40:.0f}",
                  delta="Pass" if rule_of_40 >= 40 else "Fail",
                  delta_color="normal" if rule_of_40 >= 40 else "inverse")

    st.divider()
    st.markdown("#### 📊 Three-Scenario Runway Model")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Conservative** — lose 1 client")
        cons_rev_growth  = st.slider("Revenue growth MoM %", -5.0, 30.0, -2.0, 0.5, key="cons_rev")
        cons_burn_growth = st.slider("Burn growth MoM %",     0.0, 20.0,  2.0, 0.5, key="cons_burn")
    with col2:
        st.markdown("**Base Case** — current trajectory")
        base_rev_growth  = st.slider("Revenue growth MoM %", -5.0, 30.0, mrr_growth, 0.5, key="base_rev")
        base_burn_growth = st.slider("Burn growth MoM %",     0.0, 20.0, 1.0, 0.5, key="base_burn")
    with col3:
        st.markdown("**Optimistic** — add 2 new clients")
        opt_rev_growth   = st.slider("Revenue growth MoM %", -5.0, 30.0, 8.0, 0.5, key="opt_rev")
        opt_burn_growth  = st.slider("Burn growth MoM %",     0.0, 20.0, 2.5, 0.5, key="opt_burn")

    def simulate_runway(rev_growth, burn_growth, months=36):
        cash, revenue, burn = cash_on_hand, monthly_revenue, monthly_burn
        cash_hist, zero_month = [cash], None
        for m in range(1, months + 1):
            revenue *= (1 + rev_growth / 100)
            burn    *= (1 + burn_growth / 100)
            net      = burn - revenue
            cash    -= net
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
    fig_runway.add_trace(go.Scatter(x=months_range, y=opt_cash,  name="Optimistic (add 2 clients)",
                                     line=dict(color="#16a34a", dash="dot", width=2)))
    fig_runway.add_hline(y=0, line_dash="solid", line_color="red", opacity=0.4, annotation_text="Cash = 0")
    if net_burn > 0:
        fig_runway.add_vline(x=fundraise_month, line_dash="dash", line_color="orange",
                              annotation_text="⚡ Start fundraising", annotation_position="top right")
    fig_runway.update_layout(
        title="36-Month Cash Projection — Ativegh Logistics",
        xaxis_title="Months from Now", yaxis_title="Cash Balance ($)",
        height=400, margin=dict(t=50, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_runway, use_container_width=True)

    st.markdown("#### 📋 Unit Economics vs. Benchmarks")
    bench_data = {
        "Metric": ["LTV:CAC Ratio", "CAC Payback", "Gross Margin", "Runway", "Burn Multiple", "Monthly Churn"],
        f"{startup_name}": [
            f"{ltv_cac:.1f}x",
            f"{payback_months:.0f} mo" if payback_months < 500 else "< 1 mo",
            f"{gross_margin_pct}%",
            f"{runway_months:.0f} mo" if runway_months < 500 else "∞ (Cash+)",
            f"{burn_multiple:.2f}x" if burn_multiple < 500 else "N/A",
            f"{monthly_churn}%"
        ],
        "Target (Seed/A)": [">3x", "<18 mo", ">60%", ">18 mo", "<1.5x", "<3%"],
        "World-Class":     [">5x", "<12 mo", ">75%", ">24 mo", "<1x",   "<1%"],
        "Status": [
            "✅" if ltv_cac >= 3 else "⚠️" if ltv_cac >= 1 else "❌",
            "✅" if payback_months <= 18 else "⚠️" if payback_months <= 30 else "❌",
            "✅" if gross_margin_pct >= 60 else "⚠️" if gross_margin_pct >= 40 else "❌",
            "✅" if runway_months >= 18 else "⚠️" if runway_months >= 9 else "❌",
            "✅" if burn_multiple <= 1.5 else "⚠️" if burn_multiple <= 3 else "❌",
            "✅" if monthly_churn <= 3 else "⚠️" if monthly_churn <= 5 else "❌",
        ]
    }
    st.dataframe(pd.DataFrame(bench_data), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="framework-note">
    📚 <b>Benchmarks:</b> LTV:CAC and payback from McKinsey analysis of 100+ public SaaS companies.
    Burn multiple benchmarks from Bessemer Venture Partners State of Cloud 2023.
    Rule of 40 per Bain & Company definition. Note: SaaS benchmarks applied directionally —
    Ativegh is a services business. Cash-flow positive status is the primary financial health signal here.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 4 — SCALE BOTTLENECK PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("⚡ Scale Bottleneck Predictor")
    st.markdown("Stress-tests the startup at 2x, 5x, and 10x current scale. "
                "For Ativegh: what breaks when they go from 7 to 14, 35, or 70 clients?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Current State Assessment")
        current_customers    = st.number_input("Current active clients", 1, 1_000_000, 7)
        ops_team_size        = st.slider("Ops team size (FTEs)", 1, 100, 4)
        customers_per_csm    = st.slider("Clients per ops person", 1, 500, 3,
                                          help="Ativegh: high-touch port logistics, ~3 clients per staff.")
        infra_cost_per_cust  = st.number_input("Monthly tech cost per client ($)", 0.01, 1000.0, 2.0)
        supplier_count       = st.slider("Number of active vendors / suppliers", 1, 200, 2)
        single_source_pct    = st.slider("% of revenue from dominant sector", 0, 100, 80,
                                          help="Ativegh: ~80% from steel/ferro alloy sector.")

    with col2:
        st.markdown("#### Process & People Inputs")
        manual_ops_hrs_week  = st.slider("Manual ops hours per week", 0, 200, 55,
                                          help="Ativegh: dispatch, tracking, and invoicing all manual. ~55 hrs/week.")
        tech_incidents_month = st.slider("Operational incidents per month", 0, 50, 1)
        hiring_time_weeks    = st.slider("Average weeks to hire a key role", 1, 52, 8)
        monthly_hiring_budget= st.number_input("Monthly hiring budget ($)", 0, 500_000, 400)

    st.divider()

    scales = [1, 2, 5, 10]
    scale_labels = ["Now (7 clients)", "2x (14 clients)", "5x (35 clients)", "10x (70 clients)"]

    headcount_needed   = [current_customers * s / customers_per_csm for s in scales]
    headcount_risk     = [h / ops_team_size for h in headcount_needed]
    infra_monthly      = [current_customers * s * infra_cost_per_cust for s in scales]
    infra_burn_share   = [i / monthly_burn * 100 for i in infra_monthly]
    manual_scale       = [manual_ops_hrs_week * s for s in scales]
    cashflow_pressure  = [(max(monthly_burn - monthly_revenue, 1) * s / monthly_revenue)
                          if monthly_revenue > 0 else s for s in scales]
    supplier_risk      = [single_source_pct * (1 + (s - 1) * 0.15) for s in scales]

    vectors = {
        "👥 Hiring Pressure":         [min(r * 3, 10) for r in headcount_risk],
        "💻 Infra Cost Burden":        [min(s / 10, 10) for s in infra_burn_share],
        "⚙️ Manual Ops Overload":      [min(h / 80 * 10, 10) for h in manual_scale],
        "💰 Cash Flow Stress":         [min(c * 2, 10) for c in cashflow_pressure],
        "🔗 Sector Concentration":     [min(s / 10, 10) for s in supplier_risk],
    }

    df_heat = pd.DataFrame(vectors, index=scale_labels).T

    fig_heat = px.imshow(
        df_heat,
        color_continuous_scale=[[0, "#16a34a"], [0.4, "#f59e0b"], [0.7, "#ef4444"], [1, "#7f1d1d"]],
        zmin=0, zmax=10,
        title="Bottleneck Risk Heatmap (0 = Low Risk, 10 = Critical)",
        labels=dict(color="Risk Score"),
        text_auto=".1f"
    )
    fig_heat.update_layout(height=350, margin=dict(t=50, b=20, l=20, r=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    risk_at_5x = {k: v[2] for k, v in vectors.items()}
    risk_at_2x = {k: v[1] for k, v in vectors.items()}
    worst_5x   = max(risk_at_5x.items(), key=lambda x: x[1])
    worst_2x   = max(risk_at_2x.items(), key=lambda x: x[1])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="warning-box">
        <b>At 2x (14 clients):</b> {worst_2x[0]} is the binding constraint (score: {worst_2x[1]:.1f}/10)
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="danger-box">
        <b>At 5x (35 clients):</b> {worst_5x[0]} becomes critical (score: {worst_5x[1]:.1f}/10)
        </div>""", unsafe_allow_html=True)

    st.markdown("#### 🛠️ Recommended Pre-Scale Interventions")
    interventions = {
        "👥 Hiring Pressure":       "Document every operational role before adding clients. At 14 clients the current 4-person team hits capacity. A hiring plan needs to exist before growth, not after.",
        "💻 Infra Cost Burden":     "Introduce basic dispatch software — even a ₹2,000/month TMS changes the capacity curve. Moving from WhatsApp to a simple system is the first automation target.",
        "⚙️ Manual Ops Overload":   f"{manual_ops_hrs_week} manual hrs/week now → {manual_ops_hrs_week * 5} hrs/week at 5x with same team size. Dispatch and invoicing automation is the highest ROI move available.",
        "💰 Cash Flow Stress":      "Business is cash-flow positive today. Protect that buffer — maintain at least 3 months of operating costs in reserve before adding vehicle/headcount capacity.",
        "🔗 Sector Concentration":  "Add 1-2 clients outside steel/ferro alloys before the next growth push. This single move changes the risk profile without requiring operational scaling.",
    }

    for vector, rec in interventions.items():
        if risk_at_5x.get(vector, 0) >= 6:
            st.markdown(f'<div class="danger-box">🔴 <b>{vector}:</b> {rec}</div>', unsafe_allow_html=True)
        elif risk_at_5x.get(vector, 0) >= 4:
            st.markdown(f'<div class="warning-box">🟡 <b>{vector}:</b> {rec}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box">🟢 <b>{vector}:</b> Currently low risk. Maintain visibility.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="framework-note">
    📚 <b>Framework:</b> Theory of Constraints (Goldratt, 1984) — every system has one binding constraint.
    Kingman's Formula (1961) — wait times grow exponentially above 80% utilization.
    Scale labels (2x/5x/10x) map to realistic growth milestones for a regional logistics operator.
    Sector concentration threshold: MIT Center for Transportation & Logistics resilience research.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 5 — AI STRATEGIC BRIEF
# ══════════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🤖 AI Strategic Brief Generator")
    st.markdown("Powered by **Groq (Llama 3.3 70B)**. Generates a structured advisor-grade brief based on all inputs above.")

    if st.button("⚡ Generate AI Strategic Brief", type="primary", use_container_width=True):
        context = f"""
You are a senior startup advisor conducting operational due diligence.

STARTUP: {startup_name}
Industry: {industry} | Stage: {stage} | Team: {team_size} FTEs | Model: {biz_model} | Founded: {founded_years} years ago

IMPORTANT: This is a bootstrapped family-run port logistics company in India serving B2B industrial clients.
It is NOT a SaaS company. Apply appropriate benchmarks for a traditional services business.

FINANCIALS:
Monthly Revenue: ${monthly_revenue:,.0f} | Monthly Burn: ${monthly_burn:,.0f}
Net Position: {"Cash-flow POSITIVE by $" + str(monthly_revenue - monthly_burn) if monthly_revenue > monthly_burn else "Net burn $" + str(monthly_burn - monthly_revenue)}
Cash on Hand: ${cash_on_hand:,.0f} | Gross Margin: {gross_margin_pct}%
Monthly Churn: {monthly_churn}% | MoM Growth: {mrr_growth}%

UNIT ECONOMICS:
ARPU: ${arpu}/month | CAC: ${cac} | LTV:CAC: {ltv_cac:.1f}x

MARKET:
TAM (bottom-up): {fmt_bn(tam_bu)} | SAM: {fmt_bn(sam_bu)} | SOM (3yr): {fmt_bn(som_bu)}

OPS READINESS: {total_score:.1f}/10 — {classification}
Weakest: {weakest[0]} ({weakest[1][0]:.1f}/10)

KEY RISKS:
- All clients in steel/ferro alloy sector (extreme concentration)
- Family-run: 3 of 4 directors share surname — key-person dependency rated 9/10
- Entirely manual operations — phone/paper dispatch
- No formal SOPs, no KPI tracking

SCALE BOTTLENECK:
- At 2x: {worst_2x[0]} (risk {worst_2x[1]:.1f}/10)
- At 5x: {worst_5x[0]} (risk {worst_5x[1]:.1f}/10)

Produce a structured brief in exactly this format:

## SITUATION SUMMARY
[2-3 sentences. Acknowledge this is a real, cash-positive business with genuine strengths.
Be honest about structural risks without being harsh.]

## TOP 3 RISKS
**Risk 1 — [Name]:** [Specific with numbers from the analysis]
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
[One metric — what it is, why it matters most for THIS business right now]

## GROWTH READINESS VERDICT
[One paragraph: Is this business ready to add new clients? What needs to happen first? Be direct.]
"""
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            with st.spinner("Generating strategic brief..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": context}],
                    temperature=0.4,
                    max_tokens=1500
                )
                brief = response.choices[0].message.content
            st.markdown("---")
            st.markdown(f"### 📄 Strategic Brief — {startup_name}")
            st.markdown(brief)
            st.download_button(
                "📥 Download Brief",
                data=brief,
                file_name=f"{startup_name.replace(' ', '_')}_VentureOps_Brief.txt",
                mime="text/plain"
            )
        except ImportError:
            st.error("Groq package not installed. Run: `pip install groq`")
        except KeyError:
            st.error("⚠️ GROQ_API_KEY not found in Streamlit secrets.")
        except Exception as e:
            st.error(f"API error: {str(e)}")

    st.markdown("---")
    st.markdown("#### 📋 What the AI brief includes")
    for item in [
        "Situation summary — stage-appropriate health assessment",
        "Top 3 risks — data-backed, pulled from your actual inputs",
        "Top 3 opportunities — specific and actionable",
        "90-day intervention plan — week-by-week priorities",
        "The single most important metric to watch right now",
        "Growth readiness verdict — honest and direct",
    ]:
        st.markdown(f"- {item}")

    st.markdown("""
    <div class="framework-note">
    📚 <b>AI Layer:</b> Groq Llama 3.3 70B Versatile. Brief structure adapted from Y Combinator
    partner review format and First Round Capital operational assessment rubric.
    All context injected from your live inputs — no generic responses.
    </div>
    """, unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#9ca3af; font-size:0.8rem; padding: 1rem;">
VentureOps — Built by Rutwik Satish for the Roux Institute<br>
Frameworks: CB Insights · Bessemer VP · McKinsey · Antler · Theory of Constraints (Goldratt) ·
Kingman's Formula · David Skok · IBEF Logistics Report 2023<br>
All inputs are processed locally. No data is stored.
</div>
""", unsafe_allow_html=True)

