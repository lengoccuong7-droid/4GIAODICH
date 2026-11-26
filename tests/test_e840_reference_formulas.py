"""Independent, hand-computed fixtures for core formulas.

These tests validate selected implementation conventions; they do not certify
all formulas or exchange-specific trading assumptions.
"""
import numpy as np
import pandas as pd
import pytest

from modules.indicators import add_indicators
from modules.risk_manager import calculate_position_size


def _frame(n=80):
    close = np.array([100 + i * 0.7 + (i % 5) * 0.2 for i in range(n)], dtype=float)
    high = close + 2.0
    low = close - 1.0
    open_ = close - 0.3
    volume = np.array([1000 + i * 10 for i in range(n)], dtype=float)
    return pd.DataFrame({"date": pd.bdate_range("2025-01-02", periods=n),
                         "open": open_, "high": high, "low": low,
                         "close": close, "volume": volume})


def test_sma_bollinger_and_clv_match_direct_reference_calculation():
    raw = _frame()
    out = add_indicators(raw)
    closes = raw.close.to_numpy()
    window = closes[-20:]
    assert out.SMA20.iloc[-1] == pytest.approx(window.mean())
    assert out.BB_UPPER.iloc[-1] == pytest.approx(window.mean() + 2 * window.std(ddof=0))
    h, l, c = raw.high.iloc[-1], raw.low.iloc[-1], raw.close.iloc[-1]
    expected_clv = ((c - l) - (h - c)) / (h - l)
    assert out.CLV.iloc[-1] == pytest.approx(expected_clv)


def test_rvol_uses_only_previous_twenty_completed_sessions():
    raw = _frame()
    out = add_indicators(raw)
    expected = raw.volume.iloc[-21:-1].mean()
    assert out.VOL_MA20.iloc[-1] == pytest.approx(expected)
    assert out.REL_VOLUME20.iloc[-1] == pytest.approx(raw.volume.iloc[-1] / expected)


def test_obv_matches_direct_signed_volume_sum():
    raw = _frame()
    out = add_indicators(raw)
    delta = raw.close.diff().fillna(0).to_numpy()
    expected = np.cumsum(np.sign(delta) * raw.volume.to_numpy())
    np.testing.assert_allclose(out.OBV.to_numpy(), expected)


def test_position_size_matches_direct_risk_budget_and_lot_rounding():
    result = calculate_position_size(100_000_000, 20_000, 19_000,
                                     risk_pct=1, max_allocation_pct=20,
                                     lot_size=100, fee_pct=0, slippage_pct=0, tax_pct=0)
    # Risk budget = 1,000,000; loss/share = 1,000; max 1,000 shares.
    assert result["risk_budget"] == pytest.approx(1_000_000)
    assert result["max_by_risk"] == 1_000
    assert result["quantity"] == 1_000
    assert result["risk_amount"] == pytest.approx(1_000_000)


def test_flat_high_low_range_produces_nan_stochastic_not_infinite_values():
    raw = _frame()
    raw["close"] = 100.0
    raw["open"] = 100.0
    raw["high"] = 100.0
    raw["low"] = 100.0
    out = add_indicators(raw)
    assert pd.isna(out.STOCH_K.iloc[-1])
    assert not np.isinf(out.select_dtypes(include=["number"]).to_numpy()).any()
