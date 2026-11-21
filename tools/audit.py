#!/usr/bin/env python3
"""Soát những lỗi cabin_check KHÔNG bắt được (RULE_CARD §8).

  python3 tools/audit.py export_final.zip

1. face13 trên ảnh D## xoay 90°: left_eye_* phải có y lớn hơn right_eye_*
   (y bằng nhau = template chưa xoay — COMMON_ERRORS mục "face13 nằm thẳng đứng")
2. Cặp _rgb/_ir cùng cảnh lệch nhãn hoặc thuộc tính
3. Ảnh S## có person nhưng thiếu box face (GUIDE §4.2)
4. Nhãn dùng sai phạm vi (object trên D##, hand trên S##…)
5. Bề rộng box face trên D## so với ngưỡng 60 px của face13
"""
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

OMS = {"person", "face", "object", "child_seat", "infant_seat"}
DMS = {"person", "face", "face13", "hand", "phone"}
MIN_W = 60
bad = 0


def A(el):
    return {a.get("name"): (a.text or "").strip() for a in el.findall("attribute")}


def say(msg, is_bad=True):
    global bad
    bad += is_bad
    print(("  ✗ " if is_bad else "  · ") + msg)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "export_final.zip"
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    src = zipfile.ZipFile(path).read("annotations.xml") if zipfile.is_zipfile(path) else open(path, "rb").read()
    I = {os.path.splitext(os.path.basename(i.get("name", "")))[0]: i for i in ET.fromstring(src).findall("image")}

    print(f"AUDIT {path} — {len(I)} ảnh\n")
    print("1. face13 trên ảnh xoay 90°")
    for n, i in sorted(I.items()):
        for sk in i.findall("skeleton"):
            p = {q.get("label"): (float(q.get("points").split(",")[1]) if q.get("points") else None)
                 for q in sk.findall("points")}
            L = [v for k, v in p.items() if k.startswith("left_eye") and v is not None]
            R = [v for k, v in p.items() if k.startswith("right_eye") and v is not None]
            if not (L and R):
                continue
            ml, mr = sum(L) / len(L), sum(R) / len(R)
            if ml > mr + 1:
                say(f"{n}: left y={ml:.0f} > right y={mr:.0f}", False)
            elif abs(ml - mr) <= 1:
                say(f"{n}: hai mắt cùng y ({ml:.0f}) — template CHƯA XOAY theo ảnh (GUIDE §4.6)")
            else:
                say(f"{n}: left y={ml:.0f} < right y={mr:.0f} — LẬT trái/phải (GUIDE §4.4-2)")

    print("\n2. cặp _rgb / _ir")
    for k in [f"S{i:02d}" for i in range(1, 11)]:
        a, b = I.get(k + "_rgb"), I.get(k + "_ir")
        if a is None or b is None:
            continue
        msgs = []
        ta = A(a.findall("tag")[0]) if a.findall("tag") else {}
        tb = A(b.findall("tag")[0]) if b.findall("tag") else {}
        for key in ("light", "camera_blocked"):
            if ta.get(key) != tb.get(key):
                msgs.append(f"frame_meta.{key}: rgb={ta.get(key)} ir={tb.get(key)}")
        sig = lambda im: sorted((x.get("label"), tuple(sorted(A(x).items()))) for x in im.findall("box"))
        sa, sb = sig(a), sig(b)
        if len(sa) != len(sb):
            msgs.append(f"số box khác: rgb={len(sa)} ir={len(sb)}")
        else:
            for (la, aa), (lb, ab) in zip(sa, sb):
                if la != lb:
                    msgs.append(f"nhãn khác: rgb={la} ir={lb}")
                else:
                    d = {x: (dict(aa).get(x), dict(ab).get(x)) for x in dict(aa)
                         if dict(aa).get(x) != dict(ab).get(x)}
                    if d:
                        msgs.append(f"{la}: " + ", ".join(f"{x} rgb={v[0]} ir={v[1]}" for x, v in d.items()))
        for m in msgs:
            say(f"{k}: {m}")

    print("\n3. ảnh S## thiếu box face cho người lớn")
    for n, i in sorted(I.items()):
        if not n.startswith("S"):
            continue
        np_ = sum(1 for b in i.findall("box") if b.get("label") == "person")
        nf = sum(1 for b in i.findall("box") if b.get("label") == "face")
        if np_ != nf:
            say(f"{n}: person={np_} nhưng face={nf} (GUIDE §4.2)")

    print("\n4. nhãn dùng sai phạm vi")
    for n, i in sorted(I.items()):
        used = {b.get("label") for b in i.findall("box")} | {s.get("label") for s in i.findall("skeleton")}
        wrong = used - (OMS if n.startswith("S") else DMS)
        if wrong:
            say(f"{n}: {', '.join(sorted(wrong))} không được dùng trên ảnh này")

    print("\n5. ngưỡng 60 px của face13 (ảnh D##)")
    for n, i in sorted(I.items()):
        if not n.startswith("D"):
            continue
        for b in i.findall("box"):
            if b.get("label") != "face":
                continue
            w = float(b.get("xbr")) - float(b.get("xtl"))
            has = len(i.findall("skeleton")) > 0
            if (w >= MIN_W) != has:
                say(f"{n}: face rộng {w:.0f} px nhưng {'KHÔNG có' if not has else 'lại có'} face13")
            else:
                say(f"{n}: face {w:.0f} px, {'có' if has else 'không'} face13", False)

    print(f"\n{'='*60}\n{bad} chỗ cần xử lý (script cabin_check không bắt được những chỗ này).")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
