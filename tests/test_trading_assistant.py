import pandas as pd
from modules.trading_assistant import build_trading_assistant

def sample_frame():
    dates = pd.date_range("2025-01-01", periods=90, freq="B")
    close = [100 + (i % 12) * 0.4 - (i // 25) * 0.8 for i in range(90)]
    return pd.DataFrame({
        "date": dates, "open": [v - 0.2 for v in close],
        "high": [v + 1.0 for v in close], "low": [v - 1.0 for v in close],
        "close": close, "volume": [100000 + (i % 5) * 1000 for i in range(90)]
    })

def test_assistant_returns_support_resistance_and_two_scenarios():
    result = build_trading_assistant(sample_frame())
    assert result["ready"] is True
    assert result["support"] is not None
    assert result["resistance"] is not None
    assert "entry_low" in result["tplus"]
    assert "trigger" in result["breakout"]
    assert result["breakout"]["volume_required"] > 0

def test_assistant_rejects_insufficient_data():
    result = build_trading_assistant(sample_frame().head(15))
    assert result["ready"] is False
