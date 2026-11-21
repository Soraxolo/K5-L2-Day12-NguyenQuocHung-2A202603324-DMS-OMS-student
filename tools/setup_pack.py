#!/usr/bin/env python3
"""Bước 0: giải nén gói ảnh của mã mình vào repo và điền mã vào các file nộp.

  python3 tools/setup_pack.py G05            # giải nén + điền mã + in 22 ảnh cốt lõi
  python3 tools/setup_pack.py G05 --dry-run  # chỉ kiểm, không ghi gì

Gói ảnh nằm ở ~/day12-bundles/<Gxx>.zip (giải nén từ bundle coach phát).
Script KHÔNG mở ảnh, chỉ đọc tên file và manifest.csv.
"""
import argparse
import csv
import io
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLES = os.path.join(os.path.expanduser("~"), "day12-bundles")
PLACEHOLDER_FILES = ["TEAM.md", "class_list_v0.md", "self_review.md", "exit_ticket.md", "prompts.md"]
CORE_OMS = [f"S{i:02d}_{m}.png" for i in range(1, 9) for m in ("rgb", "ir")]
CORE_DRIVER = [f"D{i:02d}.png" for i in range(1, 7)]
EXTRA_OMS = [f"S{i:02d}_{m}.png" for i in (9, 10) for m in ("rgb", "ir")]


