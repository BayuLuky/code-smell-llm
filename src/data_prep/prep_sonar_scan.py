# =====================================================================
# src/data_prep/prep_sonar_scan.py  —  SIAPKAN DATASET UNTUK DIPINDAI
# ---------------------------------------------------------------------
# Menata seluruh sampel dataset final ke satu folder pindai SonarQube:
#   data/sonar_scan/java/<id>.java
#   data/sonar_scan/python/<id>.py
#
# Method Java yang berdiri sendiri (Long Method, Feature Envy, LPL)
# DIBUNGKUS dalam kelas pembungkus agar menjadi kode yang valid; sampel
# yang sudah berupa kelas (God Class, Data Class) dibiarkan apa adanya.
# Keputusan dibuat otomatis dengan parser javalang. Python disalin apa
# adanya (sudah valid sebagai modul mandiri).
#
# Nama berkas = id sampel, sehingga tiap temuan SonarQube nanti bisa
# dikembalikan ke sampel & label yang tepat (via ground_truth.csv).
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\prep_sonar_scan.py
# =====================================================================

import sys
import shutil
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd
import javalang

DATASET = config.DATA_DIR / "dataset"
GT = DATASET / "ground_truth.csv"
SCAN = config.DATA_DIR / "sonar_scan"
MANIFEST = config.LABELS_DIR / "sonar_scan_manifest.csv"

WRAPPER = "CodeSmellSample"


def java_parses(code):
    try:
        javalang.parse.parse(code)
        return True
    except Exception:
        return False


def prep():
    if not GT.exists():
        print("ground_truth.csv belum ada. Jalankan assemble_dataset.py dulu.")
        return
    gt = pd.read_csv(GT)
    if SCAN.exists():
        shutil.rmtree(SCAN)

    rows = []
    for _, r in gt.iterrows():
        sid, lang, label = r["id"], r["language"], r["label"]
        code = (DATASET / r["code_path"]).read_text(encoding="utf-8")

        if lang == "java":
            if java_parses(code):
                status = "ok"                       # sudah valid (kelas)
            else:
                wrapped = f"public class {WRAPPER} {{\n" + \
                          textwrap.indent(code, "    ") + "\n}\n"
                if java_parses(wrapped):
                    code, status = wrapped, "wrapped"   # method dibungkus
                else:
                    code, status = wrapped, "failed"    # tetap ditulis, ditandai
            outdir, ext = SCAN / "java", "java"
        else:
            status = "ok"
            outdir, ext = SCAN / "python", "py"

        outdir.mkdir(parents=True, exist_ok=True)
        dest = outdir / f"{sid}.{ext}"
        dest.write_text(code, encoding="utf-8")
        rows.append({"id": sid, "language": lang, "label": label,
                     "scan_path": str(dest.relative_to(SCAN)).replace("\\", "/"),
                     "status": status})

    man = pd.DataFrame(rows)
    man.to_csv(MANIFEST, index=False)

    print("=== Folder pindai siap ===")
    print(f"Lokasi : {SCAN}")
    print(f"Total  : {len(man)} sampel\n")
    print("Status penyiapan Java:")
    jv = man[man["language"] == "java"]
    print(jv["status"].value_counts().to_string())
    if (jv["status"] == "failed").any():
        print("\n[PERHATIAN] Ada sampel Java yang gagal diparse bahkan setelah dibungkus:")
        print(jv[jv["status"] == "failed"]["id"].tolist())
    print(f"\nManifest pemetaan: {MANIFEST}")


if __name__ == "__main__":
    prep()
