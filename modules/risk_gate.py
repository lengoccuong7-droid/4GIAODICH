"""Explicit, auditable risk-gate rules for canonical actions."""
from __future__ import annotations

ACTIONS = {"ENTER_LONG", "WAIT", "REDUCE", "NO_TRADE"}


def apply_risk_gate(proposed_action, *, data_quality_status="OK", sizing_status="OK",
                    sizing_quantity=1, portfolio_status="UNKNOWN", portfolio_hard_veto=False,
                    require_portfolio_context=False, module_results=None):
    proposed = str(proposed_action or "WAIT").upper()
    if proposed not in ACTIONS:
        raise ValueError(f"Hành động không hợp lệ: {proposed}")
    final = proposed
    reasons = []
    if data_quality_status == "ERROR":
        reasons.append("Data Quality báo lỗi nghiêm trọng; không mở vị thế mới.")
        if final == "ENTER_LONG":
            final = "NO_TRADE"
    try:
        quantity_value = float(sizing_quantity or 0)
        quantity_valid = (not isinstance(sizing_quantity, bool) and quantity_value > 0
                          and quantity_value.is_integer())
    except (TypeError, ValueError, OverflowError):
        quantity_valid = False
    if final == "ENTER_LONG" and (sizing_status != "OK" or not quantity_valid):
        final = "WAIT"
        reasons.append("Không có quy mô vị thế hợp lệ theo ngân sách rủi ro.")
    if final == "ENTER_LONG":
        if portfolio_hard_veto:
            final = "NO_TRADE"
            reasons.append("Risk Gate chặn do rủi ro danh mục.")
        elif portfolio_status == "UNKNOWN":
            reasons.append("Rủi ro danh mục chưa xác định.")
            if require_portfolio_context:
                final = "WAIT"
                reasons.append("Cấu hình yêu cầu dữ liệu danh mục trước khi mở vị thế.")
    for item in (module_results or {}).values():
        if isinstance(item, dict) and item.get("status") == "ERROR":
            reasons.append(f"Module {item.get('module', 'unknown')} báo lỗi.")
            if final == "ENTER_LONG":
                final = "NO_TRADE"
            break
    return {"proposed_action": proposed, "final_action": final,
            "risk_gate": {"status": "VETO" if final != proposed else "WARNING" if reasons else "PASS",
                          "original_action": proposed, "final_action": final,
                          "override_reason": reasons}}
