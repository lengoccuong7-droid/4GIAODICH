from __future__ import annotations
import math

def calculate_position_size(capital_vnd, entry_price, stop_price, risk_pct=1.0,
                             max_allocation_pct=20.0, lot_size=100, price_multiplier=1.0,
                             fee_pct=0.15, slippage_pct=0.10, tax_pct=0.10):
    """Risk-based quantity including estimated round-trip transaction costs.

    Cost inputs are percentages per side; estimates are conservative and configurable.
    """
    try:
        vals = [float(capital_vnd), float(entry_price), float(stop_price), float(price_multiplier),
                float(risk_pct), float(max_allocation_pct), float(fee_pct), float(slippage_pct), float(tax_pct)]
        if not all(math.isfinite(v) for v in vals):
            raise ValueError
        capital, entry, stop, mult, risk_p, alloc_p, fee_p, slip_p, tax_p = vals
        if isinstance(lot_size, bool):
            raise ValueError
        lot_numeric = float(lot_size)
        if not math.isfinite(lot_numeric) or not lot_numeric.is_integer():
            raise ValueError
        lot = int(lot_numeric)
        if (capital <= 0 or entry <= 0 or stop <= 0 or stop >= entry or mult <= 0 or lot <= 0
                or not 0 <= risk_p <= 100 or not 0 <= alloc_p <= 100
                or min(fee_p, slip_p, tax_p) < 0):
            raise ValueError
    except (TypeError, ValueError, OverflowError):
        return {"quantity": 0, "risk_budget": 0.0, "position_value": 0.0, "risk_amount": 0.0, "status": "INPUT_INVALID"}
    budget = capital * risk_p / 100.0
    # Buy costs + sell costs (including sell tax) are added to the price loss.
    buy_cost_rate = (fee_p + slip_p) / 100.0
    sell_cost_rate = (fee_p + slip_p + tax_p) / 100.0
    per_share = ((entry - stop) + entry * buy_cost_rate + stop * sell_cost_rate) * mult
    max_by_risk = int(budget // per_share) if per_share > 0 else 0
    cash_per_share = entry * mult * (1 + buy_cost_rate)
    max_by_alloc = int((capital * alloc_p / 100.0) // cash_per_share)
    qty = max(0, min(max_by_risk, max_by_alloc))
    qty = (qty // lot) * lot
    value = qty * entry * mult
    risk = qty * per_share
    return {"quantity": qty, "risk_budget": budget, "position_value": value, "risk_amount": risk,
            "risk_pct_of_capital": risk / capital * 100, "allocation_pct": value / capital * 100,
            "max_by_risk": max_by_risk, "max_by_allocation": max_by_alloc,
            "estimated_cost_per_share": (entry * buy_cost_rate + stop * sell_cost_rate) * mult,
            "status": "OK" if qty else "NO_POSITION"}
