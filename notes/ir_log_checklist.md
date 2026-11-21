# Tìm gì để ghi `ir_log.csv` (E4)

Rubric cần **≥ 4 quan sát**, mỗi dòng có: một **khung**, một **hiện tượng**, một **trường nhãn bị ảnh hưởng**,
và tác động lên nhãn. Cột `source` phải tách đúng:

| `source` | Ảnh | Là gì |
|---|---|---|
| `IR_sim` | `S##_ir` | IR **mô phỏng** của SVIRO (ảnh dựng bằng máy tính, đèn đỏ + kênh đỏ) |
| `real_IR` | `D##` | NIR **thật** của Drive&Act |

**Lỗi bị trừ điểm:** ghi hiện tượng của IR thật lên ảnh S## (chói kính, mắt sáng, sáng yếu dần theo
khoảng cách). SVIRO **không** tái hiện các hiện tượng đó. Đừng ghi chúng cho S##.

Cách sinh dòng nhanh nhất: mỗi lần copy shape từ `S##_rgb` sang `S##_ir` mà bạn **phải đổi một giá trị
thành `unknown`** → đó chính là một dòng `ir_log`.

---

## Trên `S##_ir` (IR_sim) — tìm những thứ sau

| Hiện tượng cần kiểm | Trường nhãn bị ảnh hưởng |
|---|---|
| Mất màu hoàn toàn → không phân biệt được loại đồ vật bằng màu, phải đoán bằng hình dạng | `object.type` |
| Vật tối nằm trên ghế tối → mép vật lẫn vào nền, box khó ôm sát | box `object` (vị trí/kích thước) |
| Áo tối + dây an toàn (nếu có) cùng độ sáng → không thấy dải chéo | `person.seatbelt` |
| Ghế trẻ em có khăn/áo phủ, trên ảnh IR-sim không còn thấy lòng ghế | `child_seat.occupied` |
| Người ngồi sâu trong bóng → bỏ sót hẳn một `person` so với bản RGB | thiếu box `person` |
| Mặt mất chi tiết, không phân biệt mắt mở/nhắm | `face` (OMS chỉ box nên ghi: không thể thêm thuộc tính mắt) |
| Mép ghế / cột xe và vật có cùng độ sáng → ranh giới `seat` khó xác định | `object.seat` / `person.seat` |

**So trực tiếp RGB ↔ IR-sim bằng script (tùy chọn, GUIDE §5 lộ trình Mở rộng):**
```bash
pip install pillow numpy
cd ~/day12-dms-oms && python3 scripts/rgb_ir_diff.py G05/oms --out ir_pairs
```
(`ir_pairs/` đã bị `.gitignore` chặn.)

## Trên `D##` (real_IR) — tìm những thứ sau

| Hiện tượng cần kiểm | Trường nhãn bị ảnh hưởng |
|---|---|
| Đốm phản xạ đèn LED trên tròng kính che hẳn một mắt | `eye_left` **hoặc** `eye_right` → `unknown` |
| Kính râm trên NIR trông **trong suốt** → dễ ghi sai `glasses=none` | `glasses` → `sun` hoặc `unknown` |
| Đồng tử/giác mạc sáng rực (eye glint) làm mất khe mắt | `eye_*` → `unknown`; cờ `occluded` ở `*_eye_*` |
| Ánh sáng yếu dần theo khoảng cách → tay ở xa đèn tối gần như nền | box `hand` (có/không vẽ), `hand.on_wheel` |
| Vùng gần đèn cháy sáng (overexposed) → mất mép mí, đặt điểm `face13` phải bật cờ | cờ `occluded` của `*_eye_upper`/`*_eye_lower` |
| Vật tối trong tay không thấy cạnh/góc/màn hình | **không vẽ** `phone` (GUIDE §4.7) |
| Da sáng, áo tối → mép `person` phía thân dưới khó xác định | box `person` |
| Không có màu → không suy được hướng nhìn từ màu tròng, chỉ dựa hình đầu/mắt | `gaze_zone` → `other` nếu không chắc |
| Dây an toàn cùng độ sáng với áo, hoặc ở vùng tối | `seatbelt` → `unknown` |

---

## Mẫu một dòng tốt (không phải để copy nguyên, phải thay bằng khung thật của mình)

```
S04_ir,IR_sim,"túi đen trên ghế lẫn vào nền ghế tối, chỉ thấy đường viền trên",object.type,"RGB thấy rõ là bag; trên IR-sim giữ bag theo hình dạng nhưng box phải nới 3-4 px vì không thấy mép dưới"
D02,real_IR,"đốm phản xạ LED phủ kín tròng kính bên mắt phải tài xế",eye_right,"ghi unknown (không phải closed); 4 điểm right_eye_* bật cờ occluded"
```

## Dòng bị coi là chung chung (tránh)

- `"IR rõ hơn"` — không có khung, không có trường nhãn
- `"ảnh tối khó gán"` — không nói hiện tượng gì, ảnh hưởng trường nào
