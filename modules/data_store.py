"""Local, offline-first OHLCV history store for manual CSV/XLSX updates."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional
import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS market_history (
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, date)
);
CREATE INDEX IF NOT EXISTS idx_market_history_date ON market_history(date);
"""


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=20)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def upsert_market_data(frame: pd.DataFrame, db_path: str | Path) -> dict:
    """Insert new symbol/date rows and update corrected existing rows."""
    required = ["date", "symbol", "open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise ValueError("Thiếu cột dữ liệu: " + ", ".join(missing))
    data = frame[required].copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    data["symbol"] = data["symbol"].astype(str).str.strip().str.upper()
    if data[required].isna().any().any():
        raise ValueError("Dữ liệu có ô trống hoặc ngày không hợp lệ; không cập nhật kho.")
    if data.duplicated(["symbol", "date"]).any():
        raise ValueError("Tệp có mã/ngày trùng lặp; hãy xử lý trước khi cập nhật.")

    inserted = updated = unchanged = 0
    with _connect(db_path) as conn:
        for row in data.itertuples(index=False, name=None):
            date, symbol, opn, high, low, close, volume = row
            old = conn.execute(
                "SELECT open,high,low,close,volume FROM market_history WHERE symbol=? AND date=?",
                (symbol, date),
            ).fetchone()
            values = tuple(float(v) for v in (opn, high, low, close, volume))
            if old is None:
                conn.execute(
                    "INSERT INTO market_history(symbol,date,open,high,low,close,volume) VALUES(?,?,?,?,?,?,?)",
                    (symbol, date, *values),
                )
                inserted += 1
            elif all(abs(float(a) - b) <= max(1e-9, abs(b) * 1e-10) for a, b in zip(old, values)):
                unchanged += 1
            else:
                conn.execute(
                    "UPDATE market_history SET open=?,high=?,low=?,close=?,volume=?,updated_at=CURRENT_TIMESTAMP WHERE symbol=? AND date=?",
                    (*values, symbol, date),
                )
                updated += 1
    return {"inserted": inserted, "updated": updated, "unchanged": unchanged, "received": len(data)}


def load_market_history(db_path: str | Path, symbols: Optional[list[str]] = None) -> pd.DataFrame:
    path = Path(db_path)
    if not path.exists():
        return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])
    with _connect(path) as conn:
        if symbols:
            marks = ",".join("?" for _ in symbols)
            rows = pd.read_sql_query(
                f"SELECT date,symbol,open,high,low,close,volume FROM market_history WHERE symbol IN ({marks}) ORDER BY symbol,date",
                conn, params=[s.upper() for s in symbols],
            )
        else:
            rows = pd.read_sql_query(
                "SELECT date,symbol,open,high,low,close,volume FROM market_history ORDER BY symbol,date", conn
            )
    if not rows.empty:
        rows["date"] = pd.to_datetime(rows["date"], errors="coerce")
    return rows


def market_history_summary(db_path: str | Path) -> dict:
    path = Path(db_path)
    if not path.exists():
        return {"symbols": 0, "rows": 0, "latest_date": None}
    with _connect(path) as conn:
        symbols, rows, latest = conn.execute(
            "SELECT COUNT(DISTINCT symbol),COUNT(*),MAX(date) FROM market_history"
        ).fetchone()
    return {"symbols": int(symbols or 0), "rows": int(rows or 0), "latest_date": latest}
