# THẺ QUY TẮC — Ngày 12 (in ra hoặc mở tab thứ hai)

Rút từ GUIDE §4 + COMMON_ERRORS + đọc trực tiếp `scripts/cabin_check.py`.
Mục tiêu: gán 22 ảnh mà không mắc lỗi script bắt được, và không mắc 3 lỗi script **không** bắt được.

---

## 0. Bốn câu tự hỏi trước mỗi ảnh

1. Đã đặt tag `frame_meta` chưa? (**đặt TRƯỚC box đầu tiên**)
2. `modality` khớp tên file chưa? `_rgb` → `rgb`; `_ir` → `ir`; `D##` → `ir`.
3. Ảnh này là S## hay D##? → quyết định được gán label nào (bảng §2 dưới).
4. Có trường nào mình đang **đoán** không? → đổi thành `unknown`.

## 1. Bản đồ ghế (S##) — dán lên màn hình

```
        ẢNH (camera ở trước, nhìn về SAU xe)
   ┌─────────────┬──────────────┬─────────────┐
   │ trái ảnh    │  giữa ảnh    │  phải ảnh   │
   │ rear_RIGHT  │ rear_middle  │ rear_LEFT   │
   └─────────────┴──────────────┴─────────────┘
```

Trái ảnh = **phải xe**. Lật ngược là lỗi nặng nhất của buổi và `cabin_check` **không bắt được**
(script không có đáp án) — chỉ `diff` với bạn hoặc coach phát hiện.
Cách tự kiểm: quay lưng vào màn hình, tay phải mình chỉ về phía nào của màn hình thì phía đó là `rear_right`.

Bộ cốt lõi là **BMW X5 → có đủ 3 ghế sau**. `rear_middle` hợp lệ.
(`rear_middle` chỉ thành ERROR nếu manifest ghi xe `i3`/`zoe` — chỉ xảy ra ở phần mở rộng.)

## 2. Ảnh nào gán label nào

| | `frame_meta` | `person` | `face` | `face13` | `hand` | `phone` | `child_seat` | `infant_seat` | `object` |
|---|---|---|---|---|---|---|---|---|---|
| **S## (OMS)** | ✅ | ✅ | ✅ *chỉ box, thuộc tính để default* | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **D## (DMS)** | ✅ | ✅ `seat=driver` | ✅ *đủ 4 thuộc tính* | ✅ nếu mặt ≥ 60 px | ✅ | ✅ nếu thấy rõ | ❌ | ❌ | ❌ |

Chai nước / cốc / kính trên tay tài xế ở D##: **không vẽ gì cả** (DMS không có `object`, và nó không phải `phone`).

## 2b. Trẻ em đang ngồi → KHÔNG gán gì cho vị trí ghế đó

Phán quyết của coach trong buổi (21/11). Thấy một đứa trẻ **đang ngồi** trong ghế trẻ em:

- **Không** vẽ `person` cho đứa trẻ
- **Không** vẽ `child_seat` cho cái ghế đó — §4.1 định nghĩa `child_seat` là ghế **đang trống**
- Ghi khung đó vào `notes/ca_kho.md`, **không** đếm vào số ghế trống

Ghế trẻ em / nôi xách **đang trống** thì vẫn gán bình thường.
Giá trị `occupied = yes` coach thêm vào schema: **không dùng** cho bộ ảnh hôm nay.

## 3. Giá trị mặc định CVAT điền sẵn = bẫy

CVAT tự điền giá trị **đầu danh sách** cho mọi thuộc tính. Vẽ xong là phải mở **DETAILS** sửa ngay:

| Label | Thuộc tính | CVAT điền sẵn | Nguy hiểm vì |
|---|---|---|---|
| `person`, `child_seat`, `infant_seat`, `object` | `seat` | **`driver`** | Trên S## thì `seat=driver` luôn sai → WARN |
| `hand` | `whose` / `side` | `driver` / **`left`** | Hai tay cùng `side=left` → **ERROR** |
| `phone` | `state` | `held` | |
| `face` | `gaze_zone` | **`other`** | `other` hợp lệ nhưng phải ghi lý do vào ghi chú |
| `object` | `type` | `other` | |
| `frame_meta` | `modality` | **`ir`** | Ảnh `_rgb` bị bỏ sót → sai `modality` |
| `infant_seat` | `facing` | `rear` | |

