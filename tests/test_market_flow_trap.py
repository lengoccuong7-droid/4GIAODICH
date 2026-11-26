import numpy as np
import pandas as pd
from modules.market_flow_trap import analyze_flow_and_traps


def base_frame(n=80):
    close = np.linspace(100, 110, n)
    return pd.DataFrame({
        "date": pd.bdate_range("2026-01-01", periods=n),
        "open": close - 0.2, "high": close + 0.5, "low": close - 0.5,
        "close": close, "volume": np.full(n, 10000.0),
    })


def test_insufficient_data_is_explicit():
    assert analyze_flow_and_traps(base_frame(20))["status"] == "INSUFFICIENT_DATA"


def test_latest_bull_trap_is_pending_until_follow_through_exists():
    df = base_frame()
    prior_high = df.high.iloc[-21:-1].max()
    i = df.index[-1]
    df.loc[i, ["open", "high", "low", "close", "volume"]] = [
        prior_high + 1, prior_high + 2, prior_high - 1, prior_high - .5, 30000
    ]
    result = analyze_flow_and_traps(df)
    assert result["metrics"]["bull_trap_events_5"]
    assert result["metrics"]["bull_trap_events_5"][-1]["status"] == "PENDING"
    assert result["trap_risk"] == "MODERATE"


def test_bull_trap_confirmed_by_two_following_closes_below_level():
    df = base_frame()
    i = len(df) - 4
    prior_high = df.high.iloc[i-20:i].max()
    df.loc[i, ["open", "high", "low", "close", "volume"]] = [
        prior_high + .3, prior_high + 2, prior_high - 1, prior_high - .2, 30000
    ]
    for j in (i+1, i+2):
        df.loc[j, ["open", "high", "low", "close", "volume"]] = [
            prior_high - .3, prior_high + .1, prior_high - 1.2, prior_high - .7, 18000
        ]
    result = analyze_flow_and_traps(df)
    events = result["metrics"]["bull_trap_events_5"]
    assert any(e["status"] == "CONFIRMED" for e in events)
    assert result["trap_risk"] == "HIGH"


def test_bull_trap_invalidated_if_price_reclaims_event_high():
    df = base_frame()
    i = len(df) - 4
    prior_high = df.high.iloc[i-20:i].max()
    df.loc[i, ["open", "high", "low", "close", "volume"]] = [
        prior_high + .3, prior_high + 2, prior_high - 1, prior_high - .2, 30000
    ]
    df.loc[i+1, ["open", "high", "low", "close", "volume"]] = [
        prior_high + 1, prior_high + 3, prior_high, prior_high + 2.5, 18000
    ]
    result = analyze_flow_and_traps(df)
    events = result["metrics"]["bull_trap_events_5"]
    assert any(e["status"] == "INVALIDATED" for e in events)


def test_breakout_is_not_confirmed_on_event_day_alone():
    df = base_frame()
    i = len(df) - 1
    prior_high = df.high.iloc[i-20:i].max()
    df.loc[i, ["open", "high", "low", "close", "volume"]] = [
        prior_high, prior_high + 2, prior_high - .2, prior_high + 1, 25000
    ]
    result = analyze_flow_and_traps(df)
    events = result["metrics"]["breakout_confirmations"]
    assert events and events[-1]["status"] == "PENDING"


def test_output_never_claims_known_participant_identity():
    result = analyze_flow_and_traps(base_frame())
    assert any("không xác định" in x.lower() for x in result["cautions"])
    assert "flow_bias" in result



def test_bear_trap_confirmed_by_two_following_closes_above_level():
    df = base_frame()
    i = len(df) - 4
    prior_low = df.low.iloc[i-20:i].min()
    df.loc[i, ["open", "high", "low", "close", "volume"]] = [
        prior_low + .2, prior_low + 1, prior_low - 2, prior_low + .3, 30000
    ]
    for j in (i+1, i+2):
        df.loc[j, ["open", "high", "low", "close", "volume"]] = [
            prior_low + .3, prior_low + 1.2, prior_low - .1, prior_low + .8, 18000
        ]
    result = analyze_flow_and_traps(df)
    events = result["metrics"]["bear_trap_events_5"]
    assert any(e["status"] == "CONFIRMED" for e in events)
