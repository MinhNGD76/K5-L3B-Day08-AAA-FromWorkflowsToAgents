# Bonus report: B3

- Topic + nguồn: B3 Verifier/aggregator chống khuếch đại lỗi. Google Research / Google DeepMind / MIT, *Towards a Science of Scaling Agent Systems*, arXiv:2512.08296 (theo `docs/bonus_topics.md`, slide 17, 22, 42).
- CLAIM của nguồn: kiến trúc không có kiểm chứng tập trung dễ lan truyền lỗi hơn kiến trúc có điều phối và kiểm chứng tập trung. (Nhóm chỉ đọc abstract và tóm tắt; các con số 17,2× và 4,4× trong đề bài chưa được đối chiếu với toàn văn.)
- BOUNDARY: nguồn dùng LLM thật, nhiều benchmark. Ở đây: MockLLM, 14 claim public và 10 claim tự viết, 5 seed. Verifier là code, không phải LLM.
- HYPOTHESIS trên LogiX: verifier code đối chiếu dữ kiện với order có cấu trúc sẽ đưa pass rate của swarm về bằng workflow trên cả hai bộ, với cost/success cao hơn workflow vì swarm vẫn gọi model.
- Biến cố định / thay đổi: cố định claim, seed `11,22,33,44,55`, bảng giá, tool, evaluator, và nguyên logic swarm (kể cả điểm yếu ở seed chia hết cho 5). Biến duy nhất: thêm bước verifier trước khi ghi.
- Lệnh tái lập (chạy trong `src/`):
  - `python -m bonus.run_b3` (sinh `reports/bonus_swarm_verified.json`, gồm cả hai bộ)
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json`
  - `python -m pytest -q tests/test_bonus_swarm_verified.py`
- File report + run id: `src/reports/bonus_swarm_verified.json`; mỗi trial có `run_id` dạng `R-swarm_verified-<claim>-s<seed>`.

## Cách làm

`bonus/swarm_verified.py` giữ nguyên luồng swarm. Sau khi quote, một bước code đối chiếu `delay_days`, `status`, `damage_verified` mà quote đã dùng với order row do investigator chỉ đọc trả về. Nếu lệch thì quote lại từ order row (tối đa một vòng) và ghi sự kiện `verifier_override` vào trace. Host vẫn là bên duy nhất ghi tiền.

Bộ case tự viết gồm 10 claim trong `bonus/cases.jsonl` và `bonus/world.json`: ticket nói quá (X-01), nói thiếu (X-02), nhiều con số (X-03), nói dối hỏng hàng và số ngày (X-04), sát ngưỡng ba ngày (X-06, X-09), và các case đối chứng ticket khớp hoặc không có số (X-05, X-07, X-10, X-08). Nhãn viết tay theo `docs/business_rules.md`, không sinh bằng `compensation.quote`. Workflow, vốn tính từ order row, cho cùng kết quả với các nhãn này.

## Kết quả

Số liệu từ `reports/bonus_swarm_verified.json`. Cost là VND mô phỏng.

**Bộ public (14 claim × 5 seed)**

| Shape | Pass rate | pass^5 | Variance | Cost/success |
| --- | ---: | ---: | ---: | ---: |
| workflow | 1,000 | 1,000 | 0,000000 | 27,86 |
| swarm | 0,986 | 0,929 | 0,000816 | 49,57 |
| swarm_verified | 1,000 | 1,000 | 0,000000 | 57,57 |

**Bộ tự viết (10 claim × 5 seed)**

| Shape | Pass rate | pass^5 | Variance | Cost/success |
| --- | ---: | ---: | ---: | ---: |
| workflow | 1,000 | 1,000 | 0,000000 | 30,00 |
| swarm | 0,880 | 0,400 | 0,057600 | 60,89 |
| swarm_verified | 1,000 | 1,000 | 0,000000 | 64,98 |

Safety: `trial_pass` kiểm chuỗi cấm, ledger và audit trên mọi trial; không trial nào của `swarm_verified` bị loại vì rò secret hay refund sai.

**Số lần verifier can thiệp:** 1 trên public (C-002, seed 55: vé nói 5 ngày, order 2 ngày) và 7 trên bộ tự viết (cả 7 ở seed 55). 6 trong 7 lần làm đổi kết quả, tức đúng 6 trial mà swarm gốc sai. Lần còn lại (X-08) vé nói 1 ngày, order 2 ngày nhưng quyền lợi hỏng hàng vẫn cho cùng 90.000 VND, nên verifier can thiệp mà không đổi kết quả.

**Trace minh họa** (X-01, seed 55; trích từ trace của lần chạy):
`model_override {delay_days: 9}` → `verifier_override {facts: {delay_days: {used: 9, row: 1}}, requoted_vnd: 0}` → status `denied`, không có dòng ledger.

## Kết luận

Ủng hộ giả thuyết. Verifier đưa swarm về cùng pass rate, pass^5 và variance với workflow trên cả hai bộ. Cái giá: cost/success cao gấp khoảng 2,1 lần workflow trên public (57,57 so với 27,86) và 2,2 lần trên bộ tự viết, và cao hơn cả swarm gốc, vì verifier thêm lần gọi tool.

Câu hỏi "nếu verifier đã thay cả phần quyết định thì swarm còn giữ lại giá trị gì?": trên LogiX, không còn gì đo được. Verifier requote từ order row, đúng là logic của workflow; các lần gọi `peer` và `parse` của swarm chỉ tạo ra cơ hội sai (số ngày trong ticket) chứ không thêm dữ kiện nào mà order row chưa có. Kết luận này đảo ngược nếu có tác vụ mà dữ kiện cần thiết không nằm trong dữ liệu có cấu trúc, tức verifier không có chuẩn để đối chiếu.

Kết quả không vượt quá dữ liệu: bộ tự viết do nhóm thiết kế để nhắm vào điểm yếu đã biết, nên pass rate của swarm 0,88 trên bộ này chỉ cho thấy điểm yếu có thật chứ không đại diện cho phân bố claim thực tế.

## Giới hạn

MockLLM, latency `unavailable`. Điểm yếu của swarm chỉ kích hoạt ở seed chia hết cho 5 theo thiết kế của lab, nên "7 lần can thiệp" đều ở seed 55 là hệ quả của cách dựng, không phải tần suất lỗi thực tế. Verifier chỉ kiểm ba trường; không kiểm lỗi ở chỗ khác (chọn clause, approval) vì host đã chặn các lỗi đó. Bonus chỉ được tính khi shape nhóm chọn đạt hidden pass rate ≥ 0,80, điều chưa được xác nhận. Lệnh `lab8.benchmark` với `--extra-shape` (ghi `reports/bonus_benchmark.json`) chỉ chạy bộ tự viết; số liệu hai bộ lấy từ `bonus_swarm_verified.json`.
