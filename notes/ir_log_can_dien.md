# `ir_log.csv` — còn thiếu 3 dòng, cần bạn mở ảnh xem

Rubric E4 cần **≥ 4 quan sát**, và cột `source` phải tách `IR_sim` (ảnh `S##`) với `real_IR` (ảnh `D##`).
Hiện có **1 dòng** (`D01`), rút từ chính bản nhãn của bạn. Ba dòng còn lại phải là quan sát của bạn.

## Vì sao không rút thêm được từ dữ liệu

Cả 8 cặp `S0x_rgb` / `S0x_ir` trong bài bạn **giống hệt nhau từng thuộc tính**. Không có giá trị nào
bị hạ xuống khi sang ảnh IR, nên bản nhãn không ghi lại hiện tượng IR nào.

## Cách lấy 3 dòng trong 10 phút

Mở CVAT, với **3 cảnh bất kỳ** trong `S01`–`S08`, bật `S0x_rgb` rồi bấm `F` sang `S0x_ir`, nhìn
đúng một câu hỏi: **thứ gì mình thấy ở ảnh màu mà ảnh xám không còn thấy?**

Những chỗ hay mất nhất trên IR-sim (chỉ ghi cái bạn thật sự thấy):

| Tìm gì | Trường nhãn bị ảnh hưởng |
|---|---|
| Mất màu → không phân biệt được loại đồ vật, phải đoán bằng hình dạng | `object.type` |
| Vật tối nằm trên ghế tối, mép vật lẫn vào nền | box `object` (vị trí/kích thước) |
| Ghế trẻ em có vải phủ, không còn thấy lòng ghế | `child_seat.occupied` |
| Người ngồi trong bóng, trên ảnh IR gần như biến mất | thiếu box `person` |
| Ranh giới giữa hai ghế mờ đi | `seat` |

**Không** ghi cho ảnh `S##`: chói kính, mắt sáng, phản xạ LED, ánh sáng yếu dần theo khoảng cách —
đó là hiện tượng IR **thật**, SVIRO không tái hiện (GUIDE §3). Ghi nhầm là bị trừ.

Nếu soi 3 cảnh mà thật sự không mất gì, thì **ghi đúng như vậy** và lấy thêm dòng từ ảnh `D##`
(`real_IR`) — ở đó chắc chắn có hiện tượng: tròng kính khó đọc, đốm phản xạ, vùng tối xa đèn.
Một nhận định trung thực "cảnh này IR-sim không làm mất gì, vì <lý do>" vẫn là một quan sát.

## Mẫu dòng

```
<khung>,<IR_sim|real_IR>,"<hiện tượng cụ thể>",<trường nhãn>,"<mình đã gán thế nào và vì sao>"
```

Thêm bằng:

```bash
cd ~/day12-dms-oms && cat >> ir_log.csv <<'TXT'
S0?_ir,IR_sim,"...",object.type,"..."
TXT
```
