# ĐẶC TẢ KIẾN TRÚC E8.4 — BOT TRADER SWING MULTI

## 1. Trạng thái tài liệu

Đây là **đặc tả mục tiêu**, không phải xác nhận E8.4 đã được triển khai. Mã nguồn trong gói này vẫn thuộc nhánh E8.3.9; Giai đoạn 9 đang ở trạng thái HOLD theo `PHASE9_ACCEPTANCE_E8.3.9.md`. Các hạng mục E8.4 chỉ được chuyển thành trạng thái hoàn thành sau khi có mã nguồn, kiểm thử và biên bản xác minh tương ứng.

## 2. Nguyên tắc không thay đổi

- Giữ đúng 3 tab: TỔNG QUAN, DẤU CHÂN DÒNG TIỀN, TRỢ LÝ TRADING.
- Một nguồn dữ liệu chuẩn, một Unified Snapshot cho mỗi lần phân tích, một định nghĩa cho mỗi công thức và một Central Decision Engine tạo Final Action.
- Phân biệt dữ liệu đo được, proxy, giả định, dữ liệu thiếu và kết quả suy luận.
- Risk Gate được phép hạn chế/từ chối hành động theo quy tắc minh bạch; không tự tạo hành động mở vị thế.
- `NO_TRADE` đi thẳng tới Decision Explainer, không tạo Action Plan giao dịch.
- Không tự động đặt lệnh, không khẳng định khả năng sinh lời và không xem backtest là dự báo chắc chắn.
- Thay đổi theo hướng tăng cường, không xóa/chuyển module cũ nếu chưa kiểm tra quan hệ import, dữ liệu và regression.

## 3. Luồng dữ liệu và quyết định chuẩn

`Data Ingestion → Data Quality → ENRICH ONCE → Unified Snapshot → Analysis Modules → Module Contracts → Central Decision Engine → Risk Management → Risk Gate → Final Action → Action Routing → Decision Explainer → Decision Journal → 3-tab UI`.

`ENRICH ONCE` là công đoạn xử lý, không phải một tầng kiến trúc độc lập. Data Quality có kiểm tra khi nhập và kiểm tra lại tại thời điểm tạo Snapshot (freshness, lịch sử, khoảng trống phiên, tính nhất quán). Snapshot phải bất biến và có `snapshot_id`, `data_as_of`, `schema_version`, `data_version`, `formula_version`, `engine_version`, `config_version`, `data_status`.

Mỗi module phân tích nhận cùng Snapshot và trả hợp đồng chuẩn tối thiểu gồm `module_id`, `status`, `signal`, `confidence`, `evidence`, `limitations`, `source_refs`, `snapshot_id`, `calculation_version`. Không dùng confidence như xác suất đã hiệu chuẩn nếu chưa có quy trình hiệu chuẩn độc lập.

## 4. Phân định trách nhiệm module

- `support_resistance`: vùng hỗ trợ/kháng cự, số lần kiểm tra, trạng thái phá vỡ; không tính Position Size hoặc tự quyết định giao dịch.
- `risk_analysis`: đánh giá điều kiện rủi ro thị trường/giá; không thay thế Risk Manager.
- `risk_manager`: khoảng cách vô hiệu, mức rủi ro giao dịch, Position Sizing, Risk/Reward và chi phí giả định.
- `portfolio_manager`: vốn, exposure, concentration, vị thế và rủi ro danh mục; thiếu dữ liệu là `UNKNOWN`, không phải 0.
- `event_market_risk`: sự kiện có thể ảnh hưởng quyết định (ví dụ lịch công bố thông tin, ĐHCĐ, đáo hạn phái sinh); nguồn và thời điểm rà soát phải được lưu.
- `risk_gate`: áp dụng các hard/soft constraints, lưu proposed action, final action, rule, evidence và lý do.
- `action_plan`: chỉ tạo kế hoạch phù hợp Final Action; WAIT phải phân biệt chưa có vị thế và đang có vị thế.
- `decision_explainer` và `decision_journal`: giải thích và lưu dấu vết theo Snapshot/Decision ID.

## 5. Knowledge Hub và registry

Ba thành phần có trách nhiệm riêng:

1. Knowledge Hub: định nghĩa, quy tắc, tài liệu và nguồn tham chiếu.
2. Formula Registry: ID công thức, công thức, tham số, seed/warm-up, đơn vị, nguồn tham chiếu, phiên bản, trạng thái xác minh.
3. Calculation Registry: ánh xạ calculation ID tới hàm triển khai, schema đầu vào/đầu ra và test fixture.

Không đánh dấu `VERIFIED` chỉ vì unit test chạy qua. Mỗi công thức cần fixture tham chiếu độc lập, quy ước biên, sai số cho phép và kiểm tra phiên bản. Các công thức chưa đủ chứng cứ giữ `PENDING_INDEPENDENT_VALIDATION`.

## 6. Đặc thù thị trường Việt Nam

### 6.1. Settlement và T+

Quản lý theo từng lô (lot), lịch thanh toán và ngày làm việc thực tế. Tách `total_position`, `available_to_sell`, `pending_buy`, `pending_sell`, `settlement_schedule`. Không hard-code số ngày lịch; cấu hình lịch nghỉ, ngày thanh toán và quy tắc thị trường được xác minh. Risk Gate kiểm tra lượng khả dụng trước khi mô phỏng giảm/bán.

