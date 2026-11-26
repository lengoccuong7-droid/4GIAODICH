from modules.action_plan import build_action_plan
from modules.central_decision_engine import decide
from modules.portfolio_manager import assess_portfolio_risk


def test_no_trade_bypasses_action_plan():
    result = build_action_plan("NO_TRADE", {"plan": {"reference_trigger": 100}})
    assert result["status"] == "BYPASSED"
    assert result["plan_type"] == "NONE"


def test_enter_long_uses_new_position_plan():
    result = build_action_plan("ENTER_LONG", {"plan": {"entry_zone_low": 95, "reference_trigger": 100},
        "sizing": {"quantity": 100}})
    assert result["plan_type"] == "NEW_POSITION_ENTRY"
    assert result["trigger"] == 100
    assert result["quantity"] == 100


def test_wait_with_existing_holding_is_not_new_entry_plan():
    result = build_action_plan("WAIT", {"position": {"mode": "MANAGE_EXISTING", "quantity": 500,
        "management_action": "GIỮ VÀ THEO DÕI"}, "plan": {"reference_trigger": 100}})
    assert result["plan_type"] == "HOLD_AND_MONITOR"
    assert result["quantity_held"] == 500
    assert "entry_zone_low" not in result


def test_reduce_routes_to_existing_position_plan():
    result = build_action_plan("REDUCE", {"position": {"mode": "MANAGE_EXISTING", "quantity": 900,
        "suggested_reduce_at_tp1_quantity": 300, "management_action": "GIẢM MỘT PHẦN"}})
    assert result["plan_type"] == "POSITION_REDUCTION"
    assert result["suggested_reduce_quantity"] == 300


def test_central_engine_maps_existing_stop_breach_to_reduce():
    report = {"status": "MANAGE_POSITION", "position": {"mode": "MANAGE_EXISTING",
        "quantity": 100, "status": "EXIT_RULE_TRIGGERED"}}
    result = decide(report, portfolio_risk={"status": "OK", "hard_veto": False, "warnings": []})
    assert result["final_action"] == "REDUCE"
    assert result["decision_context"] == "EXISTING_POSITION"


def test_central_engine_keeps_existing_hold_as_wait():
    report = {"status": "MANAGE_POSITION", "position": {"mode": "MANAGE_EXISTING",
        "quantity": 100, "status": "HOLD_AND_MONITOR"}}
    result = decide(report)
    assert result["final_action"] == "WAIT"
    assert result["decision_context"] == "EXISTING_POSITION"


def test_portfolio_manager_reports_focus_symbol_exposure_without_new_entry():
    result = assess_portfolio_risk({"equity_vnd": 100_000_000, "positions": [
        {"symbol": "AAA", "market_value": 20_000_000, "risk_value": 1_000_000}]},
        proposed_value=0, focus_symbol="AAA")
    assert result["status"] == "OK"
    assert result["metrics"]["focus_symbol_exposure_pct"] == 20
    assert result["metrics"]["known_stop_risk_vnd"] == 1_000_000


def test_module_error_does_not_cancel_existing_position_reduction():
    report = {"status": "MANAGE_POSITION", "position": {"mode": "MANAGE_EXISTING",
        "quantity": 100, "status": "EXIT_RULE_TRIGGERED"}}
    result = decide(report, module_results={"flow": {"module": "flow", "status": "ERROR"}})
    assert result["final_action"] == "REDUCE"
    assert result["risk_gate"]["status"] == "WARNING"
