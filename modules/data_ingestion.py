"""Prepare manually supplied OHLCV files before persisting them."""
from __future__ import annotations
import pandas as pd
from modules.price_units import normalize_price_unit
from modules.data_quality import assess_data_quality


def prepare_market_upload(frame: pd.DataFrame, price_multiplier: float = 1.0) -> tuple[pd.DataFrame, dict]:
    required = ["date", "symbol", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError("Thiếu cột dữ liệu: " + ", ".join(missing))
    staged = frame[required].copy()
    staged["symbol"] = (
        staged["symbol"].astype(str).str.strip().str.upper()
        .str.replace("-", "", regex=False).str.replace("_", "", regex=False)
    )
    if staged["symbol"].isin(["", "NAN", "NONE", "NULL", "UNKNOWN"]).any():
        raise ValueError("Có dòng thiếu mã hợp lệ; không cập nhật kho dữ liệu.")
    if staged.duplicated(["symbol", "date"]).any():
        raise ValueError("Tệp có mã/ngày trùng lặp; hãy làm sạch trước khi cập nhật.")

    index_mask = staged["symbol"].eq("VNINDEX")
    stock_rows = staged.loc[~index_mask].copy()
    index_rows = staged.loc[index_mask].copy()
    if not stock_rows.empty:
        median_price = float(pd.to_numeric(stock_rows["close"], errors="coerce").median())
        multiplier = float(price_multiplier)
        if multiplier == 1000.0 and median_price >= 1000:
            raise ValueError("Giá trong tệp có vẻ đã là đồng/cổ phiếu. Chọn Đồng/cổ phiếu để tránh nhân 1.000 lần.")
        if multiplier == 1.0 and 0 < median_price < 1000:
            raise ValueError("Giá trong tệp có vẻ đang ở nghìn đồng/cổ phiếu. Chọn Nghìn đồng/cổ phiếu nếu đúng nguồn.")
        stock_rows = normalize_price_unit(stock_rows, multiplier)
    # VNINDEX is an index level, never scaled as a stock price.
    result = pd.concat([stock_rows, index_rows], ignore_index=True).sort_values(["symbol", "date"])
    result = result.reset_index(drop=True)
    quality = assess_data_quality(result)
    if quality.get("status") == "ERROR":
        raise ValueError("Data Quality từ chối dữ liệu nhập: " + "; ".join(quality.get("issues", [])))
    return result, {
        "stock_rows": len(stock_rows), "benchmark_rows": len(index_rows),
        "price_multiplier": float(price_multiplier), "benchmark_symbol": "VNINDEX" if len(index_rows) else None,
        "data_quality": quality,
    }
