"""Position-lot and settlement state normalization for simulation.

Settlement dates are supplied by the caller; this module deliberately does not
assume an exchange calendar or hard-code T+ rules.
"""
from __future__ import annotations
from datetime import date, datetime
from math import isfinite


def _as_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def build_position_state(lots, as_of, pending_sell=0):
    if not isinstance(lots, list):
        raise TypeError("lots phải là danh sách")
    asof = _as_date(as_of)
    if asof is None:
        raise ValueError("as_of phải là ngày hợp lệ")
    total = available = pending_buy = 0
    schedule = []
    for i, lot in enumerate(lots):
        if not isinstance(lot, dict):
            raise ValueError(f"Lô {i} không hợp lệ")
        qty_raw = lot.get("quantity")
        if isinstance(qty_raw, bool):
            raise ValueError("quantity phải là số nguyên dương")
        try:
            qty_float = float(qty_raw)
        except (TypeError, ValueError):
            raise ValueError("quantity phải là số nguyên dương")
        if not isfinite(qty_float) or qty_float <= 0 or not qty_float.is_integer():
            raise ValueError("quantity phải là số nguyên dương")
        qty = int(qty_float)
        settle = _as_date(lot.get("settlement_date"))
        if settle is None:
            state = "UNKNOWN"
        elif settle <= asof:
            state = "AVAILABLE"
            available += qty
        else:
            state = "PENDING_BUY"
            pending_buy += qty
        total += qty
        schedule.append({"lot_id": lot.get("lot_id", str(i + 1)), "quantity": qty,
                         "settlement_date": settle.isoformat() if settle else None,
                         "status": state})
    if isinstance(pending_sell, bool):
        raise ValueError("pending_sell phải là số nguyên không âm")
    try:
        pending_sell_value = float(pending_sell)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("pending_sell phải là số nguyên không âm")
    if not isfinite(pending_sell_value) or pending_sell_value < 0 or not pending_sell_value.is_integer():
        raise ValueError("pending_sell phải là số nguyên không âm")
    pending_sell_int = int(pending_sell_value)
    available_to_sell = max(0, available - pending_sell_int)
    status = "UNKNOWN" if any(x["status"] == "UNKNOWN" for x in schedule) else "OK"
    return {"status": status, "as_of": asof.isoformat(), "total_position": total,
            "available_to_sell": available_to_sell, "pending_buy": pending_buy,
            "pending_sell": pending_sell_int, "settlement_schedule": schedule}
