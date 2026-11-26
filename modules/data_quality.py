from __future__ import annotations
import numpy as np
import pandas as pd


def assess_data_quality(frame: pd.DataFrame, stale_after_days: int = 7, reference_date=None) -> dict:
    """Audit OHLCV structure without silently repairing or imputing source data."""
    if frame is None or frame.empty:
        return {"status": "ERROR", "score": 0, "issues": ["Không có dữ liệu."], "metrics": {}}
    required = ["date", "symbol", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        return {"status": "ERROR", "score": 0, "issues": ["Thiếu cột: " + ", ".join(missing)], "metrics": {}}

    x = frame.copy()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    for c in ["open", "high", "low", "close", "volume"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    numeric = x[["open", "high", "low", "close", "volume"]].to_numpy(dtype=float)
    finite_rows = np.isfinite(numeric).all(axis=1)
    date_bad = x["date"].isna()
    symbol_bad = x["symbol"].isna() | x["symbol"].astype(str).str.strip().str.upper().isin(["", "NAN", "NONE", "NULL", "UNKNOWN"])
    invalid_rows = int((date_bad | symbol_bad | ~finite_rows).sum())
    duplicate_rows = int(x.duplicated(["symbol", "date"], keep=False).sum())
    price_bad = (x[["open", "high", "low", "close"]] <= 0).any(axis=1)
    volume_bad = x["volume"] < 0
    ohlc_bad = (
        (x["high"] < x[["open", "low", "close"]].max(axis=1)) |
        (x["low"] > x[["open", "high", "close"]].min(axis=1))
    )
    invalid_price = int(price_bad.fillna(True).sum())
    invalid_ohlc = int(ohlc_bad.fillna(True).sum())
    negative_volume = int(volume_bad.fillna(True).sum())
    zero_volume = int((x["volume"] == 0).sum())
    last = x["date"].max()
    today = pd.Timestamp(reference_date).normalize() if reference_date is not None else pd.Timestamp.now().normalize()
    stale_days = int((today - last.normalize()).days) if pd.notna(last) else None
    future_dates = int((x["date"].dt.normalize() > today).sum())

    issues = []
    if invalid_rows: issues.append(f"{invalid_rows} dòng có ngày/mã/số liệu thiếu hoặc không hữu hạn.")
    if duplicate_rows: issues.append(f"{duplicate_rows} dòng thuộc nhóm trùng mã/ngày.")
    if invalid_price: issues.append(f"{invalid_price} dòng có giá OHLC không dương.")
    if invalid_ohlc: issues.append(f"{invalid_ohlc} dòng sai quan hệ OHLC.")
    if negative_volume: issues.append(f"{negative_volume} dòng có khối lượng âm.")
    if zero_volume: issues.append(f"Có {zero_volume} phiên khối lượng bằng 0; cần xác minh phiên không giao dịch/nguồn dữ liệu.")
    if future_dates: issues.append(f"Có {future_dates} ngày dữ liệu nằm trong tương lai.")
    if stale_days is not None and stale_days > stale_after_days:
        issues.append(f"Dữ liệu cuối cách hiện tại {stale_days} ngày; cần kiểm tra độ trễ.")

    hard_errors = any([invalid_rows, duplicate_rows, invalid_price, invalid_ohlc, negative_volume, future_dates])
    warning = bool(zero_volume or (stale_days is not None and stale_days > stale_after_days))
    status = "ERROR" if hard_errors else "WARNING" if warning else "OK"
    deductions = 20 * sum(bool(v) for v in [invalid_rows, duplicate_rows, invalid_price, invalid_ohlc, negative_volume, future_dates])
    if zero_volume: deductions += 5
    if stale_days is not None and stale_days > stale_after_days: deductions += 10
    score = max(0, 100 - deductions)
    return {
        "status": status, "score": score, "issues": issues or ["Không phát hiện lỗi cấu trúc cơ bản."],
        "metrics": {"rows": len(x), "symbols": int(x["symbol"].nunique(dropna=True)),
                    "start": x["date"].min(), "end": last, "stale_days": stale_days,
                    "duplicates": duplicate_rows, "invalid_rows": invalid_rows,
                    "invalid_price": invalid_price, "invalid_ohlc": invalid_ohlc,
                    "negative_volume": negative_volume, "zero_volume": zero_volume,
                    "future_dates": future_dates}
    }


def assess_snapshot_quality(frame: pd.DataFrame, stale_after_days: int = 7,
                            reference_date=None, min_rows: int = 50,
                            max_calendar_gap_days: int = 10) -> dict:
    """Snapshot-time validation: base OHLCV integrity plus history/freshness checks.

    Large date gaps and short history are warnings, not fabricated missing candles.
    A calendar gap is a review signal because exchange holidays may be legitimate.
    """
    result = assess_data_quality(frame, stale_after_days=stale_after_days,
                                 reference_date=reference_date)
    if frame is None or frame.empty or result.get("status") == "ERROR":
        return result
    x = frame.copy()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"]).sort_values("date")
    warnings = []
    if len(x) < int(min_rows):
        warnings.append(f"Lịch sử có {len(x)} phiên, dưới ngưỡng tham chiếu {int(min_rows)} phiên.")
    gaps = x["date"].diff().dt.days
    large_gaps = gaps[gaps > int(max_calendar_gap_days)]
    if not large_gaps.empty:
        warnings.append(f"Có {len(large_gaps)} khoảng cách ngày lớn hơn {int(max_calendar_gap_days)} ngày; cần đối chiếu lịch nghỉ và dữ liệu nguồn.")
    existing_issues = result.get("issues", [])
    result["issues"] = list(existing_issues) + warnings
    result["metrics"]["history_rows"] = int(len(x))
    result["metrics"]["large_calendar_gaps"] = int(len(large_gaps))
    if warnings and result.get("status") == "OK":
        result["status"] = "WARNING"
        result["score"] = max(0, int(result.get("score", 100)) - min(20, 5 * len(warnings)))
    return result
