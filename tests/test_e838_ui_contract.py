from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_app_keeps_exactly_three_primary_tabs():
    source = (ROOT / 'app.py').read_text(encoding='utf-8')
    matches = re.findall(r'st\.tabs\(\[(.*?)\]\)', source, flags=re.S)
    assert len(matches) == 1
    assert matches[0].count('·') == 3
    assert 'TỔNG QUAN' in matches[0]
    assert 'DẤU CHÂN DÒNG TIỀN' in matches[0]
    assert 'TRỢ LÝ TRADING' in matches[0]


def test_mobile_responsive_styles_remain_present():
    source = (ROOT / 'app.py').read_text(encoding='utf-8')
    assert '@media(max-width:700px)' in source
    assert 'overflow-x:auto' in source
    assert 'white-space:nowrap' in source


def test_app_version_is_e840_dev2():
    source = (ROOT / 'config.py').read_text(encoding='utf-8')
    assert 'APP_VERSION = "8.4.0-dev2"' in source


def test_backup_restore_is_exposed_in_existing_sidebar():
    source = (ROOT / 'app.py').read_text(encoding='utf-8')
    assert 'SAO LƯU / KHÔI PHỤC DỮ LIỆU' in source
    assert 'TẢI BẢN SAO LƯU DỮ LIỆU' in source
    assert 'KHÔI PHỤC DỮ LIỆU' in source
    assert source.count('st.tabs(') == 1
