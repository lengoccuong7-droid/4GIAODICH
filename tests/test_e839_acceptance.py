import pandas as pd

from modules.portfolio_manager import summarize_portfolio
from modules.formula_registry import FORMULAS
from modules.central_decision_engine import decide


def test_missing_stop_is_unknown_not_zero_risk():
    positions = pd.DataFrame([
        {"symbol": "AAA", "quantity": 100, "entry_price": 10, "market_price": 11},
    ])
    result = summarize_portfolio(positions, 10_000)
    assert result["risk_status"] == "UNKNOWN"
    assert result["total_risk"] is None
    assert result["risk_pct_of_capital"] is None
    assert pd.isna(result["positions"].iloc[0]["risk_value"])


def test_stop_risk_is_calculated_when_stop_is_present():
    positions = pd.DataFrame([
        {"symbol": "AAA", "quantity": 100, "entry_price": 10, "market_price": 11, "stop_price": 9},
    ])
    result = summarize_portfolio(positions, 10_000)
    assert result["risk_status"] == "KNOWN"
    assert result["risk_coverage_pct"] == 100.0
    assert result["total_risk"] == 100.0


def test_formula_registry_does_not_claim_unverified_formulas_are_verified():
    # E8.4 expands the catalog to cover calculations already implemented in code.
    assert len(FORMULAS) >= 28
    assert all(item["status"] == "PENDING_INDEPENDENT_VALIDATION" for item in FORMULAS)


def test_existing_position_reduction_is_not_overridden_by_module_error():
    report = {"status": "EXIT_RULE_TRIGGERED", "position": {"mode": "MANAGE_EXISTING", "quantity": 100}}
    result = decide(report, module_results={"diagnostic": {"status": "ERROR", "module": "diagnostic"}})
    assert result["final_action"] == "REDUCE"
