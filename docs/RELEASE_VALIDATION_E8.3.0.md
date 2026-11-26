# Release validation — E8.3.0

- Baseline: `BOT_TRADER_SWING_MULTI_E8.2.0.zip`; original archive left untouched.
- Scope: incremental implementation of the three approved E8.3 corrections, plus two-stage data-quality checks retained within the existing architecture.
- Automated tests: **99 passed**.
- Python compile check: **passed** (`python -m compileall -q app.py config.py modules tests`).
- Navigation source check: exactly one `st.tabs(...)` call with exactly three tabs; existing navigation regression tests pass.
- Streamlit runtime: **not verified**. Streamlit is not installed in the packaging environment and package installation could not reach the package index.
- Real-market validation: not performed; synthetic sample data is not market evidence.
- Original E8.2.0 ZIP: unchanged.

## Implemented E8.3 changes

1. ENTER_LONG / WAIT / REDUCE receive distinct action-plan types; WAIT on an existing position becomes HOLD_AND_MONITOR; NO_TRADE bypasses Action Plan.
2. Processing contract is Data Quality → Enrich Once → Unified Snapshot → Analysis Modules. Enrich Once remains a processing step, not a new architectural layer.
3. Tab 3 can save user-entered simulated holdings locally. The shared snapshot passes the validated holdings into Portfolio Manager and Central Decision Engine. Missing portfolio context remains UNKNOWN.
4. Data quality is checked before storage and checked again at snapshot time for freshness, minimum history and large calendar gaps. Large gaps are warnings because exchange holidays can be legitimate.

## Known limitations

- Portfolio is user-entered and local; no broker/account synchronization.
- Portfolio metrics are only as complete as the holdings, prices, equity and stop references entered by the user.
- Backtest is sequential single-position replay, not simultaneous multi-symbol portfolio simulation.
- OHLCV-derived flow values are proxies, not participant identity or order-flow data.
- No automatic order execution.
