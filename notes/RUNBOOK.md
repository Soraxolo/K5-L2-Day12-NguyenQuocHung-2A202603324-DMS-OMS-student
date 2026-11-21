# RUNBOOK — Ngày 12, chạy trên máy này

Repo làm việc: `/home/hung/day12-dms-oms`
CVAT: `/home/hung/cvat-day2`, **v2.74.1**, đang chạy, `http://localhost:8080` trả 200.
Python: `python3` 3.12.7 (lệnh trong tài liệu viết `python` → trên máy này gõ **`python3`**).

> Lớp dùng v2.82.0, máy này v2.74.1. Lab chạy được trên 2.7x — `INSTALL_CVAT.md` §7 đã nói
> riêng về bản 2.7x ("menu vẽ chỉ hiện tooltip khi rê, phải bấm vào biểu tượng").
> **Đừng nâng cấp hôm nay**: nâng cấp CVAT giữa buổi có rủi ro mất dữ liệu Day 11 đang nằm trong
> cùng volume. Nếu skeleton `face13` không tạo được trên 2.74.1 thì mới báo coach và xử lý.
> Tuyệt đối không chạy `docker compose down -v`.

---

## Bước 0 — chép bộ ảnh (14:00)

Coach phát **một bundle chứa cả 12 mã**: `~/Downloads/Day12_learner_bundles_G01-G12-*.zip`.
Đã giải nén sẵn 12 gói ra `~/day12-bundles/` (`G01.zip` … `G12.zip`, mỗi gói ~19–20 MB).

**Chỉ được dùng gói của mã coach giao cho mình.** Dùng sai mã thì nhãn của mình bị so với đáp án
SVIRO của mã khác, và `diff` với bạn cùng mã sẽ là hai bộ ảnh khác nhau.

Một lệnh làm hết Bước 0 (thay `G05` bằng mã thật):

```bash
cd ~/day12-dms-oms && python3 tools/setup_pack.py G05
```

Script sẽ: kiểm gói có đủ 22 ảnh cốt lõi → đọc `manifest.csv` xem xe nào (quyết định `rear_middle`
có hợp lệ) → giải nén vào repo → điền mã vào `TEAM.md`, `class_list_v0.md`, `self_review.md`,
`exit_ticket.md`, `prompts.md` → kiểm `.gitignore` có chặn ảnh → in đúng 22 đường dẫn cần chọn
trong CVAT và ba lệnh checkpoint đã điền sẵn mã.

Xem trước mà không ghi gì: thêm `--dry-run`.

**Đã kiểm cả 12 gói:** gói nào cũng có 20 ảnh `oms/` (S01–S10 ×2) + 6 ảnh `driver/` (D01–D06)
+ `ATTRIBUTION.txt`, `SOURCES.txt`, `labels_cabin_v1.json`, hai `manifest.csv`, và một thư mục
`scripts/` **bản cũ — không dùng** (README dặn chỉ chạy `scripts/` của repo).

**Mọi cảnh của cả 12 mã đều là xe `x5` (BMW X5) → có đủ 3 ghế sau, `rear_middle` hợp lệ.**

**Truyền `--manifest Gxx/oms/manifest.csv`** — đúng file `oms`. File `Gxx/driver/manifest.csv` chỉ
có cột `group,name`, không có cột `car`, nên vô dụng với `cabin_check` (không gây lỗi, chỉ không
có tác dụng).

## Bước 0b — chạy thử script (2 phút, làm trước khi gán)

```bash
cd ~/day12-dms-oms && python3 tools/make_demo_export.py --run
```

`DEMO_clean` phải ra `0 lỗi, 0 cảnh báo`; `DEMO_errors` in ra mặt chữ của các lỗi hay gặp.
Hai file này là số bịa trong `tools/demo/`, không phải bài nộp.

## Bước 1 — tạo project + task trong CVAT

