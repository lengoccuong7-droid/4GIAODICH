import numpy as np
import pandas as pd
import pytest

from modules.contracts import normalize_module_result
from modules.central_decision_engine import decide
from modules.portfolio_manager import assess_portfolio_risk
from modules.unified_analytics import build_unified_snapshot


def market(symbol="AAA", n=220):
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2025-01-01", periods=n)
    close = 10000 * np.exp(np.cumsum(rng.normal(0.001, 0.006, n)))
    return pd.DataFrame({"date": dates, "symbol": symbol, "open": close*.998,
        "high": close*1.012, "low": close*.988, "close": close,
        "volume": 500000 + np.arange(n)*1000})


def test_contract_adapts_legacy_payload_and_preserves_evidence():
    raw = {"status": "OK", "evidence": ["e1"], "cautions": ["c1"], "score": 10}
    result = normalize_module_result("legacy", raw, "2025-01-01")
    assert result["status"] == "OK"
    assert result["evidence"] == ["e1"]
    assert result["warnings"] == ["c1"]
    assert result["payload"] == raw


def test_portfolio_missing_context_is_unknown_not_zero():
    result = assess_portfolio_risk(None, proposed_value=1000)
    assert result["status"] == "UNKNOWN"
    assert result["hard_veto"] is False
    assert "không giả định" in result["warnings"][0]


def test_portfolio_limit_can_veto_new_position():
    result = assess_portfolio_risk(
        {"equity_vnd": 100_000_000, "positions": [{"market_value": 75_000_000}]},
        proposed_value=10_000_000)
    assert result["hard_veto"] is True
    assert result["status"] == "BLOCKED"


def test_central_engine_converts_ready_setup_and_applies_veto():
    report = {"status": "TRADE_PLAN_READY", "sizing": {"status": "OK", "quantity": 100}}
    allowed = decide(report, portfolio_risk={"status": "OK", "hard_veto": False, "warnings": []})
    blocked = decide(report, portfolio_risk={"status": "BLOCKED", "hard_veto": True,
                                             "warnings": ["Vượt hạn mức."]})
    assert allowed["final_action"] == "ENTER_LONG"
    assert blocked["proposed_action"] == "ENTER_LONG"
    assert blocked["final_action"] == "NO_TRADE"
    assert blocked["risk_gate"]["status"] == "VETO"


def test_central_engine_requires_portfolio_when_configured():
    report = {"status": "TRADE_PLAN_READY", "sizing": {"status": "OK", "quantity": 100}}
    result = decide(report, portfolio_risk={"status": "UNKNOWN", "hard_veto": False,
                                            "warnings": ["Thiếu danh mục"]},
                    require_portfolio_context=True)
    assert result["final_action"] == "WAIT"


def test_snapshot_contains_canonical_decision_and_module_contracts():
    stock = market("AAA")
    snap = build_unified_snapshot("AAA", stock)
    assert snap["snapshot_id"] == snap["analysis_id"]
    assert snap["decision_id"]
    assert snap["decision"]["final_action"] in {"ENTER_LONG", "WAIT", "REDUCE", "NO_TRADE"}
    assert snap["module_results"]["data_quality"]["status"] in {"OK", "WARNING"}
    assert snap["decision_explanation"]["action"] == snap["decision"]["final_action"]


def test_snapshot_rejects_hard_data_quality_errors_before_analysis():
    stock = market("AAA")
    stock.loc[5, "high"] = stock.loc[5, "low"] - 1
    with pytest.raises(ValueError, match="Data Quality"):
        build_unified_snapshot("AAA", stock)
