# Danh sách lớp v0 — Nguyễn Quốc Hùng · Gxx

Viết tiếp từ slide 54. Mỗi lớp trả lời: **model cần nhận ra cái này để làm gì?**
Cột cuối ghi theo kinh nghiệm gán 22 khung hôm nay (16 khung SVIRO IR-sim + 6 khung NIR thật).

## DMS (ít nhất 6 lớp)

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng DMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `eye_state` (gán **riêng từng mắt**) | open / closed / unknown | Phát hiện buồn ngủ: đo tỷ lệ thời gian mắt nhắm (PERCLOS) và số lần nhắm dài | Có, nhưng mất khi đèn LED phản xạ trên tròng kính → phải có giá trị `unknown` để model không học đốm sáng thành "mắt nhắm" |
| 2 | `gaze_zone` | road / mirror_l / mirror_r / mirror_c / cluster / center / lap / other | Đo thời gian mắt rời đường (eyes-off-road); cảnh báo mất tập trung. Phân biệt rời đường **hợp lý** (gương, đồng hồ) với **không hợp lý** (màn hình giữa, đùi) | Có, suy từ hướng đầu + khe mắt. Không có màu nên không dùng được màu tròng mắt; khung nào không chắc phải để `other` |
| 3 | `head_pose` (yaw / pitch, suy từ `face13`) | góc, liên tục | Vẫn đo được hướng chú ý khi mắt bị kính râm hoặc đốm sáng che — là tín hiệu dự phòng cho `gaze_zone` | Có. 13 điểm mặt vẫn đặt được trên NIR, kể cả ảnh xoay 90° |
| 4 | `glasses` | none / clear / sun / unknown | Hai việc: (a) để model học được cả người đeo kính; (b) **cổng tin cậy** — biết khi nào `eye_state` không đáng tin để hạ mức tin của cảnh báo buồn ngủ | Khó: trên NIR kính râm có thể trông trong suốt. Đây là lớp dễ gán sai nhất ở phần DMS hôm nay |
| 5 | `hand_on_wheel` (thuộc tính của `hand`) | yes / no / unknown | Phát hiện rời tay vô lăng ở xe L2; đếm thời gian trước khi yêu cầu tài xế nhận lại quyền điều khiển | Có, nếu tay nằm trong vùng đèn chiếu tới. Tay ở xa đèn tối gần như nền → `unknown` |
| 6 | `phone_use` (thuộc tính `state` của `phone`) | held / mounted / lap / (không có box = không dùng) | Phát hiện dùng điện thoại cầm tay — hành vi bị cấm, khác với điện thoại gắn giá (`mounted`) là hợp pháp | Một phần: chỉ gán khi thấy cạnh, góc hoặc màn hình. Vật tối trong tay trên NIR nhiều khi không đủ bằng chứng |
| 7 | `seatbelt` (tài xế) | worn_correct / worn_incorrect / not_worn / unknown | Nhắc thắt dây; `worn_incorrect` (dải dưới nách, sau lưng) nguy hiểm nhưng cảm biến khoá dây **không** phát hiện được — chỉ camera làm được | Hạn chế: dây cùng độ sáng với áo tối thì không thấy → `unknown` |
| 8 | `face_visible` / mức che mặt (**đề xuất thêm cho v1.x**) | visible / partially_occluded / not_visible | **Cổng đầu ra:** khi không thấy mặt thì hệ thống phải báo "không xác định", không được im lặng coi như tài xế bình thường. Hôm nay guideline chỉ nói "không thấy mặt thì không vẽ box" — tức là mất mặt và không có mặt trong khung bị trộn thành một | Có |
| 9 | `secondary_activity` (**đề xuất thêm cho v1.x**) | drinking / eating / reaching / grooming / none | Phân biệt mất tập trung do hành vi phụ với buồn ngủ — hai cảnh báo khác nhau. Xem câu leo thang số 2 | Có, qua hình dáng tay + vật trong tay |

## OMS (ít nhất 6 lớp)

| # | Lớp / thuộc tính | Giá trị | Để làm gì (chức năng OMS) | Nhìn thấy được trên IR? |
|---|---|---|---|---|
| 1 | `seat_occupancy` (từng ghế) | empty / adult / child_seat / infant_seat / object | Lớp nền của OMS: quyết định bật/tắt túi khí từng ghế, nhắc thắt dây đúng ghế, đếm số người trong xe | Có (nhận bằng hình dạng và vị trí). Người ngồi sâu trong bóng dễ bị bỏ sót trên IR-sim |
| 2 | `occupant_class` | adult / child / unknown | Điều chỉnh lực bung túi khí; trẻ em ngồi ghế trước cần tắt túi khí. Gán sai lớp này gây thương tích thật | Có, nhưng suy từ kích thước nên cần `unknown`; bộ ảnh cốt lõi hôm nay **không có trẻ em ngồi** → lớp này chưa có dữ liệu để học |
| 3 | `infant_seat` + `facing` | rear / front | Nôi xách **quay về sau** bắt buộc phải tắt túi khí ghế trước; quay về trước thì không. Chỉ `facing` quyết định, không phải việc có nôi hay không | Có — hướng nhận được bằng hình dạng, không cần màu |
| 4 | `child_seat` + `occupied` | no / unknown (v1.0 **không có** `yes`) | Nhắc "quên trẻ trong xe" sau khi tài xế rời xe và khoá cửa | Hạn chế: khăn/áo phủ lòng ghế trên IR-sim thì phải để `unknown`. Xem câu leo thang số 1 |
| 5 | `object_type` | bag / box / cup / other | Nhắc đồ bỏ quên khi rời xe (xe dịch vụ, taxi, xe chia sẻ) | Hạn chế: IR mất màu nên chỉ còn hình dạng. `bag` vs `box` tối màu rất dễ lẫn → phải để `other` |
| 6 | `rear_seatbelt` (từng hành khách sau) | worn_correct / worn_incorrect / not_worn / unknown | Nhắc thắt dây hàng ghế sau — nhiều xe không có cảm biến khoá dây cho ghế giữa | Hạn chế như DMS. **Bộ SVIRO không có ai thắt dây**, nên không dạy được `worn_correct` — xem RUBRIC phần mở rộng (b) |
| 7 | `occupant_count` (suy từ lớp 1) | 0 … 5 | Xe dịch vụ: đối chiếu số khách; điều hoà theo vùng có người; phát hiện quá tải | Có |
| 8 | `camera_blocked` (`frame_meta`) | yes / no | **Tự chẩn đoán:** camera bị che/bẩn thì cả DMS và OMS phải báo lỗi hệ thống, không được trả "cabin trống". Đây là lớp về **chất lượng khung**, không phải về người | Có |
| 9 | `modality` (`frame_meta`) | rgb / ir | Chọn nhánh model và chọn tập thuộc tính hợp lệ: khung `ir` không được sinh nhãn dựa trên màu. Cũng cần để **đánh giá riêng** độ chính xác ban ngày và ban đêm | — (là siêu dữ liệu của khung) |

