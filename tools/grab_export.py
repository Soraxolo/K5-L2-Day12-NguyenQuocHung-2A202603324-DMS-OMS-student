#!/usr/bin/env python3
"""Lấy file export CVAT mới nhất từ ~/Downloads vào repo với tên đúng.

  python3 tools/grab_export.py part_A          # -> ./part_A.zip
  python3 tools/grab_export.py export_final    # -> ./export_final.zip
  python3 tools/grab_export.py part_B --dry-run

Kiểm luôn ba điều trước khi chép: là zip CVAT thật (có annotations.xml), KHÔNG kèm ảnh
(RULES §2), và đếm số ảnh trong XML để biết export đủ task chưa.
"""
import argparse
import glob
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.join(os.path.expanduser("~"), "Downloads")
IMG = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
ALLOWED = {"part_A", "part_B", "export_final", "export_final_v2", "export_extra", "peer_export_final"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="tên đích, không cần .zip: " + ", ".join(sorted(ALLOWED)))
    ap.add_argument("--from", dest="src", help="chỉ định thẳng file nguồn thay vì tìm trong ~/Downloads")
    ap.add_argument("--downloads", default=DL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    name = re.sub(r"\.zip$", "", args.name)
    if name not in ALLOWED:
        print(f"LỖI: tên '{name}' không nằm trong danh sách SUBMISSION: {', '.join(sorted(ALLOWED))}")
        return 1

    if args.src:
        src = args.src
    else:
        cand = sorted(glob.glob(os.path.join(args.downloads, "*.zip")), key=os.path.getmtime, reverse=True)
        cand = [c for c in cand if "learner_bundles" not in os.path.basename(c)]
        if not cand:
            print(f"LỖI: không thấy file .zip nào trong {args.downloads}")
            return 1
        src = cand[0]
    if not os.path.exists(src):
        print(f"LỖI: không thấy {src}")
        return 1

    print(f"Nguồn: {os.path.basename(src)}  ({os.path.getsize(src)/1024:.0f} KB)")
    if not zipfile.is_zipfile(src):
        print("LỖI: không phải zip hợp lệ")
        return 1
    z = zipfile.ZipFile(src)
    inner = [n for n in z.namelist() if not n.endswith("/")]
    imgs = [n for n in inner if n.lower().endswith(IMG)]
    xmls = [n for n in inner if n.endswith(".xml")]
    print(f"Bên trong: {', '.join(os.path.basename(n) for n in inner[:5])}"
          + (f" … (+{len(inner)-5})" if len(inner) > 5 else ""))
    if imgs:
        print(f"DỪNG: có {len(imgs)} file ảnh trong zip. Export lại và BỎ CHỌN \"Save images\" (RULES §2).")
        return 1
    if not xmls:
        print("DỪNG: không có annotations.xml — sai định dạng, phải là 'CVAT for images 1.1'.")
        return 1

    root = ET.fromstring(z.read(xmls[0]))
    images = root.findall("image")
    done = [i for i in images if any(t.get("label") == "frame_meta" for t in i.findall("tag"))]
    names = sorted(os.path.splitext(i.get("name", "").split("/")[-1])[0] for i in images)
    print(f"XML: {len(images)} ảnh trong task · {len(done)} ảnh đã có tag frame_meta")
    todo = [n for n in names if n not in {os.path.splitext(os.path.basename(i.get('name','')))[0] for i in done}]
    if todo:
        print(f"  chưa gán ({len(todo)}): {', '.join(todo[:12])}" + (" …" if len(todo) > 12 else ""))
    print("  CVAT luôn export cả task → ở checkpoint nhớ dùng --only cho đúng phạm vi đã gán.")
    foreign = [n for n in names if not re.fullmatch(r"(S\d{2}_(rgb|ir)|D\d{2})", n)]
    if foreign:
        print(f"DỪNG: {len(foreign)} ảnh không phải tên của Ngày 12 ({', '.join(foreign[:4])}…).\n"
              "  Đây là export của task khác (ví dụ Ngày 11). Chọn đúng task Day12-Gxx rồi export lại,\n"
              "  hoặc chỉ định thẳng file bằng --from <duong/dan.zip>.")
        return 1

    dest = os.path.join(ROOT, name + ".zip")
    if args.dry_run:
        print(f"\n--dry-run: sẽ chép → {dest}")
        return 0
    shutil.copy2(src, dest)
    print(f"\nĐã chép → {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