## 4. Chuỗi thao tác chuẩn

**S##_rgb** → tag `frame_meta` (`rgb`, `light=unknown`, `camera_blocked=no`)
→ với **từng ghế có người/vật**: box + `seat` theo xe
→ người lớn: `person` (+ `seatbelt` = `not_worn` hoặc `unknown`) và một box `face`
→ ghế trẻ em trống: `child_seat` + `occupied` (`no`/`unknown`, **không có `yes`**)
→ ghế em bé: `infant_seat` + `facing`
→ đồ vật: `object` + `type`
→ vật nằm **trong** ghế trẻ em: **2 box riêng**, cùng `seat`
→ ghế trống: **không box**, chỉ đếm vào ghi chú
→ Ctrl+S.

**S##_ir** → chọn hết shape trên `_rgb`, Ctrl+C → sang `_ir`, Ctrl+V
→ sửa `frame_meta.modality` thành `ir`
→ **xét lại từng thuộc tính**: trường nào trên ảnh IR không còn thấy → `unknown`
→ kiểm box có lệch pixel không → Ctrl+S.
⚠️ Đây là chỗ sinh `ir_log`: mỗi lần bạn phải đổi một giá trị thành `unknown` là **một dòng ir_log**.

**D##** → tag `frame_meta` (`ir`, `light` theo cảnh, `camera_blocked`)
→ `person` `seat=driver` + `seatbelt`
→ `face` + 4 thuộc tính (`eye_left`, `eye_right`, `glasses`, `gaze_zone`)
→ đo bề rộng box `face`: ≥ 60 px → `face13`; < 60 px → bỏ `face13`
→ `hand` cho **mỗi** bàn tay thấy được (tay hành khách: `whose=passenger`)
→ `phone` nếu thấy cạnh/góc/màn hình
→ Ctrl+S.

## 5. Ảnh D## xoay 90° — nhớ bằng hình

```
   y nhỏ ┌──────────────────────┐
         │                      │   đầu ở PHẢI ảnh
         │   mắt PHẢI  ·        │   mặt hướng về x nhỏ
         │                 ĐẦU  │
         │   mắt TRÁI   ·       │   ⇒ mắt TRÁI của tài xế có y LỚN HƠN
   y lớn └──────────────────────┘
          x nhỏ            x lớn
```

- **Không xoay ảnh lại.**
- `face13` vừa vẽ ra sẽ nằm **thẳng đứng** (template của CVAT) → phải kéo quay ~90°. Script chỉ so trục x nên **không bắt được** template đặt sai chiều.
- Mí "trên" (`*_eye_upper`) về phía **x lớn** (phía trán); mí "dưới" về phía **x nhỏ**.
- Script sẽ WARN `"left_eye_outer nằm bên trái ảnh so với right_eye_outer"` **dù bạn gán đúng** → kiểm bằng trục y, rồi ghi một dòng giải thích ở cuối `check_cpB.txt` / `check_final.txt`.

## 6. Quyết định nhanh các thuộc tính hay sai

**`eye_left` / `eye_right`** (gán **riêng từng mắt**, không suy từ mắt kia)
- Thấy khe mắt mở (kể cả đang liếc xuống) → `open`
- Thấy rõ **hai mí khép** → `closed`
- Chỉ là *không thấy* (đốm phản xạ LED, tròng kính râm tối, bị tay/vật che, mặt quá nhỏ) → `unknown`
- Câu tự hỏi: *"tôi thấy mí khép, hay tôi chỉ không thấy?"*

