import numpy as np
import pandas as pd
import pytest

from modules.walk_forward import build_walk_forward_folds, walk_forward_validate


def _market(symbol, n=300, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2025-01-01', periods=n)
    close = 10000 * np.exp(np.cumsum(rng.normal(0.0003, 0.01, n)))
    return pd.DataFrame({
        'date': dates, 'symbol': symbol, 'open': close * .999,
        'high': close * 1.01, 'low': close * .99,
        'close': close, 'volume': 500000 + np.arange(n) * 100,
    })


def test_fold_ranges_are_chronological_disjoint_and_expanding():
    folds = build_walk_forward_folds(400, warmup=50, train_size=100,
                                     validation_size=30, test_size=40, step_size=40)
    assert len(folds) == 5
    for f in folds:
        assert f['train_end'] < f['validation_start']
        assert f['validation_end'] < f['test_start']
        assert f['test_start'] <= f['test_end']
    assert folds[1]['train_end'] > folds[0]['train_end']


def test_fold_builder_rejects_invalid_sizes():
    with pytest.raises(ValueError):
        build_walk_forward_folds(100, warmup=0)
    with pytest.raises(ValueError):
        build_walk_forward_folds(100, step_size=0)


def test_walk_forward_selects_only_on_validation_and_tests_once():
    stock, benchmark = _market('AAA'), _market('VNINDEX', seed=2)
    calls = []

    def fake_backtest(frame, benchmark=None, warmup=50, test_start_index=None,
                      test_end_index=None, **params):
        calls.append((test_start_index, test_end_index, params.get('tag')))
        # Validation score is candidate-specific; test echoes selected candidate.
        if params.get('tag') == 'B':
            score = 2.0
        else:
            score = 1.0
        return {'closed_trades': 5, 'expectancy_pct': score,
                'test_start_index': test_start_index, 'test_end_index': test_end_index,
                'tag': params.get('tag')}

    result = walk_forward_validate(
        stock, benchmark, warmup=50, train_size=100, validation_size=30,
        test_size=40, parameter_candidates=[{'tag': 'A'}, {'tag': 'B'}],
        min_validation_trades=3, backtest_fn=fake_backtest,
    )
    assert result['status'] == 'OK'
    assert result['fold_count'] >= 1
    first = result['folds'][0]
    assert first['selected_params'] == {'tag': 'B'}
    assert first['test_result']['tag'] == 'B'
    assert first['test_result']['test_start_index'] == first['test_start']
    assert first['test_result']['test_end_index'] == first['test_end']
    assert len(calls) == result['fold_count'] * 5  # 2 candidates x train/validation + 1 test


def test_no_candidate_passes_validation_skips_oos_test():
    stock, benchmark = _market('AAA'), _market('VNINDEX', seed=3)

    def fake_backtest(frame, benchmark=None, **kwargs):
        return {'closed_trades': 0, 'expectancy_pct': None}

    result = walk_forward_validate(
        stock, benchmark, warmup=50, train_size=100, validation_size=30,
        test_size=40, parameter_candidates=[{}], min_validation_trades=3,
        backtest_fn=fake_backtest,
    )
    assert result['status'] == 'NO_VALID_OOS_TESTS'
    assert result['folds'][0]['test_result']['status'] == 'SKIPPED'


def test_backtest_plan_respects_test_end_boundary():
    from modules.plan_backtest import backtest_plan
    stock, benchmark = _market('AAA', n=220, seed=4), _market('VNINDEX', n=220, seed=5)
    start, end = 150, 179
    result = backtest_plan(stock, benchmark=benchmark, warmup=50,
                           test_start_index=start, test_end_index=end)
    assert 'error' not in result
    assert result['test_start_index'] == start
    assert result['test_end_index'] == end
    assert result['sessions_tested'] == end - start + 1
    assert pd.to_datetime(result['trades'][0]['entry_date']) <= stock.date.iloc[end] if result['trades'] else True
    assert all(pd.to_datetime(t['exit_date']) <= stock.date.iloc[end] for t in result['trades'])


def test_walk_forward_rejects_duplicate_dates_in_benchmark():
    stock, benchmark = _market('AAA'), _market('VNINDEX', seed=6)
    benchmark = pd.concat([benchmark, benchmark.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="benchmark có ngày trùng"):
        walk_forward_validate(stock, benchmark, warmup=50, train_size=100,
                              validation_size=30, test_size=40)


def test_trap_forward_stats_is_available_and_explicitly_forward_looking_diagnostic():
    from modules.plan_backtest import trap_forward_stats
    stock = _market('AAA', n=180, seed=7)
    result = trap_forward_stats(stock, warmup=60, horizon=5)
    assert result
    assert result["horizon_sessions"] == 5
    assert "baseline_avg_pct" in result
