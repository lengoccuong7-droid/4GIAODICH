# BOT TRADER SWING MULTI V6.3.1

## Điểm mới
- Tab Tổng quan ưu tiên nhận định bằng văn bản dễ hiểu.
- Trạng thái VN-Index được diễn giải thành bối cảnh thuận lợi, rủi ro, trung tính hoặc chưa đủ dữ liệu.
- Điểm sàng lọc được giải thích rõ; điểm 0 không bị hiểu nhầm là xác suất thắng bằng 0.
- Tab Dấu chân dòng tiền có phần diễn giải trước các chỉ số proxy.
- Không suy diễn OHLCV thành giao dịch của tổ chức/khối ngoại/tự doanh.

## Cài đặt
1. Giải nén toàn bộ ZIP.
2. Giữ nguyên cấu trúc thư mục.
3. Cài thư viện theo `requirements.txt` nếu môi trường chưa có.
4. Chạy `streamlit run app.py` tại thư mục gốc dự án.

## Nâng cấp từ V6.3.0
Sao lưu thư mục dự án và cơ sở dữ liệu trước khi thay thế. Giải nén V6.3.1 rồi thay mã nguồn cũ bằng toàn bộ mã nguồn mới. Không xóa tệp cơ sở dữ liệu cá nhân nếu muốn giữ lịch sử đã nhập.

## Kiểm thử
Đã chạy `python -m compileall -q app.py modules` và `pytest -q`: 80/80 kiểm thử đạt.
Lưu ý: kiểm thử tự động không thay thế việc chạy thử giao diện trên Replit với dữ liệu thực tế của người dùng.
