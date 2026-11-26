"""Small local JSON store for user-entered simulated portfolio positions."""
from __future__ import annotations
import json
import math
from pathlib import Path
from datetime import datetime, timezone


def load_portfolio(path="data/portfolio_positions.json") -> dict:
    target = Path(path)
    if not target.exists():
        return {"equity_vnd": None, "positions": [], "updated_at": None}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("positions", []), list):
            raise ValueError("Portfolio JSON không đúng cấu trúc")
        data.setdefault("equity_vnd", None)
        data.setdefault("updated_at", None)
        return data
    except (OSError, json.JSONDecodeError, ValueError):
        return {"equity_vnd": None, "positions": [], "updated_at": None, "load_error": True}


def save_portfolio(portfolio: dict, path="data/portfolio_positions.json") -> str:
    if not isinstance(portfolio, dict) or not isinstance(portfolio.get("positions"), list):
        raise ValueError("Danh mục không hợp lệ")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"equity_vnd": portfolio.get("equity_vnd"),
               "positions": portfolio.get("positions", []),
               "updated_at": datetime.now(timezone.utc).isoformat()}
    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(target)
    return str(target)


def upsert_position(portfolio: dict, position: dict) -> dict:
    symbol = str(position.get("symbol", "")).strip().upper()
    if not symbol:
        raise ValueError("Thiếu mã cổ phiếu")
    required = ("quantity", "entry_price", "market_price")
    if any(position.get(key) is None for key in required):
        raise ValueError("Cần nhập số lượng, giá vốn và giá hiện tại")
    qty = int(position["quantity"])
    entry = float(position["entry_price"])
    market = float(position["market_price"])
    if qty <= 0 or entry <= 0 or market <= 0 or not all(math.isfinite(v) for v in (entry, market)):
        raise ValueError("Số lượng và giá phải là số hữu hạn lớn hơn 0")
    stop = position.get("stop_price")
    stop = float(stop) if stop not in (None, "") else None
    if stop is not None and (stop <= 0 or not math.isfinite(stop)):
        raise ValueError("Stop tham chiếu phải là số hữu hạn lớn hơn 0")
    normalized = {"symbol": symbol, "quantity": qty, "entry_price": entry,
                  "market_price": market, "stop_price": stop}
    result = [p for p in portfolio.get("positions", []) if str(p.get("symbol", "")).upper() != symbol]
    result.append(normalized)
    return {"equity_vnd": portfolio.get("equity_vnd"), "positions": result}
