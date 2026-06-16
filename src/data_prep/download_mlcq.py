# =====================================================================
# src/data_prep/download_mlcq.py  —  MENGUNDUH DATASET MLCQ
# ---------------------------------------------------------------------
# Mengunduh file MLCQCodeSmellSamples.csv (~7,5 MB) dari Zenodo dan
# menyimpannya ke folder data/mlcq/.
#
# Jalankan dari folder UTAMA proyek (yang ada config.py-nya):
#     python src\data_prep\download_mlcq.py
# =====================================================================

import sys
from pathlib import Path

# Baris berikut membuat skrip ini bisa menemukan config.py yang berada
# di folder utama proyek. __file__ = lokasi skrip ini (di src/data_prep/).
# .resolve().parents[2] naik dua tingkat: data_prep -> src -> folder utama.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config          # sekarang config.py bisa di-import
import requests        # library untuk mengunduh dari internet

# Alamat unduh langsung file CSV utama di Zenodo (dari API resmi Zenodo).
MLCQ_URL = (
    "https://zenodo.org/api/records/3666840/files/"
    "MLCQCodeSmellSamples.csv/content"
)

# Lokasi penyimpanan: data/mlcq/MLCQCodeSmellSamples.csv
OUT_PATH = config.MLCQ_DIR / "MLCQCodeSmellSamples.csv"


def download():
    config.ensure_dirs()  # pastikan folder data/mlcq/ sudah ada

    # Bila file sudah pernah diunduh, jangan unduh ulang (hemat waktu).
    if OUT_PATH.exists():
        print(f"File sudah ada, lewati unduh:\n  {OUT_PATH}")
        return

    print("Mengunduh MLCQ dari Zenodo ...")
    # stream=True artinya unduh sedikit demi sedikit (tidak menumpuk di
    # memori sekaligus) — aman untuk file besar.
    with requests.get(MLCQ_URL, stream=True, timeout=60) as r:
        r.raise_for_status()  # bila gagal (mis. 404), hentikan dgn error jelas
        total = int(r.headers.get("content-length", 0))  # ukuran total (byte)
        downloaded = 0
        with open(OUT_PATH, "wb") as f:           # "wb" = tulis mode biner
            for chunk in r.iter_content(chunk_size=8192):  # per 8 KB
                f.write(chunk)
                downloaded += len(chunk)
                if total:  # tampilkan persentase kemajuan
                    pct = downloaded * 100 // total
                    print(f"\r  {pct}%  ({downloaded // 1024} KB)", end="")

    print(f"\nSelesai. Tersimpan di:\n  {OUT_PATH}")


if __name__ == "__main__":
    download()
