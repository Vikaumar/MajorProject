"""
Streamlit Dashboard for Temporal EVT-Clustering Framework
Premium Research-Grade Interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

st.set_page_config(
    page_title="Climate Risk Velocity Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# PREMIUM CSS DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global Overrides ─────────────────────────────── */
html, body, p, h1, h2, h3, h4, h5, h6, span, div, input, select, textarea, button, label, td, th, li, a {
    font-family: 'Inter', sans-serif !important;
}
/* Preserve Material Icons for Streamlit's built-in icon buttons */
[data-testid="stSidebar"] button[kind="headerNoPadding"] span,
[data-testid="collapsedControl"] span,
.material-symbols-rounded,
[class*="Icon"] span {
    font-family: 'Material Symbols Rounded', sans-serif !important;
}
.stApp {
    background: linear-gradient(160deg, #03050a 0%, #080d1a 40%, #0a0f1e 100%);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060a14 0%, #0a1020 50%, #080d18 100%) !important;
    border-right: 1px solid rgba(79,141,245,0.15);
}
/* Hide header, menus, deploy, and all toggle buttons */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
/* Hide ALL sidebar close/collapse buttons */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="baseButton-headerNoPadding"],
section[data-testid="stSidebar"] > div:first-child > button,
section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
    display: none !important;
}
/* Lock sidebar permanently open */
section[data-testid="stSidebar"] {
    min-width: 280px !important;
    transform: none !important;
}

/* ── Hero Header ──────────────────────────────────── */
.hero-header {
    background: linear-gradient(135deg, #0a1628 0%, #0f1d35 50%, #0a1628 100%);
    border: 1px solid rgba(79,141,245,0.2);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4f8df5, #00d2ff, #a855f7, #4f8df5);
    background-size: 300% 100%;
    animation: shimmer 4s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.hero-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #4f8df5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: #64748b;
    font-size: 14px;
    font-weight: 400;
    letter-spacing: 0.3px;
}

/* ── Glassmorphism Metric Cards ───────────────────── */
.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(79,141,245,0.15);
    border-radius: 14px;
    padding: 22px 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(79,141,245,0.35);
    box-shadow: 0 12px 40px rgba(79,141,245,0.12);
}
.glass-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #4f8df5);
    border-radius: 14px 14px 0 0;
}
.card-icon { font-size: 22px; margin-bottom: 10px; display: block; }
.card-label {
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 6px;
}
.card-value {
    color: #e2e8f0;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.1;
}
.card-delta {
    font-size: 12px;
    font-weight: 600;
    margin-top: 8px;
    padding: 3px 10px;
    border-radius: 20px;
    display: inline-block;
}
.delta-up { background: rgba(34,197,94,0.15); color: #22c55e; }
.delta-down { background: rgba(239,68,68,0.15); color: #ef4444; }

/* ── Warning Alert Card ────────────────────────── */
.alert-card {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.25);
    animation: pulse-border 2.5s ease-in-out infinite;
}
.alert-card::after { background: #ef4444 !important; }
@keyframes pulse-border {
    0%, 100% { border-color: rgba(239,68,68,0.25); box-shadow: 0 0 20px rgba(239,68,68,0.05); }
    50% { border-color: rgba(239,68,68,0.5); box-shadow: 0 0 30px rgba(239,68,68,0.15); }
}

/* ── Section Headers ──────────────────────────────── */
.section-hdr {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 18px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(100,116,139,0.15);
}
.section-hdr-icon {
    width: 36px; height: 36px;
    background: rgba(79,141,245,0.12);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.section-hdr-text {
    font-size: 18px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -0.3px;
}

/* ── Sidebar Styles ───────────────────────────────── */
.sidebar-brand {
    text-align: center;
    padding: 10px 10px 12px 10px;
    border-bottom: 1px solid rgba(79,141,245,0.12);
    margin-bottom: 10px;
}
.sidebar-brand-icon { font-size: 32px; display: block; margin-bottom: 4px; }
.sidebar-brand-title {
    font-size: 15px;
    font-weight: 800;
    background: linear-gradient(135deg, #4f8df5, #00d2ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.3px;
    margin-bottom: 2px;
}
.sidebar-brand-sub {
    font-size: 9px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}
/* Reduce Streamlit's default sidebar spacing */
[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
    gap: 0.5rem !important; /* Compress the gap between widgets */
}
[data-testid="stSidebar"] hr {
    margin: 0.5em 0px !important; /* Compress the horizontal rules */
}
[data-testid="stSidebar"] div.stRadio > div {
    gap: 0px !important; /* Compress radio button list */
}
[data-testid="stSidebar"] .stMarkdown {
    margin-bottom: -10px !important; /* Compress markdown blocks */
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}
.status-green { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }
.status-yellow { background: #eab308; box-shadow: 0 0 8px rgba(234,179,8,0.5); }
.cat-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 3px;
}

/* ── Info Panels ──────────────────────────────────── */
.info-panel {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(100,116,139,0.15);
    border-radius: 12px;
    padding: 18px 22px;
    margin: 12px 0;
}
.info-panel h4 {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

/* ── Methodology Cards ────────────────────────────── */
.method-card {
    background: rgba(15,23,42,0.5);
    border: 1px solid rgba(79,141,245,0.12);
    border-radius: 14px;
    padding: 24px;
    height: 100%;
    transition: border-color 0.3s;
}
.method-card:hover { border-color: rgba(79,141,245,0.35); }
.method-step {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #4f8df5, #00d2ff);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 800; font-size: 14px;
    margin-bottom: 14px;
}
.method-title { color: #e2e8f0; font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.method-desc { color: #64748b; font-size: 13px; line-height: 1.6; }

/* ── Data Table Styling ───────────────────────────── */
.styled-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(100,116,139,0.15);
}
.styled-table th {
    background: rgba(15,23,42,0.8);
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 14px 16px;
    text-align: left;
}
.styled-table td {
    padding: 12px 16px;
    color: #e2e8f0;
    font-size: 13px;
    border-top: 1px solid rgba(100,116,139,0.08);
    background: rgba(10,15,30,0.4);
}
.styled-table tr:hover td { background: rgba(79,141,245,0.05); }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PLOTLY CHART TEMPLATE
# ══════════════════════════════════════════════════════════════
CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(6,8,15,0.4)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    title_font=dict(family="Inter, sans-serif", color="#e2e8f0", size=16),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(100,116,139,0.15)",
        borderwidth=1, font=dict(size=11, color="#94a3b8")
    ),
    margin=dict(l=60, r=30, t=60, b=50),
    xaxis=dict(gridcolor="rgba(100,116,139,0.08)", zerolinecolor="rgba(100,116,139,0.1)"),
    yaxis=dict(gridcolor="rgba(100,116,139,0.08)", zerolinecolor="rgba(100,116,139,0.1)"),
    hoverlabel=dict(bgcolor="#0f1d35", bordercolor="#4f8df5", font_size=12, font_family="Inter"),
)

COLORS = {
    "Fossil Fuel": "#ef4444",
    "ESG / Clean Energy": "#06b6d4",
    "Benchmark": "#eab308",
    0: "#06b6d4",   # Safe
    1: "#eab308",   # Warning
    2: "#ef4444",   # Crash
}
CAT_COLORS_CSS = {
    "Fossil Fuel": "rgba(239,68,68,0.15); color: #ef4444",
    "ESG / Clean Energy": "rgba(6,182,212,0.15); color: #06b6d4",
    "Benchmark": "rgba(234,179,8,0.15); color: #eab308",
}

# ══════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    data_dir = config.DATA_DIR
    try:
        clusters = pd.read_csv(os.path.join(data_dir, "cluster_assignments.csv"), index_col=0)
        warning_alerts = pd.read_csv(os.path.join(data_dir, "warning_alerts.csv"), index_col=0)
        trans_matrix = pd.read_csv(os.path.join(data_dir, "transition_matrix.csv"), index_col=0)
        prices = pd.read_csv(os.path.join(data_dir, "prices.csv"), index_col=0, parse_dates=True)

        if clusters is not None:
            clusters['cluster'] = clusters['cluster'].astype(int)
            clusters['Category'] = [config.TICKER_CATEGORY.get(t, "Unknown") for t in clusters.index]

        all_derivs = {}
        for ticker in config.ALL_TICKERS:
            path = os.path.join(data_dir, f"derivatives_{ticker}.csv")
            if os.path.exists(path):
                df_der = pd.read_csv(path, index_col=0)
                df_der.index = pd.to_datetime(df_der.index)
                all_derivs[ticker] = df_der

        rolling_labels = None
        rl_path = os.path.join(data_dir, "rolling_cluster_labels.csv")
        if os.path.exists(rl_path):
            rolling_labels = pd.read_csv(rl_path, index_col=0, parse_dates=True)

        return clusters, warning_alerts, trans_matrix, prices, all_derivs, rolling_labels
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None

clusters, warning_alerts, trans_matrix, prices, all_derivs, rolling_labels = load_data()

if clusters is None:
    st.error("Data not found. Please run the main.py pipeline first to generate the output CSVs.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("""
