# CHANGELOG V4.5.1 — Trap Detection 2.0

- Nâng cấp nhận diện Bull Trap/Bear Trap theo cấu trúc sự kiện và diễn biến tối đa 3 phiên tiếp theo.
- Phân biệt CONFIRMED, PENDING, INVALIDATED và UNCONFIRMED; không gắn nhãn bẫy đã xác nhận ngay tại phiên breakout thất bại ban đầu.
- Bổ sung kiểm tra breakout giữ vùng, breakout có retest và breakout thất bại.
- Bổ sung bảng sự kiện Trap Detection 2.0 trong Tab 2 — Dấu chân dòng tiền.
- Giữ tương thích các khóa kết quả cũ: `trap_risk`, `trap_label`, `bull_trap_events_5`, `bear_trap_events_5`.
- Nhấn mạnh giới hạn: OHLCV chỉ tạo proxy, không chứng minh thao túng hoặc xác định danh tính dòng tiền lớn.

