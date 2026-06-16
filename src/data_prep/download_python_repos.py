# =====================================================================
# src/data_prep/download_python_repos.py  —  KOLAM SUMBER PYTHON
# ---------------------------------------------------------------------
# Mengunduh beberapa repositori Python populer (dikunci pada versi
# tertentu agar reproducible), lalu mengekstrak HANYA berkas .py-nya ke:
#   data/raw/python_pool/<repo>/...
#
# Kolam ini dipakai untuk SEMUA kebutuhan Python: smell objektif (otomatis),
# kandidat smell subjektif (anotasi manual), dan kode bersih (non_smells).
#
# Sifat: resumable (repo yang sudah terekstrak dilewati), tahan gagal.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\download_python_repos.py
# =====================================================================

import sys
import io
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import requests

POOL_DIR = config.RAW_DIR / "python_pool"

# Daftar repo: (pemilik, nama_repo, versi_tag). Versi dikunci demi
# reproducibility. Boleh Anda tambah/kurangi sesuai kebutuhan.
REPOS = [
    ("pallets",      "click",        "8.1.7"),
    ("pallets",      "flask",        "3.0.3"),
    ("psf",          "requests",     "v2.31.0"),
    ("scrapy",       "scrapy",       "2.11.2"),
    ("django",       "django",       "4.2.13"),
    ("scikit-learn", "scikit-learn", "1.4.2"),
]


def download_one(owner: str, repo: str, tag: str) -> int:
    dest = POOL_DIR / repo

    # Resumable: bila sudah ada berkas .py, lewati.
    if dest.exists() and any(dest.rglob("*.py")):
        n = len(list(dest.rglob("*.py")))
        print(f"  {repo:<14} sudah ada ({n} berkas .py), dilewati")
        return n

    url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/tags/{tag}"
    print(f"  {repo:<14} mengunduh ...", end=" ", flush=True)
    r = requests.get(url, timeout=180)
    r.raise_for_status()

    tar = tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz")
    dest_resolved = dest.resolve()
    count = 0
    for member in tar.getmembers():
        if not (member.isfile() and member.name.endswith(".py")):
            continue
        # Tarball berisi folder root berversi, mis. 'click-8.1.7/src/..'.
        # Buang bagian root itu agar rapi.
        parts = member.name.split("/", 1)
        rel = parts[1] if len(parts) > 1 else parts[0]
        out = (dest / rel).resolve()

        # Pengaman: jangan tulis di luar folder tujuan (anti path-traversal).
        if not str(out).startswith(str(dest_resolved)):
            continue

        out.parent.mkdir(parents=True, exist_ok=True)
        f = tar.extractfile(member)
        if f is not None:
            out.write_bytes(f.read())
            count += 1

    print(f"{count} berkas .py diekstrak")
    return count


def main():
    POOL_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Mengunduh kolam sumber Python ===")
    total = 0
    for owner, repo, tag in REPOS:
        try:
            total += download_one(owner, repo, tag)
        except Exception as e:
            print(f"  {repo:<14} GAGAL: {str(e)[:60]}")
    print(f"\nTotal berkas .py di kolam: {total}")
    print(f"Lokasi kolam: {POOL_DIR}")


if __name__ == "__main__":
    main()
