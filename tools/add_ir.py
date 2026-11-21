#!/usr/bin/env python3
"""Thêm một dòng vào ir_log.csv mà không cần gõ CSV bằng tay.

  python3 tools/add_ir.py S01_ir object.type "túi đen lẫn vào nền ghế" "giữ bag theo hình dạng"

Tự điền cột `source` từ tên khung (S## → IR_sim, D## → real_IR) và chặn lỗi hay bị trừ điểm:
ghi hiện tượng của IR thật lên ảnh IR-sim.
"""
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_IR_WORDS = re.compile(r"chói|loá|lóa|phản xạ LED|mắt sáng|glint|glare|đèn LED", re.I)
# chỗ-trống trong hướng dẫn: <...>, [...], "...", hoặc chữ "điền"
PLACEHOLDER = re.compile(r"^\s*[<\[].*[>\]]\s*$|^\s*[.…]+\s*$|điền|bạn thấy gì", re.I)


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    frame, field, phenom, effect = sys.argv[1:]
    for label, val in (("hiện tượng", phenom), ("tác động lên nhãn", effect)):
        v = val.strip().strip(".…")
        if PLACEHOLDER.search(val) or len(v) < 15:
            print(f"DỪNG: phần '{label}' đang là \"{val}\" — chưa phải một quan sát.\n"
                  "  Thay bằng điều bạn thật sự nhìn thấy khi bật qua lại giữa ảnh _rgb và _ir.\n"
                  "  Ví dụ: \"áo tối và nền ghế cùng độ sáng, không còn thấy vùng vai để truy dải dây\"")
            return 1
    code = frame.strip().upper()
    if code.startswith("S"):
        source = "IR_sim"
        if REAL_IR_WORDS.search(phenom):
            print(f"DỪNG: '{REAL_IR_WORDS.search(phenom).group(0)}' là hiện tượng IR THẬT, "
                  f"ảnh {code} là IR mô phỏng của SVIRO (GUIDE §3). Ghi vậy sẽ bị trừ điểm.")
            return 1
        if not code.endswith("_IR"):
            print(f"CHÚ Ý: quan sát IR nên ghi cho khung '_ir' (bạn ghi {frame}).")
    elif code.startswith("D"):
        source = "real_IR"
    else:
        print(f"DỪNG: tên khung '{frame}' không phải S##_ir hay D##.")
        return 1

    p = os.path.join(ROOT, "ir_log.csv")
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        if ((r.get("frame_id") or "").strip().upper() == frame.strip().upper()
                and (r.get("affected_field") or "").strip().lower() == field.strip().lower()):
            print(f"DỪNG: đã có dòng cho {frame} · {field}.\n"
                  f"  Hiện tại: \"{r.get('phenomenon')}\"\n"
                  "  Rubric cần 4 quan sát KHÁC NHAU. Chọn khung hoặc trường nhãn khác.")
            return 1
    with open(p, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([frame, source, phenom, field, effect])
    n = sum(1 for r in csv.DictReader(open(p, encoding="utf-8-sig")) if (r.get("frame_id") or "").strip())
    print(f"Đã thêm: {frame} · {source} · {field}")
    print(f"ir_log.csv hiện có {n}/4 quan sát." + ("  ĐỦ RỒI." if n >= 4 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
