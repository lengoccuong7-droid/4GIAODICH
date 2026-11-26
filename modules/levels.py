"""Structure levels, volume narrative and holder guidance. Pure functions on OHLCV."""
from __future__ import annotations
import pandas as pd

def _f(v): return f"{v:,.0f}".replace(",", ".")

def add_ma_series(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.sort_values("date").reset_index(drop=True).copy()
    for n in (10, 20):
        x[f"MA{n}"] = x.close.rolling(n, min_periods=n).mean()
        x[f"VMA{n}"] = x.volume.rolling(n, min_periods=n).mean()
    return x

def structure_levels(frame: pd.DataFrame) -> dict:
    x = add_ma_series(frame); l = x.iloc[-1]
    prior = x.iloc[-21:-1]
    atr = float((x.high - x.low).tail(14).mean())
    return {"close": float(l.close), "ma10": _n(l.MA10), "ma20": _n(l.MA20),
            "high20": float(prior.high.max()), "low20": float(prior.low.min()),
            "low10": float(x.low.tail(10).min()), "low5": float(x.low.tail(5).min()),
            "atr_proxy": atr, "stop_atr": float(l.close - 1.5 * atr)}

def _n(v): return None if pd.isna(v) else float(v)

def volume_narrative(frame: pd.DataFrame) -> dict:
    x = add_ma_series(frame); l = x.iloc[-1]
    v5 = x.volume.tail(5).tolist()
    falling = all(v5[i] > v5[i + 1] for i in range(4)) or sum(v5[i] > v5[i + 1] for i in range(4)) >= 3
    rel = float(l.volume / l.VMA20) if l.VMA20 else None
    need = float(l.VMA20 * 1.3) if l.VMA20 else None
    if rel is None: txt = "Chưa đủ dữ liệu khối lượng."
    elif rel < 0.7: txt = f"Thanh khoản đang cạn: phiên cuối chỉ bằng {rel:.2f} lần trung bình 20 phiên" + (", và giảm dần trong 5 phiên gần nhất." if falling else ".")
    elif rel < 1.1: txt = f"Thanh khoản trung bình ({rel:.2f} lần trung bình 20 phiên)."
    else: txt = f"Thanh khoản tăng ({rel:.2f} lần trung bình 20 phiên)."
    return {"rel_volume": rel, "falling_5": bool(falling), "text": txt,
            "breakout_volume_needed": need, "vma10": _n(l.VMA10), "vma20": _n(l.VMA20)}

def watch_levels_text(frame, vol=None) -> list[str]:
    lv, vol = structure_levels(frame), vol or volume_narrative(frame)
    out = [f"Mốc cảnh báo gần: {_f(lv['low5'])} (đáy 5 phiên)" + (f" và MA20 ≈ {_f(lv['ma20'])}" if lv["ma20"] else "") + ".",
           f"Mốc cắt lỗ tham chiếu: {_f(lv['low10'])} (đáy 10 phiên); theo 1,5 biên độ ≈ {_f(lv['stop_atr'])}.",
           f"Kháng cự gần: {_f(lv['high20'])} (đỉnh 20 phiên). Hỗ trợ lớn: {_f(lv['low20'])} (đáy 20 phiên)."]
    if vol["breakout_volume_needed"]:
        out.append(f"Chỉ tin breakout trên {_f(lv['high20'])} khi khối lượng từ ≈ {_f(vol['breakout_volume_needed'])} cp trở lên (1,3 lần trung bình 20 phiên).")
    return out

def holder_guide(frame, entry: float, qty: int, stop: float | None = None, max_loss_vnd: float | None = None) -> dict:
    lv, vol = structure_levels(frame), volume_narrative(frame)
    c = lv["close"]; pnl_pct = (c / entry - 1) * 100; pnl_vnd = (c - entry) * qty
    base_stop = stop if stop and 0 < stop < c else None
    if max_loss_vnd and qty > 0:   # price at which total loss from cost equals tolerance
        loss_stop = entry - max_loss_vnd / qty
        base_stop = max(base_stop or 0, loss_stop) if loss_stop > 0 else base_stop
    struct = lv["low10"]
    stop_ref = max(base_stop, struct) if (base_stop and base_stop < c) else (struct if struct < c else lv["stop_atr"])
    in_profit = c > entry
    trail = max(stop_ref, lv["low5"]) if in_profit and lv["low5"] < c else stop_ref
    status = "THỦNG CẮT LỖ – XEM XÉT THOÁT" if c <= stop_ref else ("ĐANG LÃI – THEO DÕI, DỜI STOP" if in_profit else "ĐANG LỖ – GIỮ KỶ LUẬT STOP")
    notes = [vol["text"]]
    if c < (lv["ma20"] or 0): notes.append("Giá dưới MA20: xu hướng ngắn hạn yếu đi.")
    if vol["falling_5"] and in_profit: notes.append("Lãi nhưng thiếu lực khối lượng: cân nhắc dời stop lên để bảo vệ lãi.")
    notes.append("Không mua thêm/bình quân giá xuống khi chưa có tín hiệu xác nhận. Nhớ T+2 khi bán lại.")
    return {"status": status, "pnl_pct": pnl_pct, "pnl_vnd": pnl_vnd, "stop_reference": stop_ref,
            "trailing_reference": trail, "loss_if_stop_vnd": (entry - stop_ref) * qty,
            "loss_if_stop_pct": (stop_ref / entry - 1) * 100, "resistance": lv["high20"], "notes": notes}
