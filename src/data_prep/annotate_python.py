# =====================================================================
# src/data_prep/annotate_python.py  —  ALAT ANOTASI MANUAL TERPANDU
# ---------------------------------------------------------------------
# Menyajikan kandidat smell subjektif (dari filter_python_candidates.py)
# satu per satu, urut dari skor tertinggi, lalu Anda memberi keputusan:
#   [y] ya, ini smell-nya     [n] bukan
#   [s] lewati                [o] buka cuplikan di editor
#   [u] batalkan keputusan terakhir
#   [q] simpan & keluar
#
# Keputusan disimpan per-penilai ke data/labels/annotations_<nama>.csv
# (mendukung penilai kedua untuk uji kappa). Resumable & berhenti otomatis
# saat sebuah kelas mencapai 42 terkonfirmasi.
#
# Jalankan dari folder utama proyek:
#     python src\data_prep\annotate_python.py
# =====================================================================

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config
import pandas as pd

CAND_CSV = config.LABELS_DIR / "python_candidates.csv"
CAND_DIR = config.RAW_DIR / "python" / "_candidates"
TARGET = 42
CLASSES = ["god_class", "data_class", "feature_envy"]


def ann_path(nama):
    return config.LABELS_DIR / f"annotations_{nama}.csv"


def load_decisions(nama):
    p = ann_path(nama)
    if p.exists():
        try:
            return pd.read_csv(p).to_dict("records")
        except Exception:
            return []
    return []


def save_decisions(nama, decisions):
    pd.DataFrame(decisions).to_csv(ann_path(nama), index=False)


def confirmed_counts(decisions):
    c = {k: 0 for k in CLASSES}
    for d in decisions:
        if d["final_label"] in c:
            c[d["final_label"]] += 1
    return c


def preview(snippet_path, n=40):
    try:
        lines = Path(snippet_path).read_text(encoding="utf-8").splitlines()
    except Exception:
        print("   (cuplikan tidak ditemukan)")
        return
    for ln in lines[:n]:
        print("   | " + ln)
    if len(lines) > n:
        print(f"   ... ({len(lines) - n} baris lagi — tekan 'o' untuk buka penuh)")


def main():
    if not CAND_CSV.exists():
        print("Daftar kandidat belum ada. Jalankan filter_python_candidates.py dulu.")
        return

    df = pd.read_csv(CAND_CSV)
    nama = input("Nama penilai (mis. bayu): ").strip() or "anon"
    decisions = load_decisions(nama)
    decided = {d["sample_id"] for d in decisions}
    counts = confirmed_counts(decisions)
    session = []   # urutan sample_id yg diputuskan di sesi ini (untuk undo)

    print(f"\nMemuat {len(decisions)} keputusan sebelumnya.")
    print(f"Terkonfirmasi sejauh ini: {counts}\n")

    for label in CLASSES:
        sub = df[df["proposed_label"] == label].sort_values("score", ascending=False)
        for _, row in sub.iterrows():
            if counts[label] >= TARGET:
                break
            if row["sample_id"] in decided:
                continue

            while True:
                print("\n" + "=" * 64)
                print(f"[{label}]  terkonfirmasi {counts[label]}/{TARGET}")
                print(f"  id     : {row['sample_id']}")
                print(f"  sumber : {row['source_file']}  (unit: {row['unit_name']})")
                print(f"  metrik : {row['metrics']}   skor {row['score']}")
                print("-" * 64)
                snip = CAND_DIR / label / f"{row['sample_id']}.py"
                preview(snip)
                print("-" * 64)
                jwb = input("  [y]a [n]o [s]kip [o]pen [u]ndo [q]uit > ").strip().lower()

                if jwb == "o":
                    try:
                        os.startfile(str(snip))   # Windows: buka di app default
                    except Exception as e:
                        print(f"  (tak bisa membuka: {e})")
                    continue

                if jwb == "u":
                    if session:
                        last = session.pop()
                        decisions = [d for d in decisions if d["sample_id"] != last]
                        decided.discard(last)
                        counts = confirmed_counts(decisions)
                        save_decisions(nama, decisions)
                        print(f"  (dibatalkan: {last} — akan muncul lagi di sesi berikutnya)")
                    else:
                        print("  (belum ada keputusan di sesi ini untuk dibatalkan)")
                    continue

                if jwb == "q":
                    save_decisions(nama, decisions)
                    print(f"\nTersimpan ke {ann_path(nama)}. Terkonfirmasi: {confirmed_counts(decisions)}")
                    return

                if jwb in ("y", "n", "s"):
                    final = label if jwb == "y" else ("tidak" if jwb == "n" else "skip")
                    decisions.append({
                        "sample_id": row["sample_id"], "proposed_label": label,
                        "final_label": final, "source_file": row["source_file"],
                        "unit_name": row["unit_name"], "start_line": row["start_line"],
                        "end_line": row["end_line"], "annotator": nama})
                    decided.add(row["sample_id"])
                    session.append(row["sample_id"])
                    if final == label:
                        counts[label] += 1
                    save_decisions(nama, decisions)
                    break

                print("  (input tidak dikenal — ketik y, n, s, o, u, atau q)")

    print(f"\nSelesai meninjau semua kandidat. Terkonfirmasi akhir: {confirmed_counts(decisions)}")
    save_decisions(nama, decisions)


if __name__ == "__main__":
    main()
