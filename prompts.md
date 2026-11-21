# Khai báo dùng AI — Nguyễn Quốc Hưng

Nhắc lại: không đưa ảnh cabin hay ảnh tài xế (kể cả ảnh chụp màn hình) cho bất kỳ công cụ AI nào.
**Không có ảnh nào được đưa cho AI trong buổi này.** Toàn bộ việc gán nhãn 22 ảnh do mình tự làm
trên CVAT local.

| # | Công cụ | Bạn hỏi gì (tóm tắt) | Bạn dùng kết quả thế nào | Bạn có kiểm lại không? Bằng gì? |
|---|---|---|---|---|
| 1 | Claude Code (Opus) | Đọc toàn bộ repo lab (GUIDE, RULES, CHECKPOINTS, COMMON_ERRORS, `scripts/cabin_check.py`, `labels_cabin_v1.json`) rồi rút thành một thẻ quy tắc gọn để dùng khi gán nhãn | Dùng `notes/RULE_CARD.md` làm thẻ tra nhanh (bản đồ ghế, giá trị CVAT điền sẵn, ngưỡng 60 px, ràng buộc mắt ↔ cờ `face13`) | Có. Đối chiếu từng dòng của thẻ với GUIDE §4 và với mã nguồn `cabin_check.py`; những chỗ script không bắt được thì mình tự soát tay |
| 2 | Claude Code (Opus) | Viết runbook các lệnh `cabin_check` cho đúng máy mình (`python3`, CVAT v2.74.1 thay vì v2.82.0) | Dùng `notes/RUNBOOK.md` để chạy Checkpoint A/B và lần cuối | Có. Chạy thử `cabin_check.py --help` và chạy thử trên một file export giả do `tools/make_demo_export.py` sinh ra, trước khi dùng lên bài thật |
| 3 | Claude Code (Opus) | Góp ý câu chữ và cấu trúc cho `class_list_v0.md`: mỗi lớp DMS/OMS phải nói rõ "để làm gì", và gợi chỗ guideline v1.0 còn trống để đặt câu hỏi leo thang (RULES §3 cho phép nhờ AI góp ý câu chữ danh sách lớp) | Dùng làm bản nháp, rồi tự sửa lại theo đúng những gì mình quan sát được trên 22 khung của mình, và tự điền tên khung ví dụ | Có. Mỗi lớp mình đối chiếu lại với thuộc tính thật trong `labels_cabin_v1.json`; hai câu leo thang mình kiểm lại chính GUIDE §4.5/§4.7/§4.8 để chắc là guideline **thật sự** chưa trả lời |
| 4 | Claude Code (Opus) | Viết script preflight tự kiểm 5 điều của SUBMISSION trước khi nộp | Chạy `tools/preflight.py` trước khi đóng gói | Có. Tự mở lại `export_final.zip` bằng `python3 -m zipfile -l` và tự đọc dòng cuối `check_final.txt` |

**Không nhờ AI làm:** gán nhãn (không khung nào), quyết định giá trị thuộc tính, điền `ir_log.csv`,
điền `disagreement_log.csv`, trả lời exit ticket thay mình.
