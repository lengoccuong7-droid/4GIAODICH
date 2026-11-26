# E8.4.0-dev2 — thay đổi và kiểm định

## Thay đổi mã nguồn

- Đồng bộ `schema_version`, fingerprint định danh và `calculation_contract` của Unified Snapshot sang `8.4.0`; tránh snapshot mới vẫn mang nhãn schema `8.3.0`.
- Risk Gate từ chối quantity Boolean, phân số, không hữu hạn hoặc không chuyển đổi được; không tự ép quantity sai định dạng thành số nguyên.
- Position State kiểm tra `pending_sell` là số nguyên hữu hạn không âm trước khi tính số lượng có thể bán.
- Backtest sử dụng giá khớp cơ sở do Execution Simulator trả về (giá mở cửa có price improvement hoặc giá giới hạn), sau đó mới áp dụng slippage và giới hạn giá.
- Bổ sung import còn thiếu cho `trap_forward_stats`; trước đây gọi hàm có thể phát sinh `NameError`.
- Bổ sung fixture tính độc lập bằng phép tính trực tiếp cho SMA20, Bollinger Bands, CLV, RVOL20, OBV và Position Sizing; bổ sung edge case Stochastic khi toàn bộ cửa sổ phẳng.
- Bổ sung kiểm thử snapshot schema, pending sell, quantity Risk Gate, benchmark ngày trùng và trap forward diagnostics.
- Chuẩn hóa Module Contracts với `module_id`, `signal`, `limitations`, `source_refs`, `snapshot_id` và `calculation_version`; mọi kết quả module trong snapshot được gắn cùng snapshot ID.

## Kiểm thử tái lập

- `python -m pytest -q`: **150 passed**.
- `python -m compileall -q app.py config.py modules tests`: **passed**.
- Streamlit runtime: **chưa xác minh** vì môi trường hiện tại không có package `streamlit`.

## Giới hạn còn mở — chưa được tuyên bố hoàn tất

- 28 mục Formula Registry vẫn `PENDING_INDEPENDENT_VALIDATION`. Fixture hiện tại kiểm tra một số phép tính lõi, không đủ để đánh dấu toàn bộ công thức VERIFIED.
- RSI/ATR/ADX hiện dùng EWM `adjust=False`, `alpha=1/n`; chưa chuyển sang SMA-seeded Wilder vì cần quyết định chuẩn tham chiếu tương thích.
- Snapshot là immutable-by-convention, chưa phải cấu trúc bất biến được runtime cưỡng chế.
- Walk-forward hiện chạy các fold độc lập; vốn và vị thế chưa liên tục xuyên fold.
- Chưa tích hợp nguồn Corporate Actions/Event Calendar có kiểm chứng; chưa thể tự điều chỉnh dữ liệu giá hay đánh giá sự kiện doanh nghiệp.
- Price limit, tick size, settlement date phải được cung cấp đúng theo mã/sàn/ngày; không được coi cấu hình mặc định là bộ quy tắc giao dịch Việt Nam đầy đủ.
- Execution Simulator là xấp xỉ OHLCV, không mô phỏng hàng đợi sổ lệnh, độ sâu thị trường hoặc xác suất khớp thực tế.
- Streamlit UI, luồng nhập/xuất file, backup/restore và hiển thị trên thiết bị thật cần được người dùng chạy kiểm tra trong môi trường có dependencies.

## Kết luận

E8.4.0-dev2 là bản phát triển có kiểm thử tự động, **chưa phải bản nghiệm thu cuối hoặc hệ thống giao dịch sản xuất**. Chỉ sử dụng cho nghiên cứu, học tập và mô phỏng.
