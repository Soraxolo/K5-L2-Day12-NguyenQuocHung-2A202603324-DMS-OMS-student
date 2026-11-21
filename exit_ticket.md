# Exit ticket — Ngày 12

Làm cá nhân, không mở slide, khoảng 10 phút. Ghi đáp án ngay dưới mỗi câu.

**Họ tên:** Nguyễn Quốc Hưng · **Mã:** G05

---

**Câu 1 · Chọn một.** Camera DMS trên nhiều xe tự chiếu đèn LED cận hồng ngoại khoảng 940 nm lên mặt tài xế. Lý do chính là gì?

- A. Để đo nhiệt độ da và phát hiện tài xế bị sốt
- B. Để có ảnh mặt ổn định cả ngày lẫn đêm mà không làm chói mắt tài xế
- C. Để có ảnh màu đẹp hơn cho cuộc gọi video
- D. Để camera nhìn xuyên qua mọi loại kính râm

Đáp án: **B**

Lý do: 940 nm nằm ngoài vùng mắt người thấy được, nên đèn sáng liên tục cả ban ngày lẫn ban đêm mà
tài xế không bị chói. Nhờ tự chiếu sáng, độ sáng khuôn mặt không phụ thuộc đèn đường hay nắng, nên
model nhận được ảnh ổn định suốt 24 giờ.
A sai: đó là ảnh nhiệt (hồng ngoại sóng dài 8–14 µm), khác hẳn NIR. C sai: NIR cho ảnh đơn sắc, không
có màu. D sai: hôm nay chính mình thấy ngược lại — trên NIR, kính râm có thể trông trong suốt **hoặc**
phản xạ thành đốm sáng che mắt, nên có khung phải để `eye_* = unknown`.

**Câu 2 · Số, 2 chữ số thập phân.** Camera DMS chạy 30 khung hình/giây. Model ước lượng yaw của đầu tài xế lớn hơn 30° liên tục từ khung hình số 240 đến khung hình số 314, **tính cả khung 240 và khung 314**. Tài xế không nhìn đường trong bao nhiêu giây?

Đáp án: **2.50 s**

Cách tính: 314 − 240 + 1 = **75** khung (tính cả hai đầu). 75 ÷ 30 = **2,50 s**.

**Câu 3 · Chọn tất cả đáp án đúng.** Những câu nào đúng về dữ liệu cabin so với dữ liệu camera ngoài xe?

- A. Không thể làm mờ mặt tài xế như làm mờ mặt người qua đường, vì model DMS cần chính khuôn mặt.
- B. Ban đêm, ảnh cabin thường là ảnh hồng ngoại đen trắng, nên thuộc tính màu áo không gán được.
- C. Camera OMS nhìn về phía sau xe, nên ghế ở bên trái ảnh là ghế bên phải của xe.
- D. Vật trong cabin thường ở xa và nhỏ, nhiều vật trong một ảnh.
- E. Cảnh cabin cố định nên không cần guideline hay QC riêng.

Đáp án: **A, B, C**

- A đúng: khuôn mặt là **chính** tín hiệu DMS (mắt, hướng đầu, 13 điểm mặt). Làm mờ mặt là xoá mất dữ liệu,
  nên quyền riêng tư phải xử lý bằng cách khác — giữ ảnh trong phạm vi dự án, đúng như RULES §2 của lab này.
- B đúng: hôm nay toàn bộ 6 khung D## và 8 khung S##_ir đều không có màu; mình phải nhận đồ vật bằng
  hình dạng và vị trí, và `object.type` có khung phải để `other` vì mất màu.
- C đúng: đây là bẫy lớn nhất của phần OMS — trái ảnh là `rear_right`.
- D sai: ngược lại. Vật trong cabin ở **gần**, **to** trong khung, và mỗi ảnh chỉ có vài vật. Ở xa và nhỏ,
  nhiều vật trong một ảnh là đặc điểm của camera ngoài xe (người đi bộ, xe cộ, biển báo).
- E sai: cảnh cố định không làm mất nhu cầu guideline. Chính vì cố định mà sinh ra những quy ước riêng
  dễ sai hàng loạt nếu không có guideline: ghế gọi theo xe (không theo ảnh), trái/phải theo người
  (không theo ảnh), ảnh D## xoay 90°, `occupied` không có `yes`, SVIRO không có ai thắt dây.
