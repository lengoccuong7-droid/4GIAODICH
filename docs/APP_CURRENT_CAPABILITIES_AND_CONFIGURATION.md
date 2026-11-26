# BOT TRADER SWING MULTI — Báo cáo cấu hình và liên kết hiện trạng

**Ngày kiểm tra:** 2026-11-22  
**APP_VERSION trong `config.py`:** 8.3.9  
**Thư mục kiểm tra:** bản làm việc `BOT_TRADER_SWING_MULTI_E8.3.9`  
**Kết quả kiểm tra tại thời điểm lập báo cáo:** `pytest -q` — 134 passed; `compileall` đã được kiểm tra trong báo cáo E8.4.7.  
**Trạng thái phát hành:** HOLD — chưa nghiệm thu phát hành.

## 1. Tóm tắt ứng dụng đang có

Ứng dụng là công cụ nghiên cứu/phân tích và mô phỏng cổ phiếu Việt Nam theo Swing 3–10 phiên. Dữ liệu thị trường được người dùng nhập thủ công; không kết nối broker và không tự đặt lệnh.

Giao diện có đúng 3 tab:
1. **TỔNG QUAN:** điểm sàng lọc 0–100, cấu trúc giá, bối cảnh VN-Index, sức mạnh tương đối, quyết định trung tâm, Action Plan, biểu đồ, giải thích và nhật ký quyết định.
2. **DẤU CHÂN DÒNG TIỀN:** proxy từ OHLCV, CLV/OBV-volume, cấu trúc tích lũy/hấp thụ/phân phối tiềm năng, bất thường giá-khối lượng, bull trap/bear trap/breakout và trạng thái xác nhận.
3. **TRỢ LÝ TRADING:** kịch bản T+ và breakout, hỗ trợ/kháng cự, stop/targets tham chiếu, danh mục mô phỏng, kho tri thức, kho công thức, kho tính toán, backtest và Walk-forward.

## 2. Cấu hình mặc định

Giá trị trong `config.py`:
- Vốn mô phỏng mặc định: 100.000.000 VND.
- Rủi ro mỗi giao dịch: 1,0%.
- Tỷ trọng tối đa mỗi mã: 20,0%.
- Bước lô mặc định: 100 cổ phiếu.
- Thuế bán mặc định: 0,10%.
- Phong cách rủi ro: CÂN BẰNG.
- Chân trời Swing: 3–10 phiên.
- SMA: 5, 10, 20, 30, 40, 50, 100, 200.
- EMA: 12, 20, 26, 50, 200.
- RSI/ATR/ADX/MFI: 14; Bollinger Bands: 20.
- Đơn vị giá mặc định: Đồng/cổ phiếu; có lựa chọn Nghìn đồng/cổ phiếu.

Các điều khiển Sidebar hiện cho phép:
- NAV mô phỏng: mặc định 100 triệu VND; min 0; bước 5 triệu.
- Rủi ro/giao dịch: 0,1–5%; mặc định 1%; bước 0,1%.
- Tỷ trọng tối đa/mã: 1–100%; mặc định 20%; bước 1%.
- Lô: mặc định 100; bước 1.
- Sàn lựa chọn: HOSE/HNX/UPCoM; biên độ mô phỏng hiện đặt lần lượt 7%/10%/15% trong `app.py`.
- Phí mỗi chiều: mặc định 0,15%; khoảng nhập 0–2%.
- Trượt giá mỗi chiều: mặc định 0,10%; khoảng nhập 0–2%.
- Thuế bán: mặc định 0,10%; khoảng nhập 0–2%.
- Vị thế mô phỏng: CHƯA CÓ HÀNG hoặc ĐANG CÓ HÀNG; nhập số lượng, giá vốn, stop tham chiếu.

Lưu ý: biên độ sàn trong UI là tham số mô phỏng hiện được hard-code trong app; cần xác minh quy tắc hiện hành theo mã/sàn và phiên giao dịch trước khi dùng như dữ liệu thực tế.

## 3. Đầu vào dữ liệu

OHLCV chuẩn:
`date,symbol,open,high,low,close,volume`

- Có thể tải nhiều CSV/XLSX/XLS/TXT hoặc dán bảng CSV.
- Nếu tệp không có cột symbol, nhập mã ở ô Symbol hint; hint chỉ áp dụng an toàn cho một tệp.
- VNINDEX dùng symbol `VNINDEX`, được giữ nguyên điểm số và không nhân hệ số đơn vị giá cổ phiếu.
- Dữ liệu ngành tùy chọn: `date,sector,close`; `volume` tùy chọn.
- Nên nạp ít nhất 50 phiên cho phân tích; Backtest yêu cầu nhiều hơn tùy warm-up và các đoạn kiểm định.

Tệp mẫu:
- `sample_data/OHLCV_TEMPLATE.csv`
- `sample_data/SECTOR_INDEX_TEMPLATE.csv`
- `sample_data/DEMO_SYNTHETIC_OHLCV.csv` — dữ liệu tổng hợp, không phải dữ liệu thị trường thật.

