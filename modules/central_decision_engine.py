"""Canonical action engine and risk gate for live analysis and replay."""
from __future__ import annotations
from .contracts import normalize_module_result
from .risk_gate import apply_risk_gate

ACTIONS = {"ENTER_LONG", "WAIT", "REDUCE", "NO_TRADE"}

def _held_quantity(position: dict) -> int:
    try:
        return max(0, int(float(position.get("quantity", 0) or 0)))
    except (TypeError, ValueError, OverflowError):
        return 0

def _legacy_action(report: dict) -> str:
    status = str(report.get("status", "")).upper()
    position = report.get("position") or {}
    if status in {"EXIT_RULE_TRIGGERED", "STOP_TOUCHED_INTRADAY", "TARGET_1_REACHED",
                  "TARGET_1_TOUCHED_INTRADAY", "TARGET_2_REACHED", "TARGET_2_TOUCHED_INTRADAY"}:
        return "REDUCE"
    if status == "TRADE_PLAN_READY":
        return "ENTER_LONG"
    if status == "STAND_ASIDE":
        return "NO_TRADE"
    if position and (str(position.get("mode", "")).upper() == "MANAGE_EXISTING"
                     or _held_quantity(position) > 0):
        held_status = str(position.get("status", "")).upper()
        if held_status in {"EXIT_RULE_TRIGGERED", "STOP_TOUCHED_INTRADAY",
                           "TARGET_1_REACHED", "TARGET_1_TOUCHED_INTRADAY",
                           "TARGET_2_REACHED", "TARGET_2_TOUCHED_INTRADAY"}:
            return "REDUCE"
        return "WAIT"
    if position and str(position.get("mode", "")).upper() == "MANAGE_EXISTING":
        return "WAIT"
    return "WAIT"

def decide(report: dict, module_results: dict | None = None,
           portfolio_risk: dict | None = None, require_portfolio_context: bool = False) -> dict:
    """Canonical action engine; delegates all veto logic to the shared Risk Gate."""
    proposed = _legacy_action(report or {})
    quality = (report or {}).get("evidence", {}).get("data_quality_status")
    sizing = (report or {}).get("sizing") or {}
    pr = portfolio_risk or {"status": "UNKNOWN", "hard_veto": False,
                            "warnings": ["Chưa có dữ liệu danh mục."]}
    gate = apply_risk_gate(
        proposed,
        data_quality_status=quality or "OK",
        sizing_status=sizing.get("status", "UNKNOWN"),
        sizing_quantity=sizing.get("quantity", 0),
        portfolio_status=pr.get("status", "UNKNOWN"),
        portfolio_hard_veto=bool(pr.get("hard_veto")),
        require_portfolio_context=require_portfolio_context,
        module_results=module_results,
    )
    position = (report or {}).get("position") or {}
    return {
        **gate,
        "portfolio_risk": pr,
        "decision_context": "EXISTING_POSITION" if (
            str(position.get("mode", "")).upper() == "MANAGE_EXISTING"
            or _held_quantity(position) > 0
        ) else "NEW_POSITION",
        "module_results": module_results or {},
        "engine": "CENTRAL-1.2",
    }
