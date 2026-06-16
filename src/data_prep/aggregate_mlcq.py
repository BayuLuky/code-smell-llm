# =====================================================================
# src/data_prep/aggregate_mlcq.py  —  KONSENSUS REVIEWER + DIAGNOSTIK
# ---------------------------------------------------------------------
# MLCQ menilai tiap potongan kode dengan BANYAK reviewer. Skrip ini
# menggabungkan penilaian itu menjadi SATU konsensus per (potongan kode,
# smell), lalu menampilkan berapa banyak contoh yang tersedia untuk tiap
# smell. Tujuannya: membantu Anda memilih "aturan konsensus" sambil
# melihat angka nyata, sebelum menyusun rencana 500 berkas (langkah 1.4).
#
# Hasil tambahan: menyimpan tabel konsensus ke data/labels/ untuk dipakai
# lagi nanti.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\aggregate_mlcq.py
# =====================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

CSV_PATH = config.MLCQ_DIR / "MLCQCodeSmellSamples.csv"
OUT_PATH = config.LABELS_DIR / "mlcq_consensus.csv"

# Mengubah severity (teks) menjadi angka tingkat, agar bisa dibandingkan.
SEVERITY_RANK = {"none": 0, "minor": 1, "major": 2, "critical": 3}

# Menerjemahkan nama smell MLCQ -> nama kelas di proyek kita (config).
MLCQ_TO_CLASS = {
    "blob":         "god_class",
    "data class":   "data_class",
    "feature envy": "feature_envy",
    "long method":  "long_method",
}


def aggregate():
    if not CSV_PATH.exists():
        print("File MLCQ belum ada. Jalankan dulu download_mlcq.py")
        return

    config.ensure_dirs()
    df = pd.read_csv(CSV_PATH, sep=";")  # MLCQ memakai pemisah titik koma

    # Ubah severity teks -> angka. Nilai tak dikenal jadi 0 (none).
    df["rank"] = df["severity"].map(SEVERITY_RANK).fillna(0).astype(int)

    # --- KONSENSUS per (sample_id, smell) lewat suara terbanyak ---
    # Kelompokkan semua review untuk kombinasi potongan-kode + smell.
    grup = df.groupby(["sample_id", "smell"])

    baris_konsensus = []
    for (sample_id, smell), g in grup:
        ranks = g["rank"].tolist()
        n = len(ranks)                                   # jumlah reviewer
        # "ketat": reviewer menganggap smell ada bila severity >= major(2)
        suara_ketat   = sum(1 for r in ranks if r >= 2)
        # "longgar": severity >= minor(1)
        suara_longgar = sum(1 for r in ranks if r >= 1)
        # Suara terbanyak: ada bila lebih dari separuh reviewer setuju.
        ada_ketat   = suara_ketat   > n / 2
        ada_longgar = suara_longgar > n / 2

        info = g.iloc[0]  # ambil 1 baris untuk menyalin metadata kode
        baris_konsensus.append({
            "sample_id": sample_id,
            "kelas": MLCQ_TO_CLASS.get(smell, smell),
            "type": info["type"],
            "repository": info["repository"],
            "commit_hash": info["commit_hash"],
            "path": info["path"],
            "start_line": info["start_line"],
            "end_line": info["end_line"],
            "link": info["link"],
            "n_reviews": n,
            "ada_ketat": ada_ketat,
            "ada_longgar": ada_longgar,
        })

    kon = pd.DataFrame(baris_konsensus)
    kon.to_csv(OUT_PATH, index=False)
    print(f"Tabel konsensus disimpan: {OUT_PATH}")
    print(f"Total kombinasi (potongan kode x smell): {len(kon)}\n")

    # --- DIAGNOSTIK 1: contoh POSITIF per smell (di bawah 2 aturan) ---
    print("=== Jumlah contoh POSITIF per smell ===")
    print(f"{'smell':<22}{'ketat (major+)':>16}{'longgar (minor+)':>18}")
    for kelas in ["long_method", "god_class", "feature_envy", "data_class"]:
        sub = kon[kon["kelas"] == kelas]
        print(f"{kelas:<22}{int(sub['ada_ketat'].sum()):>16}"
              f"{int(sub['ada_longgar'].sum()):>18}")

    # --- DIAGNOSTIK 2: di tingkat POTONGAN KODE (aturan ketat) ---
    # Tiap potongan kode bisa positif utk >1 smell. Untuk benchmark
    # SATU label, kita lihat: berapa yang positif tepat 1 smell (bersih),
    # berapa yang tanpa smell (kandidat non-smells), berapa yang ambigu.
    print("\n=== Di tingkat potongan kode (aturan KETAT) ===")
    satu_smell = 0   # positif tepat 1 smell -> contoh smell yang jelas
    nol_smell = 0    # tidak ada smell -> kandidat non-smells
    ambigu = 0       # positif >1 smell -> dibuang (membingungkan model)
    for sample_id, g in kon.groupby("sample_id"):
        jml_positif = int(g["ada_ketat"].sum())
        if jml_positif == 1:
            satu_smell += 1
        elif jml_positif == 0:
            nol_smell += 1
        else:
            ambigu += 1
    print(f"  Positif tepat 1 smell (contoh jelas) : {satu_smell}")
    print(f"  Tanpa smell (kandidat non-smells)    : {nol_smell}")
    print(f"  Ambigu / >1 smell (dibuang)          : {ambigu}")


if __name__ == "__main__":
    aggregate()
