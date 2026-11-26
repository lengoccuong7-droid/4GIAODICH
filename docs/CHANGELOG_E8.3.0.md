# E8.3.0 — Corrected architecture baseline

Kế thừa E8.2.0, giữ nguyên toàn bộ cấu trúc hiện có và ba tab.

## Thay đổi

- Chuẩn hóa Action Plan theo Final Action: ENTER_LONG, WAIT, REDUCE có kế hoạch phù hợp; NO_TRADE bypass Action Plan.
- WAIT khi đang có vị thế trở thành HOLD_AND_MONITOR, không hiển thị như kế hoạch mở vị thế mới.
- Bổ sung local portfolio store để nhập/lưu nhiều vị thế mô phỏng trong Tab 3.
- Truyền danh mục và vị thế hiện tại vào Portfolio Manager/Central Decision Engine; tính phơi nhiễm mã, phơi nhiễm gộp và rủi ro stop đã biết.
- Giữ nguyên UNKNOWN khi thiếu danh mục hoặc dữ liệu vị thế không đầy đủ.
- Bổ sung kiểm tra chất lượng ở hai thời điểm: ingestion trước khi lưu và snapshot-time (freshness, độ dài lịch sử, khoảng cách ngày) trước khi phân tích.
- Chuẩn hóa thứ tự Data Quality → Enrich Once → Unified Snapshot → Analysis Modules.
- Tăng engine identifier lên CENTRAL-1.1 và snapshot schema lên 8.3.0.

## Không thay đổi

- Không thêm tab.
- Không thêm tầng kiến trúc.
- Không thêm API dữ liệu tự động hoặc chức năng đặt lệnh.
- Giữ lại các module phân tích, chi phí mô phỏng, T+2 và logic backtest hiện có.
