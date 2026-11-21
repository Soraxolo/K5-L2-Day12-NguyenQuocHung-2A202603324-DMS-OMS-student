#!/usr/bin/env python3
"""Preflight cho bài nộp Ngày 12: kiểm 5 điều của SUBMISSION.md + các yêu cầu E1–E5, rồi đóng gói.

  python3 tools/preflight.py              # chỉ kiểm, không sửa gì
  python3 tools/preflight.py --pack       # kiểm rồi tạo zip nộp (dừng nếu còn FAIL)
  python3 tools/preflight.py --pack --force   # đóng gói kể cả khi còn FAIL (dùng khi nộp muộn, thiếu phần)

Chỉ dùng thư viện chuẩn. Script này KHÔNG sửa nhãn và KHÔNG tạo bằng chứng thay bạn.
"""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import zipfile

NAME = "NguyenQuocHung"
MSSV = "2A202603324"
FOLDER = f"K5-L2-DAY12-{NAME}-{MSSV}-DMSOMS"

REQUIRED = [
    ("export_final.zip", "E1 export CVAT for images 1.1, không kèm ảnh"),
    ("check_cpA.txt", "E2 Checkpoint A"),
    ("check_cpB.txt", "E2 Checkpoint B"),
    ("check_final.txt", "E2 lần cuối, phải 0 lỗi"),
    ("disagreement_log.csv", "E3 review chéo"),
    ("ir_log.csv", "E4 quan sát IR"),
    ("class_list_v0.md", "E5 danh sách lớp"),
    ("self_review.md", "tự đánh giá"),
    ("exit_ticket.md", "exit ticket"),
    ("TEAM.md", "ai review ai"),
    ("prompts.md", "khai báo dùng AI"),
]
OPTIONAL = ["export_final_v2.zip", "check_final_v2.txt", "export_extra.zip", "check_extra.txt"]
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []


def say(level, msg, hint=""):
    results.append((level, msg, hint))


def check_present():
    for fn, what in REQUIRED:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            say("FAIL", f"thiếu {fn} ({what})")
        elif os.path.getsize(p) == 0:
            say("FAIL", f"{fn} rỗng")
        else:
            say("OK", f"có {fn}")
    for fn in OPTIONAL:
        if os.path.exists(os.path.join(ROOT, fn)):
            say("INFO", f"có thêm {fn}")


def check_zip(fn):
    """SUBMISSION điều 1 + 4: zip chỉ chứa annotations.xml."""
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p):
        return
    if not zipfile.is_zipfile(p):
        say("FAIL", f"{fn} không phải file zip hợp lệ", "export lại từ CVAT, đừng đổi tên file khác thành .zip")
        return
    with zipfile.ZipFile(p) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
    bad = [n for n in names if n.lower().endswith(IMAGE_EXT)]
    if bad:
        say("FAIL", f"{fn} có {len(bad)} file ảnh ({bad[:3]}…)",
            'export lại và BỎ CHỌN "Save images" (RULES §2: ảnh không ra khỏi máy)')
    if any(os.path.basename(n).lower() == "manifest.csv" for n in names):
        say("FAIL", f"{fn} có manifest.csv", "SUBMISSION điều 4: không kèm manifest")
    if not any(n.endswith(".xml") for n in names):
        say("FAIL", f"{fn} không có annotations.xml", "sai định dạng export; phải là CVAT for images 1.1")
    mb = os.path.getsize(p) / 1e6
    if mb > 5:
        say("WARN", f"{fn} nặng {mb:.1f} MB", "export đúng chỉ vài chục KB — nghi còn kèm ảnh")
    if not bad:
        say("OK", f"{fn}: chỉ có {', '.join(sorted(set(os.path.basename(n) for n in names)))} ({mb*1000:.0f} KB)")


