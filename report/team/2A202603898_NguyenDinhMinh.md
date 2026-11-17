# Báo cáo cá nhân — 2A202603898_NguyenDinhMinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Minh
- MSSV: 2A202603898
- Email: 26ai.minhnd7@vinuni.edu.vn
- GitHub: https://github.com/MinhNGD76

## 2. Phần việc phụ trách

Shape A `workflow` và tích hợp.

- Viết shape `workflow` tại `src/lab8/shapes/workflow.py`.
- Viết test bổ sung cho shape này tại `src/tests/test_workflow_extra.py`.
- Review `single.py` của Khánh, ghép ba branch, chạy `check_submission`, điền `TEAM.md` và phần workflow trong `group_report.md`: **chưa làm** tại thời điểm viết báo cáo này.

## 3. Đóng góp cụ thể

Commit chính: `b852fc8` (workflow và `test_workflow_extra.py`); `cdc5e93` và `5b2acaa` (merge nhánh của Khánh và Trình vào `minh`).

Quyết định kỹ thuật:

- Luồng cố định, không gọi MockLLM (`model_calls = 0`): đọc claim bằng `get_claim_view` → thiếu `order_id` trả `needs_info` → `lookup_order`, không thấy hoặc không thuộc principal trả `escalated` → `compute_compensation` → quote bằng 0 trả `denied` → quote lớn hơn 0 gọi `durability.issue_refund`.
- Truyền **quote đầy đủ** vào `issue_refund` để host tự trừ phần đã hoàn trước đó theo đơn (T13, T14), không tự trừ trong shape.
- Quote lớn hơn 0 mà host từ chối vẫn giữ `proposal_amount` là quote; xung đột số tiền trả `failed`.
- Truyền `crash_at` vào `issue_refund` và không bắt `InjectedCrash`. Trước khi ném tiếp, shape ghi trace để trace vẫn tồn tại khi crash.
- Chữ trong ticket được coi là dữ liệu: không lấy `order_id` hay số ngày trễ từ ticket, nên không dính lỗi của swarm ở seed 55.
- Mọi nhánh return đi qua `finish()` nên ledger, audit và trace do host/thư viện sinh ra. Trace chỉ ghi field đã qua allowlist (`get_claim_view`, `lookup_order`, quote), không ghi claim row hay order row thô.

Test đã thêm (`src/tests/test_workflow_extra.py`):

- `test_workflow_trace_never_leaks_secret_or_pii`: quét trace và kết quả của toàn bộ claim public, không có `CANARY_SECRET_`, số điện thoại hay địa chỉ.
- `test_workflow_unknown_claim_fails_with_valid_trace`: claim không tồn tại trả `failed`, `proposal_amount = 0`, trace có `run_id` đúng và `events` là list.
- `test_workflow_is_seed_independent_and_uses_no_model`: C-002 ở seed 11 và 55 đều `denied`, `model_calls = 0`.

## 4. Bằng chứng

Chạy trong `src/` trên branch `minh`:

- `python -m lab8.smoke`: `lab8.smoke pass`.
- `python -m pytest -q` (cổng host): 57 passed.
- `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed.
- `python -m pytest -q tests/test_workflow_extra.py`: 3 passed.
- Toàn bộ ma trận student: 124 failed, 124 passed. Phần fail là 62 test của `single` và 62 test của `orchestrator`, vì hai shape này chưa được ghép vào.

Sau khi ghép ba shape, chạy lại trên `minh`: `pytest -q` 75 passed; ma trận student 248 passed; benchmark 4 shape × 14 claim × 5 seed và `crash_test` `20/20` do công cụ sinh ra (`src/reports/benchmark.json`, `crash.json`); ablation `src/reports/ablation_r1.json`. Số benchmark khớp với file Trình đã nộp. Run id dẫn chứng: `R-workflow-C-001-s11`. Lưu ý `lab8.crash_test` hiện chạy cố định shape swarm (`crash_test.py:124`), nên kết quả `20/20` của lệnh đó không chứng minh workflow an toàn khi crash. Với workflow, bằng chứng crash hiện là test T12 trong ma trận student.

## 5. Công cụ AI đã dùng

- Claude Code: đọc repo để lên kế hoạch phân công, viết nháp `workflow.py` và `test_workflow_extra.py`, review và ghép nhánh, chạy benchmark/crash, soạn nháp báo cáo nhóm, research card và báo cáo này.
- Tự kiểm tra: chạy lại smoke, cổng host, 62 test student của workflow và 3 test bổ sung ở trên, đọc kết quả thật thay vì tin vào mô tả của công cụ. Đã xác nhận `compute_compensation` chỉ dùng policy `is_current` và `effective_date <= as_of`.

## 6. Tự đánh giá

- Làm được: shape workflow đầy đủ, qua 62/62 test student và cổng host vẫn xanh.
- Còn thiếu: hidden grade (giảng viên chạy), việc đọc bản gốc paper R1 để điền CLAIM/BOUNDARY và URL trong research card, và các thành viên tự nộp link LMS.
- Giới hạn: kết luận hiện chỉ dựa trên MockLLM và bộ claim public; chưa có số hidden.
