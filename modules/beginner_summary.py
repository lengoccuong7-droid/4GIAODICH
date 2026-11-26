"""Plain-language summary for non-expert users, built only from analyze_swing_setup output."""
from __future__ import annotations

GLOSSARY = {
    "Stop-loss (cắt lỗ)": "Mức giá bạn đặt trước để thoát lệnh nếu sai, nhằm giới hạn thua lỗ.",
    "Vùng kích hoạt": "Mức giá mà khi giá chạm tới, kịch bản mua mới được coi là bắt đầu.",
    "Mục tiêu": "Mức giá dự kiến chốt lời, tính theo bội số của rủi ro (R).",
    "R:R": "Lãi dự kiến chia cho lỗ tối đa. 1,5 nghĩa là lãi kỳ vọng gấp 1,5 lần mức lỗ chấp nhận.",
    "Bẫy tăng/giảm": "Giá phá vùng quan trọng rồi quay lại, khiến người đuổi theo bị kẹt.",
    "T+2": "Cổ phiếu mua hôm nay chỉ bán được sau 2 phiên.",
}

def _v(x): return f"{x:,.0f}".replace(",", ".") if isinstance(x, (int, float)) else "—"

def build_beginner_summary(rep: dict) -> dict:
    st, plan, sz = rep.get("status"), rep.get("plan") or {}, rep.get("sizing") or {}
    ft = rep.get("flow_trap") or {}
    out = {"symbol": rep.get("symbol"), "score": rep.get("score"), "plan_lines": [], "why": [], "warnings": []}
    if st == "TRADE_PLAN_READY":
        out["level"], out["headline"] = "ok", "CÓ KỊCH BẢN MUA CÓ ĐIỀU KIỆN"
        out["action"] = (f"Chỉ mua nếu giá chạm {_v(plan['reference_trigger'])}đ (vùng {_v(plan['entry_zone_low'])}–"
                         f"{_v(plan['entry_zone_high'])}đ). Nếu giá mở cửa vượt vùng này thì bỏ qua, không đuổi giá.")
        out["plan_lines"] = [f"Số lượng tối đa: {sz.get('quantity',0):,} cp (~{_v(sz.get('position_value'))}đ)",
                             f"Cắt lỗ: {_v(plan['invalidation'])}đ (lỗ tối đa ~{_v(sz.get('risk_amount'))}đ)",
                             f"Chốt lời 1: {_v(plan['target_1'])}đ · Chốt lời 2: {_v(plan['target_2'])}đ",
                             "Đặt sẵn mức cắt lỗ ngay khi mua. Cổ phiếu mua hôm nay chỉ bán được sau 2 phiên (T+2)."]
    elif st == "WAIT_CONFIRMATION":
        out["level"], out["headline"] = "wait", "CHỜ THÊM – CHƯA MUA"
        out["action"] = "Chưa đủ điều kiện. Đừng mua lúc này; xem lại sau mỗi phiên."
    elif st == "STAND_ASIDE":
        out["level"], out["headline"] = "stop", "ĐỨNG NGOÀI – KHÔNG MUA"
        out["action"] = "Xu hướng/cấu trúc giá chưa ủng hộ. Giữ tiền mặt và chờ mã khác."
    elif st in ("MANAGE_POSITION", "POSITION_INPUT_REQUIRED"):
        out["level"], out["headline"] = "hold", "ĐANG GIỮ HÀNG – QUẢN LÝ RỦI RO"
        pos = rep.get("position") or {}
        out["action"] = f"Tình trạng: {pos.get('status','—')}. Kiểm tra mức cắt lỗ {_v(pos.get('reference_invalidation'))}đ."
    else:
        out["level"], out["headline"] = "stop", "CHƯA ĐỦ DỮ LIỆU"
        out["action"] = "; ".join(rep.get("reasons", [])[:2]) or "Cần ít nhất 50 phiên dữ liệu hợp lệ."
    out["why"] = (rep.get("positives") or [])[:3] + (rep.get("negatives") or [])[:2]
    out["blockers"] = rep.get("blockers") or []
    if ft.get("trap_risk") in ("HIGH", "MODERATE"):
        out["warnings"].append("Có dấu hiệu bẫy giá/breakout thất bại gần đây: không mua đuổi.")
    out["warnings"] += ["Không dùng margin. Không dồn quá 20% vốn vào một mã.",
                        "Đây là kịch bản tham khảo, không phải khuyến nghị đầu tư hay cam kết lợi nhuận."]
    return out
