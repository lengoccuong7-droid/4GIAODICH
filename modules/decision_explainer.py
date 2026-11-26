"""Human-readable explanation for canonical decisions."""
def explain_decision(decision: dict, report: dict | None = None) -> dict:
    report = report or {}
    action = decision.get("final_action", "WAIT")
    labels = {"ENTER_LONG": "Có thể xem xét kế hoạch mở vị thế có điều kiện",
              "WAIT": "Chờ xác nhận thêm", "REDUCE": "Rà soát giảm hoặc quản trị vị thế",
              "NO_TRADE": "Không mở vị thế mới"}
    reasons = list((report.get("blockers") or [])[:5])
    reasons.extend(decision.get("risk_gate", {}).get("override_reason", []))
    if not reasons:
        reasons = list((report.get("positives") or [])[:3])
    return {"action": action, "summary": labels.get(action, "Chưa có kết luận"),
            "reasons": reasons, "limitations": report.get("limitations", [])}
