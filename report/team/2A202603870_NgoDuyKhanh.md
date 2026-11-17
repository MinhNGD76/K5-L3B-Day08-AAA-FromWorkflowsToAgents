# Báo cáo cá nhân — Ngô Duy Khánh

## 1. Thông tin thành viên

- Họ tên: Ngô Duy Khánh
- MSSV: 2A202603870
- Email: dtonyk231@gmail.com
- GitHub: https://github.com/dkhanhdev
- Vai trò: Thành viên 2 — Single agent và kiểm chứng crash safety.
- Branch thực hiện: `codex/member2-single-agent`.

## 2. Phần việc phụ trách

Phạm vi đã thực hiện gồm triển khai Shape B trong `src/lab8/shapes/single.py`, bổ sung kiểm thử riêng trong `src/tests/test_single_team.py`, chạy kiểm thử public của Single và test mặc định, chạy crash suite chính thức và chuẩn bị tài liệu bàn giao. Code và kiểm thử được thực hiện với sự hỗ trợ của Codex; chi tiết công cụ và giới hạn xác nhận được ghi ở mục 5–6.

## 3. Đóng góp cụ thể

### Triển khai Single agent

- Giữ nguyên giao diện `run_claim`, sử dụng `run_react` với `max_steps=8` và `worker=True` để giới hạn vòng lặp và quyền gọi tool.
- Gọi MockLLM ở mỗi lượt quyết định và tính chi phí vào Budget. Do MockLLM không cung cấp structured tool-call API, adapter ánh xạ trạng thái quan sát thành hành động đọc `lookup_order`, sau đó kết thúc điều tra. Đây là mô phỏng có kiểm soát, chưa đánh giá khả năng lựa chọn tool của LLM thật.
- Dùng dữ liệu order đã kiểm tra principal làm nguồn sự thật; không lấy số ngày trễ từ ticket để ghi đè order. Không đưa ticket thô vào prompt hoặc trace.
- Sau vòng đọc, code gọi `compute_compensation` và truyền quote đầy đủ vào `issue_refund`. Host chịu trách nhiệm approval, trần theo đơn và chống ghi trùng.
- Truyền tiếp `crash_at`, để `InjectedCrash` truyền ra ngoài và đóng kết nối trong `finally`.
- Xử lý các nhánh unknown claim, thiếu order, order không nhìn thấy, quote bằng 0, host từ chối, thành công và hết bước; tạo kết quả và trace bằng `finish`.

### Kiểm thử và bằng chứng

Bổ sung các test sau trong `src/tests/test_single_team.py`:

| Test | Mục đích |
| --- | --- |
| `test_single_recovers_at_each_crash_window` | Ba trường hợp tham số: trước effect, sau effect trước checkpoint, sau checkpoint; resume và retry vẫn một refund và một committed audit |
| `test_single_read_loop_is_bounded_and_counted` | Xác nhận cấu hình tối đa 8 bước, worker chỉ đọc và đếm model calls ở nhánh thành công |
| `test_single_step_cap_does_not_write` | Mô phỏng runtime trả step_cap; shape trả failed và không tạo refund |
| `test_single_unknown_claim_writes_valid_trace` | Unknown claim trả failed và tạo trace đúng run_id, có events, không chứa canary secret |

Tổng cộng 6 trường hợp kiểm thử khi tính ba tham số crash. Test step_cap kiểm cách shape xử lý kết quả giới hạn, không tự chứng minh mọi hành vi lặp của runtime.

### Commit

- `71ae5d1`: triển khai Single, thêm test và tài liệu bàn giao.
- `30de945`: lưu kết quả crash suite chính thức do công cụ sinh.

## 4. Bằng chứng

Các lệnh được chạy trong `src/`, bằng Python của môi trường `.venv`:

```powershell
python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k "single and not workflow and not orchestrator and not swarm"
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m lab8.crash_test --count 20 --out reports/crash.json
```

| Kiểm tra | Kết quả đã ghi nhận |
| --- | --- |
| Public matrix dành riêng Single | 62 passed, 186 deselected |
| Test mặc định sau tích hợp cả ba thành viên | 75 passed, 248 deselected |
| Crash suite chính thức, chạy lại sau tích hợp | crash_safety 20/20 |
| Toàn bộ public student matrix sau tích hợp | 248 passed, 75 deselected |

File bằng chứng: `src/reports/crash.json`. Tài liệu kỹ thuật: `report/team/member2_handoff.md`. Crash suite chính thức kiểm host và swarm tham chiếu; bằng chứng crash/resume riêng Single nằm trong test mới và public T12. Các kết quả này phản ánh lần kiểm chứng tại thời điểm triển khai, cần chạy lại nếu code tích hợp thay đổi.

## 5. Công cụ AI đã dùng

Sử dụng Codex để đọc tài liệu repo, đề xuất và triển khai code Single, viết test, chạy lệnh kiểm chứng, tạo branch, commit và tổng hợp báo cáo. Không gọi API model thật trong code lab; phần mô phỏng sử dụng MockLLM có sẵn.

Kết quả AI được đối chiếu bằng public matrix, test mặc định và crash suite; các số liệu ở mục 4 lấy từ đầu ra công cụ thực chạy. Những lệnh này do Codex thực hiện trong workspace theo yêu cầu của thành viên. Báo cáo không khẳng định thành viên đã tự chạy lại hoặc tự giải thích đầy đủ code; phần xác nhận đó cần thực hiện trước khi nộp.

## 6. Tự đánh giá

### Trạng thái có bằng chứng

Phần Single đã được triển khai, có commit kỹ thuật và test bổ sung; đạt các kiểm thử public nêu trên. Ranh giới chính của thiết kế là model tham gia bước đọc, còn code tính tiền và host quyết định ghi refund. Không sửa thước đo để đạt kết quả kiểm thử.

### Giới hạn và công việc còn lại

- Chưa kiểm chứng hidden pass rate; không khẳng định đạt ngưỡng hidden 75%.
- Benchmark bốn shape đã có: Single đạt pass_rate=1.0, pass^5=1.0, cost/success mô phỏng khoảng 28.563 VND trên 70 trial public. Đây là kết quả trong reports/benchmark.json do thành viên 3 cung cấp, không phải benchmark do thành viên 2 chạy. Research card và ablation vẫn cần nhóm hoàn thiện.
- Đã review lại Orchestrator sau tích hợp: make_handoff chỉ cấp tool đọc và facts rỗng; runtime chặn write tool; trace không sao chép parent context; quote đầy đủ và crash_at được chuyển cho host; mọi nhánh kết thúc qua finish. Không phát hiện lỗi cần sửa trong phạm vi review.
- Đã điền thông tin và dòng đóng góp vào TEAM.md; code ba thành viên đã tích hợp. Kết quả kiểm tra cập nhật ghi trong mục 4.
- Thành viên cần tự đọc, chạy lại, giải thích code và bổ sung nhận xét cá nhân về phần đã hiểu, khó khăn và bài học thực tế. Báo cáo này chưa thay cho tự đánh giá chủ quan của thành viên.

### Kiểm tra hồ sơ sau tích hợp

`lab8.check_submission` xác nhận code ba shape và report benchmark/crash hợp lệ; còn 1 FAIL vì research_card chưa có câu nghiên cứu và ablation. Đây là phần nghiên cứu chung chưa hoàn tất, không được xem các kiểm thử xanh là toàn bộ bài đã sẵn sàng nộp.
