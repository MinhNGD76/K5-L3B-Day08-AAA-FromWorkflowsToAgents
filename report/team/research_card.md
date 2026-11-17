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
| CÂU | R1 / R2 / R3 / R4 | R2 — Failure taxonomy; mở rộng câu hỏi sang lỗi kiểm chứng dữ kiện trong Single. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., Why Do Multi-Agent LLM Systems Fail?, 2025, https://arxiv.org/abs/2503.13657 ; nghiên cứu thực nghiệm/taxonomy MAST. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST phân loại lỗi thành ba nhóm: specification/system design, inter-agent misalignment, task verification/termination. Đây là phân loại từ nguồn, không phải kết quả thí nghiệm của nhóm. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn nghiên cứu multi-agent; ablation của nhóm chỉ khảo sát Single với MockLLM và 14 claim giả. Liên hệ với lỗi kiểm chứng là cách vận dụng của nhóm, không phải kết luận paper về LogiX-VN. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Thay ticket bằng yêu cầu sai (99 ngày trễ, đòi 999999999 VND, ignore policy) sẽ làm pass rate Single thay đổi 0 điểm phần trăm, cost/success thay đổi 0 VND, vì code chỉ tin order và không dùng ticket trong model prompt. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ nguyên Single, MockLLM, tools, world/order/policy, evaluator, pricing, 14 claim và seed 11/22/33/44/55; SQLite mới mỗi trial. Chỉ thay trường ticket trong bản sao claims ở bộ nhớ. 70 baseline + 70 treatment. Không sửa data/config/thước đo. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến nếu ranh giới hỏng: tin ticket và hoàn sai. Đo pass rate, pass^5, cost/success và sai khác ghép cặp ở status/passed/reason/cost/model_calls/tool_calls/steps. trial_pass cũng kiểm trace và ledger theo expected. |

## Kết quả ablation

- Người phụ trách: Ngô Duy Khánh (thành viên 2), có Codex hỗ trợ triển khai và thực thi.
- Lệnh chạy trong src (PowerShell): `$env:PYTHONPATH='.'; ../.venv/Scripts/python.exe scripts/member2_ticket_ablation.py`
- File report: `src/reports/member2_ticket_ablation.json`; mỗi trial có run_id trong baseline/trials và treatment/trials. Run id định danh theo shape/claim/seed có thể trùng giữa hai nhánh, vì vậy cần đọc cùng nhãn baseline/treatment.
- Giới hạn: MockLLM không phải model sản xuất, latency là unavailable. Không đổi topology; thí nghiệm chỉ đo độ bất biến trước ticket trong Single. Ticket không được đưa vào prompt nên kết quả không chứng minh chống prompt injection của LLM thật.

- Kết quả thực chạy: baseline 70/70 và treatment 70/70 trial pass; cả hai pass rate=1.0, pass^5=1.0, seed variance=0, cost/success=28.562857142857144 VND mô phỏng. Không có sai khác ở 70 cặp trial trên các field so sánh. Hypothesis phù hợp dữ liệu trong phạm vi bộ public này.
