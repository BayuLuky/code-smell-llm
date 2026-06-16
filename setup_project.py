#!/usr/bin/env python3
# =====================================================================
# setup_project.py  —  PEMBUAT STRUKTUR FOLDER
# ---------------------------------------------------------------------
# Jalankan SEKALI di awal untuk membuat semua folder & file kosong yang
# diperlukan. Jalankan dengan:
#     python setup_project.py
# Aman dijalankan berulang: folder yang sudah ada tidak akan rusak.
# =====================================================================

from pathlib import Path

# Folder utama = lokasi skrip ini berada.
ROOT = Path(__file__).parent

# Daftar semua folder yang akan dibuat (relatif terhadap ROOT).
FOLDERS = [
    "data/mlcq",
    "data/raw/java",
    "data/raw/python",
    "data/processed/java",
    "data/processed/python",
    "data/labels",
    "src/data_prep",
    "src/detectors",
    "src/evaluation",
    "results/predictions",
    "results/metrics",
    "results/figures",
    "notebooks",
]

# Folder di dalam "src/" adalah folder kode Python. Agar bisa di-import
# antar-file, tiap folder kode butuh file kosong bernama __init__.py.
PYTHON_PACKAGES = ["src", "src/data_prep", "src/detectors", "src/evaluation"]


def main():
    # 1) Buat tiap folder. parents=True -> ikut buat folder induk bila
    #    perlu. exist_ok=True -> tidak error bila sudah ada.
    for folder in FOLDERS:
        path = ROOT / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [folder]  {folder}")

        # Git mengabaikan folder kosong. File ".gitkeep" kosong dipakai
        # sebagai penanda agar folder tetap terlacak di Git/GitHub.
        (path / ".gitkeep").touch()

    # 2) Buat file __init__.py kosong di tiap folder kode Python.
    for pkg in PYTHON_PACKAGES:
        init_file = ROOT / pkg / "__init__.py"
        init_file.touch()  # touch() = buat file kosong bila belum ada
        print(f"  [python]  {pkg}/__init__.py")

    print("\nStruktur proyek berhasil dibuat.")
    print("Langkah berikutnya: jalankan 'pip install -r requirements.txt'")


if __name__ == "__main__":
    main()