**`glasses`** — nói về kính **đang đeo**
- Không đeo (kể cả đang **cầm** kính trên tay) → `none`
- Kính cận, xuyên được tròng → `clear`
- Kính râm → `sun`
- Không nhìn rõ vùng mắt (cúi, quay đi, tóc/tay che, ảnh tối) → `unknown`
- Trên NIR kính râm có thể trông **trong suốt** → không chắc thì `unknown`, đừng chọn `none` cho nhanh.

**`gaze_zone`** — `road` / `mirror_l` / `mirror_r` / `mirror_c` / `cluster` / `center` / `lap` / `other`.
`other` khi ngoài các vùng trên **hoặc không chắc** → ghi lý do vào ghi chú.

**`seatbelt`**
- `worn_correct`: dải chéo vai → hông đối diện
- `worn_incorrect`: dưới nách / sau lưng / lệch vai
- `not_worn`: **thấy rõ** không có dây
- `unknown`: không thấy (tối, bị che, đang thắt dở)
- **S## (SVIRO): chỉ `not_worn` hoặc `unknown`.** `worn_*` → WARN.
- Không suy từ ảnh kia cùng cảnh (RGB thấy → IR vẫn phải tự xét).

**`hand.side`** = trái/phải **của chính người đó**, không theo phía ảnh.
Hai box cùng `(whose, side)` → **ERROR**. Mỗi người tối đa 1 tay trái + 1 tay phải.
`on_wheel=no` là **bình thường** (xe đang tự lái) — đừng "sửa" thành `yes`.

**`phone`** — chỉ vẽ khi thấy ít nhất một phần hình dạng (cạnh, góc, màn hình).
Tay áp tai cầm vật tối mà không thấy phần nào như vậy → **không vẽ**.
Hộp sáng trên màn hình/áp phích không phải điện thoại.

**`face`** — không thấy mặt (quay đi, bị che gần hết, không thấy cả mắt lẫn mũi) → **không vẽ box**, ghi lý do vào ghi chú.

## 7. `face13` — 13 điểm, đúng tên

```
left_eye_outer   left_eye_inner   left_eye_upper   left_eye_lower
right_eye_outer  right_eye_inner  right_eye_upper  right_eye_lower
nose_tip         mouth_left       mouth_right      lip_upper        lip_lower
```

- Điểm mí/khóe đặt ở **mép**, nơi mí gặp mắt — không đặt giữa tròng.
- Bị che nhưng **đoán chắc** được vị trí → `occluded`; **không đoán được** → `outside`.
- **Không đặt điểm "cho đủ".**
- Mọi điểm đều **phải có cờ** `occluded`/`outside` (0 hoặc 1) — thiếu là **ERROR**.
- Mặt < 60 px: chỉ box `face`, **không** `face13` → script ERROR nếu vẽ.
- Chỉ vẽ trên D##. Người lớn S## chỉ có box `face`.

**Ràng buộc chéo script kiểm (`check_eye_flags`):**
- `eye_<side> = unknown` nhưng **không** điểm `<side>_eye_*` nào có cờ → WARN
- `eye_<side> = open/closed` nhưng **cả 4** điểm `<side>_eye_*` đều bị che → WARN
⇒ Nhất quán: mắt `unknown` thì các điểm mắt đó phải có `occluded`/`outside`.

## 8. Script bắt được gì / KHÔNG bắt được gì

**ERROR (phải hết sạch trước khi nộp)**
- Số ảnh khác `--expect`
- Tag `frame_meta` ≠ đúng 1 cái / ảnh
- Thiếu hoặc sai giá trị bất kỳ thuộc tính nào
- Label/kiểu hình không có trong guideline (vẽ polygon, polyline…)
- Box suy biến (< 2 px một chiều)
- `face13` không đủ đúng 13 điểm, hoặc điểm thiếu cờ
- `face13` trên mặt < 60 px
- Hai `hand` cùng `(whose, side)`
- `rear_middle` trên xe 2 ghế sau (i3/zoe)

