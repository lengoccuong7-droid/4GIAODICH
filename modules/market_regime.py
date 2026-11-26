from __future__ import annotations
import pandas as pd
from .indicators import add_indicators


def assess_market_regime(data: pd.DataFrame, benchmark_symbol: str | None = None,
                         min_breadth_symbols: int = 5) -> dict:
    """Assess market regime only from a real benchmark or a broad enough universe.

    A single stock is never accepted as a proxy for the whole market.
    """
    if data is None or data.empty or "symbol" not in data:
        return {"regime": "CHƯA ĐỦ DỮ LIỆU", "confidence": "THẤP",
                "reasons": ["Chưa có dữ liệu thị trường hoặc benchmark."]}
    frame = data.copy()
    frame["symbol"] = frame["symbol"].astype(str).str.strip().str.upper()
    symbols = set(frame.symbol.unique())
    benchmark = str(benchmark_symbol).upper() if benchmark_symbol else None
    if benchmark not in symbols:
        benchmark = "VNINDEX" if "VNINDEX" in symbols else None
    if benchmark:
        e = add_indicators(frame[frame.symbol == benchmark].sort_values("date"))
        r = e.iloc[-1]
        c, m20, m50 = r.get("close"), r.get("SMA20"), r.get("SMA50")
        if pd.notna(c) and pd.notna(m20) and pd.notna(m50):
            m20_old = e.iloc[-6].get("SMA20") if len(e) >= 6 else None
            ret20 = (float(c) / float(e.close.iloc[-21]) - 1) * 100 if len(e) >= 21 and float(e.close.iloc[-21]) > 0 else None
            rising = pd.notna(m20_old) and float(m20) > float(m20_old)
            falling = pd.notna(m20_old) and float(m20) < float(m20_old)
            if c > m20 > m50 and rising and (ret20 is None or ret20 > 0):
                regime, status = "TĂNG", "THUẬN LỢI"
            elif (c < m20 < m50 and falling) or (ret20 is not None and ret20 <= -5.0):
                regime, status = "GIẢM", "RỦI RO"
            else:
                regime, status = "ĐI NGANG/CHUYỂN PHA", "TRUNG TÍNH"
            reasons = [f"{benchmark}: Close {c:,.2f}; MA20 {m20:,.2f}; MA50 {m50:,.2f}; MA20 {'tăng' if rising else 'giảm' if falling else 'chưa rõ độ dốc'}."]
            if ret20 is not None:
                reasons.append(f"Biến động 20 phiên: {ret20:+.2f}%.")
            return {"regime": regime, "status_label": status, "confidence": "TRUNG BÌNH", "benchmark": benchmark,
                    "return_20_pct": ret20, "reasons": reasons}
        return {"regime": "CHƯA ĐỦ DỮ LIỆU", "confidence": "THẤP", "benchmark": benchmark,
                "reasons": [f"Có benchmark {benchmark} nhưng chưa đủ dữ liệu tính MA20/MA50."]}

    # Breadth is a fallback only for a genuinely broad cross-section.
    if len(symbols) < int(min_breadth_symbols):
        return {"regime": "CHƯA ĐỦ DỮ LIỆU", "confidence": "THẤP",
                "reasons": [f"Không có VN-Index; chỉ có {len(symbols)} mã. Cần benchmark hoặc tối thiểu {min_breadth_symbols} mã để ước lượng độ rộng thị trường."]}
    states = []
    for _, f in frame.groupby("symbol"):
        e = add_indicators(f.sort_values("date"))
        r = e.iloc[-1]
        if pd.notna(r.get("SMA20")) and pd.notna(r.get("SMA50")):
            states.append(bool(r.close > r.SMA20 > r.SMA50))
    if len(states) < min_breadth_symbols:
        return {"regime": "CHƯA ĐỦ DỮ LIỆU", "confidence": "THẤP",
                "reasons": [f"Chỉ {len(states)} mã có đủ dữ liệu MA20/MA50; cần ít nhất {min_breadth_symbols} mã."]}
    breadth = sum(states) / len(states)
    regime = "TĂNG" if breadth >= .65 else ("GIẢM" if breadth <= .35 else "PHÂN HÓA/ĐI NGANG")
    status = "THUẬN LỢI" if regime == "TĂNG" else "RỦI RO" if regime == "GIẢM" else "TRUNG TÍNH"
    return {"regime": regime, "status_label": status, "confidence": "THẤP", "breadth": breadth,
            "source_type": "BREADTH_PROXY",
            "reasons": [f"Độ rộng thị trường ước lượng từ {len(states)} mã: {breadth:.1%} mã có Close > MA20 > MA50; đây không thay thế VN-Index."]}
