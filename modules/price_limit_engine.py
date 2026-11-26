"""Configurable price-band calculations; exchange rules must be supplied."""
from __future__ import annotations
import math


def calculate_price_limits(reference_price, band_pct, tick_size=1):
    values = (reference_price, band_pct, tick_size)
    if any(isinstance(v, bool) for v in values):
        raise ValueError("Giá, biên độ và bước giá phải là số hợp lệ")
    ref, band, tick = map(float, values)
    if not all(math.isfinite(v) for v in (ref, band, tick)) or ref <= 0 or band < 0 or band >= 100 or tick <= 0:
        raise ValueError("Tham số giá không hợp lệ")
    raw_upper, raw_lower = ref * (1 + band / 100), ref * (1 - band / 100)
    upper = math.floor(raw_upper / tick + 1e-12) * tick
    lower = math.ceil(raw_lower / tick - 1e-12) * tick
    return {"reference_price": ref, "upper_limit": upper, "lower_limit": lower,
            "band_pct": band, "tick_size": tick}


def validate_ohlc_within_limits(open_price, high, low, close, limits):
    vals = [float(v) for v in (open_price, high, low, close)]
    if not all(math.isfinite(v) and v > 0 for v in vals):
        return {"valid": False, "reason": "OHLC không hợp lệ"}
    o, h, l, c = vals
    if h < max(o, c, l) or l > min(o, c, h):
        return {"valid": False, "reason": "Quan hệ OHLC không hợp lệ"}
    lo, hi = float(limits["lower_limit"]), float(limits["upper_limit"])
    valid = lo <= min(vals) and max(vals) <= hi
    return {"valid": valid, "reason": None if valid else "OHLC vượt biên độ cấu hình"}
