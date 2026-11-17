# Báo cáo cá nhân — Triệu Hải Đăng Trình

## 1. Thông tin thành viên

- Họ tên: Triệu Hải Đăng Trình
- MSSV: 2A202603874
- Email: chưa được cung cấp
- GitHub: DangTrinhdzZ
- Vai trò: Thành viên 3 — Orchestrator + benchmark
- Branch thực hiện: `trinh-stage3`

## 2. Phần việc phụ trách

Triển khai Shape C trong `src/lab8/shapes/orchestrator.py`, bổ sung test kỹ thuật riêng trong `src/tests/test_orchestrator_team.py`, review chéo Workflow, tích hợp nguyên lịch sử branch Workflow và Single để chạy benchmark bốn shape, sinh report bằng công cụ của lab và điền ADR từ số liệu thực chạy.

## 3. Đóng góp cụ thể

### Thiết kế Orchestrator

- Giữ nguyên chữ ký `run_claim`; mở SQLite bằng `connect` và luôn đóng trong `finally`.
- Tạo `Budget`, run id bằng `make_run_id("orchestrator", claim_id, seed)` và `Trace` cho mọi đường trả về.
- Đọc claim qua `get_claim_view`; ticket được coi là dữ liệu không tin cậy và không được đưa vào handoff, prompt hoặc trace.
- Tạo handoff bằng `make_handoff`; `allowed_tools` chỉ gồm `lookup_order`, `lookup_policy`, `lookup_refund_history` và `compute_compensation`. Investigator chạy qua `run_readonly_investigators` với registry chỉ đọc.
- Chỉ trace handoff đã sanitize và kết quả điều tra đã thu gọn. Không trace parent context, principal id, claim/order row thô, secret, raw headers hoặc PII.
- Dùng order view đã kiểm tra principal làm nguồn sự thật và dùng `compute_compensation` tính tiền. Quote bằng 0 bị từ chối trước host; quote dương được truyền đầy đủ cùng `crash_at` vào `issue_refund`.
- Host quyết định approval, cap theo order, idempotency và ledger. Shape ánh xạ host conflict thành `failed`, host từ chối thành `denied`, thành công thành `resolved`; mọi nhánh kết thúc bằng `finish`.

### Test đã thêm

`src/tests/test_orchestrator_team.py` có 12 trường hợp thực thi, bao phủ:

- handoff đúng allowlist, facts đúng `FACT_KEYS`, chỉ cấp tool đọc;
- worker không gọi được `issue_refund` hoặc nhận `append_audit`;
- ticket, parent secret, raw headers, principal id, SĐT, địa chỉ, internal note và tên hàng không xuất hiện trong handoff/trace;
- unknown claim và missing order tạo trace đúng contract;
- order ngoài principal trả `escalated`;
- quote bằng 0 không gọi host và không ghi ledger;
- approval không hợp lệ vẫn đi qua host, trả `denied` và có audit `policy_denied`;
- retry cùng claim chỉ có một refund và một audit committed;
- ba crash window truyền ra ngoài, resume vẫn đúng một refund/một audit;
- proposal giữ full quote 150.000 VND trong khi host cap effect còn 120.000 VND.

### Commit và tích hợp

- Commit kỹ thuật cá nhân: `75522d2` — `feat: implement orchestrator with safe handoff`.
- Merge giữ nguyên lịch sử Thành viên 2: `c961b2e`; các commit gốc gồm `71ae5d1`, `30de945`, `9c705d9` từ `origin/dkhanh-single-agent`.
- Merge giữ nguyên lịch sử Thành viên 1: `0485fd7`; commit gốc `b852fc8` từ `origin/minh`.
- Không sửa báo cáo cá nhân của Thành viên 2 và không nhận code Workflow/Single là đóng góp cá nhân.

## 4. Bằng chứng

Các lệnh chạy trong `src/` bằng `.venv`:

```powershell
.\.venv\Scripts\python.exe -m lab8.smoke
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.pytest-tmp-integrated-default -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q tests/test_orchestrator_team.py --basetemp=.pytest-tmp-orchestrator-team -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k "orchestrator" --basetemp=.pytest-tmp-matrix-orchestrator -p no:cacheprovider
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
```

| Kiểm tra | Kết quả thực chạy |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Test mặc định sau tích hợp | 75 passed, 248 deselected |
| Public matrix Orchestrator | 62 passed, 186 deselected |
| Test riêng Orchestrator | 12 passed |
| Crash suite chính thức | 20/20 |
| Benchmark | 4 shape, 14 claim, 5 seed, 280 trial |

Số liệu Orchestrator trong `src/reports/benchmark.json`: pass rate 1.000; pass^5 1.000; seed min–max 1.000–1.000; variance 0; cost/success 55.714285714285715 VND mô phỏng; mean/p95 steps 3.7142857142857144/4; latency `unavailable`. Run id dẫn chứng: `R-orchestrator-C-001-s11`.

Review Workflow trên commit `b852fc8` xác nhận shape dùng order làm nguồn sự thật, `compute_compensation`, full quote, `crash_at` và trace mọi nhánh. Điểm cần Thành viên 1 xem lại: Workflow vẫn bắt `InjectedCrash` để ghi trace rồi `raise`; exception không bị nuốt nhưng contract yêu cầu không bắt exception này. Không sửa code Workflow trong phần đóng góp cá nhân.

## 5. Công cụ AI đã dùng

Sử dụng Codex để đọc contract và source, triển khai Orchestrator, viết test, chạy kiểm chứng, review Workflow, tích hợp Git và tổng hợp báo cáo. Code lab không gọi model thật. Kết quả do AI tạo được đối chiếu bằng smoke, test mặc định, public matrix, test riêng, crash suite, benchmark JSON, `git diff` và rà secret trước commit.

## 6. Giới hạn và blocker

- Chưa có hidden grader; không khẳng định hidden pass rate hoặc ngưỡng 0.75.
- Chưa chạy ablation hợp lệ chỉ thay một biến; `research_card.md` giữ trống dữ liệu nghiên cứu và ghi blocker, không bịa source/run id/kết quả.
- Benchmark dùng MockLLM và public corpus 14 claim; latency không đo được và được ghi `unavailable`.
- Môi trường `.venv` dùng Python 3.14.3, ngoài dải 3.11–3.13 được tài liệu công bố; test đã pass nhưng vẫn cần CI hoặc máy dùng phiên bản hỗ trợ để xác nhận tính tương thích.
- Lệnh `-k "orchestrator and not workflow and not single and not swarm"` trong yêu cầu chỉ chọn 2 test vì tên hàm chung chứa `single_run`; lệnh `-k "orchestrator"` mới chọn đúng 62 case Orchestrator.
- Workflow còn điểm review về việc bắt rồi ném lại `InjectedCrash`; Thành viên 1 cần quyết định sửa trên branch của mình và chạy lại test trước khi chốt nhóm.
