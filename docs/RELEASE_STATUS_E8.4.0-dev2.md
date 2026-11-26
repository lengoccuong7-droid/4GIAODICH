# Trạng thái bàn giao — BOT TRADER SWING MULTI E8.4.0-dev2

## Phạm vi bàn giao

- Bản phát triển kế thừa mã nguồn E8.3.9; không ghi đè bản gốc.
- Giữ giao diện Streamlit đúng 3 tab: Tổng quan, Dấu chân dòng tiền, Trợ lý Trading.
- Có Formula Registry 28 mục, Unified Snapshot schema 8.4.0, Module Contracts, Risk Gate, Position State, Execution Simulator và walk-forward orchestration.
- Có bộ kiểm thử hồi quy và dữ liệu mẫu tổng hợp để chạy thử.

## Kết quả kiểm định trong môi trường đóng gói

- `pytest -q`: 150 passed.
- `compileall`: passed.
- `app.py` khai báo đúng 3 tab chính.
- Streamlit runtime: không chạy được trong môi trường đóng gói do package `streamlit` không có sẵn và môi trường không truy cập được PyPI. Người dùng cần cài dependencies từ `requirements.txt` trước khi chạy.

## Các giới hạn chưa được nghiệm thu

1. Formula Registry có 28 mục nhưng toàn bộ vẫn ở trạng thái `PENDING_INDEPENDENT_VALIDATION`; fixture độc lập hiện chỉ bao phủ một tập con. Không được hiểu 150 test pass là 28 công thức đã được chứng minh đúng.
2. Walk-forward tạo các fold train/validation/test theo thời gian, chọn ứng viên trên validation và chạy test riêng; vốn và vị thế không được duy trì liên tục xuyên các fold.
3. Chưa tích hợp nguồn Corporate Actions và lịch sự kiện doanh nghiệp đã xác minh.
4. Tick size, price limit và lịch settlement phải được cấu hình theo sàn/mã/ngày. Không coi cấu hình mặc định là bộ quy tắc thị trường Việt Nam hoàn chỉnh.
5. Execution Simulator dùng xấp xỉ OHLCV, không tái tạo order book, queue priority, market impact hoặc xác suất khớp thực tế.
6. Cần chạy thử UI, import/export và backup/restore trên máy người dùng có đủ dependencies.

## Hướng dẫn chạy

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Phân loại sử dụng

Bản này dành cho học tập, nghiên cứu và mô phỏng. Không kết nối broker, không tự động đặt lệnh, không cam kết lợi nhuận và không phải khuyến nghị mua/bán chứng khoán.
