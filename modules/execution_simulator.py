"""Conservative OHLCV order-fill approximation, not an order-book simulator."""
from __future__ import annotations
import math

STATUSES = {"FILLED", "PARTIALLY_FILLED", "PENDING", "REJECTED", "EXPIRED"}


def simulate_limit_order(*, side, quantity, limit_price, open_price, high, low, volume,
                          participation_rate=0.05, tick_size=1):
    side = str(side).upper()
    if side not in {"BUY", "SELL"}:
        raise ValueError("side phải là BUY hoặc SELL")
    if isinstance(quantity, bool) or int(quantity) != quantity or quantity <= 0:
        raise ValueError("quantity phải là số nguyên dương")
    vals = [limit_price, open_price, high, low, volume, participation_rate, tick_size]
    if any(isinstance(v, bool) for v in vals):
        raise ValueError("Tham số khớp lệnh không hợp lệ")
    lp, op, hi, lo, vol, part, tick = map(float, vals)
    if not all(math.isfinite(v) for v in (lp, op, hi, lo, vol, part, tick)) or min(lp, op, hi, lo, tick) <= 0 or vol < 0 or not 0 < part <= 1 or hi < lo:
        raise ValueError("Dữ liệu khớp lệnh không hợp lệ")
    touched = (op <= lp or lo <= lp) if side == "BUY" else (op >= lp or hi >= lp)
    if not touched or vol <= 0:
        return {"status": "PENDING", "requested_quantity": int(quantity), "filled_quantity": 0,
                "remaining_quantity": int(quantity), "fill_price": None,
                "assumption": "OHLCV không xác nhận khả năng khớp trong phiên."}
    # A limit order cannot execute worse than its limit; price improvement is not inferred.
    capacity = max(0, math.floor(vol * part))
    filled = min(int(quantity), capacity)
    if filled <= 0:
        status = "PENDING"
    elif filled < int(quantity):
        status = "PARTIALLY_FILLED"
    else:
        status = "FILLED"
    return {"status": status, "requested_quantity": int(quantity),
            "filled_quantity": filled, "remaining_quantity": int(quantity) - filled,
            "fill_price": (min(op, lp) if side == "BUY" else max(op, lp)) if filled else None,
            "assumption": "Giá khớp giả định tại giá giới hạn; OHLCV không tái tạo hàng đợi sổ lệnh."}
