# =====================================================================
# src/data_prep/fetch_java_code.py  —  MENGUNDUH KODE JAVA DARI GITHUB
# ---------------------------------------------------------------------
# Membaca java_mlcq_manifest.csv lalu mengunduh berkas .java asli dari
# GitHub (memakai repo + commit + path). Berkas disimpan UTUH ke:
#   data/raw/java/<label>/<sample_id>.java
#
# Sifat skrip:
#   - Resumable: berkas yang sudah ada dilewati (aman dijalankan ulang).
#   - Tahan gagal: tautan mati (404) dicatat, proses tetap lanjut.
#   - Sopan: jeda singkat antar-unduhan agar tidak membebani server.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\fetch_java_code.py
# =====================================================================

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd
import requests

MANIFEST = config.LABELS_DIR / "java_mlcq_manifest.csv"
LOG_GAGAL = config.LABELS_DIR / "java_fetch_gagal.csv"


def repo_to_owner_repo(repository: str) -> str:
    """Ubah alamat repo MLCQ menjadi bentuk 'owner/repo'.
    Contoh: 'git@github.com:apache/syncope.git' -> 'apache/syncope'."""
    s = repository.strip()
    if s.startswith("git@github.com:"):
        s = s[len("git@github.com:"):]
    if s.startswith("https://github.com/"):
        s = s[len("https://github.com/"):]
    if s.endswith(".git"):
        s = s[:-4]
    return s


def raw_url(repository: str, commit: str, path: str) -> str:
    """Susun alamat unduh 'raw' GitHub untuk satu berkas pada commit
    tertentu."""
    owner_repo = repo_to_owner_repo(repository)
    p = str(path).lstrip("/")   # buang garis miring di depan path
    return f"https://raw.githubusercontent.com/{owner_repo}/{commit}/{p}"


def fetch():
    if not MANIFEST.exists():
        print("Manifest belum ada. Jalankan dulu select_java_mlcq.py")
        return

    df = pd.read_csv(MANIFEST)
    config.ensure_dirs()

    ok = gagal = lewat = 0
    gagal_baris = []

    for i, row in df.iterrows():
        out_dir = config.RAW_DIR / "java" / row["label"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{row['sample_id']}.java"

        # Lewati bila sudah pernah diunduh.
        if out_file.exists():
            lewat += 1
        else:
            url = raw_url(row["repository"], row["commit_hash"], row["path"])
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200:
                    out_file.write_text(r.text, encoding="utf-8")
                    ok += 1
                else:
                    gagal += 1
                    gagal_baris.append({"sample_id": row["sample_id"],
                                        "label": row["label"],
                                        "alasan": f"HTTP {r.status_code}",
                                        "url": url})
            except Exception as e:
                gagal += 1
                gagal_baris.append({"sample_id": row["sample_id"],
                                    "label": row["label"],
                                    "alasan": str(e)[:60], "url": url})
            time.sleep(0.3)  # jeda sopan

        print(f"\r  {i + 1}/{len(df)}  (ok {ok}, gagal {gagal}, lewat {lewat})",
              end="")

    print()

    # Catat kegagalan ke file agar bisa ditinjau.
    if gagal_baris:
        pd.DataFrame(gagal_baris).to_csv(LOG_GAGAL, index=False)
        print(f"{gagal} berkas gagal diunduh. Detail tersimpan: {LOG_GAGAL}")

    # Ringkasan akhir per kelas (berapa berkas berhasil tersimpan).
    print(f"\nSelesai. Berhasil {ok}, gagal {gagal}, dilewati {lewat}.")
    print("\n=== Jumlah berkas tersimpan per kelas ===")
    for label in df["label"].unique():
        folder = config.RAW_DIR / "java" / label
        jml = len(list(folder.glob("*.java"))) if folder.exists() else 0
        print(f"  {label:<20} {jml}")


if __name__ == "__main__":
    fetch()
