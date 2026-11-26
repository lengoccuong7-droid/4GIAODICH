import pandas as pd
from modules.data_store import upsert_market_data, load_market_history, market_history_summary


def frame(rows):
    return pd.DataFrame(rows, columns=["date", "symbol", "open", "high", "low", "close", "volume"])


def test_upsert_appends_updates_and_avoids_duplicates(tmp_path):
    db = tmp_path / "history.sqlite3"
    first = frame([
        ("2026-01-01", "DXG", 10, 11, 9, 10.5, 1000),
        ("2026-01-02", "VNINDEX", 1200, 1210, 1190, 1205, 100000),
    ])
    result = upsert_market_data(first, db)
    assert result["inserted"] == 2
    assert result["updated"] == 0
    assert result["unchanged"] == 0

    second = frame([
        ("2026-01-01", "DXG", 10, 11, 9, 10.6, 1000),
        ("2026-01-03", "DXG", 10.6, 11, 10.2, 10.8, 1500),
    ])
    result = upsert_market_data(second, db)
    assert result["inserted"] == 1
    assert result["updated"] == 1
    assert result["unchanged"] == 0

    loaded = load_market_history(db)
    assert len(loaded) == 3
    assert float(loaded[(loaded.symbol == 'DXG') & (loaded.date == pd.Timestamp('2026-01-01'))].close.iloc[0]) == 10.6
    summary = market_history_summary(db)
    assert summary == {"symbols": 2, "rows": 3, "latest_date": "2026-01-03"}


def test_upsert_identical_rows_are_unchanged(tmp_path):
    db = tmp_path / "history.sqlite3"
    data = frame([("2026-01-01", "FPT", 10, 11, 9, 10.5, 1000)])
    upsert_market_data(data, db)
    result = upsert_market_data(data, db)
    assert result["unchanged"] == 1
    assert result["inserted"] == 0
    assert result["updated"] == 0
