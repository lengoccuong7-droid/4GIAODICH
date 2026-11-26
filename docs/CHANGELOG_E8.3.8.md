# E8.3.8 — Giai đoạn 8: Giao diện và vận hành

## Phạm vi đã triển khai trên bản nguồn E8.3.1 có thể truy xuất
- Giữ nguyên đúng 3 tab chính; không thêm tab mới.
- Giữ CSS responsive hiện có cho màn hình nhỏ, cuộn ngang tab và bố cục nội dung.
- Thêm sao lưu dữ liệu cục bộ từ thư mục `data/` dưới dạng ZIP chỉ chứa danh sách tệp dữ liệu được cho phép; không đóng gói mã nguồn.
- Thêm khôi phục có xác nhận của người dùng, kiểm tra danh sách tệp, ngăn path traversal, xác thực JSON/JSONL/CSV và `PRAGMA integrity_check` cho SQLite trước khi thay thế.
- Nâng nhãn phiên bản ứng dụng lên E8.3.8; phiên bản schema snapshot không tự ý thay đổi vì đây không phải thay đổi cấu trúc snapshot.

## Kiểm thử
- Pytest: 111 passed.
- `python -m compileall -q app.py config.py modules tests`: passed.
- Kiểm tra tĩnh: đúng 3 tab, CSS responsive tồn tại, chức năng backup/restore được gắn trong sidebar.

## Chưa thể xác nhận
- Streamlit chưa được cài trong môi trường thực thi; cài đặt bị chặn do môi trường không có kết nối package index. Vì vậy chưa thể chạy Streamlit AppTest hoặc xác nhận tương tác trình duyệt thực tế.
- Chưa kiểm thử trên thiết bị iOS/Android và màn hình máy tính thực tế.
- Bộ ZIP nguồn E8.3.1 không chứa các thay đổi Giai đoạn 2–7 từng được mô tả trước đó. Không được coi Giai đoạn 7 hoặc các giai đoạn trung gian là đã được xác minh trong bản này.
- Chưa tạo ZIP phát hành.
