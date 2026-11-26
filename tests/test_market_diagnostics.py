import numpy as np
import pandas as pd
from modules.indicators import add_indicators
from modules.market_diagnostics import classify_stock_phase, market_status_label
from modules.market_regime import assess_market_regime


def frame(symbol='AAA', n=100, trend=1):
    dates = pd.bdate_range('2025-01-01', periods=n)
    close = np.linspace(10000, 12000, n) if trend > 0 else np.linspace(12000, 9000, n)
    return pd.DataFrame({'date': dates, 'symbol': symbol, 'open': close-10,
                         'high': close+100, 'low': close-100, 'close': close,
                         'volume': np.full(n, 1_000_000.0)})


def test_single_stock_never_becomes_market_benchmark():
    out = assess_market_regime(frame())
    assert out['regime'] == 'CHƯA ĐỦ DỮ LIỆU'
    assert market_status_label(out) == 'CHƯA ĐỦ DỮ LIỆU'


def test_vnindex_market_status_uses_benchmark_trend():
    out = assess_market_regime(frame('VNINDEX', trend=1))
    assert out['benchmark'] == 'VNINDEX'
    assert out['status_label'] in ('THUẬN LỢI', 'TRUNG TÍNH', 'RỦI RO')


def test_stock_phase_returns_one_of_required_states():
    enriched = add_indicators(frame())
    out = classify_stock_phase(enriched)
    assert out['phase'] in ('TÍCH LŨY / ĐI NGANG', 'TĂNG GIÁ', 'PHÂN PHỐI / CUNG ÁP ĐẢO', 'SUY YẾU', 'CHUYỂN PHA / CHƯA RÕ', 'CHƯA ĐỦ DỮ LIỆU')
    assert out['confidence'] in ('THẤP', 'TRUNG BÌNH')
