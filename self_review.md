# Tự đánh giá — Nguyễn Quốc Hùng · G02

Trong buổi mình gán hai bộ: **G05** làm bộ tập (không nộp) và **G02** là bài nộp này.
Phần tự đánh giá dưới đây lấy lỗi thật từ các vòng export–kiểm của cả hai bộ.

## 1. Tự rà soát 4 cảnh

| Ảnh | Đối tượng | Loại lỗi | Ghi chú | Đã sửa? |
|---|---|---|---|---|
| S01_rgb | `person` | `missing` | Có box `person` nhưng **không có box `face`**. GUIDE §4.2 yêu cầu người lớn trên ảnh OMS phải có cả hai. `cabin_check` không bắt được lỗi này — phát hiện bằng `tools/audit.py` | Rồi |
| S07_rgb | `person` | `missing` | Y hệt S01: thiếu box `face`. Lặp trên cả `_rgb` lẫn `_ir` của hai cảnh, tổng 4 box thiếu | Rồi |
| D02 | `frame_meta` | `missing` | Quên dán tag cho cả khung. Đây là ERROR duy nhất của bộ G02 ở vòng export đầu | Rồi |
| D02 | `phone` | `extra` | Mình vẽ box `phone`, bạn Hoàng Trọng Trà không vẽ. §4.7 chỉ cho vẽ khi thấy cạnh, góc hoặc màn hình. Cần xem lại ở độ phóng lớn xem mình có vẽ thừa không | Chưa — xem mục 3 |

## 2. Lỗi mình lặp lại nhiều nhất hôm nay

**Lỗi:** quên dán tag `frame_meta` cho **đúng một khung `D##`**, và chỉ phát hiện ra ở lần export cuối.
Lặp lại ở **cả hai bộ**:

| Bộ | Khung bị quên | Phát hiện lúc nào |
|---|---|---|
| G05 | `D06` | `cabin_check` ở export cuối |
| G02 | `D02` | `cabin_check` ở export cuối |

**Vì sao mình mắc:** trên ảnh `D##` mình vào là vẽ ngay `person` → `face` → `face13` → `hand`, vì
phần `face13` tốn thời gian nhất nên chiếm hết chú ý. Tag `frame_meta` không vẽ ra hình gì trên
canvas, nên nhìn màn hình không thấy nó thiếu — khung vẫn trông đầy đủ. Ảnh `S##` không bị vì ở đó
mình làm theo thứ tự tag trước, còn ảnh `D##` thì bị cuốn vào việc đặt 13 điểm.

**Lần sau tránh bằng cách:** dán `frame_meta` là thao tác **đầu tiên** của mỗi khung, trước cả box
`person`, đúng như GUIDE §4.3 ghi — mình biết luật này nhưng chỉ áp dụng được ở phần OMS. Và chạy
`cabin_check --only` sau mỗi 2 khung `D##` thay vì đợi tới cuối: cả hai lần lỗi này đều tồn tại hàng
chục phút trước khi bị phát hiện.

**Lỗi hạng hai, đã sửa được trong buổi:** ở bộ G05 mình để nguyên giá trị mặc định `seat = driver`
sau khi `Ctrl+V` từ ảnh `_rgb` sang `_ir` — **ba lần** (`S01_ir.object`, `S02_ir.infant_seat`,
`S05_ir.person`). Sang bộ G02 lỗi này **không tái diễn lần nào**, và `tools/audit.py` báo cả 8 cặp
`_rgb`/`_ir` khớp nhau hoàn toàn. Cái sửa được là thao tác: sau mỗi lần dán, mở DETAILS đọc lại
`seat` của từng hộp trước khi `Ctrl+S`.

## 3. Ghi chú về disagreement_log

Một dòng bạn của mình đúng và mình sai: …

Mình học được gì từ dòng đó: …
