# BOT TRADER SWING MULTI – V4.4.1

## Mục tiêu bản sửa
Sửa cấu trúc điều hướng gây nhầm lẫn ở V4.4.0, đưa Scanner thành tab chính riêng, đưa đánh giá dòng tiền/bẫy giá ra vị trí dễ tìm và dùng chung kết quả phân tích trong phiên.

## Điều chỉnh
1. Chuẩn hóa thành đúng 5 tab chính:
   - Tổng quan
   - Dòng tiền & bẫy giá
   - Scanner
   - Phân tích chi tiết
   - Swing Trading
2. Scanner được tách khỏi Trợ lý AI; không còn nằm chung trong cùng nhóm tab phụ.
3. Trợ lý AI và Knowledge Hub được chuyển vào tab Phân tích chi tiết.
4. Tab Dòng tiền & bẫy giá hiển thị trực tiếp proxy dòng tiền, RVOL, OBV proxy, cảnh báo bẫy tăng/giảm, sự kiện nghi vấn và giới hạn dữ liệu.
5. Shared Analysis Context tính `flow_trap` một lần; tab Dòng tiền và Swing Trading dùng chung kết quả đó.
6. Bổ sung kiểm thử cấu trúc 5 tab và kiểm thử trường flow_trap trong shared context.

## Kiểm thử
- `pytest -q`: 41 passed.
- `python -m compileall -q .`: passed.
- ZIP integrity: kiểm tra sau khi đóng gói.

## Giới hạn
- Chưa thực hiện kiểm thử giao diện Streamlit trên trình duyệt/iPhone trong môi trường build vì Streamlit không được cài sẵn.
- Dòng tiền lớn chỉ là suy luận proxy từ OHLCV; không xác định danh tính tổ chức hoặc bên mua/bán chủ động.
- Chưa có kiểm định walk-forward/out-of-sample chứng minh hiệu quả chiến lược.
