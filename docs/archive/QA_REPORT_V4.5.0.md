# QA Report – BOT TRADER SWING MULTI V4.5.0

## Phạm vi thay đổi
- Tổ chức lại giao diện chính thành đúng 3 tab: **Tổng quan**, **Dấu chân dòng tiền**, **Chiến lược**.
- Sidebar gom dữ liệu đầu vào và thông số vốn/vị thế.
- Tab Tổng quan hiển thị điểm Swing 0–100, 5 nhóm điểm, xu hướng, nhận định và biểu đồ thu gọn.
- Tab Dấu chân dòng tiền tách riêng khối ngoại, tự doanh, lệnh lớn và OBV/CLV proxy.
- Bổ sung file dòng tiền tùy chọn CSV/XLSX với schema: `date`, `foreign_net_value`, `proprietary_net_value`, `large_buy_value`, `large_sell_value`.
- Tab Chiến lược hiển thị riêng hai chế độ chưa có hàng / đang có hàng, cùng trigger, SL, TP, sizing, quản trị vị thế và điều kiện chặn.
- Giữ lại các module phân tích, shared context và Swing Trading Expert từ V4.4.1; không viết lại engine.

## Kiểm thử tự động
- `python -m compileall -q .`: passed.
- `pytest -q`: **43 passed**.
- Navigation regression: đúng 3 tab cấp 1.
- Flow-input regression: dữ liệu khối ngoại/tự doanh/lệnh lớn là tùy chọn, không suy diễn từ OHLCV.
- Strategy-view regression: có hai chế độ vị thế.

## Giới hạn chưa được xác nhận
- Không có kết nối nhà cung cấp dữ liệu thị trường trực tuyến trong bản này.
- Khối ngoại/tự doanh/lệnh lớn chỉ có kết quả khi người dùng nạp file đúng schema; app không tự lấy dữ liệu đó.
- OBV/CLV là proxy OHLCV, không xác định danh tính tổ chức hay bên chủ động khớp lệnh.
- Chưa thực hiện kiểm thử giao diện trình duyệt/điện thoại trong môi trường Streamlit runtime.
- Chưa có walk-forward/out-of-sample validation; điểm 0–100 là điểm heuristic, không phải xác suất thắng.

## Trạng thái phát hành
V4.5.0 là bản tái cấu trúc giao diện và luồng đầu vào/đầu ra trên nền V4.4.1. Phù hợp để chạy thử và đánh giá quy trình; chưa được chứng nhận hiệu quả sinh lời.
