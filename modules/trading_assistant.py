"""Rule-based educational trading assistant built only from the shared OHLCV snapshot.

All price levels are statistical reference levels for paper-trading/simulation,
not personalized investment advice or guaranteed execution prices.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from modules.support_resistance import find_support_resistance


def _num(value):
    try:
        value = float(value)
        return value if np.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def build_trading_assistant(frame: pd.DataFrame) -> dict:
    if frame is None or len(frame) < 25:
        return {"ready": False, "status": "CHƯA ĐỦ DỮ LIỆU", "message": "Cần tối thiểu 25 phiên OHLCV để tính các vùng tham chiếu."}
    x = frame.copy().sort_values("date" if "date" in frame.columns else frame.index.name or frame.columns[0]).reset_index(drop=True)
    required = {"high", "low", "close", "volume"}
    if not required.issubset(x.columns):
        return {"ready": False, "status": "THIẾU DỮ LIỆU", "message": "Cần đủ High, Low, Close và Volume."}
    for col in required:
        x[col] = pd.to_numeric(x[col], errors="coerce")
    x = x.dropna(subset=["high", "low", "close", "volume"])
    if len(x) < 25:
        return {"ready": False, "status": "CHƯA ĐỦ DỮ LIỆU", "message": "Dữ liệu hợp lệ còn dưới 25 phiên."}

    close = float(x.close.iloc[-1])
    prev_close = float(x.close.iloc[-2])
    levels = find_support_resistance(x, window=min(60, len(x)), pivot_span=2, tolerance_pct=0.012)
    support = _num(levels.get("support"))
    resistance = _num(levels.get("resistance"))

    if "ATR14" in x.columns:
        atr = _num(x["ATR14"].iloc[-1])
    else:
        prev_close_series = x.close.shift(1)
        true_range = pd.concat([
            x.high - x.low,
            (x.high - prev_close_series).abs(),
            (x.low - prev_close_series).abs(),
        ], axis=1).max(axis=1)
        atr = _num(true_range.tail(14).mean()) or float((x.high - x.low).tail(14).mean())
    vma20 = _num(x["VOL_MA20"].iloc[-1]) if "VOL_MA20" in x.columns else _num(x.volume.tail(20).mean())
    last_volume = float(x.volume.iloc[-1])
    volume_ratio = last_volume / vma20 if vma20 and vma20 > 0 else None

    # Reference stop buffers account for ordinary volatility; they are not guarantees.
    tplus = {"status": "CHỜ ĐIỀU KIỆN", "entry_low": None, "entry_high": None,
             "stop": None, "trigger": None, "target_1": None, "target_2": None,
             "conditions": [], "reason": "Chưa có vùng hỗ trợ hợp lệ để xây dựng kịch bản."}
    if support is not None and support > 0 and atr > 0:
        entry_low = support
        entry_high = support + 0.25 * atr
        stop = support - 0.5 * atr
        tplus.update({"entry_low": entry_low, "entry_high": entry_high, "stop": stop,
                      "trigger": support + 0.15 * atr,
                      "conditions": [
                          "Giá kiểm định vùng hỗ trợ và đóng cửa trở lại phía trên vùng kích hoạt.",
                          "Nến xác nhận có thân/đóng cửa tích cực; không mua chỉ vì giá chạm hỗ trợ.",
                          "Khối lượng không tăng đột biến theo chiều giảm.",
                      ]})
        near_support = support <= close <= support * 1.025
        reclaimed = close > (support + 0.15 * atr) and close > prev_close
        if near_support and reclaimed and (volume_ratio is None or volume_ratio <= 1.5):
            tplus["status"] = "CÓ ĐIỀU KIỆN THEO DÕI XÁC NHẬN"
            tplus["reason"] = "Giá ở gần hỗ trợ và có dấu hiệu hồi; cần phiên xác nhận tiếp theo."
        elif close < support:
            tplus["status"] = "VÔ HIỆU – KHÔNG THEO KỊCH BẢN HỖ TRỢ"
            tplus["reason"] = "Giá đã đóng cửa dưới hỗ trợ tham chiếu. Chờ hình thành cấu trúc mới."
        elif close > entry_high * 1.025:
            tplus["status"] = "CHƯA ĐẾN VÙNG THEO DÕI"
            tplus["reason"] = "Giá đang cách xa vùng hỗ trợ; không đuổi theo kịch bản hồi tại hỗ trợ."
        else:
            tplus["reason"] = "Chưa có nến xác nhận hồi phục đủ điều kiện tại vùng hỗ trợ."
        risk = (entry_high - stop) if stop < entry_high else None
        if risk and risk > 0:
            tplus["target_1"] = entry_high + risk
            tplus["target_2"] = entry_high + 2 * risk

    # Breakout: close above resistance buffer AND volume confirmation.
    breakout = {"status": "CHỜ BREAKOUT", "trigger": None, "stop": None,
                "target_1": None, "target_2": None, "volume_required": (1.3 * vma20 if vma20 else None),
                "conditions": [], "reason": "Chưa có kháng cự hợp lệ để xây dựng kịch bản breakout."}
    if resistance is not None and resistance > 0 and atr > 0:
        trigger = resistance + max(100.0, resistance * 0.002)
        stop = resistance - 0.5 * atr
        risk = trigger - stop
        breakout.update({"trigger": trigger, "stop": stop,
                         "target_1": trigger + risk, "target_2": trigger + 2 * risk,
                         "conditions": [
                             f"Đóng cửa vượt {trigger:,.0f} đồng, không chỉ vượt trong phiên.",
                             "Khối lượng phiên breakout tối thiểu 1,3 lần bình quân 20 phiên.",
                             "Ưu tiên chờ kiểm định lại vùng breakout và giữ được vùng này.",
                         ]})
        above = close > trigger
        vol_ok = volume_ratio is not None and volume_ratio >= 1.3
        if above and vol_ok:
            breakout["status"] = "BREAKOUT ĐỦ ĐIỀU KIỆN SƠ BỘ – CHỜ KIỂM ĐỊNH"
            breakout["reason"] = "Giá đóng cửa vượt ngưỡng và khối lượng đạt điều kiện; vẫn cần theo dõi retest."
        elif above and not vol_ok:
            breakout["status"] = "VƯỢT GIÁ NHƯNG THIẾU XÁC NHẬN KHỐI LƯỢNG"
            breakout["reason"] = "Không xác nhận breakout khi thanh khoản chưa đạt ngưỡng."
        else:
            breakout["reason"] = "Giá đóng cửa chưa vượt ngưỡng kích hoạt breakout."

    return {
        "ready": True, "close": close, "previous_close": prev_close,
        "support": support, "resistance": resistance,
        "support_zone": levels.get("support_zone"), "resistance_zone": levels.get("resistance_zone"),
        "support_touches": levels.get("support_touches", 0),
        "resistance_touches": levels.get("resistance_touches", 0),
        "atr14": atr, "vma20": vma20, "last_volume": last_volume,
        "volume_ratio": volume_ratio, "tplus": tplus, "breakout": breakout,
        "method": levels.get("method", "Pivot High/Low gom cụm"),
        "warning": "Các mốc là vùng tham chiếu mô phỏng từ OHLCV, không phải khuyến nghị mua/bán hoặc giá khớp chắc chắn. Stop có thể trượt giá; cần tính đến phí, thanh khoản và quy định T+.",
    }
