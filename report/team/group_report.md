# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: AAA (lớp L3B)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 5866b21

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

## Phần đóng góp của thành viên 2 — Single và durability

Single sử dụng run_react với tối đa 8 lượt, worker=True, mỗi lượt decide được tính vào Budget qua MockLLM. Adapter quyết định hành động đọc theo trạng thái vì MockLLM không có API tool-call có cấu trúc. Order đã kiểm phạm vi principal là nguồn sự thật; ticket không dùng để ghi đè số ngày trễ. Sau vòng đọc, code tính compensation và truyền quote đầy đủ cho host. Host kiểm approval, trần theo đơn và idempotency; crash_at được truyền tiếp và InjectedCrash không bị nuốt.

Trace gồm sự kiện react, quote và decision; không ghi ticket hay parent context. Sáu trường hợp test riêng kiểm ba cửa sổ crash, retry, cấu hình vòng đọc/đếm model call, xử lý step_cap và trace của unknown claim. Public matrix Single ban đầu đạt 62/62; test mặc định sau tích hợp đạt 75 passed. Crash suite chính thức đạt 20/20 (host và swarm); crash riêng Single được kiểm chứng bằng test riêng và public T12.

Thành viên 2 đã review Orchestrator: handoff qua allowlist, investigator chỉ đọc, trace tóm tắt dữ liệu an toàn, full quote và crash_at chuyển đến host. Benchmark do thành viên 3 cung cấp cho Single có 70 trial, pass rate và pass^5 bằng 1.0, cost/success mô phỏng 28.563 VND. Chưa suy rộng kết quả public thành hidden hoặc hiệu năng LLM thật.

### Thí nghiệm bổ sung của thành viên 2 (ticket ablation)

- Giả thuyết: thay ticket bằng yêu cầu sai (99 ngày trễ, đòi 999999999 VND, ignore policy) không đổi pass rate và cost/success của Single, vì code chỉ tin order và không đưa ticket vào prompt. Giả thuyết gần như hiển nhiên đúng theo thiết kế, nên thí nghiệm này xác nhận thiết kế hơn là có khả năng bác bỏ.
- Kết quả thực chạy: baseline 70/70 và treatment 70/70 trial pass; cả hai pass rate=1.0, pass^5=1.0, seed variance=0, cost/success=28.562857142857144 VND mô phỏng. Không có sai khác ở 70 cặp trial trên các field so sánh. Hypothesis phù hợp dữ liệu trong phạm vi bộ public này.

Chỉ thay ticket, giữ nguyên điều kiện còn lại; thí nghiệm này tách biệt với ablation của phiếu nghiên cứu (R1, xem `research_card.md`); phương pháp theo hướng failure taxonomy (MAST, Cemri et al. 2025, arXiv:2503.13657, nhóm chưa kiểm lại nguồn). Thực hiện bởi Ngô Duy Khánh với Codex hỗ trợ. Lệnh chạy trong `src/`: `python scripts/member2_ticket_ablation.py` (cần `PYTHONPATH=.`); script `src/scripts/member2_ticket_ablation.py`, kết quả `src/reports/member2_ticket_ablation.json`. Script và JSON report được lưu để tái lập; không sửa dữ liệu gốc.
