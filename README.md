# BOT TRADER SWING MULTI E8.4.0-dev2

Bản phát triển tiếp nối E8.3.9, giữ kiến trúc ứng dụng hiện có và nâng cấp theo từng bước có kiểm thử. Đây **chưa phải bản phát hành nghiệm thu cuối cùng**.

## Giao diện — giữ đúng 3 tab

1. **TỔNG QUAN** — kết quả phân tích và Final Action.
2. **DẤU CHÂN DÒNG TIỀN** — hành vi giá/khối lượng và các proxy OHLCV.
3. **TRỢ LÝ TRADING** — kịch bản mô phỏng, quản trị vị thế, nhật ký và tiện ích dữ liệu.

## Thay đổi trong E8.4.0-dev2

- Mở rộng Formula Registry từ 16 lên 28 công thức/nhóm tính toán, bao phủ thêm ROC, Williams %R, RVOL, VWAP rolling, AD Line, DI, Ichimoku, Pivot, Supertrend, Volume Z-score, Amihud proxy và Sharpe.
- Giữ trạng thái `PENDING_INDEPENDENT_VALIDATION` cho toàn bộ công thức; việc có mặt trong registry hoặc vượt unit test không đồng nghĩa đã được xác minh độc lập.
- Siết kiểm tra đầu vào Position Sizing: lô phải là số nguyên dương, không chấp nhận boolean/phân số; Risk% và Allocation% phải trong khoảng 0–100.
- Bổ sung kiểm thử hồi quy cho registry, inventory và các trường hợp đầu vào rủi ro.
- Đồng bộ schema Unified Snapshot lên 8.4.0; siết Risk Gate và kiểm tra số lượng bán chờ thanh toán.
- Sửa giá cơ sở khớp lệnh trong backtest theo kết quả Execution Simulator; bổ sung import còn thiếu cho trap forward diagnostics.
- Bổ sung fixture tham chiếu độc lập cho một số công thức lõi; chuẩn hóa Module Contracts có truy vết Snapshot ID; tổng số kiểm thử hiện tại 150.

## Chạy ứng dụng

Yêu cầu Python 3.10 trở lên:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Kiểm thử

```bash
python -m pytest -q
python -m compileall -q app.py config.py modules tests
# Kết quả hiện tại: 150 passed; compileall passed
```

## Giới hạn cần hoàn thiện trước nghiệm thu

- Các công thức vẫn chờ fixture tham chiếu độc lập và quy ước seed/warm-up được chốt.
- Snapshot hiện immutable-by-convention, chưa cưỡng chế bất biến; cần tiếp tục hoàn thiện contracts, corporate actions, settlement theo lịch và tính liên tục trạng thái danh mục trong walk-forward.
- Streamlit runtime cần được chạy thử trong môi trường cài đủ dependencies; hiện chưa xác minh do môi trường chưa cài Streamlit.
- Dữ liệu dòng tiền từ OHLCV chỉ là proxy; không xác định được giao dịch của tổ chức hay lệnh chủ động. Mô phỏng không tái tạo đầy đủ sổ lệnh.

Ứng dụng phục vụ nghiên cứu, học tập và mô phỏng; không kết nối broker, không tự đặt lệnh, không cam kết lợi nhuận và không thay thế tư vấn tài chính chuyên nghiệp.
