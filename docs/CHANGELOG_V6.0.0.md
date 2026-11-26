# CHANGELOG V6.0.0

## Mục tiêu phát hành

Tập trung giảm ma sát nhập liệu, giữ 3 tab, nâng cấp trải nghiệm Trading Desk và duy trì quy trình phân tích Swing 3–10 phiên. Không bổ sung thêm chỉ báo chỉ để tăng số lượng.

## Thay đổi

- Giao diện Trading Desk nền tối, bố cục responsive và sidebar thu gọn mặc định.
- Một luồng nạp dữ liệu duy nhất: CSV/Excel hoặc dán bảng OHLCV.
- Hỗ trợ một tệp nhiều mã; mã VNINDEX có thể nằm chung với dữ liệu cổ phiếu.
- Bỏ các ô nhập file benchmark và ngành riêng khỏi luồng chính; thiếu VNINDEX thì hiển thị giới hạn dữ liệu thị trường.
- Thêm kho OHLCV SQLite offline-first, cập nhật nối tiếp theo khóa mã/ngày.
- Báo cáo số dòng mới, dòng được sửa và dòng không đổi sau khi cập nhật.
- Thiết lập vốn/chi phí chuyển vào mục thu gọn; dữ liệu vị thế chỉ xuất hiện khi chọn đang có hàng.
- Dữ liệu khối ngoại/tự doanh/lệnh lớn nằm trong phần tùy chọn nâng cao, không bắt buộc.
- Thêm hướng dẫn định dạng dữ liệu và mẫu CSV.

## Kiểm thử

- Bổ sung kiểm thử kho dữ liệu: thêm phiên, cập nhật phiên sửa, bỏ qua phiên giống hệt.
- Giữ toàn bộ kiểm thử hồi quy V5.3.0.

- Tách logic chuẩn hóa file đầu vào thành module riêng và kiểm thử hệ số giá cổ phiếu/VNINDEX.
