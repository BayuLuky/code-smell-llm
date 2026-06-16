# =====================================================================
# src/data_prep/inspect_mlcq.py  —  MEMERIKSA ISI DATASET MLCQ (v2)
# ---------------------------------------------------------------------
# Versi tahan-banting:
#   1) Menampilkan beberapa baris MENTAH dulu (lihat format asli).
#   2) Mendeteksi bila file ternyata HTML (unduhan gagal).
#   3) Mendeteksi pemisah (koma / titik koma / tab) secara otomatis.
#   4) Baru membaca & meringkas isinya.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\inspect_mlcq.py
# =====================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

CSV_PATH = config.MLCQ_DIR / "MLCQCodeSmellSamples.csv"


def detect_separator(first_line: str) -> str:
    """Tebak pemisah dengan menghitung mana yang paling sering muncul
    di baris pertama (baris judul kolom)."""
    kandidat = {";": first_line.count(";"),
                ",": first_line.count(","),
                "\t": first_line.count("\t")}
    sep = max(kandidat, key=kandidat.get)   # ambil yang terbanyak
    return sep if kandidat[sep] > 0 else ","  # bila tak ada, default koma


def inspect():
    if not CSV_PATH.exists():
        print("File MLCQ belum ada. Jalankan dulu:")
        print("  python src\\data_prep\\download_mlcq.py")
        return

    # --- 1) Intip 5 baris mentah pertama ---
    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        head_lines = [f.readline() for _ in range(5)]
    raw_head = "".join(head_lines)

    print("=== 5 BARIS MENTAH PERTAMA ===")
    for i, line in enumerate(head_lines, 1):
        print(f"{i}: {line.rstrip()[:200]}")

    # --- 2) Deteksi unduhan gagal (isi HTML, bukan CSV) ---
    if raw_head.lstrip().startswith("<"):
        print("\n[MASALAH] File ini tampak berupa halaman HTML, bukan CSV.")
        print("Unduhan kemungkinan gagal/diblokir. Unduh ulang, atau ambil")
        print("manual dari https://zenodo.org/records/3666840 (klik file")
        print("MLCQCodeSmellSamples.csv) lalu taruh di folder data\\mlcq\\.")
        return

    # --- 3) Deteksi pemisah ---
    sep = detect_separator(head_lines[0])
    nama = {";": "titik koma (;)", ",": "koma (,)", "\t": "tab"}[sep]
    print(f"\n=== PEMISAH TERDETEKSI: {nama} ===")

    # --- 4) Baca dengan pemisah yang benar, lalu ringkas ---
    df = pd.read_csv(CSV_PATH, sep=sep)

    print("\n=== UKURAN DATA ===")
    print(f"Jumlah baris : {len(df)}")
    print(f"Jumlah kolom : {len(df.columns)}")

    print("\n=== NAMA SEMUA KOLOM ===")
    for c in df.columns:
        print(f"  - {c}")

    print("\n=== 3 BARIS PERTAMA (rapi) ===")
    print(df.head(3).to_string())

    if "smell" in df.columns:
        print("\n=== JENIS SMELL & JUMLAH BARISNYA ===")
        print(df["smell"].value_counts().to_string())

    if "severity" in df.columns:
        print("\n=== TINGKAT SEVERITY & JUMLAH BARISNYA ===")
        print(df["severity"].value_counts().to_string())

    for id_col in ["sample_id", "id", "code_name"]:
        if id_col in df.columns:
            unik = df[id_col].nunique()
            print(f"\n=== '{id_col}': {unik} sampel unik dari {len(df)} baris ===")
            if unik < len(df):
                print("  -> Sebagian sampel dinilai >1 reviewer "
                      "(akan digabung di langkah 1.5).")
            break


if __name__ == "__main__":
    inspect()
