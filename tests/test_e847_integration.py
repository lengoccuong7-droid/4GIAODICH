import numpy as np
import pandas as pd
import pytest

from modules.position_state import build_position_state
from modules.risk_gate import apply_risk_gate
from modules.price_limit_engine import calculate_price_limits, validate_ohlc_within_limits
from modules.execution_simulator import simulate_limit_order
from modules.central_decision_engine import decide
from modules.unified_analytics import build_unified_snapshot


def _ohlcv(n=100):
    rng = np.random.default_rng(901)
    close = 20_000 * np.exp(np.cumsum(rng.normal(0.0002, 0.006, n)))
    op = close * 0.999
    return pd.DataFrame({"date": pd.bdate_range("2025-01-02", periods=n), "symbol": "TST",
        "open": op, "high": np.maximum(op, close) * 1.01,
        "low": np.minimum(op, close) * 0.99, "close": close,
        "volume": np.full(n, 1_000_000)})


def test_position_state_respects_explicit_settlement_dates():
    state = build_position_state([
        {"lot_id": "A", "quantity": 100, "settlement_date": "2026-11-20"},
        {"lot_id": "B", "quantity": 200, "settlement_date": "2026-11-24"},
    ], "2026-11-22", pending_sell=20)
    assert state["total_position"] == 300
    assert state["available_to_sell"] == 80
    assert state["pending_buy"] == 200
    assert state["status"] == "OK"


def test_position_state_unknown_settlement_is_not_available():
    state = build_position_state([{"quantity": 100}], "2026-11-22")
    assert state["status"] == "UNKNOWN"
    assert state["available_to_sell"] == 0


def test_risk_gate_never_promotes_wait_to_entry():
    result = apply_risk_gate("WAIT", portfolio_status="OK")
    assert result["final_action"] == "WAIT"


def test_risk_gate_blocks_entry_when_required_portfolio_unknown():
    result = apply_risk_gate("ENTER_LONG", sizing_status="OK", sizing_quantity=100,
        portfolio_status="UNKNOWN", require_portfolio_context=True)
    assert result["final_action"] == "WAIT"
    assert result["risk_gate"]["status"] == "VETO"


def test_central_engine_uses_shared_risk_gate_and_preserves_reduce():
    result = decide({"status": "EXIT_RULE_TRIGGERED", "position": {"mode": "MANAGE_EXISTING", "quantity": 100}},
                    module_results={"broken": {"module": "broken", "status": "ERROR"}})
    assert result["final_action"] == "REDUCE"
    assert result["engine"] == "CENTRAL-1.2"


def test_price_limit_rounding_and_ohlc_validation():
    limits = calculate_price_limits(10000, 7, tick_size=10)
    assert limits["upper_limit"] == 10700
    assert limits["lower_limit"] == 9300
    assert validate_ohlc_within_limits(10000, 10600, 9900, 10500, limits)["valid"]
    assert not validate_ohlc_within_limits(10000, 10800, 9900, 10500, limits)["valid"]


def test_execution_simulator_partial_fill_and_unfilled():
    partial = simulate_limit_order(side="BUY", quantity=1000, limit_price=100,
        open_price=99, high=101, low=98, volume=10000, participation_rate=0.05)
    assert partial["status"] == "PARTIALLY_FILLED"
    assert partial["filled_quantity"] == 500
    pending = simulate_limit_order(side="BUY", quantity=100, limit_price=100,
        open_price=105, high=106, low=102, volume=10000)
    assert pending["status"] == "PENDING"


def test_snapshot_includes_lot_state_without_assuming_settlement():
    frame = _ohlcv()
    snap = build_unified_snapshot("TST", frame, position={"mode": "MANAGE_EXISTING", "quantity": 100,
        "lots": [{"quantity": 100, "settlement_date": "2025-01-03"}]})
    assert snap["position_state"]["status"] == "OK"
    assert snap["position_state"]["available_to_sell"] == 100
    assert snap["action_plan"]["action"] == snap["decision"]["final_action"]


def test_invalid_lot_quantity_is_rejected():
    with pytest.raises(ValueError):
        build_position_state([{"quantity": 10.5, "settlement_date": "2026-11-20"}], "2026-11-22")