<div class="sidebar-brand">
    <span class="sidebar-brand-icon">🌍</span>
    <div class="sidebar-brand-title">Climate Risk Velocity</div>
    <div class="sidebar-brand-sub">Temporal EVT-Clustering Framework</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", [
    "🏠  Executive Summary",
    "🔥  Risk Velocity Heatmap",
    "🔍  Asset Deep Dive",
    "🎯  Cluster Analysis",
    "📈  Comparative Analytics",
    "📚  Methodology & Theory",
], label_visibility="collapsed")

st.sidebar.markdown("---")

# Data Status
n_files = len([f for f in os.listdir(config.DATA_DIR) if f.endswith('.csv')])
st.sidebar.markdown("**📡 Data Pipeline Status**")
st.sidebar.markdown(f"""
<div style="font-size:13px; color:#94a3b8; line-height:2;">
    <span class="status-dot status-green"></span> {len(config.ALL_TICKERS)} assets loaded<br>
    <span class="status-dot status-green"></span> {n_files} data files<br>
    <span class="status-dot status-green"></span> {len(prices):,} trading days<br>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**🏷️ Asset Categories**")
for cat_name, cat_color_css in CAT_COLORS_CSS.items():
    ticks = [t for t, c in config.TICKER_CATEGORY.items() if c == cat_name]
    st.sidebar.markdown(
        f'<span class="cat-badge" style="background:{cat_color_css}">{cat_name}</span>'
        f'<br><span style="color:#475569;font-size:12px;margin-left:4px">{", ".join(ticks)}</span>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown("")

st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<div style="text-align:center;color:#334155;font-size:10px;padding:8px 0;">'
    f'Framework v2.0 · Built with Streamlit<br>Last updated: {datetime.now().strftime("%b %d, %Y")}'
    f'</div>', unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════
def section_header(icon, text):
    st.markdown(f"""
    <div class="section-hdr">
        <div class="section-hdr-icon">{icon}</div>
        <div class="section-hdr-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(icon, label, value, accent="#4f8df5", delta=None, is_alert=False):
    alert_cls = "alert-card" if is_alert else ""
    delta_html = ""
    if delta:
        cls = "delta-up" if "↑" in delta else "delta-down"
        delta_html = f'<div class="card-delta {cls}">{delta}</div>'
    return f"""
    <div class="glass-card {alert_cls}" style="--accent:{accent}">
        <span class="card-icon">{icon}</span>
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        {delta_html}
    </div>
    """

def apply_chart_layout(fig, height=500, **kwargs):
    layout = {**CHART_LAYOUT, "height": height, **kwargs}
    fig.update_layout(**layout)
    return fig

# ══════════════════════════════════════════════════════════════
# PAGE 1: EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════
if page == "🏠  Executive Summary":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Ecosystem Overview & Risk Intelligence</div>
        <div class="hero-subtitle">Real-time monitoring of climate transition risk velocity across fossil fuel, ESG, and benchmark assets</div>
    </div>
    """, unsafe_allow_html=True)

    avg_rvi = clusters["RVI"].mean() if not clusters.empty else 0.0
    max_rvi = clusters["RVI"].max() if not clusters.empty else 0.0
    n_fast = int(warning_alerts["is_warning_alert"].sum()) if not warning_alerts.empty else 0
    n_high = int((clusters["cluster"] == 2).sum()) if not clusters.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("📡", "Monitored Assets", len(config.ALL_TICKERS), "#4f8df5"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("📅", "Trading Days", f"{len(prices):,}", "#06b6d4"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("⚡", "System Avg RVI", f"{avg_rvi:.6f}", "#a855f7"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("🚨", "Warning State Alerts", n_fast, "#ef4444", is_alert=(n_fast > 0)), unsafe_allow_html=True)

    # ── Risk Velocity Alerts Panel ──
    section_header("🚨", "Risk Velocity Alerts — Warning State Assets")

    f_movers_df = warning_alerts[warning_alerts["is_warning_alert"]]

    if len(f_movers_df) > 0:
        fig_bar = go.Figure()
        for _, row in f_movers_df.iterrows():
            cat = row["category"]
            color = COLORS.get(cat, "#94a3b8")
            fig_bar.add_trace(go.Bar(
                x=[row.name], y=[row["recent_RVI"]],
                name=row.name,
                marker=dict(color=color, line=dict(width=0), opacity=0.9),
                hovertemplate=f"<b>{row.name}</b><br>Category: {cat}<br>RVI: %{{y:.6f}}<extra></extra>",
                showlegend=False,
            ))
        threshold = f_movers_df["threshold"].iloc[0]
        fig_bar.add_hline(y=threshold, line_dash="dash", line_color="#eab308", line_width=2,
                          annotation_text="Critical Threshold", annotation_font=dict(color="#eab308", size=12))
        apply_chart_layout(fig_bar, height=420,
            title=dict(text="Recent Risk Velocity Index (RVI) — Warning Alerts", font=dict(size=16)),
            xaxis_title="Asset Ticker", yaxis_title="Recent Mean RVI",
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, width="stretch")
    else:
        st.markdown("""
        <div class="info-panel" style="border-color:rgba(34,197,94,0.25);text-align:center;padding:30px">
            <span style="font-size:32px">✅</span><br>
            <span style="color:#22c55e;font-size:15px;font-weight:600;">No warning alerts detected above the critical threshold</span><br>
            <span style="color:#64748b;font-size:13px;">All assets are within normal risk velocity ranges</span>
        </div>
        """, unsafe_allow_html=True)

    # ── Category Comparison ──
    section_header("📊", "Average Risk Velocity by Category")

    grouped = warning_alerts.groupby("category")["recent_RVI"].mean().reset_index()
    grouped = grouped.sort_values("recent_RVI", ascending=True)

    fig_cat = go.Figure()
    for _, row in grouped.iterrows():
        color = COLORS.get(row["category"], "#94a3b8")
        fig_cat.add_trace(go.Bar(
            y=[row["category"]], x=[row["recent_RVI"]],
            orientation='h', name=row["category"],
            marker=dict(color=color, opacity=0.85, line=dict(width=0)),
            hovertemplate=f"<b>{row['category']}</b><br>Avg RVI: %{{x:.6f}}<extra></extra>",
            showlegend=False,
        ))
    apply_chart_layout(fig_cat, height=300,
        title=dict(text="Category Risk Comparison", font=dict(size=16)),
        xaxis_title="Average Recent RVI", yaxis_title="",
        bargap=0.4,
    )
    st.plotly_chart(fig_cat, width="stretch")

    # ── Cluster Distribution Summary ──
    section_header("🎯", "Current Risk Cluster Distribution")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        cluster_counts = clusters["cluster"].value_counts().sort_index()
        labels_list = [config.CLUSTER_LABELS.get(i, f"Cluster {i}") for i in cluster_counts.index]
        colors_list = [COLORS.get(i, "#94a3b8") for i in cluster_counts.index]

        fig_donut = go.Figure(go.Pie(
            labels=labels_list, values=cluster_counts.values,
            hole=0.65, marker=dict(colors=colors_list, line=dict(color="#0a0f1e", width=3)),
            textinfo="label+percent", textfont=dict(size=12, color="#e2e8f0"),
            hovertemplate="<b>%{label}</b><br>Assets: %{value}<br>Share: %{percent}<extra></extra>",
        ))
        fig_donut.add_annotation(text=f"<b>{len(clusters)}</b><br><span style='font-size:11px;color:#64748b'>Assets</span>",
                                 x=0.5, y=0.5, font=dict(size=24, color="#e2e8f0"), showarrow=False)
        apply_chart_layout(fig_donut, height=350, title=dict(text="Cluster Composition", font=dict(size=16)), showlegend=False)
        st.plotly_chart(fig_donut, width="stretch")

    with col_b:
        # Top risk assets table
        top_risk = clusters.nlargest(8, "RVI")[["Category", "RVI", "cluster_label"]].reset_index()
        table_rows = ""
        for _, r in top_risk.iterrows():
            cat_css = CAT_COLORS_CSS.get(r["Category"], "rgba(100,116,139,0.15); color: #94a3b8")
            table_rows += f"""<tr>
                <td style="font-weight:600">{r['Ticker']}</td>
                <td><span class="cat-badge" style="background:{cat_css}">{r['Category']}</span></td>
                <td style="font-variant-numeric:tabular-nums">{r['RVI']:.6f}</td>
                <td>{r['cluster_label']}</td>
            </tr>"""
        st.markdown(f"""
        <div class="info-panel" style="padding:0;overflow:hidden;">
            <table class="styled-table">
                <thead><tr><th>Ticker</th><th>Category</th><th>RVI</th><th>Risk Level</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2: RISK VELOCITY HEATMAP
# ══════════════════════════════════════════════════════════════
elif page == "🔥  Risk Velocity Heatmap":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Risk Velocity Heatmap</div>
        <div class="hero-subtitle">Temporal evolution of GPD parameter derivatives and composite Risk Velocity Index across all monitored assets</div>
    </div>
    """, unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns([2, 3])
    with col_ctrl1:
        param_choice = st.radio("Select Parameter", ["dxi_dt", "dsigma_dt", "RVI"],
                                horizontal=True, key="heatmap_param")
    param_labels = {"dxi_dt": "dξ/dt (Shape Velocity)", "dsigma_dt": "dσ/dt (Scale Velocity)", "RVI": "Risk Velocity Index"}

    frames = {}
    for t, df_deriv in all_derivs.items():
        if param_choice in df_deriv.columns:
            s_data = df_deriv[param_choice].copy()
            try:
                resampled = s_data.resample("ME").mean()
            except ValueError:
                resampled = s_data.resample("M").mean()
            frames[t] = resampled

    if frames:
        matrix = pd.DataFrame(frames).T
        matrix.columns = pd.to_datetime(matrix.columns)
        matrix.columns = [d.strftime("%Y-%m") if pd.notnull(d) else "N/A" for d in matrix.columns]

        # Add category ordering
        cat_order = {"Fossil Fuel": 0, "ESG / Clean Energy": 1, "Benchmark": 2}
        sort_key = [cat_order.get(config.TICKER_CATEGORY.get(t, ""), 3) for t in matrix.index]
        matrix["_sort"] = sort_key
        matrix = matrix.sort_values("_sort").drop("_sort", axis=1)

        colorscale = "RdYlGn_r" if param_choice != "RVI" else "YlOrRd"

        fig_heat = px.imshow(
            matrix.values, x=matrix.columns.tolist(), y=matrix.index.tolist(),
            color_continuous_scale=colorscale,
            aspect="auto",
            labels=dict(x="Month", y="Asset", color=param_labels[param_choice]),
        )
        apply_chart_layout(fig_heat, height=650,
            title=dict(text=f"Monthly Average: {param_labels[param_choice]}", font=dict(size=16)),
        )
        fig_heat.update_xaxes(tickangle=45, tickfont=dict(size=9))
        st.plotly_chart(fig_heat, width="stretch")

        # Summary Statistics
        section_header("📋", "Summary Statistics")
        sc1, sc2, sc3, sc4 = st.columns(4)
        flat = matrix.values.flatten()
        flat = flat[~np.isnan(flat)]
        with sc1:
            st.markdown(metric_card("📉", "Minimum", f"{np.min(flat):.6f}", "#06b6d4"), unsafe_allow_html=True)
        with sc2:
            st.markdown(metric_card("📊", "Mean", f"{np.mean(flat):.6f}", "#a855f7"), unsafe_allow_html=True)
        with sc3:
            st.markdown(metric_card("📈", "Maximum", f"{np.max(flat):.6f}", "#ef4444"), unsafe_allow_html=True)
        with sc4:
            st.markdown(metric_card("📐", "Std Dev", f"{np.std(flat):.6f}", "#eab308"), unsafe_allow_html=True)
    else:
        st.warning("Insufficient data to generate heatmap for the selected parameter.")


# ══════════════════════════════════════════════════════════════
# PAGE 3: ASSET DEEP DIVE
# ══════════════════════════════════════════════════════════════
elif page == "🔍  Asset Deep Dive":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Asset Deep Dive</div>
        <div class="hero-subtitle">Comprehensive risk velocity analysis for individual assets with GPD parameter evolution</div>
    </div>
    """, unsafe_allow_html=True)

    sel_col1, sel_col2 = st.columns([1, 3])
    with sel_col1:
        selected_asset = st.selectbox("Select Asset", config.ALL_TICKERS, key="deep_dive_asset")

    if selected_asset not in all_derivs:
        st.warning(f"No derivative data available for {selected_asset}.")
        st.stop()

    df = all_derivs[selected_asset]
    cat = config.TICKER_CATEGORY.get(selected_asset, "Unknown")
    c_color = COLORS.get(cat, "#94a3b8")

    # Asset info cards
    ac1, ac2, ac3, ac4 = st.columns(4)
    rvi_series = df["RVI"].dropna()
    with ac1:
        cat_css = CAT_COLORS_CSS.get(cat, "rgba(100,116,139,0.15); color:#94a3b8")
        st.markdown(f"""
        <div class="glass-card" style="--accent:{c_color}">
            <div class="card-label">Category</div>
            <span class="cat-badge" style="background:{cat_css};font-size:14px;padding:5px 14px">{cat}</span>
        </div>
        """, unsafe_allow_html=True)
    with ac2:
        st.markdown(metric_card("⚡", "Mean RVI", f"{rvi_series.mean():.6f}", c_color), unsafe_allow_html=True)
    with ac3:
        st.markdown(metric_card("🔺", "Max RVI", f"{rvi_series.max():.6f}", "#ef4444"), unsafe_allow_html=True)
    with ac4:
        p90 = np.nanpercentile(rvi_series, 90)
        st.markdown(metric_card("📊", "90th Pctl", f"{p90:.6f}", "#eab308"), unsafe_allow_html=True)

    # RVI Time Series
    section_header("📈", f"{selected_asset} — Risk Velocity Index Over Time")

    r_hex = int(c_color[1:3], 16)
    g_hex = int(c_color[3:5], 16)
    b_hex = int(c_color[5:7], 16)
    fill_rgba = f"rgba({r_hex},{g_hex},{b_hex},0.15)"

    fig_rvi = go.Figure()
    fig_rvi.add_trace(go.Scatter(
        x=df.index, y=df["RVI"], mode='lines', name='RVI',
        line=dict(color=c_color, width=2),
        fill='tozeroy', fillcolor=fill_rgba,
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>RVI: %{y:.6f}<extra></extra>",
    ))
    fig_rvi.add_hline(y=p90, line_dash="dash", line_color="#eab308", line_width=1.5,
                      annotation_text="90th Percentile", annotation_font=dict(color="#eab308", size=11))
    apply_chart_layout(fig_rvi, height=400,
        title=dict(text=f"Cumulative Risk Velocity Index — {selected_asset}", font=dict(size=16)),
        yaxis_title="RVI",
    )
    st.plotly_chart(fig_rvi, width="stretch")

    # GPD Parameters side by side
    section_header("🔬", "GPD Parameter Evolution")
    gp1, gp2 = st.columns(2)

    with gp1:
        fig_xi = go.Figure()
        fig_xi.add_trace(go.Scatter(
            x=df.index, y=df["xi"], mode='lines', name='ξ(t)',
            line=dict(color="#a855f7", width=1.8),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>ξ: %{y:.6f}<extra></extra>",
        ))
        apply_chart_layout(fig_xi, height=320,
            title=dict(text="Shape Parameter ξ(t)", font=dict(size=14)),
            yaxis_title="ξ (shape)",
        )
        st.plotly_chart(fig_xi, width="stretch")

    with gp2:
        fig_sigma = go.Figure()
        fig_sigma.add_trace(go.Scatter(
            x=df.index, y=df["sigma"], mode='lines', name='σ(t)',
            line=dict(color="#06b6d4", width=1.8),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>σ: %{y:.6f}<extra></extra>",
        ))
        apply_chart_layout(fig_sigma, height=320,
            title=dict(text="Scale Parameter σ(t)", font=dict(size=14)),
            yaxis_title="σ (scale)",
        )
        st.plotly_chart(fig_sigma, width="stretch")

    # Velocity derivatives
    section_header("🏎️", "Parameter Velocity (Derivatives)")
    vp1, vp2 = st.columns(2)
    with vp1:
        fig_dxi = go.Figure()
        fig_dxi.add_trace(go.Scatter(
            x=df.index, y=df["dxi_dt"], mode='lines', name='dξ/dt',
            line=dict(color="#f97316", width=1.5),
            fill='tozeroy', fillcolor="rgba(249,115,22,0.08)",
        ))
        fig_dxi.add_hline(y=0, line_color="rgba(100,116,139,0.3)", line_width=1)
        apply_chart_layout(fig_dxi, height=280,
            title=dict(text="dξ/dt — Shape Velocity", font=dict(size=14)), yaxis_title="dξ/dt")
        st.plotly_chart(fig_dxi, width="stretch")
    with vp2:
        fig_dsig = go.Figure()
        fig_dsig.add_trace(go.Scatter(
            x=df.index, y=df["dsigma_dt"], mode='lines', name='dσ/dt',
            line=dict(color="#10b981", width=1.5),
            fill='tozeroy', fillcolor="rgba(16,185,129,0.08)",
        ))
        fig_dsig.add_hline(y=0, line_color="rgba(100,116,139,0.3)", line_width=1)
        apply_chart_layout(fig_dsig, height=280,
            title=dict(text="dσ/dt — Scale Velocity", font=dict(size=14)), yaxis_title="dσ/dt")
        st.plotly_chart(fig_dsig, width="stretch")


