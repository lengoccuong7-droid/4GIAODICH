import numpy as np, pandas as pd
from modules.plan_backtest import backtest_plan
from modules.beginner_summary import build_beginner_summary

def _frame(n=260, seed=1):
    r = np.random.default_rng(seed); c = 20000 * np.exp(np.cumsum(r.normal(0.0005, 0.015, n)))
    o = c * (1 + r.normal(0, .004, n)); h = np.maximum(o, c) * 1.008; l = np.minimum(o, c) * .992
    return pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=n), "symbol": "TST", "open": o, "high": h, "low": l, "close": c, "volume": r.integers(8e5, 2e6, n)})

def _benchmark(n=260):
    c = np.linspace(1000, 1300, n)
    return pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=n), "symbol": "VNINDEX",
        "open": c-1, "high": c+5, "low": c-5, "close": c, "volume": np.full(n, 1_000_000_000)})

def test_backtest_t2_and_costs():
    r = backtest_plan(_frame(), benchmark=_benchmark())
    assert "error" not in r
    for t in r["trades"]:
        assert (pd.Timestamp(t["exit_date"]) - pd.Timestamp(t["entry_date"])).days >= 2  # T+2
        assert t["stop"] < t["entry"]

def test_backtest_short_data():
    assert "error" in backtest_plan(_frame(80), benchmark=_benchmark(80))

def test_backtest_requires_real_market_benchmark():
    assert "VN-Index" in backtest_plan(_frame())['error']

def test_summary_handles_insufficient():
    s = build_beginner_summary({"status": "INSUFFICIENT_DATA", "reasons": ["x"]})
    assert s["level"] == "stop"

def test_levels_and_holder():
    from modules.levels import add_ma_series, watch_levels_text, holder_guide, volume_narrative
    f = _frame(120); x = add_ma_series(f)
    assert abs(x.MA10.iloc[-1] - f.close.tail(10).mean()) < 1e-6 and abs(x.VMA20.iloc[-1] - f.volume.tail(20).mean()) < 1e-6
    assert len(watch_levels_text(f)) >= 3 and volume_narrative(f)["text"]
    c = float(f.close.iloc[-1]); g = holder_guide(f, c * 0.95, 1000, None, 20_000_000)
    assert g["stop_reference"] < c and g["status"]
