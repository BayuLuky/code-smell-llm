# =====================================================================
# src/data_prep/assemble_dataset.py  —  PERAKITAN DATASET FINAL
# ---------------------------------------------------------------------
# Menyatukan semua sumber label menjadi satu dataset final yang rapi:
#   data/dataset/<language>/<label>/<id>.<ext>   (cuplikan kode)
#   data/dataset/ground_truth.csv                (label + asal-usul)
#
# Sumber:
#   Java MLCQ   : long_method, god_class, feature_envy, data_class, non_smells
#   Java rule   : long_parameter_list
#   Python rule : long_method, long_parameter_list, non_smells
#   Python manual (IRISAN 2 penilai): god_class, data_class, feature_envy
#
# Kelas yang melebihi target dipangkas ke 42 secara reproducible (seed).
# Kelas yang lebih kecil dibiarkan apa adanya.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\assemble_dataset.py
# =====================================================================

import sys
import shutil
import random
import textwrap
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

TARGET = 42
DATASET_DIR = config.DATA_DIR / "dataset"
SUBJ_CLASSES = ["god_class", "data_class", "feature_envy"]
# Dua penilai resmi. HANYA file ini yang dipakai untuk irisan label final,
# sehingga file anotasi lain yang mungkin tertinggal di folder diabaikan.
ANNOTATORS = ["akbar_ts", "erick_wp"]


def manifest_dict(path, key="sample_id"):
    """Baca manifest -> dict {str(sample_id): baris}. Kosong bila tak ada."""
    if not Path(path).exists():
        return {}
    df = pd.read_csv(path)
    df[key] = df[key].astype(str)
    return df.set_index(key).to_dict("index")


def extract_python_unit(source_file, start, end):
    """Ambil ulang cuplikan dari kolam Python (dedent agar valid mandiri)."""
    p = config.RAW_DIR / "python_pool" / source_file
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    return textwrap.dedent("".join(lines[int(start) - 1:int(end)]))


def confirmed_intersection():
    """Unit yang SEMUA penilai resmi sepakat sebagai smell (final_label == kelas).
    Hanya memakai file dua penilai resmi (ANNOTATORS), mengabaikan file lain."""
    files = [config.LABELS_DIR / f"annotations_{n}.csv" for n in ANNOTATORS]
    ada = [f for f in files if f.exists()]
    if len(ada) < len(ANNOTATORS):
        hilang = [n for n, f in zip(ANNOTATORS, files) if not f.exists()]
        print(f"[PERINGATAN] File penilai tidak lengkap, hilang: {hilang}")
    if len(ada) == 0:
        return []
    dfs = []
    for f in ada:
        d = pd.read_csv(f)
        d["sample_id"] = d["sample_id"].astype(str)
        dfs.append(d.set_index("sample_id"))
    base = dfs[0]
    hasil = []
    for sid in base.index:
        label = base.loc[sid, "proposed_label"]
        sepakat = all((sid in d.index) and (d.loc[sid, "final_label"] == label)
                      for d in dfs)
        if sepakat:
            r = base.loc[sid]
            hasil.append((sid, label, r["source_file"],
                          r["start_line"], r["end_line"]))
    return hasil


def gather():
    """Kumpulkan semua sampel sebagai daftar dict."""
    s = []

    # --- JAVA MLCQ (berkas utuh) ---
    jm = manifest_dict(config.LABELS_DIR / "java_mlcq_manifest.csv")
    for label in ["long_method", "god_class", "feature_envy",
                  "data_class", "non_smells"]:
        for f in sorted((config.RAW_DIR / "java" / label).glob("*.java")):
            p = jm.get(f.stem, {})
            src = f"{p.get('repository','')}@{p.get('commit_hash','')}:" \
                  f"{p.get('path','')}:{p.get('start_line','')}-{p.get('end_line','')}"
            s.append({"language": "java", "label": label, "orig": str(f),
                      "key": f.stem, "label_source": "mlcq", "source": src})

    # --- JAVA Long Parameter List (aturan) ---
    jl = manifest_dict(config.LABELS_DIR / "lpl_java_manifest.csv")
    for f in sorted((config.RAW_DIR / "java" / "long_parameter_list").glob("*.java")):
        p = jl.get(f.stem, {})
        src = f"{p.get('repository','')}@{p.get('commit_hash','')}:{p.get('path','')}"
        s.append({"language": "java", "label": "long_parameter_list", "orig": str(f),
                  "key": f.stem, "label_source": "rule:param_count", "source": src})

    # --- PYTHON objektif (cuplikan sudah ada) ---
    po = manifest_dict(config.LABELS_DIR / "python_objective_manifest.csv")
    for label in ["long_method", "long_parameter_list"]:
        for f in sorted((config.RAW_DIR / "python" / label).glob("*.py")):
            p = po.get(f.stem, {})
            src = f"{p.get('source_file','')}:{p.get('start_line','')}"
            s.append({"language": "python", "label": label, "orig": str(f),
                      "key": f.stem, "label_source": "rule", "source": src})

    # --- PYTHON subjektif (irisan 2 penilai; ekstrak ulang dari kolam) ---
    for sid, label, sf, st, en in confirmed_intersection():
        s.append({"language": "python", "label": label,
                  "text": extract_python_unit(sf, st, en),
                  "key": f"{sf}:{st}", "label_source": "manual:both_agree",
                  "source": f"{sf}:{st}-{en}"})

    # --- PYTHON non_smells (cuplikan sudah ada) ---
    pn = manifest_dict(config.LABELS_DIR / "python_nonsmells_manifest.csv")
    for f in sorted((config.RAW_DIR / "python" / "non_smells").glob("*.py")):
        p = pn.get(f.stem, {})
        src = f"{p.get('source_file','')}:{p.get('start_line','')}"
        s.append({"language": "python", "label": "non_smells", "orig": str(f),
                  "key": f.stem, "label_source": "rule:clean", "source": src})

    return s


def assemble():
    samples = gather()
    groups = defaultdict(list)
    for x in samples:
        groups[(x["language"], x["label"])].append(x)

    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)   # mulai bersih

    rows = []
    for (lang, label), items in sorted(groups.items()):
        items.sort(key=lambda d: d["key"])           # urut stabil
        if len(items) > TARGET:                       # pangkas reproducible
            items = sorted(random.Random(config.RANDOM_SEED).sample(items, TARGET),
                           key=lambda d: d["key"])
        outdir = DATASET_DIR / lang / label
        outdir.mkdir(parents=True, exist_ok=True)
        ext = "java" if lang == "java" else "py"
        for i, x in enumerate(items, 1):
            nid = f"{lang}_{label}_{i:03d}"
            dest = outdir / f"{nid}.{ext}"
            if "text" in x:
                dest.write_text(x["text"], encoding="utf-8")
            else:
                shutil.copy(x["orig"], dest)
            rows.append({"id": nid, "language": lang, "label": label,
                         "code_path": str(dest.relative_to(DATASET_DIR)),
                         "label_source": x["label_source"], "source": x["source"]})

    gt = pd.DataFrame(rows)
    gt.to_csv(DATASET_DIR / "ground_truth.csv", index=False)

    print("=== DATASET FINAL TERAKIT ===")
    piv = gt.pivot_table(index="label", columns="language",
                         values="id", aggfunc="count", fill_value=0)
    print(piv.to_string())
    print(f"\nTOTAL SAMPEL: {len(gt)}")
    print(f"Kode    : {DATASET_DIR}\\<language>\\<label>\\")
    print(f"Label   : {DATASET_DIR / 'ground_truth.csv'}")


if __name__ == "__main__":
    assemble()