## 4. Liên kết kiến trúc hiện có trong mã nguồn

Luồng phân tích live được thể hiện trong `app.py` và `modules/unified_analytics.py`:

`CSV/XLSX hoặc Paste → prepare_market_upload → Data Quality → SQLite market_history → chọn mã/benchmark/ngành → build_unified_snapshot → enrich_once → Flow/Trap + Structure + Swing Setup → Portfolio Risk → Central Decision Engine/Risk Gate → Action Plan + Decision Explainer + Trading Assistant → 3 tab`.

Các liên kết chính:
- `app.py` gọi `build_unified_snapshot()` một lần và ba tab đọc `shared_context`.
- `modules/unified_analytics.py` tính chỉ báo qua `enrich_once()`, tạo module results, gọi `central_decide()`, tạo Action Plan và Decision Explainer.
- `modules/central_decision_engine.py` gọi `modules/risk_gate.py` để chặn/giữ hành động theo các điều kiện đã định.
- `modules/position_state.py` được gọi trong Unified Snapshot khi đầu vào position có danh sách lots; nếu thiếu dữ liệu lô/settlement, trạng thái có thể là UNKNOWN và REDUCE bị chặn số lượng thực hiện.
- `modules/plan_backtest.py` dùng `price_limit_engine` và `execution_simulator` cho mô phỏng entry theo OHLCV; đây là xấp xỉ, không phải mô phỏng sổ lệnh.
- `modules/walk_forward.py` gọi `backtest_plan()` cho train/validation/test; UI có nút chạy Walk-forward trong Tab 3.

## 5. Các kho và đường dẫn lưu dữ liệu

- `data/market_history.sqlite3`: lịch sử OHLCV cục bộ, khóa chính theo symbol + date.
- `data/sector_index.csv`: dữ liệu chỉ số ngành người dùng tải.
- `data/portfolio_positions.json`: danh mục mô phỏng người dùng nhập.
- `data/trading_knowledge.sqlite`: kho tài liệu tri thức đã lập chỉ mục.
- Nhật ký quyết định: được ghi qua `modules/decision_journal.py` vào kho cục bộ.
- Backup/restore: sidebar cho phép sao lưu/khôi phục thư mục `data`; gói sao lưu dữ liệu không chứa mã nguồn.

## 6. Danh mục công thức và kiểm thử

Formula Registry hiện có 16 công thức:
SMA, EMA, RSI14, MACD, ATR14, Bollinger Bands, Stochastic, CCI20, MFI14, OBV, CLV, CMF20, ADX14, Position Sizing, Portfolio Exposure, Maximum Drawdown.

Tất cả 16 công thức hiện vẫn mang trạng thái `PENDING_INDEPENDENT_VALIDATION`. Calculation Registry có 12 mục kiểm tra AST/tệp test; trạng thái inventory không chứng minh tính đúng toán học.

Kiểm tra mới nhất trong thư mục này: `python -m pytest -q --disable-warnings --maxfail=1` — **134 passed**. Kết quả này xác nhận test suite hiện có chạy qua, không thay thế kiểm thử UI runtime, xác minh công thức độc lập hay nghiệm thu chiến lược ngoài mẫu.

## 7. Giới hạn và trạng thái phát hành

- `APP_VERSION` vẫn là **8.3.9**, không phải một bản phát hành E8.4 đã nghiệm thu.
- README/Manifest gốc của gói ghi E8.4 là đặc tả mục tiêu; các báo cáo E8.4.4–E8.4.7 mô tả các phần mở rộng trong bản làm việc. Vì các nhánh triển khai giai đoạn trước được tạo trên các lần giải nén riêng, không được coi các báo cáo giai đoạn là bằng chứng rằng mọi thay đổi đã được hợp nhất thành một bản release duy nhất.
- Streamlit runtime chưa được xác minh trong môi trường kiểm tra hiện tại.
- Formula Registry chưa có công thức VERIFIED.
- Walk-forward có cơ chế chia train/validation/test, nhưng fold hiện được báo cáo độc lập; vốn/vị thế chưa liên tục xuyên fold. Các lần chạy thử trước không tạo đủ lệnh đóng để có bằng chứng OOS đáng tin cậy.
- Execution dựa trên OHLCV, không biết hàng đợi sổ lệnh; mô phỏng partial exit chưa đầy đủ.
- Settlement nhận ngày thanh toán từ caller; chưa kết nối lịch nghỉ/ngày thanh toán chính thức.
- Corporate Actions/adjusted OHLCV chưa được tích hợp đầy đủ.
- Không có kết nối broker, không tự động đặt lệnh, không đảm bảo lợi nhuận.

**Kết luận:** Bản mã nguồn hiện có là ứng dụng phân tích Swing 3–10 phiên với ba tab, nhập dữ liệu thủ công, Snapshot dùng chung, phân tích proxy dòng tiền/bẫy giá, quản trị danh mục mô phỏng và kiểm chứng lịch sử. Đây là bản phát triển/kiểm thử, trạng thái phát hành **HOLD**, chưa phải E8.4 release.
