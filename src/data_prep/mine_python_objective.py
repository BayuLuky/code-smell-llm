# =====================================================================
# src/data_prep/mine_python_objective.py  —  SMELL OBJEKTIF PYTHON
# ---------------------------------------------------------------------
# Menambang dua smell OBJEKTIF dari kolam Python (data/raw/python_pool):
#   - long_parameter_list : fungsi dgn parameter > 7 (tak hitung self/cls)
#   - long_method         : fungsi dgn baris kode (SLOC) > ambang
#
# Tiap sampel = SATU fungsi, diekstrak sebagai cuplikan .py mandiri ke:
#   data/raw/python/<label>/<id>.py
# Manifest dgn asal-usul (file, baris, metrik) disimpan ke data/labels/.
#
# Aturan independen (tidak memakai SonarQube, agar perbandingan adil).
# Satu fungsi diberi SATU label; LPL diprioritaskan (lebih langka).
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\mine_python_objective.py
# =====================================================================

import sys
import ast
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

POOL_DIR = config.RAW_DIR / "python_pool"
OUT_MANIFEST = config.LABELS_DIR / "python_objective_manifest.csv"

AMBANG_PARAM = config.THRESHOLDS["long_parameter_list_count"]      # > 7
AMBANG_SLOC = config.THRESHOLDS["python_long_method_sloc"]         # > 50
TARGET = 42
BUFFER = 13            # kumpulkan ~55 per kelas (cadangan utk pemangkasan)


def hitung_param(node: ast.AST) -> int:
    """Jumlah parameter sebuah fungsi, tidak menghitung self/cls."""
    a = node.args
    total = len(a.posonlyargs) + len(a.args) + len(a.kwonlyargs)
    pertama = (a.posonlyargs or a.args)
    if pertama and pertama[0].arg in ("self", "cls"):
        total -= 1
    return total


def hitung_sloc(src_lines, start, end) -> int:
    """Jumlah baris kode (abaikan baris kosong & komentar) dalam rentang."""
    n = 0
    for ln in src_lines[start - 1:end]:
        s = ln.strip()
        if s and not s.startswith("#"):
            n += 1
    return n


def potong(src_lines, start, end) -> str:
    """Ambil teks sumber baris start..end (inklusif), lalu ratakan
    indentasinya (dedent) agar method dari dalam kelas tetap valid sebagai
    berkas .py mandiri."""
    cuplikan = "".join(src_lines[start - 1:end])
    return textwrap.dedent(cuplikan)


def mine():
    if not POOL_DIR.exists():
        print("Kolam Python belum ada. Jalankan dulu download_python_repos.py")
        return

    # Kumpulkan semua berkas .py lalu acak (seeded) demi reproducibility.
    py_files = sorted(str(p) for p in POOL_DIR.rglob("*.py"))
    import random
    random.Random(config.RANDOM_SEED).shuffle(py_files)

    # Siapkan folder keluaran.
    for label in ["long_method", "long_parameter_list"]:
        (config.RAW_DIR / "python" / label).mkdir(parents=True, exist_ok=True)

    hasil = []
    n_lm = n_lpl = 0
    parse_gagal = 0
    target_total = TARGET + BUFFER

    for path in py_files:
        if n_lm >= target_total and n_lpl >= target_total:
            break
        try:
            src = open(path, encoding="utf-8").read()
            src_lines = src.splitlines(keepends=True)
            tree = ast.parse(src)
        except Exception:
            parse_gagal += 1
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)

            label = None
            metrik = None
            if hitung_param(node) > AMBANG_PARAM and n_lpl < target_total:
                label, metrik = "long_parameter_list", hitung_param(node)
                n_lpl += 1
            elif hitung_sloc(src_lines, start, end) > AMBANG_SLOC and n_lm < target_total:
                label, metrik = "long_method", hitung_sloc(src_lines, start, end)
                n_lm += 1

            if label:
                sid = f"py_{label[:2]}_{len(hasil):04d}"
                out = config.RAW_DIR / "python" / label / f"{sid}.py"
                out.write_text(potong(src_lines, start, end), encoding="utf-8")
                rel = str(Path(path).relative_to(POOL_DIR))
                hasil.append({
                    "sample_id": sid, "label": label, "language": "python",
                    "source_file": rel, "function_name": node.name,
                    "start_line": start, "end_line": end, "metric": metrik,
                })

    pd.DataFrame(hasil).to_csv(OUT_MANIFEST, index=False)
    print("=== Hasil tambang smell objektif Python ===")
    print(f"  long_method          : {n_lm}")
    print(f"  long_parameter_list  : {n_lpl}")
    print(f"  (parse gagal: {parse_gagal})")
    print(f"Manifest: {OUT_MANIFEST}")
    if n_lm < TARGET or n_lpl < TARGET:
        print(f"\n[CATATAN] Ada kelas di bawah target {TARGET}. Bisa turunkan "
              f"ambang atau tambah repo di kolam.")


if __name__ == "__main__":
    mine()
