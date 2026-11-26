import numpy as np
import pandas as pd
from modules.unified_analytics import build_unified_snapshot


def test_e83_snapshot_carries_portfolio_and_action_plan():
    rng = np.random.default_rng(7)
    n = 220
    dates = pd.bdate_range("2025-01-01", periods=n)
    close = 12000 * np.exp(np.cumsum(rng.normal(0.001, 0.005, n)))
    frame = pd.DataFrame({"date": dates, "symbol": "AAA", "open": close * .998,
        "high": close * 1.01, "low": close * .99, "close": close,
        "volume": 500000 + np.arange(n) * 500})
    portfolio = {"equity_vnd": 100_000_000, "positions": [
        {"symbol": "BBB", "market_value": 15_000_000, "risk_value": 500_000}]}
    snapshot = build_unified_snapshot("AAA", frame, portfolio=portfolio)
    assert snapshot["schema_version"] == "8.4.0"
    assert snapshot["action_plan"]["action"] == snapshot["decision"]["final_action"]
    assert snapshot["portfolio_risk"]["metrics"]["existing_exposure_vnd"] == 15_000_000
    assert snapshot["calculation_contract"]["processing_order"] == [
        "DATA_QUALITY", "ENRICH_ONCE", "UNIFIED_SNAPSHOT", "ANALYSIS_MODULES"]
