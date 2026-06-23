# =====================================================================
# src/data_prep/compute_kappa.py  —  KESEPAKATAN ANTAR-PENILAI (KAPPA)
# ---------------------------------------------------------------------
# Menghitung Cohen's kappa antara dua penilai pada anotasi smell subjektif
# Python, lalu menafsirkannya dengan tabel Landis & Koch (1977).
# Hasil dipakai untuk melaporkan inter-rater reliability di tesis.
#
# Membaca otomatis dua file data/labels/annotations_<nama>.csv.
# Menyimpan tabel ke results/metrics/kappa_table.csv.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\compute_kappa.py
# =====================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd
from sklearn.metrics import cohen_kappa_score

CLASSES = ["god_class", "data_class", "feature_envy"]
ANNOTATORS = ["akbar_ts", "erick_wp"]   # dua penilai resmi


def landis_koch(k):
    if k < 0.00: return "Poor"
    if k <= 0.20: return "Slight"
    if k <= 0.40: return "Fair"
    if k <= 0.60: return "Moderate"
    if k <= 0.80: return "Substantial"
    return "Almost perfect"


def biner(df):
    df = df.copy()
    df["ya"] = df["final_label"].isin(CLASSES).astype(int)
    return df.set_index("sample_id")


def main():
    files = [config.LABELS_DIR / f"annotations_{n}.csv" for n in ANNOTATORS]
    files = [f for f in files if f.exists()]
    if len(files) < 2:
        print(f"Butuh 2 file penilai resmi {ANNOTATORS}, baru ada {len(files)}. "
              "Tidak bisa menghitung kappa.")
        return

    A = biner(pd.read_csv(files[0]))
    B = biner(pd.read_csv(files[1]))
    nama_a = A["annotator"].iloc[0]
    nama_b = B["annotator"].iloc[0]

    shared = A.index.intersection(B.index)
    if len(shared) == 0:
        print("Tidak ada kandidat yang dinilai oleh keduanya.")
        return

    baris = []
    # keseluruhan
    ya, yb = A.loc[shared, "ya"], B.loc[shared, "ya"]
    k = cohen_kappa_score(ya, yb)
    agree = (ya == yb).mean()
    baris.append({"lingkup": "keseluruhan", "n": len(shared),
                  f"{nama_a}_ya": int(ya.sum()), f"{nama_b}_ya": int(yb.sum()),
                  "persen_sepakat": round(agree * 100, 1),
                  "kappa": round(k, 3), "tafsir": landis_koch(k)})
    # per kelas
    for kelas in CLASSES:
        idx = [s for s in shared if A.loc[s, "proposed_label"] == kelas]
        if not idx:
            continue
        aa, bb = A.loc[idx, "ya"], B.loc[idx, "ya"]
        kk = cohen_kappa_score(aa, bb) if aa.nunique() > 1 and bb.nunique() > 1 else 1.0
        baris.append({"lingkup": kelas, "n": len(idx),
                      f"{nama_a}_ya": int(aa.sum()), f"{nama_b}_ya": int(bb.sum()),
                      "persen_sepakat": round((aa == bb).mean() * 100, 1),
                      "kappa": round(kk, 3), "tafsir": landis_koch(kk)})

    tabel = pd.DataFrame(baris)
    config.METRICS_DIR.mkdir(parents=True, exist_ok=True)
    out = config.METRICS_DIR / "kappa_table.csv"
    tabel.to_csv(out, index=False)
    print(f"Penilai: {nama_a} vs {nama_b}\n")
    print(tabel.to_string(index=False))
    print(f"\nTabel disimpan: {out}")


if __name__ == "__main__":
    main()
