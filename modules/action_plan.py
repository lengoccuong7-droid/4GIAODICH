"""Action-plan routing for canonical decisions.

Plans are scenario references for education/simulation only. NO_TRADE deliberately
bypasses the plan builder and goes directly to the decision explanation.
"""
from __future__ import annotations


def build_action_plan(final_action: str, report: dict | None = None) -> dict:
    report = report or {}
    action = str(final_action or "WAIT").upper()
    position = report.get("position") or {}
    plan = report.get("plan") or {}
    sizing = report.get("sizing") or {}

    if action == "NO_TRADE":
        return {"status": "BYPASSED", "plan_type": "NONE", "action": action,
                "reason": "NO_TRADE không tạo kế hoạch mở hoặc quản trị vị thế."}
    if action == "REDUCE":
        if position.get("mode") != "MANAGE_EXISTING" or int(position.get("quantity", 0) or 0) <= 0:
            return {"status": "INSUFFICIENT_DATA", "plan_type": "POSITION_MANAGEMENT",
                    "action": action, "reason": "Thiếu dữ liệu vị thế hiện tại để lập kế hoạch giảm."}
        return {"status": "REFERENCE", "plan_type": "POSITION_REDUCTION",
                "action": action, "quantity_held": int(position.get("quantity", 0) or 0),
                "suggested_reduce_quantity": int(position.get("suggested_reduce_at_tp1_quantity", 0) or 0),
                "market_price": position.get("market_price"),
                "invalidation": position.get("reference_invalidation"),
                "target_1": position.get("target_1_reference"),
                "target_2": position.get("target_2_reference"),
                "management_action": position.get("management_action"),
                "stages": position.get("management_stages", [])}
    if action == "ENTER_LONG":
        return {"status": "REFERENCE", "plan_type": "NEW_POSITION_ENTRY", "action": action,
                "entry_zone_low": plan.get("entry_zone_low"),
                "entry_zone_high": plan.get("entry_zone_high"),
                "trigger": plan.get("reference_trigger"),
                "invalidation": plan.get("invalidation"),
                "target_1": plan.get("target_1"), "target_2": plan.get("target_2"),
                "rr_target_1": plan.get("rr_target_1"), "rr_target_2": plan.get("rr_target_2"),
                "quantity": sizing.get("quantity"), "position_value": sizing.get("position_value"),
                "risk_amount": sizing.get("risk_amount")}
    # WAIT on an existing holding is a hold/monitor plan, never a new-entry plan.
    if position.get("mode") == "MANAGE_EXISTING":
        return {"status": "REFERENCE", "plan_type": "HOLD_AND_MONITOR", "action": "WAIT",
                "quantity_held": int(position.get("quantity", 0) or 0),
                "market_price": position.get("market_price"),
                "invalidation": position.get("reference_invalidation"),
                "trailing_stop": position.get("trailing_stop_reference"),
                "management_action": position.get("management_action"),
                "stages": position.get("management_stages", []),
                "activation_conditions": report.get("next_steps", []),
                "cancellation_conditions": report.get("blockers", [])}
    # WAIT with no holding: show conditions to activate or cancel a new setup.
    return {"status": "REFERENCE", "plan_type": "WAIT_FOR_TRIGGER", "action": "WAIT",
            "entry_zone_low": plan.get("entry_zone_low"),
            "entry_zone_high": plan.get("entry_zone_high"),
            "trigger": plan.get("reference_trigger"),
            "invalidation": plan.get("invalidation"),
            "target_1": plan.get("target_1"), "target_2": plan.get("target_2"),
            "activation_conditions": report.get("next_steps", []),
            "cancellation_conditions": report.get("blockers", [])}
