import numpy as np
import pandas as pd
from modules.unified_analytics import enrich_once, build_unified_snapshot, analyze_accumulation_distribution
from modules.market_flow_trap import analyze_flow_and_traps


def market(symbol, base, seed=1, n=220):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2025-01-01', periods=n)
    close = base * np.exp(np.cumsum(rng.normal(0.0004, 0.012, n)))
    return pd.DataFrame({
        'date': dates, 'symbol': symbol, 'open': close * .998,
        'high': close * 1.012, 'low': close * .988,
        'close': close, 'volume': 900_000 + np.arange(n) * 1000,
    })


def test_canonical_ohlcv_features_are_shared_with_flow_module():
    raw = market('DXG', 10000)
    enriched = enrich_once(raw)
    flow = analyze_flow_and_traps(enriched)
    assert flow['status'] == 'OK'
    assert np.isclose(flow['metrics']['obv_proxy_level'], enriched['OBV_PROXY'].iloc[-1])
    assert np.isclose(flow['metrics']['flow_proxy_20'], enriched['SIGNED_VOLUME_PROXY'].tail(20).sum())


def test_unified_snapshot_has_one_identity_and_three_tab_payloads():
    stock = market('DXG', 10000, 1)
    benchmark = market('VNINDEX', 1200, 2)
    universe = pd.concat([stock, benchmark], ignore_index=True)
    snap = build_unified_snapshot('DXG', stock, universe=universe, benchmark=benchmark)
    assert snap['analysis_id']
    assert snap['swing_report']['symbol'] == 'DXG'
    assert snap['flow_trap']['status'] == 'OK'
    assert snap['structure_analysis']['status'] == 'OK'
    assert snap['calculation_contract']['snapshot_id'] == snap['analysis_id']
    assert snap['enriched'].iloc[-1]['OBV_PROXY'] == snap['flow_trap']['metrics']['obv_proxy_level']


def test_structure_analysis_refuses_short_history():
    raw = market('DXG', 10000, n=25)
    result = analyze_accumulation_distribution(enrich_once(raw))
    assert result['status'] == 'INSUFFICIENT_DATA'


def test_holdout_backtest_starts_at_requested_oos_boundary():
    from modules.plan_backtest import backtest_plan
    stock = market('DXG', 10000, seed=4, n=170)
    benchmark = market('VNINDEX', 1200, seed=5, n=170)
    split = 119
    result = backtest_plan(stock, benchmark=benchmark, warmup=60,
                           test_start_index=split, max_hold=10)
    assert 'error' not in result
    assert result['test_start_index'] == split
    assert result['sessions_tested'] == len(stock) - split


def test_snapshot_identity_changes_when_risk_configuration_changes():
    stock = market('DXG', 10000, seed=7)
    benchmark = market('VNINDEX', 1200, seed=8)
    a = build_unified_snapshot('DXG', stock, benchmark=benchmark, risk_pct=1.0)
    b = build_unified_snapshot('DXG', stock, benchmark=benchmark, risk_pct=1.5)
    assert a['data_fingerprint'] == b['data_fingerprint']
    assert a['analysis_id'] != b['analysis_id']


def test_historical_data_quality_uses_asof_date_not_current_date():
    from modules.data_quality import assess_data_quality
    raw = market('DXG', 10000, seed=10, n=80)
    result = assess_data_quality(raw, reference_date=raw.date.max())
    assert result['metrics']['stale_days'] == 0


def test_live_snapshot_ignores_future_benchmark_rows():
    stock = market('DXG', 10000, seed=11, n=120)
    benchmark = market('VNINDEX', 1200, seed=12, n=140)
    base = build_unified_snapshot('DXG', stock, benchmark=benchmark.iloc[:120])
    extended = build_unified_snapshot('DXG', stock, benchmark=benchmark)
    assert base['data_fingerprint'] == extended['data_fingerprint']
    assert base['analysis_id'] == extended['analysis_id']


def test_relative_volume_uses_prior_completed_twenty_sessions():
    raw = market('DXG', 10000, seed=13, n=30)
    enriched = enrich_once(raw)
    expected = float(raw.volume.iloc[-1] / raw.volume.iloc[-21:-1].mean())
    assert np.isclose(enriched['REL_VOLUME20'].iloc[-1], expected)
    assert np.isclose(enriched['VOL_MA20'].iloc[-1], raw.volume.iloc[-21:-1].mean())
