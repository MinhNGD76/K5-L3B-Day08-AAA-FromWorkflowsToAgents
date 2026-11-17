# Bàn giao thành viên 2 — Single agent

Branch: `codex/member2-single-agent`.

## Thiết kế

Single dùng `run_react(max_steps=8, worker=True)`. Mỗi lượt decide gọi MockLLM và được tính vào Budget. MockLLM không có structured tool-call API, vì vậy adapter ánh xạ trạng thái quan sát thành hành động đọc lookup_order rồi kết thúc điều tra. Đây là mô phỏng agent có kiểm soát; không chứng minh hành vi của LLM thật.

Nguồn sự thật là order đã kiểm phạm vi principal và policy hiện hành. Ticket không được dùng để sửa delay, không đưa vào prompt hoặc trace. Sau vòng đọc, code gọi compute_compensation và truyền quote đầy đủ vào issue_refund. Host kiểm approval, cap theo đơn và idempotency. crash_at được chuyển tiếp; InjectedCrash truyền ra ngoài, connection luôn đóng trong finally.

## Kiểm chứng

- Public matrix riêng Single: 62 passed.
- Test mặc định, gồm 6 test mới: 60 passed, 248 deselected.
- Test mới: ba cửa sổ crash/resume và retry; giới hạn/cấu hình read-only và đếm model call; hết bước không ghi tiền; unknown claim có trace hợp lệ.
- Crash suite chính thức được chạy bằng `python -m lab8.crash_test --count 20 --out reports/crash.json`. Suite này kiểm host và swarm; bằng chứng riêng Single nằm ở test mới và public T12.

Lệnh chọn đúng shape (vì tên test cũng có từ single):

```powershell
python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k "single and not workflow and not orchestrator and not swarm"
python -m pytest -q
```

## Review Orchestrator

Tại thời điểm review, orchestrator.py còn stub not_implemented. Chưa thể xác nhận handoff, read-only investigator hoặc trace. Khi thành viên 3 hoàn thiện, kiểm make_handoff, allowlist, không truyền parent context, full quote và crash_at.

## Nội dung dùng cho báo cáo nhóm

Kiến trúc Single giới hạn 8 lượt và tách điều tra đọc khỏi thao tác ghi tiền. Thiết kế không tin số ngày trễ trong ticket và không để model quyết tiền. Các test public đã qua, nhưng chưa có bằng chứng hidden pass rate; không suy rộng thành kết quả hidden hoặc khả năng LLM thật.

## Việc cần người dùng điền khi nộp

Copy MSSV_HoTen.md thành tên thật, thêm họ tên/MSSV/email/GitHub. Ghi commit kỹ thuật, các test ở tests/test_single_team.py và vai trò vào TEAM.md. Công cụ hỗ trợ: Codex để đọc tài liệu, viết code và chạy test; cần tự đọc/giải thích code và thực hiện kiểm chứng trước khi tự đánh giá. Không bịa thông tin cá nhân hay phần tự đánh giá.

Cùng nhóm hoàn thiện research_card theo thí nghiệm thực tế; không điền số ablation chưa chạy. Người dùng tự nộp link LMS.