## 2 câu hỏi leo thang

> Cả hai câu đều là chỗ guideline v1.0 **buộc gán một giá trị hợp lệ nhưng sai bản chất** — loại lỗi
> script không bắt được, và nếu không hỏi thì nó đi thẳng vào dữ liệu huấn luyện.

**1. `child_seat.occupied` không có giá trị `yes`, nên lớp mà OMS cần nhất lại không gán được.**

Câu hỏi: GUIDE §4.8 ghi rõ `occupied` chỉ nhận `no` hoặc `unknown`. Trên bộ ảnh của lớp thì hợp lý
(SVIRO không có trẻ ngồi, và guideline dặn "thấy hình giống trẻ em thì báo coach, không gán").
Nhưng chức năng OMS quan trọng nhất của ghế trẻ em là **biết có trẻ đang ngồi trong đó**
(tắt túi khí, nhắc quên trẻ trong xe). Vậy khi làm dữ liệu thật:
(a) `occupied = yes` sẽ được thêm ở v1.x, hay (b) trẻ đang ngồi được gán thành `person` + `occupant_class = child`
kèm một box `child_seat` riêng cùng `seat`? Nếu là (b) thì `occupied` của box `child_seat` đó ghi gì —
`unknown`, hay vẫn `no` vì "không thấy lòng ghế"?

Khung ví dụ: `[điền tên khung — ảnh S## có child_seat mà lòng ghế bị khăn/áo phủ, ví dụ S06_ir]`

Mình tạm gán thế nào và vì sao: `occupied = unknown`. Theo luật chung 4.4-1 "không thấy thì `unknown`":
mình không thấy lòng ghế nên không được ghi `no`. Ghi `no` ở đây là **khẳng định ghế trống** —
đúng là dạy model điều mình không kiểm chứng được.

**2. DMS cấm vẽ `object`, nên hành vi phụ như uống nước không để lại bằng chứng nào trong nhãn.**

Câu hỏi: GUIDE §4.2 ghi DMS "không vẽ `object`, cũng không ghi là `phone`" cho chai, cốc, kính trên tay;
và §4.7 chỉ cho vẽ `phone` khi thấy cạnh/góc/màn hình. Nhưng Drive&Act quay đúng các hành vi đó
(uống nước, tháo kính, gọi điện) và đó là mất tập trung thật. Kết quả là khung "tài xế đang uống nước"
và khung "tài xế đưa tay không lên gần mặt" có **nhãn giống nhau hoàn toàn**: `person` + `face` +
`face13` + hai `hand`, `gaze_zone` có thể cùng là `other`. Model không thể phân biệt.
Vậy v1.x sẽ: (a) mở `object` cho DMS với `type` thêm `bottle`/`cup`, (b) thêm thuộc tính
`activity` trên `person`, hay (c) chủ ý bỏ hành vi phụ ra khỏi phạm vi và chỉ phát hiện điện thoại?
Nếu là (c) thì đánh giá model về mất tập trung sẽ thiếu hẳn một nhóm nguyên nhân.

Khung ví dụ: `[điền tên khung — ảnh D## tài xế cầm chai/cốc đưa lên gần mặt]`

Mình tạm gán thế nào và vì sao: làm **đúng** v1.0 — không vẽ gì cho chai, chỉ vẽ `hand` với
`on_wheel = no`, và ghi khung này vào ghi chú ca khó. Theo RULES §4: guideline không nói tới thì
không tự đặt luật mới, nên mình không tự mở thêm label.

### Hai câu dự phòng (nếu coach đã trả lời hai câu trên)

3. `gaze_zone` là thuộc tính **bắt buộc** của mọi box `face`, nhưng không có giá trị cho
   "không xác định được hướng nhìn". §4.5 cho `other` khi "ngoài các vùng trên **hoặc không chắc"** —
   nên khung mắt nhắm hẳn và khung tài xế nhìn ra cửa sổ bên đều thành `other`. Model mất tập trung
   sẽ học `other` như một vùng nhìn, trong khi một nửa số khung `other` thực ra là "không biết".
   Có nên tách `gaze_zone = undeterminable` ở v1.x?
4. `hand.whose` chỉ có `driver` / `passenger`, không có `unknown`. Khung chỉ thấy một bàn tay ở mép ảnh,
   không thấy tay đó nối vào ai, thì bắt buộc phải **đoán** — trái với luật chung 4.4-1.
