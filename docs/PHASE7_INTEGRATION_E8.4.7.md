# E8.4.7 — Giai đoạn 7: Tích hợp mã nguồn và kiểm tra liên kết

## 1. Phạm vi triển khai

Giai đoạn này hợp nhất các thành phần có trong bản làm việc E8.3.9 thành một luồng thống nhất; không tự nhận là nghiệm thu cuối E8.4.

### Position State và Settlement metadata

- Thêm `modules/position_state.py` để tổng hợp vị thế theo lô.
- Chỉ công nhận `available_to_sell` khi lô có `settlement_date` hợp lệ và ngày đó không sau `as_of`.
- Lô thiếu ngày thanh toán được đánh dấu `UNKNOWN`, không được tính là cổ phiếu sẵn sàng bán.
- Nếu có vị thế nhưng không có dữ liệu lô, Snapshot ghi `position_state.status=UNKNOWN`.
- Với hành động `REDUCE`, Action Plan giữ nguyên ý định giảm vị thế nhưng chặn số lượng thực hiện khi settlement chưa xác định; nếu có dữ liệu lô thì số lượng giảm không vượt `available_to_sell`.
- Không hard-code lịch nghỉ, ngày thanh toán hoặc quy tắc T+ của sở giao dịch.

### Risk Gate

- Thêm `modules/risk_gate.py` làm nơi tập trung các hard/soft constraints.
- `modules/central_decision_engine.py` gọi Risk Gate; không tạo một nguồn quyết định thứ hai.
- `ENTER_LONG` bị chặn khi sizing không hợp lệ, Data Quality lỗi nghiêm trọng, module lỗi, danh mục có hard veto hoặc cấu hình yêu cầu portfolio context nhưng dữ liệu danh mục chưa biết.
- Risk Gate không tự nâng `WAIT` thành `ENTER_LONG`.
- Lỗi dữ liệu không làm mất ý định `REDUCE`; Action Plan/settlement vẫn có thể chặn việc thực hiện nếu không đủ dữ liệu.

### Price Limit và Execution

- Thêm `modules/price_limit_engine.py`: tính upper/lower limit theo reference price, band và tick size được truyền vào; không tự áp một biên độ sàn cố định.
- Thêm `modules/execution_simulator.py`: mô phỏng limit-order theo OHLCV, có participation cap và các trạng thái FILLED/PARTIALLY_FILLED/PENDING.
- `modules/plan_backtest.py` gọi Execution Simulator để kiểm tra khả năng khớp entry theo giới hạn thanh khoản; partial fill được ghi vào trade và tỷ lệ khớp được tính vào mức phơi nhiễm mô phỏng.
- Price Limit Engine được dùng để giới hạn giá entry theo biên độ cấu hình.

### Unified Snapshot và 3-tab UI

- Snapshot chứa `position_state` và `trading_assistant`.
- Trợ lý Trading được dựng trong luồng tạo Snapshot; tab không tự gọi lại `build_trading_assistant(raw)`.
- Trợ lý Trading dùng ATR14 và VOL_MA20 đã được enrich trong Snapshot nếu có.
- Data fingerprint sắp xếp chuẩn theo date/symbol trước khi hash, để hoán vị thứ tự dòng không làm thay đổi fingerprint.
- Ba tab vẫn là: TỔNG QUAN, DẤU CHÂN DÒNG TIỀN, TRỢ LÝ TRADING.

## 2. Files changed

- `modules/position_state.py` (new)
- `modules/risk_gate.py` (new)
- `modules/price_limit_engine.py` (new)
- `modules/execution_simulator.py` (new)
- `modules/central_decision_engine.py`
- `modules/unified_analytics.py`
- `modules/trading_assistant.py`
- `modules/plan_backtest.py`
- `modules/calculation_registry.py`
- `app.py`
- `tests/test_e847_integration.py` (new)

## 3. Reproducible checks

- `python -m pytest -q --disable-warnings --maxfail=1`: **134 passed**.
- `python -m compileall -q app.py modules tests`: **PASS**.
- Calculation Registry: **12/12 INVENTORY_OK**. Đây là kiểm tra AST/tệp test, không chứng minh tính đúng toán học.
- Static AST check: đúng **3 tab chính**.
- Snapshot fingerprint invariant under input row permutation: **PASS**.
- Snapshot → Central Decision → Action Plan consistency: covered by regression and integration tests.
- Backtest entry liquidity participation/partial fill: covered by deterministic integration test.

## 4. Giới hạn còn lại — không được diễn giải thành đã nghiệm thu

1. Formula Registry hiện có **16 công thức**, tất cả còn `PENDING_INDEPENDENT_VALIDATION`; unit tests không thay thế fixture tham chiếu độc lập.
2. Streamlit runtime chưa chạy được trong môi trường này vì thiếu package `streamlit`; cần người dùng kiểm tra giao diện thực tế.
3. Settlement dùng ngày `settlement_date` do caller cung cấp; chưa tích hợp lịch giao dịch/ngày nghỉ chính thức.
4. Execution Simulator là xấp xỉ OHLCV, không tái tạo sổ lệnh, queue priority hoặc fill chính xác trong phiên. Entry có participation cap; exit stop/target vẫn theo quy tắc OHLCV hiện hữu, chưa mô phỏng partial exit đầy đủ.
5. Walk-forward hiện báo cáo fold độc lập; vốn và vị thế chưa được mang liên tục qua ranh giới fold.
6. Corporate Actions, dữ liệu adjusted/raw và event calendar chưa được tích hợp đầy đủ vào toàn bộ replay.
7. Không có bằng chứng lợi nhuận ngoài mẫu đủ mạnh: các lần chạy trước cho thấy có thể không có ứng viên đủ điều kiện Validation hoặc không có lệnh đóng.
8. Đây là bản làm việc tách riêng từ E8.3.9; ZIP gốc không bị sửa. Streamlit UI runtime và kiểm tra thủ công trên môi trường người dùng còn chờ.

## 5. Kết luận Giai đoạn 7

**Đã hoàn tất phần tích hợp mã nguồn và kiểm tra tự động trong phạm vi các thành phần nêu trên. Chưa phải biên bản nghiệm thu cuối E8.4.** Các giới hạn ở Mục 4 phải được giữ lại cho đợt nghiệm thu tổng thể sau khi hoàn thành 7 giai đoạn.
