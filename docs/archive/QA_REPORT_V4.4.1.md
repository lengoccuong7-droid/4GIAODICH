# QA Report – V4.4.1

## Automated checks
- `pytest -q`: **41 passed**.
- `python -m compileall -q .`: **passed**.
- Navigation regression test confirms five named primary tabs and expected tab routing.
- Shared-analysis regression confirms the OHLCV flow/trap diagnostic is part of the shared context.
- Existing flow/trap tests cover insufficient history, false-breakout detection and the caveat that participant identity is unknown.

## Not performed
- Streamlit browser/UI runtime test and mobile layout verification (Streamlit is not installed in the build environment).
- Live market-data provider integration test.
- Walk-forward / out-of-sample strategy validation.
- Calibration of proxy thresholds against a broad, independently labelled dataset.

## Release status
V4.4.1 fixes navigation organization and exposes the flow/trap diagnostic in a dedicated top-level tab. Automated tests pass. It remains a research/QA build; do not interpret OHLCV proxies as proof of institutional trading or the strategy as validated for profitability.
