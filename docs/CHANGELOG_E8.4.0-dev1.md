# E8.4.0-dev1 — Calculation Registry & Input Guardrails

## Nền tảng

- Kế thừa bản sao làm việc từ E8.3.9; không sửa thư mục nguồn E8.3.9.
- Giữ cấu trúc giao diện 3 tab và các module cũ.

## Thay đổi mã nguồn

- Formula Registry mở rộng 16 → 28 mục, bao phủ các phép tính đang có trong indicator engine và performance metrics.
- Bổ sung mô tả rõ hơn về quy ước tính RVOL dùng 20 phiên trước phiên hiện tại, VWAP rolling theo HLC3, Ichimoku span raw và proxy thanh khoản Amihud.
- Position Sizing từ chối lot_size dạng boolean/phân số và giới hạn Risk%/Allocation% trong [0, 100].
- Cập nhật kiểm thử chấp nhận registry mở rộng; thêm kiểm thử riêng cho registry và input validation.

## Kiểm thử

- `pytest -q`: **139 passed**.
- Đây là kết quả kiểm thử Python trong môi trường hiện tại; chưa phải kiểm thử Streamlit runtime hoặc xác minh độc lập các công thức.

## Còn tồn tại

- Tất cả 28 công thức vẫn ở trạng thái `PENDING_INDEPENDENT_VALIDATION`.
- Chưa thay đổi thuật toán indicator RSI/ATR/ADX; cần thống nhất seed Wilder và kiểm tra với bộ dữ liệu tham chiếu độc lập.
- Chưa hoàn tất xác minh corporate actions, settlement calendar, event-driven execution và walk-forward có trạng thái vốn/vị thế liên tục.
