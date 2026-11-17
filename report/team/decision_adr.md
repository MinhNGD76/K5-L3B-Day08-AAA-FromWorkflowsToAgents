# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 0485fd79066f2ceaf0b8af27e218fcaf709b1df2
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.857142857142858
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 phát hiện trong public benchmark và test mặc định; hidden grader chưa chạy

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Benchmark chạy trên 14 claim, năm seed `11,22,33,44,55` và SQLite mới cho từng trial. Workflow, Single và Orchestrator đều đạt pass rate và pass^5 bằng 1.000, seed variance bằng 0. Workflow là kiến trúc ít tự chủ nhất trong ba shape đạt toàn bộ public trial, đồng thời có cost/success thấp nhất: 27.857 VND mô phỏng, so với 28.563 của Single và 55.714 của Orchestrator. Vì vậy nhóm chọn Workflow theo nguyên tắc dùng mức tự chủ thấp nhất vẫn đáp ứng yêu cầu. Swarm không được chọn vì pass rate 0.9857, pass^5 0.9286 và variance 0.000816 do một trial seed 55 sai.

## Có đáng đổi lấy multi-agent không

Trên public corpus, multi-agent không tạo thêm độ chính xác so với Workflow nhưng tăng chi phí mô phỏng; Orchestrator còn tốn khoảng gấp đôi cost/success của Workflow. Quyết định sẽ đảo lại nếu hidden grader cho thấy Workflow xuống dưới ngưỡng 0.75 hoặc Orchestrator/Single xử lý được các trường hợp mới với pass rate và pass^5 cao hơn đáng kể mà vẫn giữ leak, bypass và crash safety trong giới hạn bắt buộc. Chưa có hidden grade nên không khẳng định hidden pass rate.

## Trace và bằng chứng

Workflow trace ghi claim id/cờ có order, order view allowlist, quote và quyết định. Orchestrator trace ghi handoff đã sanitize, kết quả investigator đã thu gọn, quote và quyết định. Trace cố ý không ghi ticket, `parent_secret`, raw headers, principal id, SĐT, địa chỉ, tên hàng hoặc internal note. Trace nằm trong `src/traces/` khi chạy từ `src`; test mặc định và test riêng quét nội dung trace/result để phát hiện secret và PII.

## Giới hạn

MockLLM không phải model sản xuất; số liệu chỉ phản ánh 14 claim public và năm seed cố định. Latency là `unavailable`. Hidden grader chưa chạy; ticket ablation của Single đã chạy (xem research_card.md), nên ADR không suy rộng sang hidden pass rate hay hệ thống sản xuất. `src/reports/benchmark.json` và `src/reports/crash.json` do lệnh của lab sinh ra, không sửa tay.
