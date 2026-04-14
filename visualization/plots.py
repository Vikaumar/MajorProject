"""
Visualization Module
---------------------
Generates all charts and dashboards for the Temporal EVT-Clustering
research output.

Produces:
  1. Rolling EVT parameter line plots
  2. Velocity heatmap (seaborn)
  3. Risk Velocity Index (RVI) dashboard (Plotly)
  4. Cluster scatter in (ξ, σ) space with velocity arrows
  5. Transition Sankey diagram (Plotly)
  6. Fossil-fuel vs ESG comparative bar chart
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# ──────────────────────────────────────────────────────────────
# Style defaults
# ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor":   "#0e1117",
    "axes.edgecolor":   "#333",
    "axes.labelcolor":  "#eee",
    "text.color":       "#eee",
    "xtick.color":      "#aaa",
    "ytick.color":      "#aaa",
    "grid.color":       "#222",
    "font.family":      "sans-serif",
    "font.size":        11,
})

PALETTE = ["#00d2ff", "#ff6b6b", "#feca57", "#48dbfb",
           "#ff9ff3", "#54a0ff", "#5f27cd", "#01a3a4"]


# ──────────────────────────────────────────────────────────────
# 1. Rolling EVT Parameters
# ──────────────────────────────────────────────────────────────
def plot_rolling_params(all_params: dict[str, pd.DataFrame],
                        save: bool = True) -> None:
    """Line plots of ξ(t) and σ(t) for selected assets."""
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

    for i, ticker in enumerate(all_params):
        df = all_params[ticker]
        color = PALETTE[i % len(PALETTE)]
        axes[0].plot(df.index, df["xi"],    label=ticker, color=color, alpha=0.8, linewidth=1.2)
        axes[1].plot(df.index, df["sigma"], label=ticker, color=color, alpha=0.8, linewidth=1.2)

    axes[0].set_title("Rolling GPD Shape Parameter  ξ(t)", fontsize=14, fontweight="bold")
    axes[0].set_ylabel("ξ (shape)")
    axes[0].legend(ncol=4, fontsize=8, loc="upper left")
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title("Rolling GPD Scale Parameter  σ(t)", fontsize=14, fontweight="bold")
    axes[1].set_ylabel("σ (scale)")
    axes[1].set_xlabel("Date")
    axes[1].legend(ncol=4, fontsize=8, loc="upper left")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    if save:
        path = os.path.join(config.FIGURES_DIR, "rolling_evt_params.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"[viz] Saved → {path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────
# 2. Velocity Heatmap
# ──────────────────────────────────────────────────────────────
def plot_velocity_heatmap(all_derivs: dict[str, pd.DataFrame],
                          param: str = "dxi_dt",
                          save: bool = True) -> None:
    """Seaborn heatmap of dξ/dt (or dσ/dt) across assets × time."""

    # Build a matrix: rows = tickers, cols = dates (sampled monthly)
    frames = {}
    for ticker, df in all_derivs.items():
        series = df[param].copy()
        # Resample to month-end for readability
        series.index = pd.to_datetime(series.index)
        monthly = series.resample("ME").mean()
        frames[ticker] = monthly

    matrix = pd.DataFrame(frames).T
    matrix.columns = [d.strftime("%Y-%m") for d in matrix.columns]

    fig, ax = plt.subplots(figsize=(20, 8))
    sns.heatmap(matrix.astype(float), cmap="RdYlGn_r", center=0,
                linewidths=0.3, linecolor="#1a1a2e", ax=ax,
                cbar_kws={"label": param})
    title_map = {"dxi_dt": "dξ/dt", "dsigma_dt": "dσ/dt"}
    ax.set_title(f"Velocity Heatmap — {title_map.get(param, param)}  (monthly avg)",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Asset")
    ax.set_xlabel("Month")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=9)
    plt.tight_layout()

    if save:
        path = os.path.join(config.FIGURES_DIR, f"velocity_heatmap_{param}.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"[viz] Saved → {path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────
# 3. RVI Dashboard (Plotly interactive)
# ──────────────────────────────────────────────────────────────
def plot_rvi_dashboard(all_derivs: dict[str, pd.DataFrame],
                       save: bool = True) -> None:
    """Multi-panel interactive Plotly dashboard of RVI per asset."""

    tickers = list(all_derivs.keys())
    n = len(tickers)
    rows = (n + 1) // 2

    fig = make_subplots(rows=rows, cols=2,
                        subplot_titles=tickers,
                        vertical_spacing=0.04,
                        horizontal_spacing=0.06)

    for i, ticker in enumerate(tickers):
        r, c = divmod(i, 2)
        df = all_derivs[ticker]
        dates = df.index
        rvi = df["RVI"].values

        color = "#ff6b6b" if config.TICKER_CATEGORY.get(ticker) == "Fossil Fuel" else "#00d2ff"
        cat = config.TICKER_CATEGORY.get(ticker, "")

        fig.add_trace(go.Scatter(
            x=dates, y=rvi, mode="lines",
            name=f"{ticker} ({cat})",
            line=dict(color=color, width=1.2),
            showlegend=(i < 6),
        ), row=r+1, col=c+1)

        # Alert band — 90th percentile
        p90 = np.nanpercentile(rvi, 90)
        fig.add_hline(y=p90, line_dash="dash", line_color="#feca57",
                      opacity=0.5, row=r+1, col=c+1)

    fig.update_layout(
        title=dict(text="Risk Velocity Index (RVI) Dashboard",
                   font=dict(size=20, color="#eee")),
        height=300 * rows,
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="#ddd"),
        showlegend=True,
        legend=dict(x=1.02, y=1, font=dict(size=9)),
    )

    if save:
        path = os.path.join(config.FIGURES_DIR, "rvi_dashboard.html")
        fig.write_html(path)
        print(f"[viz] Saved → {path}")

        # Also save a static image
        try:
            fig.write_image(os.path.join(config.FIGURES_DIR, "rvi_dashboard.png"),
                            width=1800, height=300*rows, scale=2)
        except Exception:
            pass  # kaleido may not be installed


# ──────────────────────────────────────────────────────────────
# 4. Cluster Scatter with Velocity Arrows
# ──────────────────────────────────────────────────────────────
def plot_cluster_scatter(clustered: pd.DataFrame,
                         save: bool = True) -> None:
    """2D scatter in (ξ, σ) space, colour-coded by cluster, with velocity arrows."""

    fig, ax = plt.subplots(figsize=(14, 10))

    cluster_colors = {0: "#00d2ff", 1: "#feca57", 2: "#ff6b6b"}

    for _, row in clustered.iterrows():
        cl = int(row["cluster"]) if not pd.isna(row["cluster"]) else 0
        color = cluster_colors.get(cl, "#aaa")
        label = config.CLUSTER_LABELS.get(cl, f"Cluster {cl}")
        cat = config.TICKER_CATEGORY.get(row.name, "")

        # Scatter point
        ax.scatter(row["xi"], row["sigma"], color=color, s=120,
                   edgecolors="white", linewidth=0.8, zorder=5)

        # Velocity arrow
        dx = row.get("dxi_dt", 0)
        ds = row.get("dsigma_dt", 0)
        if not (np.isnan(dx) or np.isnan(ds)):
            scale = 15    # visual scale factor
            ax.annotate("", xy=(row["xi"] + dx*scale, row["sigma"] + ds*scale),
                        xytext=(row["xi"], row["sigma"]),
                        arrowprops=dict(arrowstyle="->", color=color,
                                        lw=1.8, alpha=0.7))

        # Label
        ax.annotate(row.name, (row["xi"], row["sigma"]),
                    textcoords="offset points", xytext=(6, 6),
                    fontsize=8, color="#ddd", fontweight="bold")

    # Legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=cluster_colors[i], label=config.CLUSTER_LABELS[i])
               for i in sorted(cluster_colors)]
    ax.legend(handles=handles, loc="upper left", fontsize=10)

    ax.set_xlabel("Shape Parameter ξ", fontsize=12)
    ax.set_ylabel("Scale Parameter σ", fontsize=12)
    ax.set_title("EVT Cluster Scatter with Velocity Arrows",
                 fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    if save:
        path = os.path.join(config.FIGURES_DIR, "cluster_scatter.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"[viz] Saved → {path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────
# 5. Transition Sankey Diagram
# ──────────────────────────────────────────────────────────────
def plot_transition_sankey(transition_matrix: pd.DataFrame,
                           save: bool = True) -> None:
    """Plotly Sankey diagram showing cluster migration flows."""

    labels_from = [f"{l} (t)" for l in transition_matrix.index]
    labels_to   = [f"{l} (t+1)" for l in transition_matrix.columns]
    all_labels  = labels_from + labels_to

    n = len(transition_matrix)
    source, target, value = [], [], []

    for i in range(n):
        for j in range(n):
            v = transition_matrix.iloc[i, j]
            if v > 0.001:
                source.append(i)
                target.append(n + j)
                value.append(round(v * 100, 1))

    colors_node = ["#00d2ff", "#feca57", "#ff6b6b"] * 2
    colors_link = []
    for s in source:
        c = colors_node[s % len(colors_node)]
        # Convert hex to rgba for Plotly Sankey compatibility
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        colors_link.append(f"rgba({r},{g},{b},0.4)")

    fig = go.Figure(go.Sankey(
        node=dict(pad=20, thickness=25, label=all_labels,
                  color=colors_node[:len(all_labels)]),
        link=dict(source=source, target=target, value=value,
                  color=colors_link),
    ))

    fig.update_layout(
        title=dict(text="Cluster Transition Probabilities (Sankey)",
                   font=dict(size=18, color="#eee")),
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        font=dict(color="#ddd"),
        height=500,
    )

    if save:
        path = os.path.join(config.FIGURES_DIR, "transition_sankey.html")
        fig.write_html(path)
        print(f"[viz] Saved → {path}")


# ──────────────────────────────────────────────────────────────
# 6. Fossil-Fuel vs ESG Comparative Bar Chart
# ──────────────────────────────────────────────────────────────
def plot_comparative_bar(warning_alerts: pd.DataFrame,
                         save: bool = True) -> None:
    """Bar chart comparing average RVI between fossil-fuel and ESG groups."""

    fig, ax = plt.subplots(figsize=(14, 7))

    grouped = warning_alerts.groupby("category")["recent_RVI"].mean().sort_values(ascending=False)

    colors_map = {"Fossil Fuel": "#ff6b6b", "ESG / Clean Energy": "#00d2ff",
                  "Benchmark": "#feca57"}
    colors     = [colors_map.get(c, "#aaa") for c in grouped.index]

    bars = ax.bar(grouped.index, grouped.values, color=colors,
                  edgecolor="white", linewidth=0.8, width=0.5)

    # Individual asset RVI as scatter overlay
    for _, row in warning_alerts.iterrows():
        c = colors_map.get(row["category"], "#aaa")
        cat_x = list(grouped.index).index(row["category"]) if row["category"] in grouped.index else 0
        ax.scatter(cat_x, row["recent_RVI"], color=c, s=60,
                   edgecolors="white", linewidth=0.5, zorder=5, alpha=0.8)
        ax.annotate(row.name, (cat_x, row["recent_RVI"]),
                    textcoords="offset points", xytext=(8, 0),
                    fontsize=7, color="#ccc")

    ax.set_title("Average Risk Velocity Index (RVI) by Category",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Mean RVI (last quarter)")
    ax.grid(True, axis="y", alpha=0.2)

    plt.tight_layout()
    if save:
        path = os.path.join(config.FIGURES_DIR, "comparative_rvi_bar.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"[viz] Saved → {path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────
# 7. Asset-level RVI time series (individual PNGs)
# ──────────────────────────────────────────────────────────────
def plot_individual_rvi(all_derivs: dict[str, pd.DataFrame],
                        save: bool = True) -> None:
    """Individual RVI + ξ + σ panel plots per ticker (top 6 by RVI)."""

    # Rank by mean RVI
    mean_rvi = {t: df["RVI"].mean() for t, df in all_derivs.items()}
    top = sorted(mean_rvi, key=mean_rvi.get, reverse=True)[:6]

    fig, axes = plt.subplots(3, 2, figsize=(18, 14))
    axes = axes.flatten()

    for i, ticker in enumerate(top):
        ax = axes[i]
        df = all_derivs[ticker]
        cat = config.TICKER_CATEGORY.get(ticker, "")
        color = "#ff6b6b" if cat == "Fossil Fuel" else "#00d2ff"

        ax.fill_between(df.index, 0, df["RVI"], alpha=0.3, color=color)
        ax.plot(df.index, df["RVI"], color=color, linewidth=1.2)

        p90 = np.nanpercentile(df["RVI"].dropna(), 90)
        ax.axhline(p90, color="#feca57", linestyle="--", alpha=0.6, label="90th pctl")

        ax.set_title(f"{ticker}  ({cat})", fontsize=11, fontweight="bold")
        ax.set_ylabel("RVI")
        ax.grid(True, alpha=0.2)
        ax.legend(fontsize=8)

    plt.suptitle("Top 6 Assets by Risk Velocity Index",
                 fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()

    if save:
        path = os.path.join(config.FIGURES_DIR, "top_rvi_assets.png")
        fig.savefig(path, dpi=200, bbox_inches="tight")
        print(f"[viz] Saved → {path}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────
# Master function — generate all plots
# ──────────────────────────────────────────────────────────────
def generate_all_plots(all_params, all_derivs, clustered,
                       transition_matrix, warning_alerts):
    """Convenience function to generate every visualisation."""
    print("\n" + "=" * 60)
    print("  GENERATING VISUALIZATIONS")
    print("=" * 60)

    plot_rolling_params(all_params)
    plot_velocity_heatmap(all_derivs, param="dxi_dt")
    plot_velocity_heatmap(all_derivs, param="dsigma_dt")
    plot_rvi_dashboard(all_derivs)
    plot_cluster_scatter(clustered)
    plot_transition_sankey(transition_matrix)
    plot_comparative_bar(warning_alerts)
    plot_individual_rvi(all_derivs)

    print("\n✅  All visualizations saved to:", config.FIGURES_DIR)
