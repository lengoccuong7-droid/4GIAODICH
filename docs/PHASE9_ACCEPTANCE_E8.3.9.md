# Biên bản kiểm toán Giai đoạn 9 — E8.3.9

## 1. Phạm vi và kết luận

Đây là kiểm toán trên working tree E8.3.8 hiện có. Không tạo ZIP phát hành. Kết luận hiện tại: **HOLD — chưa đủ điều kiện nghiệm thu/phát hành**.

## 2. Kết quả kiểm tra có thể tái lập

| Hạng mục | Kết quả |
|---|---|
| Pytest sau cập nhật G9 | 115 passed |
| Compileall (`app.py config.py modules tests`) | Passed |
| Số tab chính trong `app.py` | 3 |
| Formula Registry | 16 công thức; 16 `PENDING_INDEPENDENT_VALIDATION` |
| Streamlit runtime | Chưa chạy được: package `streamlit` không có trong môi trường |
| Walk-forward module độc lập | Không tìm thấy trong working tree |
| Event/Market Risk module độc lập | Không tìm thấy trong working tree |
| Scenario Simulator độc lập | Không tìm thấy trong working tree |

## 3. Sửa lỗi rủi ro dữ liệu trong G9

`modules/portfolio_manager.py::summarize_portfolio` trước đây gán `risk_value = 0` nếu thiếu `stop_price`. Điều này có thể khiến người dùng hiểu nhầm rằng rủi ro vị thế đã được xác định và bằng 0.

Đã sửa:
- Thiếu stop -> `risk_value = NaN`.
- Chỉ trả `total_risk` và `risk_pct_of_capital` khi toàn bộ vị thế có stop hợp lệ.
- Trả `risk_status = UNKNOWN` nếu có ít nhất một vị thế thiếu stop.
- Thêm `risk_coverage_pct` để thể hiện tỷ lệ vị thế có dữ liệu stop.
- Danh mục rỗng được phân biệt với danh mục có vị thế nhưng thiếu stop.

Bổ sung 4 kiểm thử G9, gồm kiểm tra missing-stop, stop hợp lệ, trạng thái xác minh Formula Registry và bảo toàn REDUCE khi module phân tích khác lỗi.

## 4. Các vấn đề chặn nghiệm thu

### 4.1. Công thức chưa được xác minh độc lập

Registry hiện có 16 công thức, tất cả đang `PENDING_INDEPENDENT_VALIDATION`. Không đổi trạng thái sang VERIFIED chỉ dựa trên việc test phần mềm chạy qua.

Một số điểm cần đối chiếu chuẩn tham chiếu:
- RSI/ATR/ADX dùng `ewm(alpha=1/n, adjust=False)` nhưng chưa khởi tạo theo seed Wilder truyền thống (SMA của n giá trị đầu tiên). Kết quả giai đoạn đầu có thể khác các nền tảng/định nghĩa chuẩn.
- EMA/MACD cần chốt quy tắc seed và warm-up.
- Stochastic khi HH=LL và CCI khi mean deviation bằng 0 cần quy ước đầu ra rõ ràng.
- Position sizing cần kiểm tra độc lập chi phí hai chiều, lô giao dịch và đơn vị giá.
- Maximum Drawdown/CAGR cần xác nhận quy ước equity ban đầu, khoảng thời gian và annualization.

### 4.2. Chưa có Walk-forward hoàn chỉnh

Không tìm thấy `walk_forward.py` trong working tree. `plan_backtest.py` có replay theo từng mốc lịch sử, benchmark as-of, T+2, phí/thuế/trượt giá, gap và giới hạn biên độ; tuy nhiên điều đó không thay thế kiểm định walk-forward theo các fold train/test, và hiện chưa có báo cáo fold ngoài mẫu có thể nghiệm thu.

### 4.3. Thiếu một số module từng được mô tả ở các giai đoạn trước

Không tìm thấy module độc lập `event_market_risk.py` và `scenario_simulator.py`. Vì vậy, không xác nhận các tính năng Event Risk/Scenario Simulator đã được tích hợp trong bản nguồn này.

### 4.4. Backtest và dữ liệu thị trường

Chưa có bằng chứng kiểm định bằng dữ liệu lịch sử đã điều chỉnh corporate actions. Cần kiểm tra thêm cách xử lý phiên không khớp, dữ liệu thiếu, cổ tức/chia tách, thanh khoản và trường hợp chạm giá sàn không thể khớp lệnh. Không xem kết quả backtest hiện tại là bằng chứng lợi nhuận tương lai.

### 4.5. Vận hành UI

Streamlit chưa cài trong môi trường; chưa xác minh luồng nhập file, thao tác ba tab, backup/restore và giao diện trên trình duyệt/thiết bị thật.

## 5. Điều kiện để chuyển trạng thái sang ACCEPTED

1. Chuẩn hóa đặc tả và seed của từng công thức; tạo fixture tham chiếu độc lập; chỉ đánh dấu VERIFIED theo từng công thức khi sai số và quy ước biên đã được duyệt.
2. Bổ sung và kiểm thử walk-forward ngoài mẫu, có chống lookahead và ghi nhận fold.
3. Tích hợp hoặc loại khỏi phạm vi phát hành các chức năng Event Risk/Scenario Simulator chưa có trong working tree; tài liệu và UI phải khớp tính năng thực tế.
4. Kiểm thử backtest trên dữ liệu đã xác minh nguồn, đơn vị giá, corporate actions và giả định khớp lệnh.
5. Cài được Streamlit trong môi trường kiểm thử và chạy smoke/UI test thực tế trên ba tab.
6. Chạy lại toàn bộ regression suite sau khi hoàn tất các mục trên.

## 6. Tệp thay đổi trong G9

- `modules/portfolio_manager.py`
- `tests/test_e839_acceptance.py`
- `docs/PHASE9_ACCEPTANCE_E8.3.9.md`
- `docs/CHANGELOG_E8.3.9.md`

Không tạo ZIP. Không tuyên bố bản phát hành đã sẵn sàng.
