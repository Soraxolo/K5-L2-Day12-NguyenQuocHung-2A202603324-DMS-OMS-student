# TEAM — Ngày 12

Mã bộ ảnh: **G05** · Hình thức: **cá nhân**

<!-- CHUA-XAC-NHAN-COACH: xoá dòng này VÀ khối ⚠ bên dưới sau khi coach xác nhận cả hai việc -->

> ⚠ **HAI VIỆC CẦN COACH XÁC NHẬN**
>
> 1. **Mã G05 chưa được coach xác nhận.** Lớp phát bundle chứa cả 12 mã, mình chọn G05 để bắt đầu
>    làm. Nếu coach giao mã khác thì mình gán lại trên gói đúng.
> 2. **Review chéo làm trên mã G02, không phải G05.** Lý do ở mục dưới. Mong coach xác nhận cách
>    này chấp nhận được, hoặc chỉ cách khác.
>
> Xoá khối này sau khi coach xác nhận cả hai.

## Vì sao review chéo làm trên mã khác

Không tìm được bạn nào cùng mã **G05**, nên không có bản thứ hai để `cabin_check diff`.
Giải pháp: mình gán **thêm một bộ 22 ảnh của mã G02** — bộ mà bạn Hoàng Trọng Trà đang làm — để
hai người có **cùng bộ ảnh** mà đối chiếu, đúng tinh thần Task 3 (so hai cách hiểu guideline của
hai người, trên cùng khung hình).

Tổng cộng mình tự gán **44 ảnh**: 22 ảnh G05 (bài nộp E1) và 22 ảnh G02 (chỉ để review chéo).
Cả hai bộ đều `cabin_check` **0 lỗi**.

- `export_final.zip` = **G05**, là bài nộp E1
- `disagreement_log.csv` = kết quả `diff` trên **G02**

| Họ tên | MSSV | Đã gán đủ 22 ảnh? | Review chéo với (peer diff) | Số dòng disagreement đã xử lý |
|---|---|---|---|---|
| Nguyễn Quốc Hùng | 2A202603324 | có (G05 và G02, 44 ảnh) | Hoàng Trọng Trà — 2A202603342 (trên mã G02) | 11 / 88 |

Ca hai bạn vẫn không thống nhất và đã hỏi coach (ghi tên ảnh + đối tượng):

- **`S03`, `S04`, `S05`, `S06`, `S08` (cả `_rgb` và `_ir`) — box `child_seat` ở cảnh có trẻ em đang ngồi.**
  Mình **không vẽ box**, theo phán quyết coach trong buổi ("trẻ em ngồi trên ghế thì không gán nhãn")
  và GUIDE §4.1 định nghĩa `child_seat` là ghế **đang trống**. Bạn Trà **vẽ `child_seat` với
  `occupied = yes`**, theo file `labels_cabin_v1.json` coach gửi bổ sung trong buổi.
  Hệ quả đo được: 10 box `occupied = yes` làm `cabin_check` báo **10 ERROR** trên bài của bạn Trà,
  vì `scripts/cabin_schema.py` vẫn chỉ cho `unknown`/`no`. Hai bọn mình cần coach chốt: dùng `yes`
  hay không gán, và `cabin_check` có bản mới không.

- **Thuộc tính mặt trên ảnh NIR — 57 dòng** (`face.eye_left/eye_right/glasses` và cờ
  `face13.*_eye_*.outside`). Mình đọc được khe mắt nên ghi `open` và đặt điểm với cờ 0; bạn Trà
  không đọc được nên ghi `unknown` và bật `outside`. Hai bên đều tự nhất quán, khác nhau ở mức tự
  tin khi đọc ảnh hồng ngoại. Cần coach xem vài khung để chốt chuẩn chung.

## Cá nhân

### NguyenQuocHung-2A202603324
- **Phần mình làm:** tự gán đủ 22 ảnh cốt lõi G05 (S01–S08 × 2 modality, D01–D06) trên CVAT local
  của mình; chạy `cabin_check` ở Checkpoint A, Checkpoint B và lần cuối (`check_final.txt` 0 lỗi);
  gán thêm 22 ảnh G02 để tạo bộ ảnh chung cho review chéo; `diff` với bạn Trà và xử lý các dòng
  bất đồng theo mục guideline; phát hiện và báo lại cho bạn Trà 10 lỗi `occupied = yes`.
- **Điều mình học được hôm nay:** …