1. `http://localhost:8080` → **Projects** → **+** → **Create a new project**
   - Name: `Day12`
   - **Labels → Raw** → dán **toàn bộ** nội dung `labels_cabin_v1.json` → **Done** → **Submit**
   - Kiểm: project thấy **9 nhãn** (`face`, `face13`, `hand`, `phone`, `person`, `child_seat`, `infant_seat`, `object`, `frame_meta`).
   - `face13` phải là kiểu **skeleton** có 13 sublabel. Nếu bản 2.74.1 không nhận `svg` → báo coach.

   In nội dung ra để dán:
   ```bash
   cat ~/day12-dms-oms/labels_cabin_v1.json
   ```

2. Trong project `Day12` → **+** → **Create a new task**
   - Name: `Day12-Gxx`
   - Subset: để trống
   - **Select files** → chọn đúng **22 ảnh**: `Gxx/oms/S01_rgb.png … S08_ir.png` (16 ảnh) và `Gxx/driver/D01.png … D06.png` (6 ảnh)
   - **KHÔNG** chọn `S09_*`, `S10_*`, **KHÔNG** chọn `manifest.csv`
   - Submit, chờ task tạo xong → mở Job → phải đếm được **22 ảnh**.

   Liệt kê đúng 22 file để đối chiếu khi chọn:
   ```bash
   cd ~/day12-dms-oms && ls G*/oms/S0[1-8]_*.png G*/driver/D0[1-6].png | sort
   ```

3. Thử script:
   ```bash
   cd ~/day12-dms-oms && python3 scripts/cabin_check.py --help
   ```

## Bước 2 — Task 1a: S01–S02 (14:30)

Gán theo `notes/RULE_CARD.md` §1, §3, §4. Thứ tự: `_rgb` trước → copy sang `_ir` → sửa thuộc tính.

## Checkpoint A — 14:45

Export task → `part_A.zip`, để trong `~/day12-dms-oms/`, rồi:

```bash
cd ~/day12-dms-oms && python3 scripts/cabin_check.py check part_A.zip --only S01,S02 --expect 4 --manifest G*/oms/manifest.csv --out check_cpA.txt
```


- Phải thấy `Ảnh: 4 · đã có frame_meta: 4`.
- **Trên 3 ERROR trong 4 ảnh này** → chuyển lộ trình **Hỗ trợ** (GUIDE §5) trước khi gán tiếp.
- Gọi coach xem các dòng `[ERROR]` trên màn hình.

## Bước 3 — Task 1b: S03–S08 + ghi `ir_log` (14:55)

Mỗi lần copy RGB→IR mà phải đổi một giá trị thành `unknown` → ghi ngay một dòng vào `ir_log.csv`.
Dùng `notes/ir_log_checklist.md` để biết tìm gì, nhưng **chỉ ghi điều mình thật sự thấy**.

## Bước 4 — Task 2a: D01–D02 (15:45)

RULE_CARD §5 (ảnh xoay), §6 (thuộc tính mặt), §7 (`face13`).
Đo bề rộng box `face` trước khi quyết định vẽ `face13` (ngưỡng 60 px).

## Checkpoint B — 16:05

```bash
cd ~/day12-dms-oms && python3 scripts/cabin_check.py check part_B.zip --only D01,D02 --expect 2 --manifest G05/oms/manifest.csv --out check_cpB.txt
```

Nếu có WARN `left_eye_outer nằm bên trái ảnh…` mà bạn đã kiểm trục y là đúng, mở file thêm một dòng ở cuối:

```bash
cat >> ~/day12-dms-oms/check_cpB.txt <<'TXT'

Giải thích cảnh báo: WARN "left_eye_outer nằm bên trái ảnh so với right_eye_outer" xuất hiện vì luật
này so theo trục x cho mặt nhìn thẳng. Ảnh D## xoay ~90°, hai mắt xếp theo trục y; đã kiểm
left_eye_* có y lớn hơn right_eye_* trên cả hai khung, nên nhãn đúng theo GUIDE §4.6.
TXT
```

