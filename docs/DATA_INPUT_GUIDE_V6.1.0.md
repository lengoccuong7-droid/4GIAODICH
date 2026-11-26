# HƯỚNG DẪN NHẬP DỮ LIỆU V6.1.0

## Chỉ cần một bộ OHLCV

Các cột bắt buộc: `date, symbol, open, high, low, close, volume`.

Ví dụ:

```csv
date,symbol,open,high,low,close,volume
2026-11-18,DXG,15000,15300,14800,15200,2500000
2026-11-18,VNINDEX,1650,1660,1645,1655,650000000
```

- Có thể tải CSV/Excel hoặc dán bảng.
- Có thể nhập nhiều mã trong một tệp.
- Nếu không có cột symbol, chỉ dùng được một mã và cần nhập mã ở ô gợi ý.
- Đưa VNINDEX vào cùng tệp nếu muốn đánh giá bối cảnh thị trường bằng benchmark.
- Chọn đúng đơn vị giá cổ phiếu; VNINDEX luôn giữ nguyên điểm số.

Không cần nạp dữ liệu chỉ báo, khối ngoại, tự doanh hoặc lệnh lớn. Không nhập dữ liệu không có nguồn rõ ràng.
