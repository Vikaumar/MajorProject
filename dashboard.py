"""
Streamlit Dashboard for Temporal EVT-Clustering Framework
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

st.set_page_config(
    page_title="Climate Risk Velocity Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0f1524;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        border-left: 5px solid #4f8df5;
    }
    .metric-title {
        color: #a0aec0;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #e2e8f0;
        font-size: 28px;
        font-weight: bold;
    }
    .fast-mover-card {
        background: linear-gradient(135deg, #2a0a18 0%, #0f1524 100%);
        border-left: 5px solid #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────
@st.cache_data
def load_data():
    data_dir = config.DATA_DIR
    try:
        clusters = pd.read_csv(os.path.join(data_dir, "cluster_assignments.csv"), index_col=0)
        fast_movers = pd.read_csv(os.path.join(data_dir, "fast_movers.csv"), index_col=0)
        trans_matrix = pd.read_csv(os.path.join(data_dir, "transition_matrix.csv"), index_col=0)
        prices = pd.read_csv(os.path.join(data_dir, "prices.csv"), index_col=0, parse_dates=True)
        
        # Pre-process clusters and fast_movers
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
                
        return clusters, fast_movers, trans_matrix, prices, all_derivs
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None

clusters, fast_movers, trans_matrix, prices, all_derivs = load_data()

if clusters is None:
    st.error("Data not found. Please run the main.py pipeline first to generate the output CSVs.")
    st.stop()


# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.title("🌍 Setup & Navigation")
st.sidebar.markdown("Quantifying Climate Transition Risk Velocity")

page = st.sidebar.radio("Navigation", [
    "Overview & Fast Movers", 
    "Risk Velocity Heatmap", 
    "Asset Deep Dive", 
    "Cluster Scatter & Migrations"
])

st.sidebar.markdown("---")
st.sidebar.subheader("Ticker Categories")
cats = list(set(config.TICKER_CATEGORY.values()))
for cat in cats:
    ticks = [t for t, c in config.TICKER_CATEGORY.items() if c == cat]
    st.sidebar.markdown(f"**{cat}**")
    st.sidebar.markdown(f"<span style='color:#a0aec0;font-size:13px'>{', '.join(ticks)}</span>", unsafe_allow_html=True)

# ── Colors ───────────────────────────────────────────────────
COLORS = {
    "Fossil Fuel": "#ff6b6b",
    "ESG / Clean Energy": "#00d2ff",
    "Benchmark": "#feca57",
    0: "#00d2ff", # Low Risk
    1: "#feca57", # Medium Risk
    2: "#ff6b6b"  # High Risk
}

# ── Main Content ─────────────────────────────────────────────

if page == "Overview & Fast Movers":
    st.title("📈 Ecosystem Overview")
    
    # Render top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    avg_rvi = clusters["RVI"].mean() if not clusters.empty else 0.0
    n_fast = fast_movers["is_fast_mover"].sum() if not fast_movers.empty else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Monitored Assets</div>
            <div class="metric-value">{len(config.ALL_TICKERS)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Trading Days</div>
            <div class="metric-value">{len(prices) if prices is not None else 0:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">System-wide Avg RVI</div>
            <div class="metric-value">{avg_rvi:.5f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card fast-mover-card">
            <div class="metric-title">Crit Fast Movers</div>
            <div class="metric-value">{n_fast}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🚨 Fast Movers (Highest Risk Velocity)")
    
    f_movers_df = fast_movers[fast_movers["is_fast_mover"]]
    
    if len(f_movers_df) > 0:
        fig_bar = px.bar(
            f_movers_df, 
            x=f_movers_df.index, 
            y="recent_RVI",
            color="category",
            color_discrete_map=COLORS,
            title="Recent Risk Velocity Index (RVI) for Fast Movers",
            labels={"recent_RVI": "Recent Mean RVI", "index": "Ticker"}
        )
        fig_bar.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        fig_bar.add_hline(y=f_movers_df["threshold"].iloc[0], line_dash="dash", line_color="yellow", annotation_text="Critical Threshold")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.success("No fast movers detected above the critical threshold.")

    st.markdown("### 📊 Comparative RVI by Category")
    grouped = fast_movers.groupby("category")["recent_RVI"].mean().reset_index()
    fig_cat = px.bar(
        grouped, 
        x="category", 
        y="recent_RVI", 
        color="category",
        color_discrete_map=COLORS,
        title="Average Risk Velocity by Category"
    )
    fig_cat.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_cat, use_container_width=True)


elif page == "Risk Velocity Heatmap":
    st.title("🔥 Risk Velocity Heatmap")
    st.markdown("Visualizing the velocity of the shape parameter ($d\\xi/dt$) and scale parameter ($d\\sigma/dt$) across all assets over time. Resampled at a monthly frequency.")
    
    param_choice = st.radio("Select Parameter", ["dxi_dt", "dsigma_dt", "RVI"], horizontal=True)
    
    frames = {}
    for t, df_deriv in all_derivs.items():
        if param_choice in df_deriv.columns:
            s_data = df_deriv[param_choice].copy()
            # Ensure it's resampled correctly regardless of pandas version
            try:
                # 'ME' is preferred for newer pandas, fallback to 'M'
                resampled = s_data.resample("ME").mean()
            except ValueError:
                resampled = s_data.resample("M").mean()
            frames[t] = resampled

    if frames:
        matrix = pd.DataFrame(frames).T
        # Convert columns to DatetimeIndex to ensure strftime works
        matrix.columns = pd.to_datetime(matrix.columns)
        matrix.columns = [d.strftime("%Y-%m") if pd.notnull(d) else "N/A" for d in matrix.columns]
        
        fig_heat = px.imshow(
            matrix, 
            color_continuous_scale="RdYlGn_r" if param_choice != "RVI" else "solar",
            aspect="auto",
            title=f"Monthly Average: {param_choice}"
        )
        fig_heat.update_layout(template="plotly_dark", height=600, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("Insufficient data to generate heatmap for the selected parameter.")


elif page == "Asset Deep Dive":
    st.title("🔍 Asset Deep Dive")
    
    selected_asset = st.selectbox("Select Asset to Analyze", config.ALL_TICKERS)
    
    df = all_derivs[selected_asset]
    cat = config.TICKER_CATEGORY.get(selected_asset, "Unknown")
    c_color = COLORS.get(cat, "#ffffff")
    
    st.markdown(f"**Category:** <span style='color:{c_color}'>{cat}</span>", unsafe_allow_html=True)
    
    st.subheader(f"{selected_asset} - Cumulative Risk Velocity Index (RVI)")
    
    # Calculate 90th percentile for chart with safety check
    rvi_series = df["RVI"].dropna()
    p90 = np.nanpercentile(rvi_series, 90) if not rvi_series.empty else 0.0
    
    # Convert hex to rgba for Plotly fillcolor
    r, g, b = int(c_color[1:3], 16), int(c_color[3:5], 16), int(c_color[5:7], 16)
    fill_c_color = f"rgba({r},{g},{b},0.2)"

    fig_rvi = go.Figure()
    fig_rvi.add_trace(go.Scatter(
        x=df.index, y=df["RVI"], 
        mode='lines', 
        name='RVI',
        line=dict(color=c_color, width=2),
        fill='tozeroy',
        fillcolor=fill_c_color
    ))
    fig_rvi.add_hline(y=p90, line_dash="dash", line_color="#feca57", annotation_text="90th Percentile")
    fig_rvi.update_layout(template="plotly_dark", height=400, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_rvi, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("GPD Shape Parameter ξ(t)")
        fig_xi = px.line(df, x=df.index, y="xi", color_discrete_sequence=["#a0aec0"])
        fig_xi.update_layout(template="plotly_dark", height=300, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_xi, use_container_width=True)
        
    with col2:
        st.subheader("GPD Scale Parameter σ(t)")
        fig_sigma = px.line(df, x=df.index, y="sigma", color_discrete_sequence=["#a0aec0"])
        fig_sigma.update_layout(template="plotly_dark", height=300, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sigma, use_container_width=True)


elif page == "Cluster Scatter & Migrations":
    st.title("🎯 Clusters & Migrations")
    
    tab1, tab2 = st.tabs(["Cluster Scatter", "Transition Sankey"])
    
    with tab1:
        st.subheader("EVT Cluster Scatter with Velocity Bubbles")
        st.markdown("Scatter plot of assets in the (ξ, σ) parameter space. Bubble size corresponds to RVI.")
        
        # cluster and Category columns are now handled in load_data
        
        fig_scatter = px.scatter(
            clusters.reset_index(),
            x="xi", y="sigma", 
            color="cluster_label",
            size="RVI",
            hover_name="Ticker",
            hover_data=["Category", "dxi_dt", "dsigma_dt"],
            color_discrete_map={"Low Risk": COLORS[0], "Medium Risk": COLORS[1], "High Risk": COLORS[2]},
            labels={"xi": "Shape Parameter (ξ)", "sigma": "Scale Parameter (σ)", "cluster_label": "Risk Level"}
        )
        fig_scatter.update_traces(marker=dict(line=dict(width=1, color='white')))
        fig_scatter.update_layout(template="plotly_dark", height=600, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with tab2:
        st.subheader("Cluster Transition Probabilities")
        
        labels_from = [f"{l} (t)" for l in trans_matrix.index]
        labels_to   = [f"{l} (t+1)" for l in trans_matrix.columns]
        all_labels  = labels_from + labels_to

        n = len(trans_matrix)
        source, target, value = [], [], []

        for i in range(n):
            for j in range(n):
                v = trans_matrix.iloc[i, j]
                if v > 0.001:
                    source.append(i)
                    target.append(n + j)
                    value.append(round(v * 100, 1))

        # Colors for the Sankey flow
        colors_node = [COLORS[0], COLORS[1], COLORS[2]] * 2
        colors_link = []
        for s in source:
            c = colors_node[s % 3]
            # convert hex to rgba
            r = int(c[1:3], 16)
            g = int(c[3:5], 16)
            b = int(c[5:7], 16)
            colors_link.append(f"rgba({r},{g},{b},0.4)")
            
        fig_sankey = go.Figure(go.Sankey(
            node=dict(
                pad=20, thickness=25, 
                label=all_labels,
                color=colors_node[:len(all_labels)]
            ),
            link=dict(
                source=source, target=target, value=value,
                color=colors_link
            )
        ))
        
        fig_sankey.update_layout(template="plotly_dark", height=600, font=dict(color="#ddd"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sankey, use_container_width=True)