Soát lại cả phần OMS đã làm (tùy chọn):
```bash
python3 scripts/cabin_check.py check part_B.zip --only S01,S02,S03,S04,S05,S06,S07,S08,D01,D02
```

## Bước 5 — Task 2b: D03–D06 (16:15)

## Bước 6 — Export cuối + tự kiểm (16:50)

Export → `export_final.zip`:

```bash
cd ~/day12-dms-oms
python3 -m zipfile -l export_final.zip                       # chỉ được thấy annotations.xml
python3 scripts/cabin_check.py check export_final.zip --expect 22 --manifest G05/oms/manifest.csv --out check_final.txt
```

Chạy đến khi dòng cuối là `Kết quả: 0 lỗi`. Mỗi WARN còn lại → thêm một dòng giải thích ở cuối `check_final.txt`.

Chạy preflight (kiểm 5 điều của SUBMISSION, tự động):

```bash
python3 ~/day12-dms-oms/tools/preflight.py
```

## Bước 7 — Review chéo (17:05)

Nhận file của bạn (USB / AirDrop / LMS — **không** phải chat), đặt tên `peer_export_final.zip`:

```bash
cd ~/day12-dms-oms
python3 scripts/cabin_check.py diff export_final.zip peer_export_final.zip --csv disagreement_log.csv
```

Mở `disagreement_log.csv`, điền **ít nhất 5 dòng** (hoặc tất cả nếu ít hơn 5): `verdict`
(`mine`/`peer`/`both_wrong`/`ambiguous`), `guideline_rule` (ví dụ `4.4-3`, `4.6`, `4.7`), `action`.
Mỗi bất đồng **phải gắn với một mục guideline** — đó là chỗ rubric chấm.
Lưu lại ở dạng **CSV UTF-8** nếu mở bằng Excel/LibreOffice.

Có sửa sau review → export lại `export_final_v2.zip`:

```bash
python3 scripts/cabin_check.py check export_final_v2.zip --expect 22 --manifest G05/oms/manifest.csv --out check_final_v2.txt
```

## Bước 8 — Task 4 + tự đánh giá (17:25)

- `class_list_v0.md`: đã có bản nháp đầy đủ → đọc lại, sửa theo ý mình, điền tên khung ví dụ thật vào 2 câu leo thang.
- `self_review.md`: §1 chọn 4 ảnh (2 S##, 2 D##) đọc lại như người lạ; §2 lỗi lặp nhiều nhất; §3 một dòng bạn đúng mình sai.
- `exit_ticket.md`: đã có đáp án nháp + lý giải → tự kiểm rồi chốt.
- `TEAM.md`: điền mã Gxx, tên bạn được ghép, số dòng disagreement đã xử lý.
- `prompts.md`: **đã khai phiên làm việc với Claude Code hôm nay** → bổ sung nếu dùng thêm.

## Bước 9 — Đóng gói + nộp

```bash
python3 ~/day12-dms-oms/tools/preflight.py --pack
```

Tạo `~/K5-L2-DAY12-NguyenQuocHung-2A202603324-DMSOMS.zip`. Nộp lên https://aithucchien.vinuni.edu.vn

Và push repo (ít nhất 2 commit cho phần của mình):

```bash
cd ~/day12-dms-oms
git add -A
git status --short          # kiểm: KHÔNG có .png/.jpg, không có G05/
git commit -m "feat(day12): nhan 22 anh cabin, checkpoint A/B, export final"
git commit --allow-empty -m "docs(day12): ir_log, class_list_v0, self_review, disagreement_log"
git push
```

## Hết khóa (không phải hôm nay)

```bash
rm -rf ~/day12-dms-oms/G*/
```
`docker compose down -v` chỉ chạy khi thật sự không cần dữ liệu CVAT nữa — nó xóa cả Day 11.
