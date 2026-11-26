"""Human-readable market and stock phase diagnostics for the 3-10 session workflow.

All classifications are rule-based heuristics over end-of-day OHLCV, not proof of
Wyckoff intent, manipulation, or institutional trading.
"""
from __future__ import annotations
import math
import pandas as pd


def classify_stock_phase(frame: pd.DataFrame, flow_trap: dict | None = None) -> dict:
    if frame is None or frame.empty or len(frame) < 50:
        return {"phase": "CHƯA ĐỦ DỮ LIỆU", "confidence": "THẤP",
                "reasons": ["Cần tối thiểu 50 phiên OHLCV để phân loại trạng thái cổ phiếu."]}
    x = frame.sort_values("date")
    r = x.iloc[-1]
    close = float(r.close)
    ma20 = float(r.SMA20) if pd.notna(r.get("SMA20")) else math.nan
    ma50 = float(r.SMA50) if pd.notna(r.get("SMA50")) else math.nan
    ma20_old = float(x.iloc[-6].SMA20) if pd.notna(x.iloc[-6].get("SMA20")) else math.nan
    rvol = float(r.REL_VOLUME20) if pd.notna(r.get("REL_VOLUME20")) else math.nan
    recent = x.iloc[-20:]
    range_pct = (float(recent.high.max()) / float(recent.low.min()) - 1) * 100 if float(recent.low.min()) > 0 else math.nan
    flow = flow_trap or {}
    metrics = flow.get("metrics", {}) if isinstance(flow, dict) else {}
    dist_proxy = flow.get("flow_bias") == "DISTRIBUTION_PROXY"
    trap_risk = str(flow.get("trap_risk", "")).upper()
    reasons: list[str] = []

    # Distribution is prioritized over a merely sideways price pattern.
    weak_supply_days = int(metrics.get("weak_high_volume_sessions_5", 0) or 0)
    if dist_proxy or weak_supply_days >= 2:
        phase = "PHÂN PHỐI NGHI VẤN / CUNG ÁP ĐẢO"
        confidence = "TRUNG BÌNH" if dist_proxy else "THẤP"
        reasons.append("Proxy cung-cầu hoặc nhiều phiên khối lượng cao nhưng đóng cửa yếu đang nghiêng về phía cung; không kết luận có tổ chức bán ra.")
    elif trap_risk == "HIGH":
        phase, confidence = "CHUYỂN PHA / CẢNH BÁO BẪY GIÁ", "TRUNG BÌNH"
        reasons.append("Có rủi ro bẫy giá/breakout thất bại cao; chưa đủ căn cứ gọi đây là phân phối.")
    elif close < ma20 < ma50 and ma20 < ma20_old:
        phase, confidence = "SUY YẾU", "TRUNG BÌNH"
        reasons.append("Giá dưới MA20, MA20 dưới MA50 và MA20 đang dốc xuống.")
    elif close > ma20 > ma50 and ma20 > ma20_old:
        phase, confidence = "TĂNG GIÁ", "TRUNG BÌNH"
        reasons.append("Giá trên MA20, MA20 trên MA50 và MA20 đang dốc lên.")
    elif (math.isfinite(range_pct) and range_pct <= 12 and ma20 > 0
          and math.isfinite(ma20) and abs(close / ma20 - 1) <= .06):
        phase, confidence = "TÍCH LŨY / ĐI NGANG", "THẤP"
        reasons.append(f"Biên độ 20 phiên khoảng {range_pct:.1f}%; chưa có xu hướng tăng/giảm đồng thuận.")
    else:
        phase, confidence = "CHUYỂN PHA / CHƯA RÕ", "THẤP"
        reasons.append("Các điều kiện xu hướng và biên độ chưa đủ đồng thuận để xếp vào một pha rõ ràng.")
    if math.isfinite(rvol):
        reasons.append(f"Khối lượng phiên cuối bằng {rvol:.2f} lần trung bình 20 phiên.")
    return {"phase": phase, "confidence": confidence, "reasons": reasons,
            "metrics": {"range_20_pct": range_pct, "relative_volume20": rvol,
                        "close": close, "sma20": ma20, "sma50": ma50}}


def market_status_label(regime: dict | None) -> str:
    regime = regime or {}
    raw = str(regime.get("regime", "CHƯA ĐỦ DỮ LIỆU")).upper()
    if "CHƯA ĐỦ" in raw:
        return "CHƯA ĐỦ DỮ LIỆU"
    if "GIẢM" in raw or "RỦI RO" in raw:
        return "RỦI RO"
    if "TĂNG" in raw or "THUẬN" in raw:
        return "THUẬN LỢI"
    return "TRUNG TÍNH"