def fail(msg):
    print(f"LỖI: {msg}")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("code", help="mã bộ ảnh coach giao, ví dụ G05")
    ap.add_argument("--bundles", default=BUNDLES, help=f"thư mục chứa Gxx.zip (mặc định {BUNDLES})")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    code = args.code.strip().upper()
    if not re.fullmatch(r"G\d{2}", code):
        fail(f"mã '{args.code}' không đúng dạng Gxx (G01…G12)")
    zpath = os.path.join(args.bundles, f"{code}.zip")
    if not os.path.exists(zpath):
        have = sorted(f[:-4] for f in os.listdir(args.bundles) if f.endswith(".zip")) \
            if os.path.isdir(args.bundles) else []
        fail(f"không thấy {zpath}. Các mã có trong {args.bundles}: {', '.join(have) or '(không có)'}")

    z = zipfile.ZipFile(zpath)
    names = [n for n in z.namelist() if not n.endswith("/")]
    base = {os.path.basename(n): n for n in names}

    # 1. kiểm gói đủ chưa
    miss = [f for f in CORE_OMS + CORE_DRIVER if f not in base]
    if miss:
        fail(f"gói {code} thiếu {len(miss)} ảnh cốt lõi: {miss}")
    print(f"Gói {code}: {len(CORE_OMS)} ảnh OMS cốt lõi + {len(CORE_DRIVER)} ảnh DMS = "
          f"{len(CORE_OMS) + len(CORE_DRIVER)} ảnh. Phần mở rộng: "
          f"{len([f for f in EXTRA_OMS if f in base])} ảnh (S09–S10).")

    # 2. đọc manifest để biết xe nào -> rear_middle có hợp lệ không
    mf = next((n for n in names if n.endswith("oms/manifest.csv")), None)
    if not mf:
        print("CẢNH BÁO: gói không có oms/manifest.csv — cabin_check sẽ phải dựa vào mẫu tên ảnh")
    else:
        rows = list(csv.DictReader(io.StringIO(z.read(mf).decode("utf-8-sig"))))
        cars = sorted({(r.get("car") or "").lower() for r in rows if r.get("car")})
        print(f"Xe trong manifest: {', '.join(cars)}", end="  ")
        if cars == ["x5"]:
            print("→ BMW X5, có đủ 3 ghế sau, `rear_middle` HỢP LỆ")
        elif {"i3", "zoe"} & set(cars):
            print("→ ⚠ có xe chỉ 2 ghế sau: KHÔNG dùng `rear_middle` cho các cảnh đó")
        else:
            print("→ kiểm lại GUIDE §3 trước khi dùng `rear_middle`")

    if args.dry_run:
        print("\n--dry-run: không ghi gì.")
        return

    # 3. giải nén vào repo
    dest = os.path.join(ROOT, code)
    if os.path.exists(dest):
        print(f"\n{code}/ đã có trong repo, bỏ qua bước giải nén (xoá trước nếu muốn làm lại).")
    else:
        z.extractall(ROOT)
        print(f"\nĐã giải nén → {dest}")
    if not os.path.isdir(dest):
        fail(f"sau khi giải nén vẫn không thấy {dest}")

    # 4. điền mã vào các file nộp
    changed = []
    for fn in PLACEHOLDER_FILES:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8").read()
        new = re.sub(r"\bGxx\b", code, txt)
        if new != txt:
            open(p, "w", encoding="utf-8").write(new)
            changed.append(fn)
    print(f"Đã điền mã {code} vào: {', '.join(changed) or '(không có chỗ nào còn Gxx)'}")

    # 5. ảnh phải bị git chặn
    try:
        out = subprocess.run(["git", "-C", ROOT, "status", "--short", "--untracked-files=all"],
                             capture_output=True, text=True).stdout
        leak = [l for l in out.splitlines() if re.search(r"\.(png|jpg|jpeg)$", l, re.I)]
        print("git: " + (f"⚠ {len(leak)} ảnh KHÔNG bị .gitignore chặn: {leak[:3]}"
                         if leak else "không ảnh nào lọt vào git ✓"))
    except FileNotFoundError:
        pass

    # 5b. gom 22 ảnh cốt lõi vào một thư mục bằng hardlink (chọn 1 lần trong CVAT)
    core = os.path.join(dest, "core22")
    os.makedirs(core, exist_ok=True)
    made = 0
    for sub, files in (("oms", CORE_OMS), ("driver", CORE_DRIVER)):
        for f in files:
            src_f, dst_f = os.path.join(dest, sub, f), os.path.join(core, f)
            if os.path.exists(dst_f):
                continue
            try:
                os.link(src_f, dst_f)       # hardlink: không tốn thêm đĩa
            except OSError:
                shutil.copy2(src_f, dst_f)  # khác filesystem thì đành copy
            made += 1
    n_core = len([f for f in os.listdir(core) if f.endswith(".png")])
    print(f"{code}/core22/: {n_core} ảnh (tạo mới {made}) — chọn cả thư mục này trong CVAT là đủ 22 ảnh, "
          f"không lẫn S09/S10 hay manifest.csv")

    # 6. in đúng 22 đường dẫn để chọn trong CVAT
    print(f"\n22 ảnh CỐT LÕI cần chọn khi tạo task `Day12-{code}` (dán vào ô tìm hoặc chọn tay):")
    for f in CORE_OMS:
        print(f"  {code}/oms/{f}")
    for f in CORE_DRIVER:
        print(f"  {code}/driver/{f}")
    print(f"\nKHÔNG chọn: {', '.join(EXTRA_OMS)} (phần mở rộng, task riêng `Day12-{code}-extra`), "
          f"và KHÔNG chọn manifest.csv.")

    print("\nLệnh checkpoint cho mã của bạn:")
    m = f"{code}/oms/manifest.csv"
    print(f"  python3 scripts/cabin_check.py check part_A.zip --only S01,S02 --expect 4 "
          f"--manifest {m} --out check_cpA.txt")
    print(f"  python3 scripts/cabin_check.py check part_B.zip --only D01,D02 --expect 2 "
          f"--manifest {m} --out check_cpB.txt")
    print(f"  python3 scripts/cabin_check.py check export_final.zip --expect 22 "
          f"--manifest {m} --out check_final.txt")
    print(f"\nLuôn truyền --manifest {m} (không phải {code}/driver/manifest.csv — file đó không có cột `car`).")
    print("Dùng scripts/ của repo, KHÔNG dùng " + code + "/scripts/ (bản cũ đi kèm gói).")


if __name__ == "__main__":
    main()
