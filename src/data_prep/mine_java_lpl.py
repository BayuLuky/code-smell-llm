# =====================================================================
# src/data_prep/mine_java_lpl.py  —  MENAMBANG LONG PARAMETER LIST (JAVA)
# ---------------------------------------------------------------------
# Long Parameter List tidak ada di MLCQ. Karena smell ini OBJEKTIF, kita
# beri label sendiri dengan aturan independen: cari method/konstruktor
# yang jumlah parameternya MELEBIHI ambang (default SonarQube: > 7).
#
# Sumber berkas: rujukan Java lain di MLCQ (yang BELUM dipakai untuk kelas
# lain), supaya tidak ada tumpang-tindih antar-kelas. Tiap berkas diunduh,
# di-parse dengan javalang, lalu diperiksa.
#
# Hasil:
#   - berkas .java disimpan ke data/raw/java/long_parameter_list/
#   - manifest data/labels/lpl_java_manifest.csv (sample_id, method, param, baris)
#
# Sifat: resumable, sopan (jeda), tahan gagal (unduh & parse).
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\mine_java_lpl.py
# =====================================================================

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd
import requests
import javalang

CONSENSUS = config.LABELS_DIR / "mlcq_consensus.csv"
USED_MANIFEST = config.LABELS_DIR / "java_mlcq_manifest.csv"
OUT_MANIFEST = config.LABELS_DIR / "lpl_java_manifest.csv"
OUT_DIR = config.RAW_DIR / "java" / "long_parameter_list"

AMBANG = config.THRESHOLDS["long_parameter_list_count"]  # > 7
TARGET = 42
BUFFER = 13            # cari sedikit lebih (total ~55) sbg cadangan
MAKS_PINDAI = 800      # batas berkas yang dipindai agar tidak berjalan lama


def repo_to_owner_repo(repository: str) -> str:
    s = repository.strip()
    if s.startswith("git@github.com:"):
        s = s[len("git@github.com:"):]
    if s.startswith("https://github.com/"):
        s = s[len("https://github.com/"):]
    if s.endswith(".git"):
        s = s[:-4]
    return s


def raw_url(repository, commit, path):
    return (f"https://raw.githubusercontent.com/"
            f"{repo_to_owner_repo(repository)}/{commit}/{str(path).lstrip('/')}")


def cari_lpl(kode: str):
    """Kembalikan (nama_method, baris, jumlah_param) bila ada method yang
    melebihi ambang; "PARSE_FAIL" bila kode gagal di-parse; atau None bila
    berhasil di-parse tetapi tidak ada LPL."""
    try:
        tree = javalang.parse.parse(kode)
    except Exception:
        return "PARSE_FAIL"  # gagal di-parse (mis. sintaks Java terlalu baru)
    for _, node in tree:
        if isinstance(node, (javalang.tree.MethodDeclaration,
                             javalang.tree.ConstructorDeclaration)):
            n = len(node.parameters)
            if n > AMBANG:
                baris = node.position.line if node.position else 0
                return (node.name, baris, n)
    return None


def mine():
    if not CONSENSUS.exists():
        print("Butuh mlcq_consensus.csv. Jalankan dulu aggregate_mlcq.py")
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CONSENSUS).drop_duplicates("sample_id")

    # Kecualikan sample_id yang sudah dipakai kelas lain (hindari overlap).
    dipakai = set()
    if USED_MANIFEST.exists():
        dipakai = set(pd.read_csv(USED_MANIFEST)["sample_id"])
    kolam = df[~df["sample_id"].isin(dipakai)]

    # Acak urutan (seeded) agar pemilihan reproducible.
    kolam = kolam.sample(frac=1, random_state=config.RANDOM_SEED)

    # Lanjutkan bila sudah ada hasil sebelumnya (resumable).
    hasil = []
    if OUT_MANIFEST.exists():
        try:
            hasil = pd.read_csv(OUT_MANIFEST).to_dict("records")
        except Exception:
            hasil = []   # manifest kosong/rusak -> mulai dari awal
    sudah_punya = {r["sample_id"] for r in hasil}

    target_total = TARGET + BUFFER
    dipindai = unduh_gagal = parse_gagal = tanpa_lpl = 0

    for _, row in kolam.iterrows():
        if len(hasil) >= target_total or dipindai >= MAKS_PINDAI:
            break
        if row["sample_id"] in sudah_punya:
            continue

        dipindai += 1
        url = raw_url(row["repository"], row["commit_hash"], row["path"])
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                unduh_gagal += 1
                continue
            kode = r.text
        except Exception:
            unduh_gagal += 1
            continue
        time.sleep(0.3)

        temuan = cari_lpl(kode)
        if temuan == "PARSE_FAIL":
            parse_gagal += 1
        elif temuan is None:
            tanpa_lpl += 1
        else:
            nama, baris, n = temuan
            out_file = OUT_DIR / f"{row['sample_id']}.java"
            out_file.write_text(kode, encoding="utf-8")
            hasil.append({
                "sample_id": row["sample_id"], "label": "long_parameter_list",
                "language": "java", "type": "function",
                "repository": row["repository"], "commit_hash": row["commit_hash"],
                "path": row["path"], "method_name": nama,
                "start_line": baris, "param_count": n,
            })

        if dipindai % 20 == 0:
            print(f"\r  dipindai {dipindai}, LPL {len(hasil)}, "
                  f"unduh gagal {unduh_gagal}, parse gagal {parse_gagal}, "
                  f"tanpa LPL {tanpa_lpl}", end="")

    print()
    pd.DataFrame(hasil).to_csv(OUT_MANIFEST, index=False)
    print(f"Selesai. LPL ditemukan: {len(hasil)} (target {TARGET}, +cadangan).")
    print(f"Dipindai {dipindai} | unduh gagal {unduh_gagal} | "
          f"parse gagal {parse_gagal} | tanpa LPL {tanpa_lpl}")
    print(f"Manifest: {OUT_MANIFEST}")
    if len(hasil) < TARGET:
        print(f"\n[CATATAN] Masih di bawah target {TARGET}. Jalankan lagi "
              f"untuk memindai lebih banyak (resumable), atau naikkan MAKS_PINDAI.")


if __name__ == "__main__":
    mine()