def check_final_txt(fn="check_final.txt"):
    """SUBMISSION điều 2: dòng 'Kết quả: 0 lỗi'."""
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p):
        return
    txt = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"Kết quả:\s*(\d+)\s*lỗi,\s*(\d+)\s*cảnh báo", txt)
    if not m:
        say("FAIL", f"{fn} không có dòng 'Kết quả: N lỗi'",
            "chạy lại bằng scripts/cabin_check.py ... --out " + fn)
        return
    err, warn = int(m.group(1)), int(m.group(2))
    if err:
        say("FAIL", f"{fn}: còn {err} lỗi", "sửa trên CVAT, export lại, chạy lại cabin_check")
    else:
        say("OK", f"{fn}: 0 lỗi")
    if warn:
        after = txt[m.end():].strip()
        if len(after) < 40:
            say("FAIL", f"{fn}: còn {warn} cảnh báo nhưng không có dòng giải thích ở cuối file",
                "RUBRIC E2: mỗi WARN còn lại cần 1 dòng giải thích — mở file và gõ thêm")
        else:
            say("OK", f"{fn}: {warn} cảnh báo, có phần giải thích ở cuối ({len(after)} ký tự)")
    nimg = re.search(r"Ảnh:\s*(\d+)\s*·\s*đã có frame_meta:\s*(\d+)", txt)
    if nimg:
        a, b = int(nimg.group(1)), int(nimg.group(2))
        if a != 22:
            say("WARN", f"{fn}: {a} ảnh (mong đợi 22)", "task chính chỉ gồm 22 ảnh cốt lõi")
        if a != b:
            say("FAIL", f"{fn}: {a} ảnh nhưng chỉ {b} ảnh có frame_meta")
        else:
            say("OK", f"{fn}: {a}/{b} ảnh có frame_meta")


def _rows(fn):
    p = os.path.join(ROOT, fn)
    if not os.path.exists(p):
        return None
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def check_ir_log():
    rows = _rows("ir_log.csv")
    if rows is None:
        return
    data = [r for r in rows if (r.get("frame_id") or "").strip()
            and "(ví dụ)" not in (r.get("phenomenon") or "")]
    if len(data) < 4:
        say("FAIL", f"ir_log.csv có {len(data)} quan sát thật, cần ≥ 4",
            "xem notes/ir_log_checklist.md để biết tìm gì")
    else:
        say("OK", f"ir_log.csv: {len(data)} quan sát")
    for r in data:
        fid = (r.get("frame_id") or "").strip().upper()
        src = (r.get("source") or "").strip()
        if src not in ("IR_sim", "real_IR"):
            say("FAIL", f"ir_log.csv {fid}: source='{src}' không hợp lệ", "chỉ IR_sim (S##) hoặc real_IR (D##)")
        elif fid.startswith("S") and src != "IR_sim":
            say("FAIL", f"ir_log.csv {fid}: ảnh S## phải là IR_sim", "RUBRIC: không lẫn IR-sim với IR thật")
        elif fid.startswith("D") and src != "real_IR":
            say("FAIL", f"ir_log.csv {fid}: ảnh D## phải là real_IR")
        if not (r.get("affected_field") or "").strip():
            say("FAIL", f"ir_log.csv {fid}: thiếu affected_field", "mỗi dòng phải chỉ ra một trường nhãn")
        if not (r.get("effect_on_label") or "").strip():
            say("WARN", f"ir_log.csv {fid}: thiếu effect_on_label")
    sim = [r for r in data if (r.get("source") or "") == "IR_sim"]
    real = [r for r in data if (r.get("source") or "") == "real_IR"]
    if data and (not sim or not real):
        say("WARN", f"ir_log.csv: {len(sim)} dòng IR_sim, {len(real)} dòng real_IR",
            "nên có cả hai loại: rubric chấm việc tách IR-sim với IR thật")
    for r in sim:
        bad = re.search(r"chói|loá|lóa|phản xạ LED|mắt sáng|glare", (r.get("phenomenon") or ""), re.I)
        if bad:
            say("FAIL", f"ir_log.csv {r.get('frame_id')}: ghi hiện tượng IR thật ('{bad.group(0)}') lên ảnh IR-sim",
                "S##_ir là ảnh mô phỏng, không có phản xạ LED thật (GUIDE §3)")


