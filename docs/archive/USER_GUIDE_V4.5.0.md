# Hướng dẫn sử dụng BOT TRADER SWING MULTI V4.5.0

## 1. Cấu trúc ứng dụng

Ứng dụng có đúng 3 tab chính:

1. **TỔNG QUAN** – điểm sàng lọc 0–100, 5 nhóm chỉ số, xu hướng, nhận định nhanh và biểu đồ giá.
2. **DẤU CHÂN DÒNG TIỀN** – khối ngoại, tự doanh, lệnh lớn và OBV/CLV proxy; kết luận VÀO / TRUNG TÍNH / RA khi có dữ liệu tương ứng.
3. **CHIẾN LƯỢC** – kế hoạch cho người chưa có hàng hoặc quản trị vị thế đang nắm giữ.

## 2. Dữ liệu đầu vào

Trong Sidebar **DỮ LIỆU & THÔNG SỐ**:

- Tải OHLCV chính: CSV/XLSX/XLS/TXT/JSON/Parquet; tối thiểu 50 phiên hợp lệ để tạo kế hoạch Swing.
- Nhập mã nếu file không có cột mã.
- Tải VN-Index và chỉ số ngành nếu muốn đánh giá sức mạnh tương đối.
- Chọn trạng thái **CHƯA CÓ HÀNG** hoặc **ĐANG CÓ HÀNG**.
- Nhập NAV, rủi ro tối đa, tỷ trọng tối đa, bước lô, phí và trượt giá.
- Khi đang có hàng, nhập số lượng, giá vốn và mức dừng lỗ giả định.

## 3. File dấu chân dòng tiền bổ sung

Đây là dữ liệu tùy chọn, không thể tự suy ra chính xác từ OHLCV. File CSV/XLSX cần có các cột:

| Cột | Ý nghĩa |
|---|---|
| `date` | Ngày giao dịch |
| `foreign_net_value` | Giá trị mua ròng khối ngoại (VND) |
| `proprietary_net_value` | Giá trị mua ròng tự doanh (VND) |
| `large_buy_value` | Giá trị lệnh lớn mua (VND) |
| `large_sell_value` | Giá trị lệnh lớn bán (VND) |

App cộng gộp 5 dòng/phiên gần nhất trong file. Với khối ngoại và tự doanh: số dương = VÀO, số âm = RA, bằng 0 = TRUNG TÍNH. Với lệnh lớn: so sánh tổng mua lớn với tổng bán lớn. Nếu không có file, app hiển thị **CHƯA CÓ DỮ LIỆU**, không tự gán nhãn.

Mẫu file: `sample_data/FLOW_DATA_TEMPLATE.csv`.

## 4. Cách đọc kết quả

### Tổng quan

Điểm 0–100 là điểm sàng lọc heuristic từ bộ máy Swing, không phải xác suất thắng. Năm nhóm điểm là các thang đánh giá hỗ trợ đọc nhanh: xu hướng, động lượng, khối lượng, dòng tiền & bẫy giá, cấu trúc & thị trường.

### Dấu chân dòng tiền

OBV/CLV được tính từ OHLCV nên chỉ là proxy. Khối ngoại, tự doanh và lệnh lớn chỉ phản ánh dữ liệu file người dùng cung cấp. App không xác minh nhà cung cấp hoặc tính đầy đủ của file.

### Chiến lược

- **Chưa có hàng:** đọc giá kích hoạt, Stop Loss, TP1/TP2, R:R, số lượng tham chiếu và điều kiện chặn.
- **Đang có hàng:** đọc giá vốn, lãi/lỗ tạm tính, mốc bảo vệ, mục tiêu và trailing stop tham chiếu.
- Nếu dữ liệu thiếu hoặc có điều kiện chặn, không xem mức giá tham chiếu là lệnh mua/bán.

## 5. Chạy ứng dụng

Windows: chạy `run_windows.bat`.

macOS/Linux: chạy `run_mac_linux.sh`.

Hoặc cài dependencies trong `requirements.txt`, sau đó chạy:

```bash
streamlit run app.py
```

## 6. Giới hạn

V4.5.0 không tự kết nối dữ liệu thị trường trực tuyến và không đặt lệnh. Dữ liệu OHLCV không chứng minh được tổ chức đang mua/bán. Chiến lược chưa được xác nhận bằng walk-forward/out-of-sample; cần kiểm thử dữ liệu thực tế trước khi dùng với tiền thật.
