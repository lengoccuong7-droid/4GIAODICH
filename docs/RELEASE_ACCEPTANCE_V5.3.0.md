# RELEASE ACCEPTANCE – V5.3.0

## Tiêu chí chức năng

| ID | Tiêu chí | Cách xác nhận | Trạng thái mã nguồn |
|---|---|---|---|
| MR-01 | Phân loại thị trường thuận lợi/trung tính/rủi ro | VN-Index với tối thiểu 50 phiên | Đã triển khai |
| MR-02 | Không lấy một mã làm đại diện thị trường | Không có benchmark và universe dưới 5 mã | Đã triển khai + test |
| ST-01 | Phân loại tích lũy/tăng/phân phối nghi vấn/suy yếu/chuyển pha | MA, biên độ, proxy dòng tiền | Đã triển khai + test |
| FL-01 | Phân tích dòng tiền OHLCV | OBV/CLV/RVOL/phiên cung mạnh | Đã triển khai |
| TR-01 | Phân biệt bẫy chờ xác nhận, xác nhận, vô hiệu, mâu thuẫn | Trap follow-through | Đã triển khai |
| PL-01 | Có vùng theo dõi, giá xác nhận, SL, TP1/TP2, R:R | Strategy engine | Đã triển khai |
| PL-02 | Không lập kế hoạch mới khi thiếu benchmark/điều kiện chặn | Market gate + blockers | Đã triển khai + test |
| PM-01 | Quản trị vị thế mô phỏng | SL/TP/trailing/giảm một phần | Đã triển khai |
| PM-02 | Không giả định thứ tự SL/TP trong cùng nến ngày | Intraday ambiguity state | Đã triển khai + test |
| RK-01 | Tính quy mô theo phí/thuế/trượt giá/lô | Risk manager | Đã triển khai + regression test |
| UI-01 | Giao diện 3 tab | Source/navigation test | Đã triển khai + test cấu trúc |

## Kết quả kiểm thử

`pytest -q`: **62 passed**.

`python -m compileall -q app.py modules tests`: đạt.

## Các kiểm tra chưa thể tuyên bố đạt

1. Kiểm thử UI end-to-end trên Streamlit/browser/mobile: chưa chạy trong môi trường build vì package Streamlit chưa được cài đặt ở đây.
2. Kiểm định hiệu quả chiến lược: chưa thể kết luận khi chưa có bộ dữ liệu OHLCV thật, sạch, đủ dài và được điều chỉnh sự kiện doanh nghiệp.
3. Walk-forward/out-of-sample và kiểm thử khớp lệnh thực tế: chưa được thực hiện.
4. Nguồn khối ngoại/tự doanh/lệnh lớn: app chỉ kiểm tra định dạng và ngày; người dùng phải xác minh nguồn dữ liệu.

## Quyết định phát hành

V5.3.0 là bản hoàn thiện chức năng theo phạm vi phần mềm và bộ kiểm thử tự động hiện có, không phải bản demo. Tuy nhiên, không được mô tả là đã chứng minh lợi thế giao dịch hoặc sẵn sàng tự động hóa quyết định tiền thật. Trước khi đánh giá hiệu quả, phải kiểm thử giao diện trên thiết bị đích và chạy walk-forward trên dữ liệu thật.
