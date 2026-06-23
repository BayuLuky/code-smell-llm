# =====================================================================
# src/data_prep/mine_python_nonsmells.py  —  KODE BERSIH (NON-SMELLS)
# ---------------------------------------------------------------------
# Mengumpulkan unit Python yang BERSIH dari smell untuk kelas non_smells.
# Diambil CAMPURAN: fungsi bersih + kelas kecil bersih, agar tipe unit
# (fungsi vs kelas) tidak menjadi petunjuk palsu bagi model.
#
# "Bersih" = lolos semua kriteria anti-smell:
#   Fungsi : 5..30 baris kode, parameter <= 4, (bila method) tidak
#            feature-envy (akses self >= akses objek lain).
#   Kelas  : 3..7 method, 30..120 baris, bukan @dataclass (bukan Data
#            Class), tidak terlalu besar (bukan God Class).
# Unit yang sudah dipakai kelas lain / sudah ditinjau / berkas tes -> dilewati.
#
# Hasil: cuplikan .py ke data/raw/python/non_smells/ + manifest.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\mine_python_nonsmells.py
# =====================================================================

import sys
import ast
import textwrap
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

POOL = config.RAW_DIR / "python_pool"
OBJ_MANIFEST = config.LABELS_DIR / "python_objective_manifest.csv"
CAND_CSV = config.LABELS_DIR / "python_candidates.csv"
OUT_DIR = config.RAW_DIR / "python" / "non_smells"
OUT_MANIFEST = config.LABELS_DIR / "python_nonsmells_manifest.csv"

# Sasaran: kira-kira separuh fungsi, separuh kelas (+ cadangan).
TARGET_FUNC = 28
TARGET_CLASS = 28

FUNC_SLOC = (5, 30)
FUNC_MAX_PARAM = 4
CLASS_METHODS = (3, 7)
CLASS_SLOC = (30, 120)


def sloc(src_lines, start, end):
    return sum(1 for ln in src_lines[start - 1:end]
               if ln.strip() and not ln.strip().startswith("#"))


def potong(src_lines, start, end):
    return textwrap.dedent("".join(src_lines[start - 1:end]))


def n_param(fn):
    a = fn.args
    total = len(a.posonlyargs) + len(a.args) + len(a.kwonlyargs)
    first = (a.posonlyargs or a.args)
    if first and first[0].arg in ("self", "cls"):
        total -= 1
    return total


def is_method(fn):
    first = (fn.args.posonlyargs or fn.args.args)
    return bool(first and first[0].arg in ("self", "cls"))


def fe_counts(fn):
    selfc = extc = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "self":
                selfc += 1
            elif node.value.id != "cls":
                extc += 1
    return selfc, extc


def is_test_file(rel):
    parts = rel.replace("\\", "/").lower().split("/")
    nama = parts[-1]
    return ("test" in parts or "tests" in parts or
            nama.startswith("test_") or nama.endswith("_test.py") or "conftest" in nama)


def load_used():
    """Kumpulan (source_file, start_line) yang TIDAK boleh dipakai non_smells:
    sudah jadi sampel smell objektif, sudah ditinjau penilai, ATAU pernah
    jadi kandidat smell subjektif (walau belum dianotasi)."""
    used = set()
    if OBJ_MANIFEST.exists():
        for _, r in pd.read_csv(OBJ_MANIFEST).iterrows():
            used.add((r["source_file"], int(r["start_line"])))
    # semua file anotasi penilai (baik y/n/skip) -> jangan dipakai non_smells
    for f in config.LABELS_DIR.glob("annotations_*.csv"):
        try:
            for _, r in pd.read_csv(f).iterrows():
                used.add((r["source_file"], int(r["start_line"])))
        except Exception:
            pass
    # SEMUA kandidat smell subjektif (termasuk yang belum dianotasi) -> kecualikan
    if CAND_CSV.exists():
        try:
            for _, r in pd.read_csv(CAND_CSV).iterrows():
                used.add((r["source_file"], int(r["start_line"])))
        except Exception:
            pass
    return used


def mine():
    if not POOL.exists():
        print("Kolam Python belum ada. Jalankan download_python_repos.py")
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    used = load_used()

    funcs, classes = [], []   # (rel, nama, start, end)
    py_files = sorted(str(p) for p in POOL.rglob("*.py"))
    random.Random(config.RANDOM_SEED).shuffle(py_files)

    for path in py_files:
        if len(funcs) >= TARGET_FUNC and len(classes) >= TARGET_CLASS:
            break
        rel = str(Path(path).relative_to(POOL))
        if is_test_file(rel):
            continue
        try:
            src = open(path, encoding="utf-8").read()
            src_lines = src.splitlines(keepends=True)
            tree = ast.parse(src)
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                continue
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            if (rel, start) in used:
                continue

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and len(funcs) < TARGET_FUNC:
                s = sloc(src_lines, start, end)
                if not (FUNC_SLOC[0] <= s <= FUNC_SLOC[1]):
                    continue
                if n_param(node) > FUNC_MAX_PARAM:
                    continue
                if is_method(node):
                    sc, ec = fe_counts(node)
                    if ec > sc:           # condong feature-envy -> bukan bersih
                        continue
                funcs.append((rel, node.name, start, end))

            elif isinstance(node, ast.ClassDef) and len(classes) < TARGET_CLASS:
                ms = [n for n in node.body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                s = sloc(src_lines, start, end)
                is_dc = any((getattr(d, "id", None) or
                             getattr(getattr(d, "func", None), "id", None)) == "dataclass"
                            for d in node.decorator_list)
                if (CLASS_METHODS[0] <= len(ms) <= CLASS_METHODS[1] and
                        CLASS_SLOC[0] <= s <= CLASS_SLOC[1] and not is_dc):
                    classes.append((rel, node.name, start, end))

    # Tulis cuplikan + manifest.
    baris = []
    for kind, items in [("func", funcs), ("class", classes)]:
        for i, (rel, nama, start, end) in enumerate(items):
            sid = f"py_ns_{kind}_{i:03d}"
            src_lines = open(POOL / rel, encoding="utf-8").read().splitlines(keepends=True)
            (OUT_DIR / f"{sid}.py").write_text(potong(src_lines, start, end), encoding="utf-8")
            baris.append({"sample_id": sid, "label": "non_smells", "language": "python",
                          "unit_type": kind, "source_file": rel, "unit_name": nama,
                          "start_line": start, "end_line": end})

    pd.DataFrame(baris).to_csv(OUT_MANIFEST, index=False)
    print("=== Kode bersih (non_smells) Python terkumpul ===")
    print(f"  fungsi bersih : {len(funcs)}")
    print(f"  kelas bersih  : {len(classes)}")
    print(f"  total         : {len(baris)}")
    print(f"Manifest: {OUT_MANIFEST}")
    if len(baris) < 42:
        print("\n[CATATAN] Di bawah 42. Bisa longgarkan kriteria atau tambah repo.")


if __name__ == "__main__":
    mine()
