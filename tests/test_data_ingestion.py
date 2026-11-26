import pandas as pd
import pytest
from modules.data_ingestion import prepare_market_upload


def test_stock_prices_scaled_but_vnindex_is_not():
    raw = pd.DataFrame([
        ("2026-01-01", "DXG", 15.0, 15.5, 14.8, 15.2, 1000),
        ("2026-01-01", "VNINDEX", 1200, 1210, 1190, 1205, 100000),
    ], columns=["date", "symbol", "open", "high", "low", "close", "volume"])
    out, meta = prepare_market_upload(raw, price_multiplier=1000)
    stock = out[out.symbol == "DXG"].iloc[0]
    index = out[out.symbol == "VNINDEX"].iloc[0]
    assert stock.close == 15200
    assert index.close == 1205
    assert meta["stock_rows"] == 1
    assert meta["benchmark_rows"] == 1


def test_rejects_suspicious_price_unit():
    raw = pd.DataFrame([
        ("2026-01-01", "FPT", 10000, 10100, 9900, 10050, 1000),
    ], columns=["date", "symbol", "open", "high", "low", "close", "volume"])
    with pytest.raises(ValueError, match="đồng/cổ phiếu"):
        prepare_market_upload(raw, price_multiplier=1000)
