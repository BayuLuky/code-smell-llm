# =====================================================================
# src/data_prep/select_java_mlcq.py  —  MEMILIH BERKAS JAVA DARI MLCQ
# ---------------------------------------------------------------------
# Membaca tabel konsensus (mlcq_consensus.csv) lalu memilih berkas Java
# untuk 5 kelas yang disuplai MLCQ:
#   long_method, god_class, feature_envy, data_class, non_smells
# (Long Parameter List Java diambil terpisah lewat aturan otomatis.)
#
# Aturan pemilihan:
#   - Pakai konsensus LONGGAR (kolom ada_longgar) sesuai keputusan kita.
#   - Hanya ambil potongan kode yang positif TEPAT 1 smell (contoh bersih,
#     tidak ambigu). Yang positif >1 smell dibuang.
#   - non_smells = potongan kode yang TIDAK positif smell apa pun.
#   - Pengambilan acak memakai RANDOM_SEED agar bisa direproduksi.
#
# Hasil: data/labels/java_mlcq_manifest.csv = "daftar belanja" berisi
# rujukan kode (repo, commit, path, baris) yang akan diunduh di langkah
# berikutnya. Skrip ini BELUM mengunduh kodenya.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\select_java_mlcq.py
# =====================================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

CONSENSUS_PATH = config.LABELS_DIR / "mlcq_consensus.csv"
MANIFEST_PATH = config.LABELS_DIR / "java_mlcq_manifest.csv"

# Kuota berkas per kelas untuk sisi Java dari MLCQ (total 209).
KUOTA = {
    "long_method": 42,
    "god_class": 42,
    "feature_envy": 42,
    "data_class": 42,
    "non_smells": 41,
}


def select():
    if not CONSENSUS_PATH.exists():
        print("File konsensus belum ada. Jalankan dulu aggregate_mlcq.py")
        return

    df = pd.read_csv(CONSENSUS_PATH)

    # --- 1) Ambil hanya baris yang POSITIF di bawah aturan longgar ---
    positif = df[df["ada_longgar"] == True]

    # Berapa banyak smell berbeda yang positif untuk tiap potongan kode?
    jml_smell_positif = positif.groupby("sample_id").size()

    # sample_id yang positif TEPAT 1 smell -> contoh bersih.
    id_satu_smell = set(jml_smell_positif[jml_smell_positif == 1].index)

    # sample_id yang TIDAK pernah positif smell apa pun -> non_smells.
    semua_id = set(df["sample_id"].unique())
    id_positif = set(positif["sample_id"].unique())
    id_tanpa_smell = semua_id - id_positif

    print(f"Total potongan kode unik       : {len(semua_id)}")
    print(f"Positif tepat 1 smell (bersih) : {len(id_satu_smell)}")
    print(f"Tanpa smell (kandidat non)     : {len(id_tanpa_smell)}\n")

    terpilih = []  # akan menampung baris-baris manifest

    # --- 2) Pilih untuk tiap kelas SMELL (bukan non_smells) ---
    for kelas in ["long_method", "god_class", "feature_envy", "data_class"]:
        kuota = KUOTA[kelas]
        # baris positif untuk kelas ini DAN potongan kodenya bersih (1 smell)
        kandidat = positif[(positif["kelas"] == kelas) &
                           (positif["sample_id"].isin(id_satu_smell))]
        tersedia = len(kandidat)

        # ambil sebanyak kuota; bila kurang, ambil semua + beri peringatan
        n_ambil = min(kuota, tersedia)
        sampel = kandidat.sample(n=n_ambil, random_state=config.RANDOM_SEED)
        sampel = sampel.copy()
        sampel["label"] = kelas
        terpilih.append(sampel)

        status = "OK" if tersedia >= kuota else f"KURANG (butuh {kuota})"
        print(f"  {kelas:<20} tersedia {tersedia:>4}, dipilih {n_ambil:>3}  [{status}]")

    # --- 3) Pilih untuk non_smells ---
    kuota = KUOTA["non_smells"]
    # ambil 1 baris perwakilan per potongan kode bersih-smell
    kand_non = df[df["sample_id"].isin(id_tanpa_smell)].drop_duplicates("sample_id")
    n_ambil = min(kuota, len(kand_non))
    sampel = kand_non.sample(n=n_ambil, random_state=config.RANDOM_SEED).copy()
    sampel["label"] = "non_smells"
    terpilih.append(sampel)
    print(f"  {'non_smells':<20} tersedia {len(kand_non):>4}, dipilih {n_ambil:>3}  [OK]")

    # --- 4) Gabung & simpan manifest ---
    manifest = pd.concat(terpilih, ignore_index=True)
    # kolom yang kita butuhkan untuk mengunduh kode nanti
    kolom = ["sample_id", "label", "type", "repository", "commit_hash",
             "path", "start_line", "end_line", "link"]
    manifest = manifest[kolom]
    manifest["language"] = "java"
    manifest.to_csv(MANIFEST_PATH, index=False)

    print(f"\nTotal berkas Java terpilih : {len(manifest)}")
    print(f"Manifest disimpan          : {MANIFEST_PATH}")


if __name__ == "__main__":
    select()
