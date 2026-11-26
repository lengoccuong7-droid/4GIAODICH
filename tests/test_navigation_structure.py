from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_three_primary_navigation_tabs_are_declared():
    source = APP.read_text(encoding="utf-8")
    expected = [
        "1 · TỔNG QUAN",
        "2 · DẤU CHÂN DÒNG TIỀN",
        "3 · TRỢ LÝ TRADING",
    ]
    start = source.index("main_tabs = st.tabs([", source.index("three-tab decision interface"))
    end = source.index("])", start)
    nav = source[start:end]
    assert all(label in nav for label in expected)
    assert source.count("with main_tabs[0]:") == 1
    assert source.count("with main_tabs[1]:") == 1
    assert source.count("with main_tabs[2]:") == 1
    assert "with main_tabs[3]:" not in source
    assert "with main_tabs[4]:" not in source


def test_primary_input_is_minimal_ohlcv_and_no_participant_upload():
    source = APP.read_text(encoding="utf-8")
    assert '"Dữ liệu OHLCV"' in source
    assert "participant_flow_file" not in source
    assert "foreign_net_value" not in source
    assert "proprietary_net_value" not in source
    assert "large_buy_value" not in source
    assert "large_sell_value" not in source
    assert "không xác định được danh tính tổ chức" in source.lower()


def test_five_extra_score_panels_are_not_displayed():
    source = APP.read_text(encoding="utf-8")
    assert "5 góc nhìn chẩn đoán" not in source
    assert "_five_scores" not in source


def test_strategy_tab_has_both_position_modes():
    source = APP.read_text(encoding="utf-8")
    assert "CHƯA CÓ HÀNG · Kế hoạch mở vị thế" in source
    assert "ĐANG CÓ HÀNG · Quản trị vị thế" in source
    assert "TẢI BÁO CÁO CHIẾN LƯỢC JSON" in source


def test_no_extra_streamlit_pages_create_hidden_navigation():
    root = APP.parent
    assert not (root / "pages").exists()
