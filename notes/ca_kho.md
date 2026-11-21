# Ghi chú ca khó — Nguyễn Quốc Hùng · G05

Guideline yêu cầu ghi chú ở §4.4-4 (`gaze_zone = other`), §4.5 (không vẽ box `face`), §4.8 (đếm
ghế trống), và RULES §4 (ca guideline không nói tới). Giữ file này để điền `self_review.md` và
`disagreement_log.csv` cuối buổi.

## Phán quyết của coach trong buổi

| # | Ca | Coach trả lời | Mình làm gì |
|---|---|---|---|
| 1 | Ảnh có **trẻ em đang ngồi** trong ghế trẻ em (ghế bên phải ảnh = `rear_left`) | **Không gán nhãn** | Không vẽ box nào cho vị trí ghế đó: không `person` cho đứa trẻ, không `child_seat` cho cái ghế. Ghi vào đây và đếm như ca ngoài phạm vi, **không** đếm là "ghế trống" |

Cơ sở: GUIDE §4.1 định nghĩa `child_seat` là "Cả ghế trẻ em, **ghế đang trống**" — ghế có trẻ ngồi
nằm ngoài từ vựng v1.0; GUIDE §3 "thấy hình giống trẻ em thì báo coach, không gán"; và phán quyết
trực tiếp của coach hôm nay.

Hệ quả: giá trị `occupied = yes` coach gửi thêm **không dùng cho bộ ảnh hôm nay**. Thêm vào schema
thì vô hại, nhưng chọn nó sẽ thành `[ERROR]` của `cabin_check` (xem `notes/RUNBOOK.md`).

## Khung cụ thể

| Khung | Ca | Mình xử lý | Mục guideline |
|---|---|---|---|
| | | | |
| S02_rgb, S02_ir | Em bé nằm trên băng ghế (bên trái ảnh = rear_right), quấn chăn | Không gán box nào cho vị trí đó, theo phán quyết coach và GUIDE §3 | §3, §4.1 |
| S01_rgb, S01_ir | Nôi xách bên phải ảnh (rear_left) có vẻ đang có em bé nằm bên trong | Vẫn gán `infant_seat` + `facing=rear`, vì label này không có thuộc tính `occupied` nên không khẳng định gì về người bên trong | §4.1, §4.8 |
