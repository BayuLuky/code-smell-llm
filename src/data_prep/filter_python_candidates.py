# =====================================================================
# src/data_prep/filter_python_candidates.py  —  PENYARING KANDIDAT
# ---------------------------------------------------------------------
# Menyaring kolam Python untuk menemukan kandidat smell SUBJEKTIF:
#   god_class, data_class, feature_envy
# Memakai metrik dari `ast` untuk MENG-URUTKAN berkas dari yang paling
# mungkin ber-smell. Tiap kandidat diekstrak sbg cuplikan .py mandiri ke
#   data/raw/python/_candidates/<label>/<id>.py
# dan dicatat di data/labels/python_candidates.csv (beserta skor & metrik).
#
# PENTING: alat ini hanya MENYODORKAN kandidat. Keputusan label final
# dibuat manual oleh Anda lewat alat anotasi berikutnya.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\filter_python_candidates.py
# =====================================================================

import sys
import ast
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

POOL = config.RAW_DIR / "python_pool"
OBJ_MANIFEST = config.LABELS_DIR / "python_objective_manifest.csv"
CAND_DIR = config.RAW_DIR / "python" / "_candidates"
OUT = config.LABELS_DIR / "python_candidates.csv"

TOP_N = 100   # berapa kandidat teratas (skor tertinggi) per kelas disajikan

# Ambang penyaring (longgar; Anda yang memutuskan final).
GC_MIN_METHODS = 8
GC_MIN_SLOC = 120
DC_MIN_ATTRS = 3
DC_MAX_METHODS = 3
FE_MIN_EXTERNAL = 3


def sloc(src_lines, start, end):
    n = 0
    for ln in src_lines[start - 1:end]:
        s = ln.strip()
        if s and not s.startswith("#"):
            n += 1
    return n


def potong(src_lines, start, end):
    return textwrap.dedent("".join(src_lines[start - 1:end]))


def is_test_file(rel: str) -> bool:
    """True bila berkas tampak sebagai kode TES (difokuskan ke kode
    produksi, kode tes umumnya bukan sasaran studi code smell)."""
    rel_low = rel.replace("\\", "/").lower()
    parts = rel_low.split("/")
    nama = parts[-1]
    if "test" in parts or "tests" in parts:      # folder tes
        return True
    if nama.startswith("test_") or nama.endswith("_test.py") or "conftest" in nama:
        return True
    return False


def methods_of(cls):
    return [n for n in cls.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def self_attrs(cls):
    """Himpunan nama atribut self.X yang muncul di dalam kelas."""
    attrs = set()
    for node in ast.walk(cls):
        if (isinstance(node, ast.Attribute) and
                isinstance(node.value, ast.Name) and node.value.id == "self"):
            attrs.add(node.attr)
    return attrs


def has_dataclass_decorator(cls):
    for d in cls.decorator_list:
        nama = getattr(d, "id", None) or getattr(getattr(d, "func", None), "id", None)
        if nama == "dataclass":
            return True
    return False


def fe_counts(method):
    """Hitung akses ke self vs ke objek lain dalam sebuah method."""
    selfc = extc = 0
    for node in ast.walk(method):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id == "self":
                selfc += 1
            elif node.value.id != "cls":
                extc += 1
    return selfc, extc


def filter_candidates():
    if not POOL.exists():
        print("Kolam Python belum ada. Jalankan download_python_repos.py")
        return

    # Unit yang sudah dipakai smell objektif -> jangan dipakai lagi.
    dipakai = set()
    if OBJ_MANIFEST.exists():
        for _, r in pd.read_csv(OBJ_MANIFEST).iterrows():
            dipakai.add((r["source_file"], int(r["start_line"])))

    kandidat = {"god_class": [], "data_class": [], "feature_envy": []}
    py_files = sorted(str(p) for p in POOL.rglob("*.py"))

    for path in py_files:
        try:
            src = open(path, encoding="utf-8").read()
            src_lines = src.splitlines(keepends=True)
            tree = ast.parse(src)
        except Exception:
            continue
        rel = str(Path(path).relative_to(POOL))
        if is_test_file(rel):     # lewati kode tes
            continue

        for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            if (rel, cls.lineno) in dipakai:
                continue
            ms = methods_of(cls)
            n_methods = len(ms)
            n_attrs = len(self_attrs(cls))
            c_sloc = sloc(src_lines, cls.lineno, getattr(cls, "end_lineno", cls.lineno))
            is_dc = has_dataclass_decorator(cls)

            # --- Data Class? (cek dulu krn @dataclass sinyal kuat) ---
            if is_dc or (n_attrs >= DC_MIN_ATTRS and n_methods <= DC_MAX_METHODS):
                skor = (1000 if is_dc else 0) + n_attrs * 10 - n_methods
                kandidat["data_class"].append(
                    (skor, rel, cls.name, cls.lineno,
                     getattr(cls, "end_lineno", cls.lineno),
                     f"attr={n_attrs},method={n_methods},dataclass={is_dc}"))
            # --- God Class? ---
            elif n_methods >= GC_MIN_METHODS and c_sloc >= GC_MIN_SLOC:
                skor = c_sloc + n_methods * 10
                kandidat["god_class"].append(
                    (skor, rel, cls.name, cls.lineno,
                     getattr(cls, "end_lineno", cls.lineno),
                     f"method={n_methods},sloc={c_sloc}"))
            else:
                # --- Feature Envy pada method-method kelas biasa ---
                for m in ms:
                    if (rel, m.lineno) in dipakai:
                        continue
                    sc, ec = fe_counts(m)
                    if ec > sc and ec >= FE_MIN_EXTERNAL:
                        kandidat["feature_envy"].append(
                            (ec - sc, rel, m.name, m.lineno,
                             getattr(m, "end_lineno", m.lineno),
                             f"self={sc},external={ec}"))

    # Urutkan tiap kelas (skor tertinggi dulu), ambil TOP_N, ekstrak cuplikan.
    baris = []
    for label, items in kandidat.items():
        items.sort(key=lambda x: x[0], reverse=True)
        folder = CAND_DIR / label
        folder.mkdir(parents=True, exist_ok=True)
        for i, (skor, rel, nama, start, end, metrik) in enumerate(items[:TOP_N]):
            sid = f"{label[:2]}_cand_{i:03d}"
            # ambil teks cuplikan dari file aslinya
            src_lines = open(POOL / rel, encoding="utf-8").read().splitlines(keepends=True)
            (folder / f"{sid}.py").write_text(potong(src_lines, start, end), encoding="utf-8")
            baris.append({"sample_id": sid, "proposed_label": label,
                          "source_file": rel, "unit_name": nama,
                          "start_line": start, "end_line": end,
                          "score": skor, "metrics": metrik, "final_label": ""})

    pd.DataFrame(baris).to_csv(OUT, index=False)
    print("=== Jumlah kandidat tersaring (teratas per kelas) ===")
    for label in kandidat:
        total = len(kandidat[label])
        disaji = min(total, TOP_N)
        print(f"  {label:<16} ditemukan {total:>4}, disajikan {disaji:>3}")
    print(f"\nCuplikan kandidat: {CAND_DIR}")
    print(f"Daftar kandidat  : {OUT}")


if __name__ == "__main__":
    filter_candidates()
