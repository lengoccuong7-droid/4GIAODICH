"""Single shared analytical context for all analysis views and the Swing decision engine.

All tab renderers should read this immutable-by-convention snapshot instead of
recomputing market/RS/timeframe/quality facts independently.
"""
from __future__ import annotations
import hashlib
import json
import pandas as pd
from .market_analysis import analyze_symbol
from .market_regime import assess_market_regime
from .relative_strength import relative_strength
from .multi_timeframe import timeframe_snapshot
from .data_quality import assess_data_quality
from .market_flow_trap import analyze_flow_and_traps


def _frame_fingerprint(frame: pd.DataFrame | None) -> str:
    if frame is None or frame.empty:
        return "EMPTY"
    cols = [c for c in ("symbol", "date", "open", "high", "low", "close", "volume") if c in frame]
    ordered = frame[cols].copy()
    if "date" in ordered:
        ordered["date"] = pd.to_datetime(ordered["date"], errors="coerce").astype(str)
    # Hash every row so edits to older history invalidate cached/shared analysis IDs.
    row_hashes = pd.util.hash_pandas_object(ordered.astype(str), index=False).values.tobytes()
    payload = f"{len(ordered)}|{','.join(cols)}|".encode() + row_hashes
    return hashlib.sha256(payload).hexdigest()[:16]


def build_shared_analysis_context(symbol: str, raw: pd.DataFrame, enriched: pd.DataFrame,
                                  universe: pd.DataFrame | None = None,
                                  benchmark: pd.DataFrame | None = None,
                                  sector: pd.DataFrame | None = None,
                                  capital_vnd: float = 100_000_000,
                                  risk_pct: float = 1.0,
                                  max_alloc_pct: float = 20.0,
                                  lot_size: int = 100) -> dict:
    """Build one coherent snapshot shared by Analysis, Assistant and Swing."""
    symbol = str(symbol or "").strip().upper()
    if not symbol or symbol in {"UNKNOWN", "NONE", "NAN"}:
        raise ValueError("Mã cổ phiếu chưa hợp lệ; không thể tạo phiên phân tích.")
    if raw is None or raw.empty or "symbol" not in raw:
        raise ValueError("Thiếu OHLCV hoặc trường mã cổ phiếu.")
    symbols = set(raw.symbol.astype(str).str.strip().str.upper())
    if symbol not in symbols:
        raise ValueError(f"Mã {symbol} không khớp dữ liệu OHLCV đã chọn.")
    market_frame = universe.copy() if universe is not None else raw.copy()
    if benchmark is not None and not benchmark.empty:
        # Explicit benchmark upload takes precedence over any same-symbol rows in the universe.
        market_frame = pd.concat([market_frame, benchmark], ignore_index=True)
        if {"symbol", "date"}.issubset(market_frame.columns):
            market_frame = market_frame.drop_duplicates(["symbol", "date"], keep="last")
    regime = assess_market_regime(market_frame)
    rs_market = relative_strength(raw, benchmark, 20) if benchmark is not None else {}
    rs_sector = relative_strength(raw, sector, 20) if sector is not None else {}
    mtf = timeframe_snapshot(raw)
    quality = assess_data_quality(raw)
    flow_trap = analyze_flow_and_traps(enriched)
    _, decision = analyze_symbol(raw, capital_vnd=float(capital_vnd), risk_pct=float(risk_pct),
                                 max_alloc_pct=float(max_alloc_pct), lot_size=int(lot_size))
    fingerprint = _frame_fingerprint(raw)
    analysis_id = hashlib.sha256(f"{symbol}|{fingerprint}".encode()).hexdigest()[:20]
    return {
        "schema_version": "1.0", "symbol": symbol, "analysis_id": analysis_id,
        "data_fingerprint": fingerprint,
        "data_timestamp": str(pd.to_datetime(raw.date).max()) if "date" in raw else None,
        "market_regime": regime, "rs_market": rs_market, "rs_sector": rs_sector,
        "multi_timeframe": mtf, "data_quality": quality,
        "flow_trap": flow_trap,
        "decision_engine": decision,
    }
