# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...

## Phần đóng góp của thành viên 2 — Single và durability

Single sử dụng run_react với tối đa 8 lượt, worker=True, mỗi lượt decide được tính vào Budget qua MockLLM. Adapter quyết định hành động đọc theo trạng thái vì MockLLM không có API tool-call có cấu trúc. Order đã kiểm phạm vi principal là nguồn sự thật; ticket không dùng để ghi đè số ngày trễ. Sau vòng đọc, code tính compensation và truyền quote đầy đủ cho host. Host kiểm approval, trần theo đơn và idempotency; crash_at được truyền tiếp và InjectedCrash không bị nuốt.

Trace gồm sự kiện react, quote và decision; không ghi ticket hay parent context. Sáu trường hợp test riêng kiểm ba cửa sổ crash, retry, cấu hình vòng đọc/đếm model call, xử lý step_cap và trace của unknown claim. Public matrix Single ban đầu đạt 62/62; test mặc định sau tích hợp đạt 75 passed. Crash suite chính thức đạt 20/20 (host và swarm); crash riêng Single được kiểm chứng bằng test riêng và public T12.

Thành viên 2 đã review Orchestrator: handoff qua allowlist, investigator chỉ đọc, trace tóm tắt dữ liệu an toàn, full quote và crash_at chuyển đến host. Benchmark do thành viên 3 cung cấp cho Single có 70 trial, pass rate và pass^5 bằng 1.0, cost/success mô phỏng 28.563 VND. Chưa suy rộng kết quả public thành hidden hoặc hiệu năng LLM thật.