def check_disagreement():
    rows = _rows("disagreement_log.csv")
    if rows is None:
        return
    if not rows:
        say("FAIL", "disagreement_log.csv không có dòng nào", "chạy cabin_check.py diff với file của bạn")
        return
    done = [r for r in rows if (r.get("verdict") or "").strip()
            and (r.get("guideline_rule") or "").strip() and (r.get("action") or "").strip()]
    need = min(5, len(rows))
    if len(done) < need:
        say("FAIL", f"disagreement_log.csv: {len(done)}/{len(rows)} dòng đã xử lý, cần ≥ {need}",
            "điền verdict + guideline_rule + action")
    else:
        say("OK", f"disagreement_log.csv: {len(done)}/{len(rows)} dòng đã xử lý")
    for r in done:
        v = (r.get("verdict") or "").strip()
        if v not in ("mine", "peer", "both_wrong", "ambiguous"):
            say("WARN", f"disagreement_log.csv {r.get('image')}: verdict='{v}' lạ",
                "dùng mine / peer / both_wrong / ambiguous")
        if not re.match(r"^\d\.\d", (r.get("guideline_rule") or "").strip()):
            say("WARN", f"disagreement_log.csv {r.get('image')}: guideline_rule='{r.get('guideline_rule')}'",
                "RUBRIC: mỗi bất đồng gắn với một mục guideline, ví dụ 4.4-3 hoặc 4.6")


def check_class_list():
    p = os.path.join(ROOT, "class_list_v0.md")
    if not os.path.exists(p):
        return
    txt = open(p, encoding="utf-8").read()
    if "| ví dụ |" in txt:
        say("FAIL", "class_list_v0.md còn dòng 'ví dụ' của mẫu", "xóa 2 dòng ví dụ trước khi nộp")
    secs = re.split(r"^## ", txt, flags=re.M)
    for key, label in (("DMS", "DMS"), ("OMS", "OMS")):
        sec = next((s for s in secs if s.startswith(key)), None)
        if not sec:
            say("FAIL", f"class_list_v0.md thiếu mục {label}")
            continue
        n = len([l for l in sec.splitlines()
                 if re.match(r"^\|\s*\d+\s*\|", l) and len([c for c in l.split("|") if c.strip()]) >= 4])
        if n < 6:
            say("FAIL", f"class_list_v0.md: {label} có {n} lớp điền đủ, cần ≥ 6")
        else:
            say("OK", f"class_list_v0.md: {label} {n} lớp")
    qs = re.findall(r"Khung ví dụ:\s*(.*)", txt)
    filled = [q for q in qs if q.strip() and "điền" not in q and q.strip() not in ("…", "...")]
    if len(filled) < 2:
        say("FAIL", f"class_list_v0.md: {len(filled)}/2 câu leo thang có khung ví dụ thật",
            "RUBRIC E5: mỗi câu hỏi phải có khung ví dụ")
    else:
        say("OK", f"class_list_v0.md: {len(filled)} câu leo thang có khung ví dụ")


def check_placeholders():
    pats = [(r"\bGxx\b", "Gxx chưa thay bằng mã thật"),
            (r"<tên bạn coach ghép>|<số dòng>|<HoVaTen>|<MSSV>|<Họ tên>", "còn chỗ trống dạng <…>"),
            (r"(?::\s*|^\s*(?:-\s*)?)(?:…|\.\.\.)\s*$", "còn chỗ '…' chưa điền")]
    for fn in ("TEAM.md", "class_list_v0.md", "self_review.md", "exit_ticket.md", "ir_log.csv"):
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8", errors="replace").read()
        for pat, why in pats:
            if re.search(pat, txt, re.M):
                say("WARN", f"{fn}: {why}")
    p = os.path.join(ROOT, "self_review.md")
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
        blank = re.findall(r"^(Lỗi|Vì sao mình mắc|Lần sau tránh bằng cách|Một dòng bạn.*?)"
                           r":\s*(?:…|\.\.\.)?\s*$", txt, re.M)
        if blank:
            say("FAIL", f"self_review.md: {len(blank)} ý còn trống ({', '.join(b[:28] for b in blank)})",
                "RUBRIC: nêu 1 lỗi mình lặp lại và cách tránh (mục 2), và 1 dòng bạn đúng mình sai (mục 3)")
        rows = [l for l in txt.splitlines() if re.match(r"^\|\s*[SD]\d", l)]
        filled = [l for l in rows if len([c for c in l.split("|") if c.strip()]) >= 4
                  and "?" not in l.split("|")[1]]
        if len(filled) < 4:
            say("FAIL", f"self_review.md: bảng rà soát 4 cảnh điền {len(filled)}/4 dòng",
                "chọn 2 ảnh S## và 2 ảnh D##, ghi loại lỗi (hoặc ok) cho từng đối tượng")


