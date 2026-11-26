"""Plotly charts: price with MA10/MA20 and volume with volume-MA10/MA20."""
from __future__ import annotations
from .levels import add_ma_series

def price_volume_figure(frame, symbol="", last_n=120):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    x = add_ma_series(frame).tail(last_n)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.65, 0.35], vertical_spacing=0.04)
    fig.add_trace(go.Candlestick(x=x.date, open=x.open, high=x.high, low=x.low, close=x.close, name="Giá",
                                 increasing_line_color="#16a34a", decreasing_line_color="#dc2626"), 1, 1)
    fig.add_trace(go.Scatter(x=x.date, y=x.MA10, name="MA10", line=dict(color="#2563eb", width=1.6)), 1, 1)
    fig.add_trace(go.Scatter(x=x.date, y=x.MA20, name="MA20", line=dict(color="#f59e0b", width=1.6)), 1, 1)
    colors = ["#16a34a" if c >= o else "#dc2626" for o, c in zip(x.open, x.close)]
    fig.add_trace(go.Bar(x=x.date, y=x.volume, name="Khối lượng", marker_color=colors, opacity=.55), 2, 1)
    fig.add_trace(go.Scatter(x=x.date, y=x.VMA10, name="KL MA10", line=dict(color="#2563eb", width=1.6)), 2, 1)
    fig.add_trace(go.Scatter(x=x.date, y=x.VMA20, name="KL MA20", line=dict(color="#f59e0b", width=1.6)), 2, 1)
    fig.update_layout(title=f"{symbol} – Giá & khối lượng (MA10/MA20)", height=560, margin=dict(l=8, r=8, t=40, b=8),
                      template="plotly_dark", paper_bgcolor="#0B1220", plot_bgcolor="#0F1928",
                      font=dict(color="#E8EEF7"), xaxis_rangeslider_visible=False,
                      legend=dict(orientation="h", y=-0.08))
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,.12)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,.12)")
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig
