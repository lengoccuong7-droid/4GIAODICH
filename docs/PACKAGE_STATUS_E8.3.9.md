# Trạng thái gói bàn giao E8.3.9

## Phạm vi gói

- Mã nguồn E8.3.9: bao gồm working tree E8.3.8 và cập nhật kiểm toán G9 về cách biểu diễn rủi ro danh mục khi thiếu Stop; APP_VERSION được đồng bộ thành 8.3.9.
- Đúng 3 tab giao diện theo kiểm tra tĩnh.
- Tài liệu đặc tả mục tiêu E8.4 được đính kèm tại `ARCHITECTURE_E8.4_SPEC.md`; E8.4 chưa được triển khai trong gói này.

## Kiểm tra tại thời điểm đóng gói

- Pytest: 115 passed.
- Compileall: passed.
- Streamlit runtime: chưa xác minh do môi trường đóng gói không cài Streamlit.
- Formula Registry: 16 công thức, chưa có công thức nào được xác minh độc lập (PENDING_INDEPENDENT_VALIDATION).
- Walk-forward độc lập: chưa có.
- Event/Market Risk module và Scenario Simulator độc lập: chưa tìm thấy trong working tree.
- Kiểm thử dữ liệu lịch sử đã điều chỉnh corporate actions và khả năng khớp lệnh thực tế: chưa đủ bằng chứng.

## Trạng thái nghiệm thu

**HOLD — gói mã nguồn và tài liệu để tiếp tục phát triển/đánh giá, không phải bản phát hành đã nghiệm thu đầy đủ.**
