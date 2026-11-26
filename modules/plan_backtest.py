"""Replay of the app's OWN 3-10 session trade plan (trigger/stop/target) with VN-market frictions and a date-aligned VN-Index regime.

Rules: signal at close t -> entry only if price reaches trigger within `valid_sessions`
(no chasing above the entry zone); T+2: cannot sell before entry_day+2; gaps exit at open;
if stop and target are both touched in one bar, stop wins (conservative); +/-limit% price band;
fees/tax/slippage. Educational validation, not a profit guarantee.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .unified_analytics import enrich_once, evaluate_unified_decision
from .data_quality import assess_data_quality
from .relative_strength import relative_strength
from .market_regime import assess_market_regime
from .central_decision_engine import decide as central_decide
from .portfolio_manager import assess_portfolio_risk
from .price_limit_engine import calculate_price_limits
from .execution_simulator import simulate_limit_order
from .market_flow_trap import analyze_flow_and_traps


def backtest_plan(frame, benchmark=None, warmup=60, capital=100_000_000, risk_pct=1.0, max_alloc_pct=20.0,
                  fee_pct=0.15, tax_pct=0.10, slip_pct=0.10, limit_pct=7.0,
                  valid_sessions=3, max_hold=10, risk_style="CÂN BẰNG", test_start_index=None,
                  sector=None, test_end_index=None, max_participation_rate=0.05, tick_size=1):
    x = enrich_once(frame.sort_values("date").copy()).reset_index(drop=True)
    n = len(x)
    if n < warmup + 30:
        return {"error": f"Cần ít nhất {warmup + 30} phiên để kiểm chứng."}
    if benchmark is None or benchmark.empty:
        return {"error": "Cần dữ liệu VN-Index đồng bộ để kiểm chứng; không dùng một cổ phiếu làm đại diện thị trường."}
    bmk = benchmark.copy()
    bmk["date"] = pd.to_datetime(bmk["date"], errors="coerce")
    bmk = bmk.dropna(subset=["date"]).sort_values("date")
    fee, slip, tax, lim = fee_pct / 100, slip_pct / 100, tax_pct / 100, limit_pct / 100
    start_index = max(int(warmup), int(test_start_index if test_start_index is not None else warmup))
    end_index = min(n - 1, int(test_end_index) if test_end_index is not None else n - 1)
    if end_index <= start_index:
        return {"error": "Mốc bắt đầu kiểm định ngoài mẫu không còn đủ dữ liệu phía sau."}
    trades, signals, i = [], 0, start_index
    replay_errors = []
    while i < end_index:
        try:
            asof = pd.to_datetime(x.date.iloc[i])
            benchmark_history = bmk[bmk.date <= asof]
            regime = assess_market_regime(benchmark_history)
            history = x.iloc[:i + 1].copy()
            history_quality = assess_data_quality(history, reference_date=asof)
            rs_m = relative_strength(history, benchmark_history, 20)
            sector_history = None
            if sector is not None and not sector.empty:
                sector_history = sector[pd.to_datetime(sector.date) <= asof].copy()
            rs_s = relative_strength(history, sector_history, 20) if sector_history is not None and not sector_history.empty else {}
            rep, _, _ = evaluate_unified_decision(history, market_regime=regime,
                rs_market=rs_m, rs_sector=rs_s, data_quality=history_quality,
                capital_vnd=capital, risk_pct=risk_pct, max_alloc_pct=max_alloc_pct,
                fee_pct=fee_pct, slippage_pct=slip_pct, tax_pct=tax_pct)
        except Exception as exc:
            replay_errors.append({"date": str(x.date.iloc[i]), "error": f"{type(exc).__name__}: {exc}"})
            i += 1
            continue
        proposed_value = float((rep.get("sizing") or {}).get("position_value") or 0.0)
        portfolio_risk = assess_portfolio_risk(
            {"equity_vnd": float(capital), "positions": []},
            proposed_value=proposed_value)
        canonical = central_decide(rep, portfolio_risk=portfolio_risk)
        if canonical.get("final_action") != "ENTER_LONG":
            i += 1
            continue
        signals += 1
        p = rep["plan"]; trig, stop, tgt, zhi = p["reference_trigger"], p["invalidation"], p["target_1"], p["entry_zone_high"]
        ent = None
        requested_qty = int((rep.get("sizing") or {}).get("quantity") or 0)
        if requested_qty <= 0:
            i += 1
            continue
        for j in range(i + 1, min(i + 1 + valid_sessions, end_index + 1)):
            b, pc = x.iloc[j], float(x.close.iloc[j - 1])
            if b.high >= trig and b.open <= zhi:
                fill_check = simulate_limit_order(
                    side="BUY", quantity=requested_qty, limit_price=float(zhi),
                    open_price=float(b.open), high=float(b.high), low=float(b.low),
                    volume=float(b.volume), participation_rate=max_participation_rate,
                    tick_size=tick_size)
                if fill_check["filled_quantity"] <= 0:
                    continue
                limits = calculate_price_limits(pc, limit_pct, tick_size=tick_size)
                base_fill = float(fill_check["fill_price"])
                f = min(base_fill * (1 + slip), float(limits["upper_limit"]), float(b.high))
                ent = (j, f, fill_check["filled_quantity"], requested_qty)
                break
        if ent is None:
            i += 1; continue
        j, ef, filled_qty, requested_qty = ent
        xi, xp, reason = None, None, None
        for k in range(j + 2, min(j + max_hold, end_index) + 1):  # T+2
            b, pc = x.iloc[k], float(x.close.iloc[k - 1])
            if b.open <= stop: xi, xp, reason = k, float(b.open), "STOP_GAP"
            elif b.low <= stop: xi, xp, reason = k, stop, "STOP"
            elif b.open >= tgt: xi, xp, reason = k, float(b.open), "TARGET_GAP"
            elif b.high >= tgt: xi, xp, reason = k, tgt, "TARGET"
            if xi is not None: break
        open_pos = False
        if xi is None:
            xi = min(j + max_hold, end_index); xp = float(x.close.iloc[xi]); reason = "TIME_EXIT"
            open_pos = (xi == end_index and j + max_hold > end_index)
        pc = float(x.close.iloc[xi - 1]); xp = max(xp * (1 - slip), pc * (1 - lim))
        cost_in = ef * (1 + fee); net_out = xp * (1 - fee - tax)
        ret = net_out / cost_in - 1; risk_unit = max(ef - stop, 1e-9)
        trades.append({"signal_date": str(x.date.iloc[i].date()), "entry_date": str(x.date.iloc[j].date()),
                       "exit_date": str(x.date.iloc[xi].date()), "entry": round(ef, 0), "exit": round(xp, 0),
                       "stop": round(stop, 0), "target": round(tgt, 0), "reason": reason,
                       "return_pct": ret * 100, "r_multiple": (net_out - cost_in) / risk_unit,
                       "setup": rep.get("setup"), "open_at_end": open_pos,
                       "requested_quantity": requested_qty, "filled_quantity": filled_qty,
                       "fill_ratio": filled_qty / requested_qty if requested_qty else 0.0})
        i = xi + 1
    closed = [t for t in trades if not t["open_at_end"]]
    open_positions = [t for t in trades if t["open_at_end"]]
    eq, curve = 1.0, [1.0]
    for t in closed:
        frac = min(max_alloc_pct / 100, (risk_pct / 100) / max((t["entry"] - t["stop"]) / t["entry"], 1e-9))
        frac *= float(t.get("fill_ratio", 1.0))
        eq *= 1 + frac * t["return_pct"] / 100; curve.append(eq)
    c = pd.Series(curve); r = [t["return_pct"] for t in closed]
    wins = sum(v for v in r if v > 0); loss = -sum(v for v in r if v < 0)
    bh = (float(x.close.iloc[end_index]) / float(x.close.iloc[start_index]) - 1) * 100
    return {"signals": signals, "trades": trades, "closed_trades": len(closed),
            "replay_errors": replay_errors, "replay_error_count": len(replay_errors),
            "decision_engine": "CENTRAL-1.2", "risk_gate_enabled": True,
            "execution_model": "OHLCV_LIMIT_APPROXIMATION",
            "max_participation_rate": max_participation_rate,
            "open_positions": len(open_positions),
            "win_rate_pct": (sum(v > 0 for v in r) / len(r) * 100) if r else None,
            "avg_r": float(np.mean([t["r_multiple"] for t in closed])) if closed else None,
            "expectancy_pct": float(np.mean(r)) if r else None,
            "profit_factor": (wins / loss) if loss else None,
            "total_return_pct": (eq - 1) * 100, "max_drawdown_pct": float((c / c.cummax() - 1).min() * 100),
            "buy_hold_pct": bh, "sessions_tested": end_index - start_index + 1,
            "test_start_index": start_index, "test_end_index": end_index,
            "enough_sample": len(closed) >= 30,
            "note": "Chỉ tính lệnh đã đóng trong thống kê hiệu suất; vị thế còn mở được báo riêng. Mẫu dưới 30 lệnh chưa đủ ý nghĩa thống kê. Quá khứ không đảm bảo tương lai."}


def trap_forward_stats(frame, warmup=60, horizon=5):
    """Forward return after each trap_risk / flow_bias state (all bars, no lookahead)."""
    x = frame.sort_values("date").reset_index(drop=True); rows = []
    for i in range(warmup, len(x) - horizon):
        ft = analyze_flow_and_traps(x.iloc[: i + 1])
        if ft.get("status") != "OK": continue
        rows.append({"trap_risk": ft["trap_risk"], "flow_bias": ft["flow_bias"],
                     "fwd": (float(x.close.iloc[i + horizon]) / float(x.close.iloc[i]) - 1) * 100})
    if not rows: return {}
    d = pd.DataFrame(rows)
    def agg(col):
        return {k: {"count": int(len(g)), "avg_fwd_pct": float(g.fwd.mean()), "pct_positive": float((g.fwd > 0).mean() * 100)}
                for k, g in d.groupby(col)}
    return {"horizon_sessions": horizon, "by_trap_risk": agg("trap_risk"), "by_flow_bias": agg("flow_bias"),
            "baseline_avg_pct": float(d.fwd.mean())}
