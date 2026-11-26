# CHANGELOG V6.2.0

## Kiến trúc
- Thêm `modules/unified_analytics.py` làm lớp tạo snapshot trung tâm.
- Thêm `add_ohlcv_features` trong `modules/indicators.py`; chuẩn hóa CLV, OBV proxy, signed volume proxy, value proxy và các đặc trưng OHLCV.
- Cùng một đường `evaluate_unified_decision` được dùng cho phân tích hiện tại và backtest lịch sử.
- Snapshot ID phản ánh dữ liệu và cấu hình quản trị rủi ro.

## Năng lực phân tích
- Phân loại cấu trúc tích lũy/hấp thụ/phân phối tiềm năng bằng dữ liệu đa phiên.
- Dùng chung Relative Volume theo baseline 20 phiên đã hoàn tất.
- So sánh sức mạnh tương đối với VN-Index và chỉ số ngành được người dùng cung cấp.
- Holdout 70/30, tín hiệu được tính tuần tự theo dữ liệu sẵn có tại từng ngày.

## Nhập liệu và giao diện
- Vẫn giữ 3 tab.
- Hỗ trợ nhiều file OHLCV trong một lần tải.
- Hỗ trợ file chỉ số ngành CSV với `date,sector,close` và tùy chọn `volume`.
- Dữ liệu ngành được lưu tại `data/sector_index.csv`.

## QA
- 75/75 pytest đạt; compileall đạt.
- Chưa chạy GUI Streamlit trong môi trường đóng gói vì thiếu Streamlit.
