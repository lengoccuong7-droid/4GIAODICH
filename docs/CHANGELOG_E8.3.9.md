# E8.3.9 — Giai đoạn 9: Kiểm toán và nghiệm thu

- Sửa `summarize_portfolio`: vị thế thiếu stop được đánh dấu UNKNOWN, không còn quy thành rủi ro 0.
- Bổ sung chỉ số độ bao phủ dữ liệu stop (`risk_coverage_pct`).
- Bổ sung 4 kiểm thử nghiệm thu G9.
- Lập biên bản kiểm toán nêu rõ 16/16 công thức chưa xác minh độc lập, chưa có walk-forward module, Event Risk/Scenario Simulator chưa hiện diện trong working tree, Streamlit runtime chưa kiểm thử.
- Trạng thái phát hành: HOLD; chưa tạo ZIP.

Kiểm thử tại thời điểm ghi nhận: 115 passed; compileall passed.

## E8.4.7 — Giai đoạn 7: Tích hợp mã nguồn (bản làm việc)
- Tập trung Risk Gate thành module dùng chung, Central Decision Engine là nguồn quyết định duy nhất.
- Bổ sung Position State theo lô và ngày settlement tường minh; thiếu settlement giữ UNKNOWN và chặn thực hiện giảm vị thế.
- Bổ sung Price Limit Engine và Execution Simulator; Backtest kiểm tra liquidity participation ở entry, ghi nhận partial fill.
- Đưa Trading Assistant vào Unified Snapshot; tab Trợ lý Trading đọc kết quả snapshot, không tự phân tích OHLCV lần hai.
- Chuẩn hóa fingerprint theo thứ tự date/symbol; bổ sung test hoán vị dòng dữ liệu.
- Bổ sung 11 kiểm thử tích hợp; toàn bộ suite hiện tại 134/134 đạt.
- Giới hạn còn lại: 16 công thức vẫn PENDING_INDEPENDENT_VALIDATION; chưa có Streamlit runtime, exchange calendar, corporate actions đầy đủ, partial exit hoặc portfolio carry-over giữa walk-forward folds. Chưa phải nghiệm thu cuối E8.4.