# ══════════════════════════════════════════════════════════════
# PAGE 4: CLUSTER ANALYSIS
# ══════════════════════════════════════════════════════════════
elif page == "🎯  Cluster Analysis":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Cluster Analysis & Migration Flows</div>
        <div class="hero-subtitle">K-Means clustering in EVT parameter space with temporal transition probability analysis</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🎯 EVT Parameter Space", "🔄 Transition Sankey"])

    with tab1:
        section_header("🎯", "EVT Cluster Scatter with Velocity Bubbles")
        st.markdown("""
        <div class="info-panel">
            <span style="color:#94a3b8;font-size:13px;">
            Assets are plotted in the (ξ, σ) parameter space. <b>Bubble size</b> represents Risk Velocity Index magnitude.
            <b>Color</b> indicates K-Means cluster assignment (Safe / Warning / Crash).
            </span>
        </div>
        """, unsafe_allow_html=True)

        fig_scatter = px.scatter(
            clusters.reset_index(), x="xi", y="sigma",
            color="cluster_label",
            size="RVI",
            hover_name="Ticker",
            hover_data={"Category": True, "dxi_dt": ":.6f", "dsigma_dt": ":.6f", "RVI": ":.6f", "xi": ":.4f", "sigma": ":.4f", "cluster_label": False},
            color_discrete_map={"Safe": COLORS[0], "Warning": COLORS[1], "Crash": COLORS[2]},
            labels={"xi": "Shape Parameter (ξ)", "sigma": "Scale Parameter (σ)", "cluster_label": "Risk Level"},
            size_max=45,
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1.5, color='rgba(255,255,255,0.4)')))
        apply_chart_layout(fig_scatter, height=600,
            title=dict(text="Asset Clustering in EVT Parameter Space", font=dict(size=16)),
        )
        st.plotly_chart(fig_scatter, width="stretch")

    with tab2:
        section_header("🔄", "Cluster Transition Probabilities")
        st.markdown("""
        <div class="info-panel">
            <span style="color:#94a3b8;font-size:13px;">
            Sankey diagram showing the probability of assets migrating between risk clusters across consecutive time windows.
            Flow width is proportional to transition probability (%).
            </span>
        </div>
        """, unsafe_allow_html=True)

        labels_from = [f"{l} (t)" for l in trans_matrix.index]
        labels_to = [f"{l} (t+1)" for l in trans_matrix.columns]
        all_labels = labels_from + labels_to

        n = len(trans_matrix)
        source, target, value, link_labels = [], [], [], []

        for i in range(n):
            for j in range(n):
                v = trans_matrix.iloc[i, j]
                if v > 0.001:
                    source.append(i)
                    target.append(n + j)
                    pct = round(v * 100, 1)
                    value.append(pct)
                    link_labels.append(f"{pct}%")

        colors_node = [COLORS[0], COLORS[1], COLORS[2]] * 2
        colors_link = []
        for s in source:
            c = colors_node[s % 3]
            r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            colors_link.append(f"rgba({r},{g},{b},0.35)")

        fig_sankey = go.Figure(go.Sankey(
            node=dict(pad=25, thickness=30, label=all_labels,
                      color=colors_node[:len(all_labels)],
                      line=dict(color="rgba(255,255,255,0.15)", width=1)),
            link=dict(source=source, target=target, value=value,
                      color=colors_link, label=link_labels),
        ))
        apply_chart_layout(fig_sankey, height=550,
            title=dict(text="Cluster Migration Flow (Transition Probabilities)", font=dict(size=16)),
        )
        st.plotly_chart(fig_sankey, width="stretch")


