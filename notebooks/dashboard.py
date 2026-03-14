import pandas as pd
import numpy as np
import sys
sys.path.append("../src")

from strategy import calculate_combined_score, select_portfolio
from backtest import run_backtest, run_benchmark, calculate_metrics
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# Load data and run strategy
# ============================================================
print("Loading data...")
prices = pd.read_csv("../data/prices.csv", index_col=0, parse_dates=True)

print("Calculating scores...")
scores  = calculate_combined_score(prices)
weights = select_portfolio(scores, top_n=50)

# Remove warmup period
first_active   = weights[weights.sum(axis=1) > 0].index[0]
prices_active  = prices.loc[first_active:]
weights_active = weights.loc[first_active:]

# SPY
spy            = yf.download("SPY", start="2018-01-01", end="2024-01-01", auto_adjust=True)["Close"]
spy_active     = spy.loc[first_active:]
spy_returns    = spy_active.pct_change().squeeze()
spy_cumulative = (1 + spy_returns).cumprod()

# Strategy
port_returns,  port_cumulative  = run_backtest(prices_active, weights_active)
bench_returns, bench_cumulative = run_benchmark(prices_active)

# Metrics
port_metrics = calculate_metrics(port_returns, "Multi-Factor Strategy")
spy_metrics  = calculate_metrics(spy_returns,  "SPY")

# Drawdown
def get_drawdown(returns):
    cumulative  = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    return (cumulative - rolling_max) / rolling_max

port_dd = get_drawdown(port_returns)
spy_dd  = get_drawdown(spy_returns)

# ============================================================
# Build Dashboard
# ============================================================
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Cumulative Returns",
        "Performance Metrics",
        "Drawdown",
        "Monthly Returns Heatmap",
        "Rolling Sharpe Ratio (6 months)",
        "Top 10 Stocks — Last Selection"
    ),
    specs=[
        [{"type": "xy"},     {"type": "table"}],
        [{"type": "xy"},     {"type": "xy"}],
        [{"type": "xy"},     {"type": "xy"}]
    ],
    row_heights=[0.35, 0.35, 0.30],
    vertical_spacing=0.12,
    horizontal_spacing=0.10
)

# ── Plot 1: Cumulative Returns ──────────────────────────────
fig.add_trace(go.Scatter(
    x=port_cumulative.index, y=port_cumulative.values - 1,
    name="Multi-Factor Strategy", line=dict(color="#2196F3", width=2)
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=spy_cumulative.index, y=spy_cumulative.values - 1,
    name="SPY", line=dict(color="#4CAF50", width=2, dash="dash")
), row=1, col=1)

fig.add_vrect(
    x0="2020-02-20", x1="2020-03-23",
    fillcolor="red", opacity=0.1, line_width=0,
    annotation_text="COVID", annotation_position="top left",
    row=1, col=1
)

# ── Plot 2: Metrics Table ───────────────────────────────────
metrics_labels = ["Total Return", "Annual Return", "Volatility", "Sharpe Ratio", "Max Drawdown"]
port_values = [
    f"{port_metrics['total_return']:.2%}",
    f"{port_metrics['annual_return']:.2%}",
    f"{port_metrics['annual_vol']:.2%}",
    f"{port_metrics['sharpe']:.2f}",
    f"{port_metrics['max_drawdown']:.2%}"
]
spy_values = [
    f"{spy_metrics['total_return']:.2%}",
    f"{spy_metrics['annual_return']:.2%}",
    f"{spy_metrics['annual_vol']:.2%}",
    f"{spy_metrics['sharpe']:.2f}",
    f"{spy_metrics['max_drawdown']:.2%}"
]

fig.add_trace(go.Table(
    header=dict(
        values=["Metric", "Multi-Factor Strategy", "SPY"],
        fill_color="#2196F3",
        font=dict(color="white", size=12),
        align="center"
    ),
    cells=dict(
        values=[metrics_labels, port_values, spy_values],
        fill_color=[
            ["#f5f5f5"] * 5,
            ["#C8E6C9", "#C8E6C9", "#f5f5f5", "#C8E6C9", "#f5f5f5"],
            ["#f5f5f5", "#f5f5f5", "#C8E6C9", "#f5f5f5", "#C8E6C9"]
        ],
        align="center",
        font=dict(size=12)
    )
), row=1, col=2)

# ── Plot 3: Drawdown ────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=port_dd.index, y=port_dd.values,
    name="Strategy Drawdown", fill="tozeroy",
    line=dict(color="#2196F3"), fillcolor="rgba(33,150,243,0.3)"
), row=2, col=1)

fig.add_trace(go.Scatter(
    x=spy_dd.index, y=spy_dd.values,
    name="SPY Drawdown", fill="tozeroy",
    line=dict(color="#4CAF50"), fillcolor="rgba(76,175,80,0.3)"
), row=2, col=1)

# ── Plot 4: Monthly Returns Heatmap ────────────────────────
monthly_returns = port_returns.resample("ME").apply(lambda x: (1 + x).prod() - 1)
monthly_df      = monthly_returns.to_frame("return")
monthly_df["year"]  = monthly_df.index.year
monthly_df["month"] = monthly_df.index.month

pivot = monthly_df.pivot(index="year", columns="month", values="return")
pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig.add_trace(go.Heatmap(
    z=pivot.values * 100,
    x=pivot.columns.tolist(),
    y=pivot.index.tolist(),
    colorscale="RdYlGn",
    zmid=0,
    text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in pivot.values * 100],
    texttemplate="%{text}",
    showscale=True,
    colorbar=dict(title="%")
), row=2, col=2)

# ── Plot 5: Rolling Sharpe ──────────────────────────────────
rolling_sharpe = port_returns.rolling(126).apply(
    lambda x: (x.mean() / x.std()) * np.sqrt(252) if x.std() > 0 else 0
)

fig.add_trace(go.Scatter(
    x=rolling_sharpe.index, y=rolling_sharpe.values,
    name="Rolling Sharpe", line=dict(color="#9C27B0", width=1.5)
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=rolling_sharpe.index,
    y=[1.0] * len(rolling_sharpe),
    name="Sharpe = 1", line=dict(color="green", dash="dash", width=1),
    showlegend=False
), row=3, col=1)

fig.add_trace(go.Scatter(
    x=rolling_sharpe.index,
    y=[0.0] * len(rolling_sharpe),
    name="Sharpe = 0", line=dict(color="red", dash="dash", width=1),
    showlegend=False
), row=3, col=1)
# ── Plot 6: Top 10 Stocks ───────────────────────────────────
last_weights  = weights.iloc[-1]
top10         = last_weights[last_weights > 0].head(10).sort_values()

fig.add_trace(go.Bar(
    x=top10.values * 100,
    y=top10.index.tolist(),
    orientation="h",
    marker_color="#2196F3",
    name="Weight %"
), row=3, col=2)

# ── Layout ──────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text="S&P 500 Alpha-Quest — Multi-Factor Strategy Dashboard",
        font=dict(size=20),
        x=0.5,
        y=0.98
    ),
    height=1200,
    showlegend=True,
    legend=dict(orientation="h", y=-0.05, x=0),
    template="plotly_white"
)

fig.update_yaxes(tickformat=".0%", row=1, col=1)
fig.update_yaxes(tickformat=".0%", row=2, col=1)

# Save
fig.write_html("../results/dashboard.html")
print("Dashboard saved to results/dashboard.html")
fig.show()