# E8.3.1 — Hoàn thiện giai đoạn 1: Ba kho tính toán

Giữ nguyên kiến trúc E8.3.0 và đúng ba tab. Không thêm architectural layer hoặc tab.

## Kho tri thức
- Tích hợp quản lý tài liệu vào expander trong Tab 3.
- Hỗ trợ TXT, MD, CSV, JSON, PDF, DOCX, XLSX, XLS theo dependencies có sẵn.
- Lưu metadata mã cổ phiếu, loại tài liệu, kỳ/phiên bản, nguồn và ngày nguồn.
- Tìm kiếm, xem nội dung trích xuất, liệt kê và xóa tài liệu qua API.
- Cơ sở dữ liệu mặc định: `data/trading_knowledge.sqlite`.
- Tài liệu chỉ là nguồn tham khảo; không tự động biến thành dữ liệu thị trường hoặc bằng chứng đã xác minh.

## Kho công thức
- Thêm `modules/formula_registry.py` làm danh mục công thức tập trung.
- Bao gồm chỉ báo kỹ thuật, OHLCV proxy, sizing, exposure và drawdown.
- Mỗi mục có mã, tên, nhóm, biểu thức, đầu vào, tham số, đầu ra, vị trí triển khai và ghi chú.
- Tất cả công thức mang trạng thái `PENDING_INDEPENDENT_VALIDATION`; chưa tuyên bố đúng chỉ vì có trong danh mục.

## Kho lập trình tính toán
- Thêm `modules/calculation_registry.py`.
- Kiểm tra tĩnh bằng AST: module tồn tại, cú pháp parse được, hàm được khai báo và tệp kiểm thử hiện diện.
- Hiển thị danh mục trong Tab 3.
- Kiểm tra AST không thay thế kiểm thử toán học độc lập.

## Kiểm thử
- Thêm `tests/test_e831_stores.py` cho lưu/tìm/xem/xóa tài liệu, tính duy nhất của mã công thức và kiểm tra danh mục module/hàm.