# ══════════════════════════════════════════════════════════════
# PAGE 5: COMPARATIVE ANALYTICS
# ══════════════════════════════════════════════════════════════
elif page == "📈  Comparative Analytics":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Comparative Analytics</div>
        <div class="hero-subtitle">Head-to-head analysis of fossil fuel vs. ESG / clean energy assets across risk velocity dimensions</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Ranking Table ──
    section_header("🏆", "Asset Risk Velocity Ranking")
    ranked = clusters.sort_values("RVI", ascending=False).reset_index()
    rank_rows = ""
    for idx, r in ranked.iterrows():
        cat_css = CAT_COLORS_CSS.get(r["Category"], "rgba(100,116,139,0.15); color:#94a3b8")
        medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"<span style='color:#475569'>{idx+1}</span>"
        rank_rows += f"""<tr>
            <td style="text-align:center">{medal}</td>
            <td style="font-weight:600">{r['Ticker']}</td>
            <td><span class="cat-badge" style="background:{cat_css}">{r['Category']}</span></td>
            <td style="font-variant-numeric:tabular-nums">{r['RVI']:.6f}</td>
            <td>{r['xi']:.4f}</td>
            <td>{r['sigma']:.4f}</td>
            <td>{r['cluster_label']}</td>
        </tr>"""
    st.markdown(f"""
    <div class="info-panel" style="padding:0;overflow:hidden;">
        <table class="styled-table">
            <thead><tr><th>#</th><th>Ticker</th><th>Category</th><th>RVI</th><th>ξ</th><th>σ</th><th>Risk Level</th></tr></thead>
            <tbody>{rank_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # ── Multi-Asset RVI Overlay ──
    section_header("📈", "Multi-Asset RVI Time Series")

    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        compare_tickers = st.multiselect(
            "Select assets to compare",
            config.ALL_TICKERS,
            default=["XOM", "ICLN", "SPY"],
            key="compare_multi"
        )

    if compare_tickers:
        fig_multi = go.Figure()
        palette = ["#ef4444", "#06b6d4", "#eab308", "#a855f7", "#f97316", "#10b981", "#ec4899", "#6366f1"]
        for i, ticker in enumerate(compare_tickers):
            if ticker in all_derivs:
                ddf = all_derivs[ticker]
                color = palette[i % len(palette)]
                fig_multi.add_trace(go.Scatter(
                    x=ddf.index, y=ddf["RVI"], mode='lines', name=ticker,
                    line=dict(color=color, width=2),
                    hovertemplate=f"<b>{ticker}</b><br>%{{x|%Y-%m-%d}}<br>RVI: %{{y:.6f}}<extra></extra>",
                ))
        apply_chart_layout(fig_multi, height=450,
            title=dict(text="RVI Comparison Across Selected Assets", font=dict(size=16)),
            yaxis_title="Risk Velocity Index", xaxis_title="Date",
        )
        st.plotly_chart(fig_multi, width="stretch")

    # ── Fossil Fuel vs ESG scatter ──
    section_header("⚔️", "Fossil Fuel vs ESG — Risk-Velocity Scatter")

    fig_vs = go.Figure()
    for _, row in clusters.reset_index().iterrows():
        cat = row["Category"]
        color = COLORS.get(cat, "#94a3b8")
        fig_vs.add_trace(go.Scatter(
            x=[row["dxi_dt"]], y=[row["dsigma_dt"]],
            mode="markers+text",
            text=[row["Ticker"]], textposition="top center",
            textfont=dict(color="#94a3b8", size=10),
            marker=dict(size=row["RVI"] * 8000 + 10, color=color, opacity=0.8,
                        line=dict(width=1, color="rgba(255,255,255,0.3)")),
            name=cat, showlegend=False,
            hovertemplate=f"<b>{row['Ticker']}</b><br>dξ/dt: {row['dxi_dt']:.6f}<br>dσ/dt: {row['dsigma_dt']:.6f}<br>RVI: {row['RVI']:.6f}<extra></extra>",
        ))
    fig_vs.add_hline(y=0, line_color="rgba(100,116,139,0.2)", line_width=1)
    fig_vs.add_vline(x=0, line_color="rgba(100,116,139,0.2)", line_width=1)
    apply_chart_layout(fig_vs, height=500,
        title=dict(text="Assets in Velocity Space (dξ/dt vs dσ/dt)", font=dict(size=16)),
        xaxis_title="dξ/dt (Shape Velocity)", yaxis_title="dσ/dt (Scale Velocity)",
    )
    st.plotly_chart(fig_vs, width="stretch")


# ══════════════════════════════════════════════════════════════
# PAGE 6: METHODOLOGY & THEORY
# ══════════════════════════════════════════════════════════════
elif page == "📚  Methodology & Theory":
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">Methodology & Theoretical Framework</div>
        <div class="hero-subtitle">Formal description of the Temporal EVT-Clustering approach to quantifying climate transition risk velocity</div>
    </div>
    """, unsafe_allow_html=True)

    section_header("🔬", "Research Pipeline Overview")

    mc1, mc2, mc3, mc4 = st.columns(4)
    steps = [
        ("1", "Data Ingestion", "Historical price data collection via Yahoo Finance for fossil fuel, ESG, and benchmark assets"),
        ("2", "EVT / GPD Fitting", "Rolling-window Peaks-Over-Threshold with Generalized Pareto Distribution parameter estimation"),
        ("3", "Temporal Derivatives", "Savitzky-Golay smoothing and numerical differentiation of ξ(t) and σ(t) to obtain risk velocities"),
        ("4", "Clustering & Detection", "K-Means clustering in parameter space with transition probability analysis and Risk Velocity Alert detection"),
    ]
    for col, (num, title, desc) in zip([mc1, mc2, mc3, mc4], steps):
        with col:
            st.markdown(f"""
            <div class="method-card">
                <div class="method-step">{num}</div>
                <div class="method-title">{title}</div>
                <div class="method-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    section_header("📐", "Key Mathematical Formulations")

    st.latex(r"""
    \text{GPD CDF: } \quad G_{\xi,\sigma}(x) = 1 - \left(1 + \frac{\xi x}{\sigma}\right)^{-1/\xi}, \quad x > 0
    """)

    fm1, fm2 = st.columns(2)
    with fm1:
        st.markdown("""
        <div class="info-panel">
            <h4>Risk Velocity Index (RVI)</h4>
            <span style="color:#e2e8f0;font-size:13px;line-height:1.8;">
            The composite Risk Velocity Index combines the temporal derivatives of both GPD parameters
            using configurable weights to create a single measure of how rapidly an asset's tail-risk
            profile is evolving.
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"""
        \text{RVI}(t) = w_\xi \left|\frac{d\xi}{dt}\right| + w_\sigma \left|\frac{d\sigma}{dt}\right|
        """)
        st.markdown(f"""
        <div style="color:#64748b;font-size:12px;margin-top:8px;">
        Current weights: w<sub>ξ</sub> = {config.VELOCITY_WEIGHT_XI}, w<sub>σ</sub> = {config.VELOCITY_WEIGHT_SIGMA}
        </div>
        """, unsafe_allow_html=True)

    with fm2:
        st.markdown("""
        <div class="info-panel">
            <h4>Risk Velocity Alert Detection</h4>
            <span style="color:#e2e8f0;font-size:13px;line-height:1.8;">
            An asset triggers a <b>Risk Velocity Alert</b> (Warning State) when its recent average RVI exceeds a
            critical threshold derived from the cross-sectional distribution of all asset RVI values,
            indicating abnormally rapid tail-risk evolution toward the Warning state.
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"""
        \text{Warning Alert:} \quad \overline{\text{RVI}}_{\text{recent}} > \mu_{\text{RVI}} + 2\sigma_{\text{RVI}}
        """)

    section_header("⚙️", "Configuration Parameters")

    params_data = [
        ("Rolling Window", str(config.ROLLING_WINDOW), "~1 trading year for GPD fitting"),
        ("POT Quantile", str(config.POT_QUANTILE), "90th percentile threshold for exceedances"),
        ("Min Exceedances", str(config.MIN_EXCEEDANCES), "Minimum data points for valid GPD fit"),
        ("Smoothing Window", str(config.SMOOTHING_WINDOW), "Savitzky-Golay window (must be odd)"),
        ("Smoothing Poly", str(config.SMOOTHING_POLY), "Polynomial order for smoothing filter"),
        ("N Clusters", str(config.N_CLUSTERS), "K-Means cluster count (Safe/Warning/Crash)"),
        ("RVI Weight ξ", str(config.VELOCITY_WEIGHT_XI), "Weight of dξ/dt in RVI formula"),
        ("RVI Weight σ", str(config.VELOCITY_WEIGHT_SIGMA), "Weight of dσ/dt in RVI formula"),
    ]
    cfg_rows = ""
    for name, val, desc in params_data:
        cfg_rows += f"""<tr>
            <td style="font-weight:600;color:#a855f7">{name}</td>
            <td style="font-variant-numeric:tabular-nums;color:#e2e8f0">{val}</td>
            <td style="color:#64748b">{desc}</td>
        </tr>"""
    st.markdown(f"""
    <div class="info-panel" style="padding:0;overflow:hidden;">
        <table class="styled-table">
            <thead><tr><th>Parameter</th><th>Value</th><th>Description</th></tr></thead>
            <tbody>{cfg_rows}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    section_header("📊", "Data Universe")

    st.markdown(f"""
    <div class="info-panel">
        <span style="color:#94a3b8;font-size:13px;line-height:2;">
        <b>Date Range:</b> {config.START_DATE} → {config.END_DATE}<br>
        <b>Fossil Fuel ({len(config.FOSSIL_FUEL_TICKERS)}):</b> {', '.join(config.FOSSIL_FUEL_TICKERS)}<br>
        <b>ESG / Clean Energy ({len(config.ESG_CLEAN_TICKERS)}):</b> {', '.join(config.ESG_CLEAN_TICKERS)}<br>
        <b>Benchmark ({len(config.BENCHMARK_TICKERS)}):</b> {', '.join(config.BENCHMARK_TICKERS)}<br>
        <b>Total Assets:</b> {len(config.ALL_TICKERS)}
        </span>
    </div>
    """, unsafe_allow_html=True)