def check_no_images_in_repo():
    """RULES §2 + SUBMISSION điều 4."""
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "ir_pairs")]
        rel = os.path.relpath(dirpath, ROOT)
        for fn in filenames:
            if fn.lower().endswith(IMAGE_EXT):
                found.append(os.path.join(rel, fn))
    if found:
        say("INFO", f"có {len(found)} file ảnh trong thư mục làm việc (bị .gitignore chặn, và preflight "
                    f"không đóng gói chúng): {found[:2]}…")
    if os.path.exists(os.path.join(ROOT, ".git")):
        try:
            out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True).stdout
            tracked = [l for l in out.splitlines() if l.lower().endswith(IMAGE_EXT)]
            if tracked:
                say("FAIL", f"git đang theo dõi {len(tracked)} file ảnh: {tracked[:3]}",
                    "RULES §2: git rm --cached các file này ngay")
            else:
                say("OK", "git không theo dõi file ảnh nào")
        except FileNotFoundError:
            pass


def do_pack(force):
    fails = [r for r in results if r[0] == "FAIL"]
    if fails and not force:
        print(f"\nKhông đóng gói: còn {len(fails)} FAIL. Sửa rồi chạy lại, hoặc thêm --force.")
        return 1
    dest = os.path.join(os.path.expanduser("~"), FOLDER)
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    n = 0
    for fn in [f for f, _ in REQUIRED] + OPTIONAL:
        src = os.path.join(ROOT, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest, fn))
            n += 1
    zpath = dest + ".zip"
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(dest)):
            z.write(os.path.join(dest, fn), f"{FOLDER}/{fn}")
    inside = zipfile.ZipFile(zpath).namelist()
    bad = [f for f in inside if f.lower().endswith(IMAGE_EXT)]
    print(f"\nĐã tạo {zpath} ({os.path.getsize(zpath)/1024:.0f} KB, {n} file)")
    print("  " + "\n  ".join(inside))
    print("CÓ ẢNH TRONG GÓI — DỪNG, KHÔNG NỘP: " + str(bad) if bad else "Không có ảnh trong gói. Nộp lên LMS.")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", action="store_true", help="đóng gói zip nộp sau khi kiểm")
    ap.add_argument("--force", action="store_true", help="đóng gói kể cả khi còn FAIL")
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    check_present()
    for z in ("export_final.zip", "export_final_v2.zip", "export_extra.zip"):
        check_zip(z)
    check_final_txt("check_final.txt")
    if os.path.exists(os.path.join(ROOT, "check_final_v2.txt")):
        check_final_txt("check_final_v2.txt")
    check_ir_log()
    check_disagreement()
    check_class_list()
    check_placeholders()
    check_no_images_in_repo()

    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "OK": 3}
    print(f"PREFLIGHT — {FOLDER}\n" + "=" * 70)
    for lvl, msg, hint in sorted(results, key=lambda r: order[r[0]]):
        print(f"[{lvl:4}] {msg}")
        if hint:
            print(f"        → {hint}")
    nf = sum(1 for r in results if r[0] == "FAIL")
    nw = sum(1 for r in results if r[0] == "WARN")
    print("=" * 70)
    print(f"Kết quả preflight: {nf} FAIL, {nw} WARN."
          + ("  Chưa nộp được." if nf else "  Đủ điều kiện nộp (WARN tự xét)."))
    code = 1 if nf else 0
    if args.pack:
        code = do_pack(args.force) or code
    sys.exit(code)


if __name__ == "__main__":
    main()
