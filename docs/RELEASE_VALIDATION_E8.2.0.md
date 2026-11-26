# Release validation — E8.2.0

- Baseline source: user-provided `BOT_TRADER_SWING_MULTI_V6.3.1(1).zip`.
- Original archive was not modified.
- Automated tests: **87 passed**.
- Python compile check: **passed** (`python -m compileall -q app.py config.py modules tests`).
- Navigation source check: one `st.tabs(...)` call containing exactly three tabs.
- Streamlit runtime: **not verified** because Streamlit is not installed in the packaging environment.
- Real-market validation: not performed; use independently verified market data and walk-forward testing before relying on model performance.

## Important limitations
- Portfolio context absent is `UNKNOWN`, not zero risk. The default is warning-only; the engine API can require portfolio context.
- Backtest is a sequential single-position replay and is not yet a full simultaneous multi-symbol portfolio simulator.
- OHLCV-derived flow labels are proxies and do not identify foreign, proprietary, or institutional participants.
- No automatic data download or order execution is included.
