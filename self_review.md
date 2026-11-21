# Tự đánh giá — Nguyễn Quốc Hùng · G05

## 1. Tự rà soát 4 cảnh

Chọn 2 ảnh S## và 2 ảnh D##, đọc lại như người lạ. Các dòng dưới đây lấy từ ba vòng
export–kiểm trong buổi (`check_cpA.txt` → `check_final.txt` → `tools/audit.py`).

| Ảnh | Đối tượng | Loại lỗi | Ghi chú | Đã sửa? |
|---|---|---|---|---|
| S01_rgb | `frame_meta` | `guess` | Ghi `light = day` vì nhìn ra cửa sổ thấy sáng. Nhưng SVIRO là ảnh dựng bằng máy tính, không có giờ thật lúc chụp — GUIDE §3 yêu cầu `unknown`. Mình đã gán một giá trị không kiểm chứng được | Rồi |
| S01_ir | `object` | `seat_flip` | `seat = driver` — không phải lật trái/phải, mà là **để nguyên giá trị CVAT điền sẵn** sau khi `Ctrl+V` từ `S01_rgb`. Ảnh SVIRO chỉ nhìn hàng ghế sau nên `driver` không thể đúng. Phải là `rear_middle` | Rồi |
| D04 | `face` | `box` | Hộp `face` ban đầu rộng 71,7 px, sau khi sửa còn 38,0 px — thu gần một nửa. Con số này quyết định có phải vẽ `face13` hay không (ngưỡng 60 px), nên nó không chỉ là chuyện hộp lỏng | Cần đo lại |
| D05 | `face13` | `lr_flip` | 13 điểm vẫn ở tư thế mặt nhìn thẳng: `left_eye_*` và `right_eye_*` có y trung bình **bằng nhau, đều 336** — nghĩa là template chưa được xoay theo ảnh D## xoay ~90°. Ba khung D02/D03/D06 mình đã xoay đúng (chênh y 34–79 px) | Chưa |

## 2. Lỗi mình lặp lại nhiều nhất hôm nay

**Lỗi:** để nguyên giá trị mặc định CVAT điền sẵn sau khi copy shape từ ảnh `_rgb` sang ảnh `_ir`.
Lặp lại **ba lần**, cả ba đều ở ảnh `_ir` và cả ba đều là `seat = driver`:

| Khung | Box | Giá trị sai | Đúng phải là |
|---|---|---|---|
| S01_ir | `object` | `seat = driver` | `rear_middle` |
| S02_ir | `infant_seat` | `seat = driver` | `rear_right` |
| S05_ir | `person` | `seat = driver` | `rear_middle` |

**Vì sao mình mắc:** mình tưởng `Ctrl+C` / `Ctrl+V` chép sang cả thuộc tính đã chọn, nên sang ảnh
`_ir` chỉ kiểm lại vị trí hộp rồi lưu. Thực tế hộp dán sang mang **giá trị mặc định** của từng
thuộc tính, và `driver` đứng đầu danh sách `seat` nên nó được điền tự động. Lỗi này im lặng: hộp
nhìn đúng chỗ, chỉ có thuộc tính sai, nên nhìn canvas không phát hiện được.

**Lần sau tránh bằng cách:** sau mỗi lần dán sang ảnh `_ir`, mở **DETAILS** của **từng** hộp và đọc
to giá trị `seat`, thay vì chỉ nhìn vị trí hộp. Và chạy `cabin_check` ngay sau mỗi cặp cảnh thay vì
đợi tới cuối — ở Checkpoint A script đã bắt được hai trong ba lần, nếu mình xử lý triệt để lúc đó
thì lần thứ ba ở S05 đã không xảy ra.

Lỗi hạng hai cùng tính chất: ghi `light = day` trên ảnh SVIRO ở **hai** khung (S01_rgb, S04_rgb) —
cũng là gán một giá trị mình không kiểm chứng được, trái luật chung 4.4-1.

## 3. Ghi chú về disagreement_log

<!-- Điền sau khi chạy: python3 scripts/cabin_check.py diff export_final.zip peer_export_final.zip --csv disagreement_log.csv -->

Một dòng bạn của mình đúng và mình sai: …

Mình học được gì từ dòng đó: …
