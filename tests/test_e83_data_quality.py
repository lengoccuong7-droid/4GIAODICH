import pandas as pd
import pytest
from modules.data_ingestion import prepare_market_upload
from modules.data_quality import assess_snapshot_quality


def test_ingestion_quality_rejects_invalid_ohlc_before_storage():
    frame = pd.DataFrame([("2026-11-20", "AAA", 10000, 9000, 9500, 9800, 1000)],
        columns=["date", "symbol", "open", "high", "low", "close", "volume"])
    with pytest.raises(ValueError, match="Data Quality từ chối"):
        prepare_market_upload(frame)


def test_snapshot_quality_warns_on_short_history_without_fabricating_rows():
    frame = pd.DataFrame({"date": pd.bdate_range("2026-01-01", periods=20),
        "symbol": "AAA", "open": 100, "high": 102, "low": 98, "close": 101, "volume": 1000})
    result = assess_snapshot_quality(frame, reference_date="2026-01-28", min_rows=50)
    assert result["status"] == "WARNING"
    assert result["metrics"]["history_rows"] == 20
    assert any("dưới ngưỡng" in item for item in result["issues"])