**WARN (phải giải thích từng cái ở cuối `check_final.txt`)**
- `light` ≠ `unknown` trên ảnh S##
- `seat = driver` / `front_passenger` trên ảnh S##
- `seatbelt = worn_*` trên ảnh S##
- Thuộc tính lạ
- Một ghế có nhiều box cùng loại, hoặc có cả `child_seat` và `infant_seat`
- `face13` không nằm trong box `face` nào / không có điểm nào hiện
- `left_eye_outer` bên trái ảnh so với `right_eye_outer` ← **bình thường trên D## xoay**
- Ràng buộc mắt ↔ cờ điểm ở §7

**Script KHÔNG bắt được (tự soát + `diff` với bạn)**
1. **Lật trái/phải ghế** (`rear_left` ↔ `rear_right`) — không có đáp án trong script
2. **`face13` đặt sai chiều** trên ảnh xoay 90° — chỉ so trục x
3. **Box lỏng / lệch mép** — không có GT để so
4. **Giá trị đoán mà vẫn hợp lệ** (ghi `none` cho người đang đeo kính, `not_worn` khi thật ra không thấy)

## 9. Export đúng cách

CVAT: task → **Actions** → **Export task dataset** → **CVAT for images 1.1** → **BỎ CHỌN "Save images"**
→ OK → trang **Requests** → chờ **Finished** → **⋮** → **Download**.
Zip đúng chỉ vài chục KB. Kiểm: `python3 -m zipfile -l export_final.zip` → chỉ thấy `annotations.xml`.

Ghi kết quả bằng `--out`, **không** dùng `> file`.

## 10. Mẹo CVAT

- Copy shape RGB→IR: chọn shape, `Ctrl+C`, sang ảnh `_ir`, `Ctrl+V`.
- Ảnh tối: **Image settings** (bánh răng trên canvas) → Brightness/Contrast. Chỉ đổi hiển thị.
- Phím tắt chỉ chạy khi **khung ảnh đang được chọn** (bấm vào ảnh một lần). `N` = vẽ lại hình cùng loại. `F`/`D` = ảnh sau/trước.
- Thuộc tính nằm trong **DETAILS** của từng đối tượng, thanh bên phải.
- Đổi label của hình: chọn hình → ô thả xuống trong danh sách đối tượng bên phải.

## 11. Hai điều kiểm được từ mã nguồn (đã chạy thử)

**(a) Luôn truyền `--manifest`.** `cabin_check` quyết định "đây là ảnh SVIRO" bằng hai đường:
tra `manifest.csv`, **hoặc** khớp mẫu tên `^S\d+_(ir|rgb)\.png$`. Nếu tên ảnh trong task bị đổi
(thêm tiền tố, đổi sang `.jpg`) **và** bạn không truyền `--manifest` thì ba cảnh báo riêng của SVIRO
(`light` ≠ unknown, `seat=driver`, `seatbelt=worn_*`) **im lặng không chạy** — tưởng sạch mà không phải.
Đã kiểm bằng `tools/make_demo_export.py`: cùng một nội dung, chỉ đổi tên ảnh thì 6 cảnh báo SVIRO
biến mất.

**(b) Box `face` trên ảnh S## vẫn phải có đủ 4 thuộc tính.** GUIDE §4.1 ghi OMS "chỉ box", nhưng
`check_attrs` đòi **mọi** thuộc tính của label có mặt — thiếu một cái là ERROR. CVAT luôn export
giá trị mặc định (`unknown`, `unknown`, `unknown`, `other`), nên **cứ để nguyên default là đạt**;
chỉ cần đừng xoá thuộc tính và đừng tự ghi giá trị đoán vào đó.

**Chạy thử trước khi gán bài thật** (xác nhận script chạy trên máy, và nhớ mặt chữ từng lỗi):

```bash
cd ~/day12-dms-oms && python3 tools/make_demo_export.py --run
```

`DEMO_clean.xml` phải ra `0 lỗi, 0 cảnh báo`. `DEMO_errors.xml` cố tình sai, in ra đúng những dòng
hay gặp nhất trong buổi. Hai file này là **số bịa, không phải bài nộp** — nằm trong `tools/demo/`,
đã bị `.gitignore` chặn và `tools/preflight.py` không đóng gói.
