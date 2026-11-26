"""Plain-language explanations for the shared OHLCV analysis snapshot."""
from __future__ import annotations


def _fmt_pct(value):
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return None


def market_explanation(regime: dict | None) -> dict:
    r = regime or {}
    label = str(r.get("status_label") or r.get("status") or r.get("regime") or "CHƯA ĐỦ DỮ LIỆU")
    ret = _fmt_pct(r.get("return_20_pct"))
    reasons = r.get("reasons") or []
    if not r or label == "CHƯA ĐỦ DỮ LIỆU":
        return {"headline": "Chưa đủ dữ liệu để đánh giá thị trường chung.",
                "detail": "Không nên lấy diễn biến của riêng một cổ phiếu để đại diện cho toàn thị trường. Cần VN-Index hoặc dữ liệu đủ rộng.",
                "caution": "Các kịch bản của cổ phiếu cần được đánh giá thận trọng hơn khi thiếu benchmark."}
    if label == "RỦI RO" or str(r.get("regime", "")).upper() == "GIẢM":
        detail = "Thị trường đang ở trạng thái bất lợi. Các cổ phiếu thường khó tăng bền hơn và tín hiệu mua cần được kiểm tra chặt chẽ."
        if ret:
            detail += f" VN-Index biến động {ret} trong 20 phiên gần nhất."
        caution = "Ưu tiên quan sát khả năng giữ vùng hỗ trợ; không xem một phiên hồi riêng lẻ là tín hiệu đảo chiều."
    elif label == "THUẬN LỢI" or str(r.get("regime", "")).upper() == "TĂNG":
        detail = "Thị trường đang có nền hỗ trợ tương đối thuận lợi cho các cổ phiếu khỏe. Tuy nhiên, từng mã vẫn phải tự xác nhận bằng giá và khối lượng."
        if ret:
            detail += f" VN-Index biến động {ret} trong 20 phiên gần nhất."
        caution = "Thị trường thuận lợi không có nghĩa mọi cổ phiếu đều an toàn hoặc phù hợp để mua đuổi."
    else:
        detail = "Thị trường chưa có xu hướng đủ rõ hoặc đang chuyển pha. Các nhóm cổ phiếu có thể diễn biến trái chiều."
        if ret:
            detail += f" VN-Index biến động {ret} trong 20 phiên gần nhất."
        caution = "Nên chọn lọc từng mã và chờ tín hiệu xác nhận thay vì suy luận rằng toàn thị trường đang tăng hoặc giảm."
    return {"headline": f"Bối cảnh thị trường: {label.lower()}.", "detail": detail,
            "caution": caution, "evidence": reasons}


def stock_explanation(report: dict | None, structure: dict | None, flow: dict | None) -> dict:
    rep, stc, flw = report or {}, structure or {}, flow or {}
    status = str(rep.get("status", ""))
    phase = str(stc.get("label") or "CHƯA ĐỦ BẰNG CHỨNG")
    positives = list(rep.get("positives") or [])[:2]
    negatives = list(rep.get("negatives") or [])[:3]
    evidence = list(stc.get("evidence") or [])[:3]
    blockers = list(rep.get("blockers") or [])[:3]
    if status in ("TRADE_PLAN_READY",):
        headline = "Có kịch bản tham khảo, nhưng chỉ hợp lệ khi đủ điều kiện xác nhận."
    elif status in ("WAIT_CONFIRMATION",):
        headline = "Tín hiệu chưa đồng thuận; nên chờ thêm thay vì vội đưa ra quyết định."
    elif status in ("STAND_ASIDE",):
        headline = "Hiện tại chưa có cấu trúc đủ tốt để xây dựng kịch bản tham khảo."
    elif status in ("MANAGE_POSITION", "POSITION_INPUT_REQUIRED"):
        headline = "Cần ưu tiên đánh giá rủi ro của vị thế đang nắm giữ."
    else:
        headline = "Chưa đủ dữ liệu hoặc điều kiện để đưa ra nhận định đáng tin cậy."
    if "PHÂN PHỐI TIỀM NĂNG" in phase:
        phase_text = "Giá và khối lượng có một số dấu hiệu nghiêng về áp lực cung. Đây mới là cảnh báo sớm, không chứng minh tổ chức đang bán ra."
    elif "TÍCH LŨY" in phase or "HẤP THỤ" in phase:
        phase_text = "Một số đặc điểm giá và khối lượng gợi ý khả năng tích lũy hoặc hấp thụ. Chưa thể kết luận có tổ chức đang gom hàng."
    elif "CHƯA ĐỦ" in phase:
        phase_text = "Dữ liệu hiện tại chưa tạo được bằng chứng đủ mạnh để phân loại cổ phiếu vào pha tích lũy hay phân phối."
    else:
        phase_text = f"Phân loại cấu trúc hiện tại: {phase}. Cần đọc cùng xu hướng giá, khối lượng và bối cảnh thị trường."
    return {"headline": headline, "phase_text": phase_text,
            "supporting": positives, "risks": negatives,
            "structure_evidence": evidence, "blockers": blockers,
            "score": rep.get("score"), "status": status}
