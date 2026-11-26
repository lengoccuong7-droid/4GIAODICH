# Hướng dẫn BOT TRADER SWING MULTI V4.4.1

## Điều hướng – 5 tab chính
1. **TỔNG QUAN**: bản đồ giao dịch, biểu đồ giá, MA và thông tin nhanh.
2. **DÒNG TIỀN & BẪY GIÁ**: tab phụ Dòng tiền & thanh khoản; tab phụ Sức mạnh tương đối & ngành. Trong tab Dòng tiền, phần cuối có đánh giá proxy dòng tiền lớn và bẫy giá đa phiên.
3. **SCANNER**: quét file OHLCV nhiều mã, xem xếp hạng nghiên cứu và tải CSV.
4. **PHÂN TÍCH CHI TIẾT**: Quant Lab & Backtest, Dữ liệu & kiểm toán, Phân tích doanh nghiệp; phía dưới là Trợ lý suy luận và Knowledge Hub.
5. **SWING TRADING**: chiến lược 5–20 phiên, chế độ chưa có hàng/đang có hàng, điểm kích hoạt, mức vô hiệu, mục tiêu, R:R, quản trị vị thế và cảnh báo dòng tiền/bẫy giá.

## Dữ liệu đầu vào
- Tải OHLCV ở Sidebar.
- Nếu file không có mã cổ phiếu, nhập mã ở trường mã cổ phiếu.
- Chọn đúng đơn vị giá.
- Có thể tải thêm VN-Index và chỉ số ngành để tính sức mạnh tương đối.
- Với Scanner, file OHLCV chính cần có nhiều mã.

## Cách đọc dòng tiền & bẫy giá
- RVOL: khối lượng phiên hiện tại so với bình quân các phiên trước.
- CLV-volume và OBV proxy: dấu hiệu áp lực cung/cầu suy luận từ giá và khối lượng.
- Bull Trap/Bear Trap: sự kiện nghi vấn, cần xác nhận ở các phiên tiếp theo.
- Proxy phân phối/hấp thụ không chứng minh có tổ chức lớn giao dịch.

## Lưu ý vận hành
Ứng dụng chỉ hỗ trợ nghiên cứu và mô phỏng; không đặt lệnh. Kiểm tra ngày dữ liệu, mã, đơn vị giá, điều chỉnh giá và chất lượng OHLCV trước khi đọc kết luận. Kết quả heuristic không phải xác suất thắng hay cam kết lợi nhuận.
