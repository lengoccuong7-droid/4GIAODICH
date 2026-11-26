# BOT TRADER SWING MULTI E8.3.9

## Nâng cấp từ E8.2

E8.3 bảo toàn kiến trúc E8.2 và đúng 3 tab. Không thiết kế lại từ đầu, không thêm tầng kiến trúc hoặc tab mới.

### Ba hiệu chỉnh kiến trúc

1. **Final Action routing**
   - ENTER_LONG → kế hoạch vị thế mới.
   - WAIT → kế hoạch chờ kích hoạt; nếu có vị thế hiện tại thì chuyển thành HOLD_AND_MONITOR.
   - REDUCE → kế hoạch quản trị/giảm vị thế hiện tại.
   - NO_TRADE → bypass Action Plan, đi thẳng Decision Explainer.
2. **Data flow**
   - Data Ingestion có kiểm tra đầu vào trước khi lưu; Data Quality kiểm tra lại freshness, lịch sử và khoảng cách ngày khi tạo snapshot.
   - Data Ingestion → Data Quality → Enrich Once → Unified Snapshot → Analysis Modules.
   - Enrich Once là bước tính toán, không phải một architectural layer riêng.
3. **Portfolio linkage**
   - Tab 3 lưu danh mục mô phỏng tại `data/portfolio_positions.json`.
   - Snapshot đọc dữ liệu danh mục và vị thế, sau đó truyền vào Portfolio Manager và Central Decision Engine.
   - Không có danh mục: `UNKNOWN`; không giả định mức phơi nhiễm bằng 0.

## Chạy ứng dụng

Windows: chạy `install_windows.bat`, sau đó `run_windows.bat`.

macOS/Linux: chạy `bash run_mac_linux.sh` hoặc cài `requirements.txt` và chạy `streamlit run app.py`.

## Kiểm thử

`python -m pytest -q`

`python -m compileall -q app.py config.py modules tests`

## Giới hạn đã biết

- Danh mục chỉ phản ánh các vị thế người dùng đã nhập; chưa tự đồng bộ tài khoản chứng khoán.
- Backtest hiện mô phỏng tuần tự một vị thế, không phải danh mục đa mã đồng thời.
- Streamlit runtime cần được kiểm tra trên máy cài dependencies; không xem compile/test logic là xác nhận giao diện runtime.
- Mọi kết quả là phân tích và mô phỏng phục vụ học tập/nghiên cứu, không phải khuyến nghị đầu tư hay tự động đặt lệnh.

## E8.3.1 — Hoàn thiện giai đoạn 1

Ba kho được tích hợp trong Tab 3 (không tạo tab mới):
- **Kho tri thức:** nạp, tìm kiếm, xem và quản lý tài liệu cục bộ tại `data/trading_knowledge.sqlite`.
- **Kho công thức:** danh mục công thức tập trung tại `modules/formula_registry.py`; các công thức vẫn chờ kiểm chứng độc lập.
- **Kho lập trình tính toán:** danh mục module/hàm tại `modules/calculation_registry.py`, kiểm tra tĩnh bằng AST và đối chiếu tệp test.

Xem `docs/CHANGELOG_E8.3.1.md` và `docs/PHASE1_STORE_ACCEPTANCE_E8.3.1.md`. Kiểm tra tĩnh và pytest không đồng nghĩa đã xác nhận tính đúng toán học của mọi công thức hoặc xác nhận Streamlit runtime.


## E8.3.8 — Giai đoạn 8: Giao diện và vận hành
- Giữ đúng ba tab và CSS responsive hiện có.
- Thêm sao lưu/khôi phục dữ liệu cục bộ từ sidebar, không đóng gói mã nguồn.
- Xem `docs/CHANGELOG_E8.3.8.md` và `docs/PHASE8_ACCEPTANCE_E8.3.8.md` để biết phạm vi đã kiểm thử và giới hạn runtime.


## Trạng thái E8.3.9

Giai đoạn 9 đang ở trạng thái HOLD theo `docs/PHASE9_ACCEPTANCE_E8.3.9.md`; chưa phải bản phát hành.
