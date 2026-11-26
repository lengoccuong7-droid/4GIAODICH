# E8.4.6 — Walk-forward Validation

## Scope implemented

- Added `modules/walk_forward.py` with chronological expanding-window fold generation.
- Each fold separates train, validation and test ranges; the test range is strictly after validation.
- Candidate selection uses validation metrics only. The selected candidate is evaluated once on the untouched test interval.
- If no candidate reaches the minimum validation trade count or has a valid selection metric, the test is skipped and reported as such.
- No parameter search is run implicitly: callers must explicitly supply `parameter_candidates`.
- Added `test_end_index` to `modules/plan_backtest.py` so each fold is bounded at its own end; entries and exits cannot run beyond that boundary. Benchmark and sector data remain filtered as-of each decision in the existing replay.
- Updated the existing Trading Assistant backtest UI in `app.py` to invoke train/validation/test walk-forward rather than labeling a single 70/30 holdout as walk-forward.

## Tests

- `tests/test_e846_walk_forward.py`: 5 tests covering chronological/disjoint folds, invalid sizes, validation-only candidate selection, skipped tests when validation is insufficient, and test-end execution boundaries.
- Full test suite: **120 passed**.
- `python -m compileall -q app.py modules tests`: **PASS**.

## Important evidence limitation

A real execution of the existing strategy on a deterministic 260-session synthetic OHLCV/benchmark sample produced two chronological folds but **zero eligible out-of-sample tests** under the default minimum of three closed validation trades. The strategy did not produce enough validation trades to qualify a candidate. This is correctly returned as `NO_VALID_OOS_TESTS`; it is not evidence of profitability or strategy failure.

When the minimum validation trade threshold was deliberately set to zero and selection used total return, both test folds executed but each produced zero closed trades and 0% simulated return. This confirms the orchestration path, not strategy efficacy. Do not use that permissive setting for performance claims.

## Known limitations retained explicitly

- Fold portfolio/equity state is reported independently; capital and open positions are not yet carried continuously across fold boundaries.
- The current strategy has no automatic parameter optimization; only explicitly supplied candidates are compared.
- OHLCV cannot reconstruct order-book queue priority or exact intraday fills.
- Corporate actions and exchange calendars are not fully incorporated into this walk-forward runner.
- UI runtime was not executed in this environment; user will perform Streamlit runtime checks.
- Prior reported E8.4.1–E8.4.5 source changes were not present in the current worktree. This implementation is based on a fresh extraction of the E8.3.9 source archive and is not represented as an integrated E8.4.1–E8.4.5 codebase.

## Source integrity

Work was performed in `/mnt/data/work_e846/BOT_TRADER_SWING_MULTI_E8.3.9/`, a separate extraction. The source ZIP was not modified. No ZIP artifact was created.
