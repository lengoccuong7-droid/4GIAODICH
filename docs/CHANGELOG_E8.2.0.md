# E8.2.0 — Centralized decision architecture

## Added
- ModuleResult contract adapter preserving legacy payloads.
- Central Decision Engine with canonical actions ENTER_LONG, WAIT, REDUCE, NO_TRADE.
- Portfolio-level risk assessment with explicit UNKNOWN state for missing context.
- Risk Gate veto and reason trace.
- Decision explanation and opt-in JSONL journal.
- Data Quality check before enrichment in unified snapshot.
- Snapshot ID and decision ID in the analysis payload.
- Backtest replay now consults the canonical engine and Risk Gate.
- UI shows final canonical action, Risk Gate status, portfolio-risk state, and recent journal records.

## Preserved
- Existing V6.3.1 analysis modules and legacy portfolio summary API.
- Exactly three main UI tabs.
- Manual CSV/Excel ingestion and local storage.
- Existing OHLCV formulas and Swing setup heuristics.

## Validation
- 87 tests passed.
- `compileall` passed (see release validation report).
- Streamlit UI runtime not exercised in the packaging environment.
