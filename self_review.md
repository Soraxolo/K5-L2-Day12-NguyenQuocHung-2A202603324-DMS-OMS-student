# Tự đánh giá — Nguyễn Quốc Hưng · G02

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

**Một dòng bạn của mình đúng và mình sai:** khung **`D01`**, thuộc tính `face.glasses` —
mình ghi `clear`, bạn Hoàng Trọng Trà ghi `unknown` (`disagreement_log.csv`, `guideline_rule = 4.5`).

Bạn ấy đúng, và bằng chứng nằm ngay trong bài của chính mình: trên khung D01 mình đã bật cờ che cho
**8 trên 13** điểm `face13`, trong đó có cả bốn điểm mắt phải, và ghi `eye_right = unknown` vì không
đọc được vùng mắt phải. Vậy mà cùng khung đó mình lại khẳng định `glasses = clear` — tức là khẳng
định tài xế đang đeo kính cận và mình nhìn xuyên được tròng. Hai nhận định này không đứng chung
được: nếu vùng mắt đủ rõ để kết luận loại kính thì mắt phải đã không phải `unknown`.

GUIDE §4.5 nói đúng tình huống này: `glasses = unknown` khi không nhìn rõ vùng mắt, và cảnh báo
"trên NIR, kính râm có thể trông trong suốt". Mình đã đọc câu đó lúc đầu buổi nhưng chỉ áp cho
`none`, không nghĩ nó áp cả cho `clear`.

**Mình học được gì từ dòng đó:** hai trường mô tả cùng một vùng trên khuôn mặt thì mức chắc chắn
của chúng phải khớp nhau. Lần sau, trước khi chọn `glasses`, mình nhìn lại `eye_left`/`eye_right`
và các cờ che của `face13` cùng khung — có `unknown` hoặc cờ che ở vùng mắt thì `glasses` khó mà
là một giá trị khẳng định. Đây cũng là lý do rubric cho điểm review chéo: một mình mình không thấy
mâu thuẫn đó, phải có người đọc bài mình bằng con mắt khác mới lộ ra.


## 4. Ghi chú về `ir_log.csv` — chưa đủ 4 quan sát

Nộp với **2 quan sát** thay vì 4 như rubric E4 yêu cầu. Nêu rõ ở đây thay vì viết cho đủ số:

| Khung | Nguồn | Có thật |
|---|---|---|
| `D01` | `real_IR` | Rút từ chính bản nhãn: `eye_right = unknown` kèm cờ che 8/13 điểm `face13` |
| `S03_ir` | `IR_sim` | Soi cặp `S03_rgb` / `S03_ir`, kết luận hình dạng vẫn đủ để giữ `type = box` |

Hai quan sát còn thiếu đáng lẽ lấy từ `S01_ir` (`person.seatbelt`) và `S02_ir`
(`child_seat.occupied`) — hai chỗ mình đang gán giá trị khẳng định (`not_worn`, `no`) nên cần kiểm
xem trên ảnh IR còn thấy rõ không. Mình chưa soi lại hai cặp ảnh này trước khi hết giờ.

Một dữ kiện liên quan, `tools/audit.py` đo được: **cả 8 cặp `_rgb`/`_ir` trong bài mình giống hệt
nhau từng thuộc tính**, không giá trị nào bị hạ xuống khi sang ảnh IR. Điều đó có thể đúng (ảnh
IR-sim của SVIRO là ảnh dựng, khá sạch), nhưng cũng có thể là dấu hiệu mình đã `Ctrl+V` rồi lưu mà
chưa soi lại ảnh `_ir` — đúng cái bẫy COMMON_ERRORS cảnh báo. Mình sẽ soi lại và bổ sung
`ir_log.csv` theo RULES §6 nếu coach cho hạn bổ sung.
