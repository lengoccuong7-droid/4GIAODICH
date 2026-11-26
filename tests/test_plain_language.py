from modules.plain_language import market_explanation, stock_explanation

def test_market_risk_explained_in_plain_language():
    out = market_explanation({"status_label":"RỦI RO", "regime":"GIẢM", "return_20_pct":-5.2, "reasons":["VNINDEX dưới MA20"]})
    assert "bất lợi" in out["detail"]
    assert "-5.20%" in out["detail"]
    assert "không xem một phiên hồi" in out["caution"]

def test_missing_market_data_is_not_guessed():
    out = market_explanation({})
    assert "Chưa đủ dữ liệu" in out["headline"]

def test_distribution_is_described_as_potential_not_fact():
    out = stock_explanation({"status":"WAIT_CONFIRMATION"}, {"label":"ÁP LỰC PHÂN PHỐI TIỀM NĂNG"}, {})
    assert "không chứng minh tổ chức" in out["phase_text"]
    assert "chờ thêm" in out["headline"]