def test_backtest_uses_execution_capacity_and_records_partial_fill(monkeypatch):
    import modules.plan_backtest as bt
    n = 100
    dates = pd.bdate_range("2025-01-02", periods=n)
    close = np.full(n, 100.0)
    frame = pd.DataFrame({"date": dates, "symbol": "TST", "open": close,
        "high": close + 1, "low": close - 1, "close": close,
        "volume": np.full(n, 1000)})
    benchmark = frame.assign(symbol="VNINDEX")
    # One deterministic future trigger and target touch after the T+2 restriction.
    frame.loc[61, ["open", "high", "low", "close"]] = [100, 103, 99, 102]
    frame.loc[63, ["open", "high", "low", "close"]] = [102, 111, 101, 110]

    def fake_evaluate(*args, **kwargs):
        return ({"status": "TRADE_PLAN_READY", "sizing": {"status": "OK", "quantity": 1000,
                 "position_value": 100000},
                 "plan": {"reference_trigger": 100, "entry_zone_high": 102,
                          "invalidation": 95, "target_1": 110}}, {}, {})

    monkeypatch.setattr(bt, "evaluate_unified_decision", fake_evaluate)
    result = bt.backtest_plan(frame, benchmark=benchmark, warmup=60,
        test_start_index=60, test_end_index=70, max_hold=5,
        max_participation_rate=0.05)
    assert "error" not in result
    assert result["execution_model"] == "OHLCV_LIMIT_APPROXIMATION"
    assert result["trades"]
    assert result["trades"][0]["requested_quantity"] == 1000
    assert result["trades"][0]["filled_quantity"] == 50
    assert result["trades"][0]["fill_ratio"] == 0.05


def test_data_quality_error_blocks_entry_but_does_not_erase_reduce_intent():
    blocked = apply_risk_gate("ENTER_LONG", data_quality_status="ERROR",
        sizing_status="OK", sizing_quantity=100, portfolio_status="OK")
    reduce = apply_risk_gate("REDUCE", data_quality_status="ERROR")
    assert blocked["final_action"] == "NO_TRADE"
    assert reduce["final_action"] == "REDUCE"
    assert reduce["risk_gate"]["status"] == "WARNING"


def test_snapshot_fingerprint_is_invariant_to_input_row_order():
    frame = _ohlcv(100)
    first = build_unified_snapshot("TST", frame)
    shuffled = frame.sample(frac=1, random_state=99).reset_index(drop=True)
    second = build_unified_snapshot("TST", shuffled)
    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["snapshot_id"] == second["snapshot_id"]


def test_trading_assistant_is_built_inside_snapshot_and_reuses_enriched_indicators():
    frame = _ohlcv(100)
    snap = build_unified_snapshot("TST", frame)
    assert "trading_assistant" in snap
    assert snap["trading_assistant"]["ready"] is True
    assert snap["trading_assistant"]["atr14"] == pytest.approx(float(snap["enriched"]["ATR14"].iloc[-1]))
    assert snap["trading_assistant"]["vma20"] == pytest.approx(float(snap["enriched"]["VOL_MA20"].iloc[-1]))


def test_existing_position_without_lot_settlement_blocks_reduce_execution_plan():
    frame = _ohlcv(100)
    snap = build_unified_snapshot("TST", frame, position={"mode": "MANAGE_EXISTING", "quantity": 100,
        "entry_price": float(frame.close.iloc[-20]), "stop_price": float(frame.close.iloc[-30])})
    state = snap["position_state"]
    assert state["status"] == "UNKNOWN"
    if snap["decision"]["final_action"] == "REDUCE":
        assert snap["action_plan"]["status"] == "BLOCKED_UNKNOWN_SETTLEMENT"
        assert snap["action_plan"]["suggested_reduce_quantity"] == 0


def test_snapshot_declares_e840_schema_and_versioned_identity():
    frame = _ohlcv(100)
    snap = build_unified_snapshot("TST", frame)
    assert snap["schema_version"] == "8.4.0"
    assert snap["calculation_contract"]["schema_version"] == "8.4.0"
    assert snap["snapshot_id"] == snap["analysis_id"]
    assert len(snap["snapshot_id"]) == 24


def test_pending_sell_requires_finite_nonnegative_integer():
    for bad in (True, -1, 1.5, float("nan"), float("inf"), "abc"):
        with pytest.raises(ValueError):
            build_position_state([{"quantity": 100, "settlement_date": "2026-11-20"}],
                                 "2026-11-22", pending_sell=bad)


def test_risk_gate_rejects_non_integer_or_boolean_quantity():
    for bad in (True, 100.5, "abc", float("inf")):
        result = apply_risk_gate("ENTER_LONG", sizing_status="OK", sizing_quantity=bad,
                                 portfolio_status="OK")
        assert result["final_action"] == "WAIT"


def test_module_contracts_carry_snapshot_and_calculation_traceability():
    frame = _ohlcv(100)
    snap = build_unified_snapshot("TST", frame)
    for module in snap["module_results"].values():
        assert module["module_id"]
        assert module["snapshot_id"] == snap["snapshot_id"]
        assert module["calculation_version"] == "8.4.0"
        assert "limitations" in module
        assert "source_refs" in module