### 6.2. Giá trần/sàn và thanh khoản

Price Limit Engine phải xác định giá tham chiếu, biên độ, quy tắc làm tròn theo sàn/mã và trạng thái phiên. Execution Simulator không được mặc định khớp tại Close. Khi chạm trần không có cung đối ứng hoặc chạm sàn không có cầu đối ứng, lệnh có thể pending/unfilled; dữ liệu OHLCV không đủ để tái tạo sổ lệnh hay thứ tự ưu tiên nên mọi ước lượng khớp phải công khai giả định.

### 6.3. Corporate Actions

Tách sự kiện điều chỉnh dữ liệu (cổ tức tiền/cổ phiếu, chia tách, thưởng, quyền mua, phát hành) khỏi sự kiện rủi ro lịch (công bố thông tin, ĐHCĐ, đáo hạn...). Raw OHLCV và Adjusted OHLCV phải phân biệt rõ. Chỉ báo phải ghi loại giá sử dụng; mô phỏng khớp lệnh dùng giá giao dịch phù hợp tại thời điểm lịch sử. Điều chỉnh giá không được tạo tín hiệu giả.

## 7. Execution Simulator và Backtest

Luồng mục tiêu: Historical As-of Data → Data Quality → Historical Snapshot → Analysis → Central Decision → Portfolio/Risk Gate → Order Intent → Price Limit/Liquidity Check → Execution Simulator → Settlement → Portfolio State Update → phiên tiếp theo.

Trạng thái mô phỏng lệnh tối thiểu: `FILLED`, `PARTIALLY_FILLED`, `PENDING`, `REJECTED`, `EXPIRED`. Ghi nhận phí, thuế, trượt giá, lô giao dịch, biên độ, thanh khoản, gap và lệnh không khớp. Phải phân biệt tín hiệu, quyết định, ý định đặt lệnh, khớp lệnh và vị thế.

Backtest cần dùng cùng logic quyết định và risk gate với luồng phân tích; dữ liệu mỗi quyết định phải as-of, không look-ahead. Walk-forward phải có fold train/validation/test, giữ đúng thứ tự thời gian, lưu tham số và kết quả từng fold; nếu chiến lược yêu cầu liên tục vốn/vị thế thì không reset trạng thái một cách tùy tiện giữa các fold.

## 8. Hiệu năng, versioning và nhiều mã

Cache theo tổ hợp `symbol + snapshot_id + formula_version + config_version`; không tái sử dụng kết quả khi dữ liệu hoặc cấu hình thay đổi. Ba tab đọc cùng kết quả đã tính. Mỗi mã có Snapshot/Decision riêng; Portfolio Manager tổng hợp exposure và rủi ro danh mục đa mã.

## 9. Database — nhóm dữ liệu mục tiêu

Các nhóm bảng có thể gồm market data, corporate actions, market events, snapshots, module results, formula/calculation registry, decisions/evidence, portfolio/position lots/settlement, orders/fills, backtest runs/trades và walk-forward folds. Trước khi tạo bảng phải kiểm tra schema SQLite hiện hữu, migration version, khóa ngoại, chỉ mục và khả năng sao lưu/khôi phục. Không tạo bảng trùng với dữ liệu hiện có.

## 10. Lộ trình triển khai đề xuất

- E8.4.1: đồng bộ Module Contracts, cây thư mục và import graph.
- E8.4.2: Knowledge Hub, Formula Registry, Calculation Registry và fixture độc lập.
- E8.4.3: Snapshot bất biến, Data Versioning và corporate actions.
- E8.4.4: Position lots, settlement schedule và trạng thái available-to-sell.
- E8.4.5: Price Limit Engine và Execution Simulator.
- E8.4.6: Risk Gate tích hợp và truy vết.
- E8.4.7: Event-driven Backtest và Walk-forward.
- E8.4.8: kiểm thử hiệu năng, UI runtime, regression và nghiệm thu.

Mỗi giai đoạn phải có thay đổi mã nguồn thực tế, unit/integration/regression tests, tài liệu cập nhật và kết quả kiểm thử có thể tái lập. Không tuyên bố hoàn thành chỉ dựa trên sơ đồ hoặc tài liệu thiết kế.

## 11. Điều kiện nghiệm thu E8.4

- Đúng 3 tab, không có quyết định riêng lẻ mâu thuẫn.
- Snapshot bất biến và có thể tái lập.
- Công thức có nguồn tham chiếu/fixture độc lập và trạng thái xác minh chính xác.
- Module Contracts nhất quán.
- T+ và settlement được kiểm tra theo lịch/quy tắc đã xác minh.
- Trần/sàn, thanh khoản, partial fill và unfilled order được mô phỏng có giả định công khai.
- Corporate Actions không làm sai lệch chuỗi chỉ báo và giá thực thi.
- Backtest không look-ahead; Walk-forward có kết quả ngoài mẫu.
- UI runtime và backup/restore được chạy thử trong môi trường có dependencies.
- Regression suite và biên bản nghiệm thu đạt.
