# Kiến trúc V4.4.1 – Five primary tabs and shared diagnostics

## Điều hướng cấp 1
1. Tổng quan: dashboard và biểu đồ giá.
2. Dòng tiền & bẫy giá: thanh khoản, proxy dòng tiền, sự kiện false breakout/breakdown và sức mạnh tương đối.
3. Scanner: sàng lọc nhiều mã độc lập.
4. Phân tích chi tiết: Quant Lab, kiểm toán dữ liệu, phân tích doanh nghiệp, Trợ lý suy luận và Knowledge Hub.
5. Swing Trading: chiến lược 5–20 phiên, mở vị thế mới hoặc quản lý vị thế đang có.

## Luồng dữ liệu
Sidebar nạp OHLCV và thông số → chuẩn hóa đơn vị giá → chọn mã → enrich chỉ báo → `build_shared_analysis_context` → các view dùng chung `analysis_id`, regime, RS, đa khung, chất lượng dữ liệu và `flow_trap`.

`flow_trap` được tính trong shared context và truyền vào `analyze_swing_setup`, tránh tab dòng tiền và tab Swing tự đưa ra các đánh giá khác nhau từ cùng một chuỗi OHLCV trong cùng lượt chạy. Nếu gọi `analyze_swing_setup` độc lập ngoài app, module vẫn tự tính flow/trap khi không được truyền kết quả.

## Giới hạn
Các kết quả dòng tiền là proxy OHLCV, không phải order-flow thực. Decision engine là luật/heuristic giải thích được, chưa phải mô hình dự báo xác suất và chưa được xác nhận hiệu quả bằng walk-forward.
