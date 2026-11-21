#!/usr/bin/env python3
"""Sinh hai file export GIẢ để chạy thử cabin_check trước khi gán bài thật.

  python3 tools/make_demo_export.py            # ghi vào tools/demo/
  python3 tools/make_demo_export.py --run      # ghi rồi chạy cabin_check lên cả hai file

Dùng để làm gì:
  1. Xác nhận cabin_check.py chạy được trên máy này (Python 3.12, tiếng Việt không lỗi font).
  2. Thấy trước mặt chữ của từng loại [ERROR] / [WARN] để trong buổi nhận ra ngay.

KHÔNG DÙNG ĐỂ NỘP. Toạ độ ở đây là số bịa, sinh bằng công thức, không nhìn ảnh nào — nó không
chứa thông tin gì về ảnh thật. Tên ảnh bên trong để đúng dạng S##_rgb.png / D##.png vì cabin_check
nhận ảnh SVIRO bằng chính mẫu tên đó (xem ghi chú 'tên ảnh' ở notes/RULE_CARD.md §8); nhưng file
nằm trong tools/demo/ (bị .gitignore chặn, preflight không đóng gói) và tên file là DEMO_*.xml.
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo")

FACE13 = ["left_eye_outer", "left_eye_inner", "left_eye_upper", "left_eye_lower",
          "right_eye_outer", "right_eye_inner", "right_eye_upper", "right_eye_lower",
          "nose_tip", "mouth_left", "mouth_right", "lip_upper", "lip_lower"]


def tag(label, **attrs):
    a = "".join(f'\n      <attribute name="{k}">{v}</attribute>' for k, v in attrs.items())
    return f'    <tag label="{label}" source="manual">{a}\n    </tag>\n'


def box(label, xyxy, **attrs):
    x1, y1, x2, y2 = xyxy
    a = "".join(f'\n      <attribute name="{k}">{v}</attribute>' for k, v in attrs.items())
    return (f'    <box label="{label}" occluded="0" xtl="{x1:.2f}" ytl="{y1:.2f}" '
            f'xbr="{x2:.2f}" ybr="{y2:.2f}" z_order="0">{a}\n    </box>\n')


def skeleton(cx, cy, hidden=(), flip=False):
    """13 điểm quanh (cx, cy) theo bố cục ảnh D## xoay 90°: trục hai mắt chạy dọc theo y,
    mắt trái của người có y LỚN hơn. `flip` cố tình đảo để thấy mặt chữ cảnh báo."""
    s = -1 if flip else 1
    pos = {
        "right_eye_outer": (cx + 34, cy - 30 * s), "right_eye_inner": (cx + 14, cy - 28 * s),
        "right_eye_upper": (cx + 26, cy - 38 * s), "right_eye_lower": (cx + 22, cy - 18 * s),
        "left_eye_outer": (cx + 36, cy + 30 * s), "left_eye_inner": (cx + 16, cy + 28 * s),
        "left_eye_upper": (cx + 28, cy + 38 * s), "left_eye_lower": (cx + 24, cy + 18 * s),
        "nose_tip": (cx - 6, cy + 2), "mouth_left": (cx - 34, cy + 16 * s),
        "mouth_right": (cx - 34, cy - 16 * s), "lip_upper": (cx - 30, cy), "lip_lower": (cx - 42, cy),
    }
    out = '    <skeleton label="face13" source="manual" z_order="0">\n'
    for p in FACE13:
        x, y = pos[p]
        occ = "1" if p in hidden else "0"
        out += (f'      <points label="{p}" occluded="{occ}" outside="0" source="manual" '
                f'points="{x:.2f},{y:.2f}"></points>\n')
    return out + "    </skeleton>\n"


def sviro_frame(code, mod, broken=False):
    """Cảnh SVIRO giả: 1 người ghế trái ảnh (= rear_right theo xe) + 1 túi ghế phải ảnh (= rear_left)."""
    # broken: 3 cảnh báo đặc trưng của ảnh SVIRO + 1 thuộc tính bỏ trống
    b = tag("frame_meta", modality=mod, light="day" if broken else "unknown", camera_blocked="no")
    b += box("person", (210, 240, 520, 780), seat="driver" if broken else "rear_right",
             seatbelt="worn_correct" if broken else "not_worn")
    b += box("face", (300, 280, 420, 420), eye_left="unknown", eye_right="unknown",
             glasses="unknown", gaze_zone="other")
    b += box("object", (820, 420, 1010, 600), seat="rear_left", type="" if broken else "bag")
    b += box("child_seat", (560, 330, 760, 700), seat="rear_middle", occupied="no")
    if broken and mod == "ir":
        b += box("object", (830, 430, 1000, 590), seat="rear_left", type="other")  # gộp 2 box 1 ghế
    return b


def driver_frame(code, broken=False):
    b = tag("frame_meta", modality="ir", light="night", camera_blocked="no")
    b += box("person", (380, 180, 1000, 1180), seat="driver", seatbelt="unknown")
    if broken:
        # mặt 48 px: dưới ngưỡng 60 px nhưng vẫn vẽ face13 -> ERROR
        b += box("face", (742, 520, 790, 580), eye_left="closed", eye_right="unknown",
                 glasses="none", gaze_zone="road")
        b += skeleton(766, 550, hidden=tuple(p for p in FACE13 if p.startswith("left_eye")), flip=True)
        b += box("hand", (520, 700, 640, 820), whose="driver", side="left", on_wheel="no")
        b += box("hand", (560, 900, 680, 1020), whose="driver", side="left", on_wheel="no")
        b += box("phone", (600, 980, 660, 1060))  # thiếu thuộc tính state
    else:
        b += box("face", (660, 420, 880, 700), eye_left="open", eye_right="unknown",
                 glasses="clear", gaze_zone="road")
        b += skeleton(770, 560, hidden=("right_eye_outer", "right_eye_inner",
                                        "right_eye_upper", "right_eye_lower"))
        b += box("hand", (520, 700, 640, 820), whose="driver", side="left", on_wheel="no")
        b += box("hand", (540, 920, 660, 1040), whose="driver", side="right", on_wheel="no")
    return b


def build(broken):
    out = ['<?xml version="1.0" encoding="utf-8"?>\n<annotations>\n  <version>1.1</version>\n']
    out.append("  <!-- FILE GIAU LAP DE CHAY THU cabin_check. KHONG PHAI BAI NOP. -->\n")
    for i in range(1, 9):
        for mod in ("rgb", "ir"):
            name = f"S{i:02d}_{mod}.png"
            out.append(f'  <image id="{len(out)}" name="{name}" width="1280" height="960">\n')
            out.append(sviro_frame(f"S{i:02d}", mod, broken and i == 1))
            out.append("  </image>\n")
    for i in range(1, 7):
        name = f"D{i:02d}.png"
        out.append(f'  <image id="{len(out)}" name="{name}" width="1280" height="1280">\n')
        out.append(driver_frame(f"D{i:02d}", broken and i == 1))
        out.append("  </image>\n")
    out.append("</annotations>\n")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="store_true", help="chạy cabin_check lên hai file vừa sinh")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    paths = {}
    for kind, broken in (("clean", False), ("errors", True)):
        p = os.path.join(OUT, f"DEMO_{kind}.xml")
        open(p, "w", encoding="utf-8").write(build(broken))
        paths[kind] = p
        print(f"đã ghi {os.path.relpath(p, ROOT)}")
    if args.run:
        for kind, p in paths.items():
            print("\n" + "=" * 70 + f"\n{kind.upper()}" +
                  ("  — phải ra 0 lỗi, 0 cảnh báo" if kind == "clean" else
                   "  — cố tình sai, để xem mặt chữ từng lỗi") + "\n" + "=" * 70, flush=True)
            subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "cabin_check.py"),
                            "check", p, "--expect", "22"])


if __name__ == "__main__":
    main()
