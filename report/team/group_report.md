# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: AAA (lớp L3B)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc rồi chọn kiến trúc ít tự chủ nhất mà vẫn đạt yêu cầu. Nhóm 3 người, mỗi người một shape: Minh làm workflow và tích hợp, Khánh làm single agent và crash safety, Trình làm orchestrator và benchmark. Swarm có sẵn để đối chứng. Mỗi người làm trên branch riêng, sau đó ghép về nhánh `minh`.

## 3. Giải pháp

Ở cả ba shape, tiền do `compute_compensation` tính từ order row đã kiểm phạm vi principal và policy hiện hành. Model không chọn số tiền, không ghi ledger. Chữ trong ticket là dữ liệu, không dùng để lấy `order_id` hay số ngày trễ. Shape truyền **quote đầy đủ** vào `durability.issue_refund` cùng `crash_at`; host kiểm approval, trần theo đơn, idempotency. `InjectedCrash` không bị bắt.

- **Workflow:** các bước Python cố định (claim → order → quote → issue_refund), không gọi MockLLM. Trace ghi cờ có order, order view allowlist, quote, quyết định.
- **Single:** vòng `run_react` tối đa 8 bước, `worker=True` nên chỉ gọi tool đọc; mỗi lượt decide tính vào Budget. Code tính tiền và gọi host sau vòng lặp.
- **Orchestrator:** dựng handoff bằng `make_handoff` (allowlist, tool chỉ đọc), investigator chạy tool đọc, orchestrator tính quote và gọi host. Trace ghi handoff đã sanitize, không ghi parent context.

## 4. Kết quả

Nguồn: `src/reports/benchmark.json` (14 claim, seed 11,22,33,44,55).

| Shape | Pass | pass^5 | Variance | Min–max | Cost/success (VND mô phỏng) | Steps trung bình |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 27.86 | 4.36 |
| single | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 28.56 | 2.79 |
| orchestrator | 1.000 | 1.000 | 0.000000 | 1.000–1.000 | 55.71 | 3.71 |
| swarm | 0.986 | 0.929 | 0.000816 | 0.929–1.000 | 49.57 | 2.80 |

Crash safety: 20/20 (`src/reports/crash.json`). Lệnh `lab8.crash_test` chạy shape swarm nên bằng chứng crash riêng cho ba shape nhóm là test T12 và `test_single_team.py`. Chưa chạy tự kiểm trên `student_drop/` và chưa có hidden grade.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- Swarm fail C-002 ở seed 55 vì tin số ngày trễ trong ticket; workflow, single và orchestrator đọc từ order row nên không dính lỗi này.
- `lab8.crash_test` chỉ chạy swarm nên không đủ chứng minh crash safety của ba shape nhóm viết; nhóm dựa thêm vào T11, T12 trong ma trận student.
- Tên branch trong ghi chú bàn giao của Khánh khác branch thật (`dkhanh-single-agent`); không ảnh hưởng code.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Kết luận chỉ dựa trên 14 claim public và MockLLM; chưa có hidden grade nên chưa khẳng định pass rate hidden ≥ 0.75. Single dùng MockLLM không có tool-call API nên `decide` là chuỗi cố định, không chứng minh hành vi LLM thật. Quyết định đảo lại nếu hidden cho thấy workflow dưới 0.75.

## 8. Tài liệu tham khảo

- Đề bài và tài liệu trong repo: `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`.
