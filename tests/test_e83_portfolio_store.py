from modules.portfolio_store import load_portfolio, save_portfolio, upsert_position


def test_portfolio_store_roundtrip(tmp_path):
    path = tmp_path / "portfolio.json"
    initial = load_portfolio(path)
    updated = upsert_position(initial, {"symbol": "aaa", "quantity": 100,
        "entry_price": 10_000, "market_price": 11_000, "stop_price": 9_500})
    updated["equity_vnd"] = 5_000_000
    save_portfolio(updated, path)
    loaded = load_portfolio(path)
    assert loaded["equity_vnd"] == 5_000_000
    assert loaded["positions"][0]["symbol"] == "AAA"
    assert loaded["positions"][0]["quantity"] == 100
