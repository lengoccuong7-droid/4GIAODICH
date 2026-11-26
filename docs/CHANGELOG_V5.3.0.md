# CHANGELOG V5.3.0

## Mục tiêu phát hành
Chuẩn hóa ứng dụng theo chiến lược Swing 3–10 phiên và đáp ứng 5 đầu ra bắt buộc: thị trường chung, pha cổ phiếu, dòng tiền/bẫy giá, kế hoạch giá có điều kiện và quản trị vị thế.

## Thay đổi
- Chuẩn hóa khung Swing trong engine thành 3–10 phiên.
- Market regime có nhãn THUẬN LỢI / TRUNG TÍNH / RỦI RO; thiếu benchmark hoặc breadth đủ rộng sẽ được báo CHƯA ĐỦ DỮ LIỆU và chặn kế hoạch mở vị thế mới.
- Thêm phân loại pha cổ phiếu theo cấu trúc MA, biên độ 20 phiên và proxy cung–cầu.
- Bổ sung hiển thị các dấu hiệu bất thường: phiên khối lượng cao/đóng cửa yếu, CLV-volume proxy, phân kỳ giá–OBV và sự kiện Trap Detection.
- Kế hoạch giá hiển thị rõ vùng theo dõi, giá xác nhận, mức vô hiệu, TP1/TP2; TP1 được đối chiếu kháng cự 50 phiên khi có dữ liệu.
- Tính quy mô vị thế đã truyền đúng phí, trượt giá và thuế bán từ Sidebar vào engine.
- Quản trị vị thế nhận diện SL/TP chạm trong phiên; nếu cùng một nến ngày chạm cả SL và TP, báo đường đi intraday không xác định thay vì giả định thứ tự khớp.
- Bổ sung gợi ý giảm một phần vị thế mô phỏng tại TP1 và bảo vệ phần còn lại.
- Không quy đổi đơn vị VN-Index/ngành theo đơn vị giá cổ phiếu.
- Làm mới README, Manifest và tiêu chí phát hành.

## Kiểm thử
- 62/62 kiểm thử tự động đạt.
- Chưa có kiểm thử giao diện Streamlit end-to-end trong môi trường build do thiếu package Streamlit.
- Chưa chứng nhận hiệu quả đầu tư; cần dữ liệu thật và kiểm định ngoài mẫu.
