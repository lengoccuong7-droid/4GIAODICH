"""Portfolio-level risk assessment. Missing context is UNKNOWN, never zero."""
from __future__ import annotations
import math

def assess_portfolio_risk(portfolio: dict | None, proposed_value: float = 0.0,
                          max_single_position_pct: float = 25.0,
                          max_gross_exposure_pct: float = 80.0,
                          focus_symbol: str | None = None) -> dict:
    """Assess saved holdings and optional new exposure. Missing context is UNKNOWN."""
    if not isinstance(portfolio, dict):
        return {"status": "UNKNOWN", "hard_veto": False,
                "warnings": ["Chưa cung cấp dữ liệu danh mục; không giả định mức phơi nhiễm bằng 0."],
                "metrics": {}, "holdings": []}
    required = ("equity_vnd", "positions")
    if any(k not in portfolio for k in required):
        return {"status": "UNKNOWN", "hard_veto": False,
                "warnings": ["Thiếu equity_vnd hoặc positions để đánh giá rủi ro danh mục."],
                "metrics": {}, "holdings": []}
    try:
        equity = float(portfolio["equity_vnd"])
        positions = portfolio["positions"]
        proposed = float(proposed_value)
        if not math.isfinite(equity) or equity <= 0 or not isinstance(positions, list) or proposed < 0:
            raise ValueError
        values, risks, symbols = [], [], []
        for p in positions:
            if not isinstance(p, dict) or "market_value" not in p:
                raise ValueError
            value = float(p["market_value"])
            if not math.isfinite(value) or value < 0:
                raise ValueError
            values.append(value)
            symbols.append(str(p.get("symbol", "")).upper())
            stop_risk = p.get("risk_value")
            if stop_risk is not None:
                stop_risk = float(stop_risk)
                if not math.isfinite(stop_risk) or stop_risk < 0:
                    raise ValueError
                risks.append(stop_risk)
            else:
                risks.append(None)
    except (TypeError, ValueError, KeyError, OverflowError):
        return {"status": "ERROR", "hard_veto": True,
                "warnings": ["Dữ liệu danh mục thiếu hoặc không hợp lệ; không thể đánh giá phơi nhiễm."],
                "metrics": {}, "holdings": []}
    gross_existing = sum(values)
    gross = gross_existing + proposed
    exposure_pct = gross / equity * 100
    single_pct = proposed / equity * 100
    focus_value = sum(v for v, s in zip(values, symbols) if focus_symbol and s == str(focus_symbol).upper())
    focus_pct = focus_value / equity * 100 if focus_symbol else None
    veto = proposed > 0 and (exposure_pct > max_gross_exposure_pct or single_pct > max_single_position_pct)
    warnings = []
    if veto:
        warnings.append("Vượt giới hạn phơi nhiễm danh mục hoặc tỷ trọng vị thế mới.")
    if any(r is None for r in risks) and positions:
        warnings.append("Chưa có stop tham chiếu cho một hoặc nhiều vị thế; rủi ro giảm giá chưa tính đủ.")
    return {"status": "BLOCKED" if veto else "OK", "hard_veto": veto,
            "warnings": warnings,
            "metrics": {"equity_vnd": equity, "gross_exposure_vnd": gross,
                        "existing_exposure_vnd": gross_existing,
                        "gross_exposure_pct": exposure_pct, "proposed_position_pct": single_pct,
                        "focus_symbol_exposure_vnd": focus_value,
                        "focus_symbol_exposure_pct": focus_pct,
                        "known_stop_risk_vnd": sum(r for r in risks if r is not None)},
            "holdings": [{"symbol": s, "market_value": v, "risk_value": r}
                         for s, v, r in zip(symbols, values, risks)]}


import pandas as pd

def summarize_portfolio(positions: pd.DataFrame, capital_vnd: float, price_multiplier: float=1.0) -> dict:
    """Summarize holdings without treating a missing stop as zero risk."""
    if positions is None or positions.empty:
        return {"positions": pd.DataFrame(), "market_value": 0.0, "unrealized_pnl": 0.0,
                "exposure_pct": 0.0, "total_risk": 0.0, "risk_status": "KNOWN",
                "risk_coverage_pct": 100.0}
    x = positions.copy()
    for c in ["quantity", "entry_price"]:
        if c not in x:
            raise ValueError(f"Thiếu cột {c}")
        x[c] = pd.to_numeric(x[c], errors="coerce").fillna(0)
    if "market_price" not in x:
        x["market_price"] = x.entry_price
    x["market_price"] = pd.to_numeric(x["market_price"], errors="coerce").fillna(x.entry_price)
    x["market_value"] = x.quantity * x.market_price * price_multiplier
    x["cost_value"] = x.quantity * x.entry_price * price_multiplier
    x["unrealized_pnl"] = x.market_value - x.cost_value
    if "stop_price" in x:
        stops = pd.to_numeric(x["stop_price"], errors="coerce")
        x["risk_value"] = (x.entry_price - stops).clip(lower=0) * x.quantity * price_multiplier
        x.loc[stops.isna(), "risk_value"] = float("nan")
    else:
        x["risk_value"] = float("nan")
    mv = float(x.market_value.sum())
    known_risk = x.risk_value.dropna()
    risk_complete = len(known_risk) == len(x)
    total_risk = float(known_risk.sum()) if risk_complete else None
    coverage = len(known_risk) / len(x) * 100
    return {"positions": x, "market_value": mv,
            "unrealized_pnl": float(x.unrealized_pnl.sum()),
            "exposure_pct": mv / capital_vnd * 100 if capital_vnd else 0,
            "total_risk": total_risk,
            "risk_pct_of_capital": total_risk / capital_vnd * 100 if capital_vnd and total_risk is not None else None,
            "risk_status": "KNOWN" if risk_complete else "UNKNOWN",
            "risk_coverage_pct": coverage}
