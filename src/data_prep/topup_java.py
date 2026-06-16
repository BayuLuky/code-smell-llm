# =====================================================================
# src/data_prep/topup_java.py  —  MENAMBAL KEKURANGAN BERKAS JAVA
# ---------------------------------------------------------------------
# Sebagian tautan MLCQ (data 2019) sudah mati, sehingga jumlah berkas
# yang berhasil diunduh kurang dari target. Skrip ini memilih kandidat
# PENGGANTI dari sisa kolam MLCQ (yang belum pernah dipilih) untuk kelas
# yang masih kurang, lalu menambahkannya ke manifest.
#
# Kita pilih sedikit LEBIH dari kekurangan (cadangan) agar tahan bila ada
# tautan mati lagi. Kelebihannya nanti dipangkas saat merakit dataset
# final. feature_envy dilewati bila kolamnya sudah habis.
#
# Alur pakai:
#   1) python src\data_prep\topup_java.py        (menambah kandidat)
#   2) python src\data_prep\fetch_java_code.py   (mengunduh yang baru)
#
# Jalankan dari folder utama proyek.
# =====================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

CONSENSUS = config.LABELS_DIR / "mlcq_consensus.csv"
MANIFEST = config.LABELS_DIR / "java_mlcq_manifest.csv"

TARGET = {"long_method": 42, "god_class": 42, "feature_envy": 26,
          "data_class": 42, "non_smells": 41}


def present_count(label: str) -> int:
    """Hitung berapa berkas .java sudah tersimpan untuk satu kelas."""
    folder = config.RAW_DIR / "java" / label
    return len(list(folder.glob("*.java"))) if folder.exists() else 0


def topup():
    if not (CONSENSUS.exists() and MANIFEST.exists()):
        print("Butuh mlcq_consensus.csv dan java_mlcq_manifest.csv lebih dulu.")
        return

    df = pd.read_csv(CONSENSUS)
    manifest = pd.read_csv(MANIFEST)
    sudah_dipilih = set(manifest["sample_id"])   # jangan pilih ulang

    # Bangun kembali kolam kandidat (logika sama dgn selector).
    positif = df[df["ada_longgar"] == True]
    jml_smell = positif.groupby("sample_id").size()
    id_satu_smell = set(jml_smell[jml_smell == 1].index)
    id_tanpa_smell = set(df["sample_id"].unique()) - set(positif["sample_id"].unique())

    tambahan = []

    def ambil(kandidat, label, kurang):
        """Pilih kandidat pengganti (kurang + cadangan), seeded."""
        kandidat = kandidat[~kandidat["sample_id"].isin(sudah_dipilih)]
        if len(kandidat) == 0:
            print(f"  {label:<20} kurang {kurang}, tapi KOLAM HABIS -> diterima apa adanya")
            return
        n = min(len(kandidat), kurang * 2 + 3)   # cadangan ekstra
        pick = kandidat.sample(n=n, random_state=config.RANDOM_SEED).copy()
        pick["label"] = label
        tambahan.append(pick)
        print(f"  {label:<20} kurang {kurang}, menambah {n} kandidat cadangan")

    print("=== Menambal kekurangan ===")
    for label in ["long_method", "god_class", "feature_envy", "data_class"]:
        kurang = TARGET[label] - present_count(label)
        if kurang <= 0:
            print(f"  {label:<20} sudah cukup")
            continue
        kand = positif[(positif["kelas"] == label) &
                       (positif["sample_id"].isin(id_satu_smell))]
        ambil(kand, label, kurang)

    # non_smells
    kurang = TARGET["non_smells"] - present_count("non_smells")
    if kurang > 0:
        kand = df[df["sample_id"].isin(id_tanpa_smell)].drop_duplicates("sample_id")
        ambil(kand, "non_smells", kurang)
    else:
        print(f"  {'non_smells':<20} sudah cukup")

    if not tambahan:
        print("\nTidak ada kandidat tambahan (semua cukup atau kolam habis).")
        return

    add = pd.concat(tambahan, ignore_index=True)
    kolom = ["sample_id", "label", "type", "repository", "commit_hash",
             "path", "start_line", "end_line", "link"]
    add = add[kolom]
    add["language"] = "java"

    baru = pd.concat([manifest, add], ignore_index=True).drop_duplicates("sample_id")
    baru.to_csv(MANIFEST, index=False)
    print(f"\nManifest: {len(manifest)} -> {len(baru)} baris.")
    print("Sekarang jalankan lagi: python src\\data_prep\\fetch_java_code.py")


if __name__ == "__main__":
    topup()
