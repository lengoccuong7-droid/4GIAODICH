import pandas as pd
from modules.data_quality import assess_data_quality
from modules.market_flow_trap import _classify_follow_through
from modules.shared_analysis import _frame_fingerprint


def _ohlcv(n=40):
    close = [100.0 + i for i in range(n)]
    return pd.DataFrame({
        "date": pd.bdate_range("2026-01-01", periods=n),
        "symbol": "AAA", "open": [v - 0.2 for v in close],
        "high": [v + 0.5 for v in close], "low": [v - 0.5 for v in close],
        "close": close, "volume": [10000.0] * n,
    })


def test_quality_flags_non_finite_and_future_rows():
    df = _ohlcv()
    df.loc[0, "volume"] = float("inf")
    df.loc[1, "date"] = pd.Timestamp.now().normalize() + pd.Timedelta(days=2)
    out = assess_data_quality(df)
    assert out["status"] == "ERROR"
    assert out["metrics"]["invalid_rows"] >= 1
    assert out["metrics"]["future_dates"] == 1


def test_quality_does_not_treat_zero_volume_as_clean():
    df = _ohlcv()
    df.loc[df.index[-1], "volume"] = 0
    out = assess_data_quality(df)
    assert out["status"] == "WARNING"
    assert out["metrics"]["zero_volume"] == 1


def test_conflicting_follow_through_is_not_confirmed():
    future = pd.DataFrame({"close": [98.0, 103.0, 99.0]})
    # Bull-trap event low=99, high=102, resistance=100.
    out = _classify_follow_through(future.assign(high=[99, 104, 100], low=[97, 98, 98]),
                                   -1, 100.0, 102.0, 99.0, "BULL_TRAP")
    assert out["status"] == "CONFLICT"

def test_fingerprint_changes_when_old_history_changes():
    df = _ohlcv()
    before = _frame_fingerprint(df)
    df.loc[0, "close"] += 0.25
    after = _frame_fingerprint(df)
    assert before != after
