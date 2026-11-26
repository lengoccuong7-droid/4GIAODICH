# RELEASE ACCEPTANCE – V6.0.0

## Tiêu chí phát hành

| ID | Tiêu chí | Cách xác nhận | Trạng thái |
|---|---|---|---|
| UI-01 | Giữ đúng 3 tab chính | Kiểm tra source/navigation regression | Đạt |
| UI-02 | Giao diện Trading Desk nền tối, responsive | CSS + Streamlit theme config | Đã triển khai; cần kiểm tra trực tiếp trên thiết bị |
| IN-01 | Một luồng nhập CSV/Excel hoặc dán bảng | Kiểm tra source + parser hiện có | Đã triển khai |
| IN-02 | Một tệp có nhiều mã và VNINDEX | Chuẩn hóa mã, tách VNINDEX khỏi cổ phiếu | Đã triển khai |
| IN-03 | Lưu lịch sử cục bộ, cập nhật nối tiếp | SQLite upsert theo symbol/date | Đạt kiểm thử |
| IN-04 | Dòng giống hệt không nhân đôi; dòng sửa được cập nhật | Unit tests data_store | Đạt kiểm thử |
| IN-05 | Không tự tải dữ liệu từ API | Không có luồng fetch dữ liệu thị trường | Đạt theo thiết kế |
| AN-01 | Dùng chung một snapshot phân tích cho 3 tab | Shared analysis context | Kế thừa V5.3.0 |
| AN-02 | Không dùng một mã làm đại diện thị trường | Market regime regression tests | Kế thừa V5.3.0 |
| TR-01 | Kế hoạch Swing 3–10 phiên có trigger/SL/TP/R:R | Swing expert tests | Kế thừa V5.3.0 |
| PM-01 | Quản trị vị thế mô phỏng và trường hợp SL/TP cùng phiên | Position management tests | Kế thừa V5.3.0 |

## Kết quả kiểm thử trong môi trường build

- `pytest -q`: **66 passed**.
- `python -m compileall -q app.py modules tests`: đạt.
- Bộ test gồm hồi quy V5.3.0 và test mới cho kho SQLite (insert/update/unchanged).

## Chưa được xác nhận

1. Streamlit chưa được cài trong môi trường build, do đó chưa chạy được browser end-to-end hoặc kiểm tra trực tiếp trên iPhone/Android.
2. Chưa chạy kiểm định hiệu quả trên bộ dữ liệu thị trường thật, sạch, đủ dài và đã điều chỉnh sự kiện doanh nghiệp.
3. Chưa có kết quả walk-forward/out-of-sample được xác nhận; không công bố win rate/expectancy/profit factor như thành tích thực.
4. Dữ liệu khối ngoại/tự doanh/lệnh lớn do người dùng cung cấp chưa được xác minh độc lập nguồn.
5. Kho SQLite lưu trên ổ đĩa của môi trường chạy app; nếu triển khai môi trường có filesystem tạm thời thì phải có chiến lược sao lưu riêng.

## Quyết định

V6.0.0 hoàn thành phạm vi nâng cấp giao diện và nhập liệu, cùng các kiểm thử tự động trong môi trường hiện có. Đây là bản hỗ trợ nghiên cứu/mô phỏng, chưa phải hệ thống đã chứng minh lợi thế giao dịch hoặc được chứng nhận dùng để giao dịch tiền thật.
