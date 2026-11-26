# CHANGELOG V6.1.0

## Mục tiêu
Tinh gọn đầu vào, giảm nhiễu giao diện và giữ trọng tâm vào chất lượng phân tích/ra quyết định. Không bổ sung chỉ báo mới.

## Thay đổi
- Bỏ file nhập khối ngoại/tự doanh/lệnh lớn khỏi luồng đầu vào chính.
- Dùng một bộ OHLCV duy nhất; VNINDEX được khuyến nghị đặt chung trong tệp.
- Tab Dấu chân dòng tiền trình bày rõ đây là proxy từ OHLCV, không gán nhãn dòng tiền tổ chức.
- Bỏ 5 bảng điểm chẩn đoán phụ khỏi Tổng quan để tránh tạo cảm giác nhiều điểm số nhưng chưa được kiểm định trọng số.
- Giữ 3 tab, kho SQLite, cập nhật nối tiếp và các module phân tích hiện có.
- Giữ thông tin vị thế chỉ khi người dùng chọn đang có hàng; thông số vốn/chi phí nằm trong phần thiết lập thu gọn.
- Cập nhật mẫu OHLCV có ví dụ mã cổ phiếu và VNINDEX.

## Kiểm thử
- 67/67 pytest đạt.
- `py_compile` đạt cho app.py, config.py và modules/*.py.
- Chưa xác nhận giao diện Streamlit runtime trong môi trường kiểm thử hiện tại.
