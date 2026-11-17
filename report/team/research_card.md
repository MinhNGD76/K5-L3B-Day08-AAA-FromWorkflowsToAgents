# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research, 2026, *Towards a Science of Scaling Agent Systems* (nguồn theo danh sách R1 của lab; URL do nhóm bổ sung, chưa kiểm tra bản gốc). Loại bằng chứng: benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Chưa đọc bản gốc nên nhóm chưa trích kết luận của paper; không điền để tránh viết rộng hơn phạm vi nguồn. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Chưa xác định vì chưa đọc paper. Giới hạn phía lab: MockLLM, 14 claim public, 5 seed cố định. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Task claims chủ yếu tuần tự (đọc đơn → tính quote → ghi), nên thêm investigator (workflow → orchestrator) không tăng pass rate (giữ 1.000) và tăng cost/success, ước tính gần gấp đôi vì thêm các lần gọi tool đọc. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, tool đọc, seed 11,22,33,44,55, 14 claim public, bảng giá, evaluator. Biến duy nhất thay đổi: shape workflow so với orchestrator (thêm tầng handoff và investigator). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Orchestrator làm lộ field qua handoff hoặc trace: đo `secret_leak_count`, `approval_bypass_count`; so pass rate, pass^5, variance, cost/success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r1.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_r1.json` (và `src/reports/benchmark.json`, cùng số liệu)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **đúng một phần**. Pass rate và pass^5 cùng 1.000, variance 0 ở cả hai shape (không đổi). Cost/success workflow 27.86 so với orchestrator 55.71 VND mô phỏng, tức khoảng gấp đôi. Chưa kiểm số cost này theo từng tool vì chỉ đọc tổng trong report. Chưa chạy hidden nên không kết luận cho bộ hidden.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.


Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
