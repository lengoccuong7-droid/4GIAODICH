# HƯỚNG DẪN NẠP DỮ LIỆU – V6.0.0

## Mục tiêu

Không kết nối API hoặc tự động tải dữ liệu. Người dùng chủ động nạp dữ liệu bằng CSV/Excel hoặc dán bảng. Ứng dụng lưu lịch sử vào SQLite cục bộ để lần sau chỉ cần nạp các phiên mới.

## Định dạng tối thiểu

| Cột | Bắt buộc | Ghi chú |
|---|---:|---|
| `date` | Có | Ngày giao dịch, ưu tiên YYYY-MM-DD |
| `symbol` | Có* | Mã cổ phiếu; có thể bỏ nếu chỉ một mã và nhập mã ở ô gợi ý |
| `open` | Có | Giá mở cửa |
| `high` | Có | Giá cao nhất |
| `low` | Có | Giá thấp nhất |
| `close` | Có | Giá đóng cửa |
| `volume` | Có | Khối lượng |

`*` Nếu tệp có nhiều mã, bắt buộc có cột `symbol`. Dùng mã `VNINDEX` cho dữ liệu VN-Index. Có thể đặt dữ liệu cổ phiếu và VN-Index chung trong một tệp.

## Cập nhật lịch sử

1. Chọn `Tải CSV / Excel` hoặc `Dán bảng dữ liệu` ở thanh bên.
2. Chọn đúng đơn vị giá của dữ liệu cổ phiếu trong phần `Tùy chọn nhập dữ liệu`. VNINDEX luôn giữ nguyên điểm số.
3. Nhấn `CẬP NHẬT KHO DỮ LIỆU`.
4. Hệ thống thêm phiên mới, bỏ qua dòng giống hệt và cập nhật dòng cũ nếu cùng mã/ngày nhưng giá trị đã được sửa.
5. Chọn mã muốn phân tích. Cả ba tab dùng chung kho lịch sử.

Kho được lưu tại `data/market_history.sqlite3` cạnh `app.py`. Khi triển khai trên máy khác, cần sao lưu thư mục `data` để giữ lịch sử đã nạp.

## Lưu ý chất lượng dữ liệu

- Không tự điền dữ liệu thiếu, không đoán mã và không tạo dữ liệu thị trường.
- Dữ liệu sai quan hệ OHLC, giá không hợp lệ, khối lượng âm hoặc trùng mã/ngày trong cùng tệp sẽ bị từ chối.
- Khi cập nhật lại cùng mã/ngày, dữ liệu mới sẽ thay thế dữ liệu cũ nếu có khác biệt. Chỉ nạp tệp từ nguồn đáng tin cậy.
- Nếu không có VNINDEX, ứng dụng phải hạ mức kết luận về thị trường và không được dùng một cổ phiếu riêng lẻ làm đại diện thị trường.
- Tệp `DEMO_SYNTHETIC_OHLCV.csv` là dữ liệu tổng hợp để thử chức năng, không phải dữ liệu thị trường thật.
