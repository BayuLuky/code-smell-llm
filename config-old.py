# =====================================================================
# config.py  —  PUSAT PENGATURAN PROYEK
# ---------------------------------------------------------------------
# File ini berisi semua "nilai tetap" (konstanta) yang dipakai di
# banyak tempat: nama kelas, lokasi folder, jumlah target sampel, dll.
# Tujuannya: kalau suatu saat perlu ganti nilai, cukup ubah DI SINI,
# tidak perlu cari-cari di banyak file. Ini praktik baik untuk menjaga
# REPRODUCIBILITY (hasil bisa diulang) seperti yang Anda janjikan di
# proposal.
# =====================================================================

from pathlib import Path  # alat bawaan Python untuk mengelola path folder

# ---------------------------------------------------------------------
# 1) LOKASI FOLDER
# ---------------------------------------------------------------------
# __file__ = lokasi file config.py ini. .parent = folder induknya.
# Jadi ROOT = folder utama proyek (code-smell-llm/), apa pun komputernya.
ROOT = Path(__file__).parent

DATA_DIR      = ROOT / "data"              # tanda "/" menyambung path
MLCQ_DIR      = DATA_DIR / "mlcq"          # CSV mentah MLCQ
RAW_DIR       = DATA_DIR / "raw"           # berkas .java / .py asli
PROCESSED_DIR = DATA_DIR / "processed"     # setelah pra-pemrosesan
LABELS_DIR    = DATA_DIR / "labels"        # ground_truth.csv

RESULTS_DIR     = ROOT / "results"
PREDICTIONS_DIR = RESULTS_DIR / "predictions"  # output tiap metode
METRICS_DIR     = RESULTS_DIR / "metrics"      # tabel hasil
FIGURES_DIR     = RESULTS_DIR / "figures"      # grafik Bab IV

# ---------------------------------------------------------------------
# 2) ENAM KELAS TARGET (5 smell + 1 non-smells)
# ---------------------------------------------------------------------
# URUTAN DAFTAR INI PENTING dan tidak boleh diubah sembarangan, karena
# nanti dipakai sebagai urutan baris/kolom pada confusion matrix 6x6.
# Memakai huruf kecil & garis bawah supaya konsisten dan mudah diproses.
CLASSES = [
    "long_method",          # indeks 0
    "god_class",            # indeks 1
    "feature_envy",         # indeks 2
    "data_class",           # indeks 3
    "long_parameter_list",  # indeks 4
    "non_smells",           # indeks 5  (kelas negatif / kode bersih)
]

# Nama "cantik" untuk ditampilkan di tabel & grafik tesis nanti.
CLASS_DISPLAY = {
    "long_method":          "Long Method",
    "god_class":            "God Class",
    "feature_envy":         "Feature Envy",
    "data_class":           "Data Class",
    "long_parameter_list":  "Long Parameter List",
    "non_smells":           "Non-Smells",
}

# ---------------------------------------------------------------------
# 3) TARGET JUMLAH SAMPEL (sesuai Subbab Ruang Lingkup)
# ---------------------------------------------------------------------
TOTAL_FILES    = 500          # total berkas
FILES_PER_LANG = 250          # 250 Java + 250 Python
LANGUAGES      = ["java", "python"]

# Stratified: usahakan seimbang antar 6 kelas pada tiap bahasa.
# 250 berkas / 6 kelas ≈ 42 per kelas. Angka ini jadi acuan sampling.
TARGET_PER_CLASS_PER_LANG = FILES_PER_LANG // len(CLASSES)  # = 41

# ---------------------------------------------------------------------
# 4) PEMETAAN SONARQUBE RULE -> KELAS  (Tabel 3.6 di proposal Anda)
# ---------------------------------------------------------------------
# Kunci = kelas target; nilai = daftar Rule ID SonarQube yang dianggap
# mewakili kelas tersebut. Dipakai saat menerjemahkan output SonarQube
# (Tahap 2) menjadi salah satu dari 6 kelas.
SONARQUBE_RULE_MAP = {
    "long_method":         ["java:S138", "python:S138"],
    "god_class":           ["java:S1200", "java:S2972"],
    "feature_envy":        ["java:S1448"],            # + heuristik (Tahap 2)
    "data_class":          ["java:S1820"],            # partial mapping
    "long_parameter_list": ["java:S107", "python:S107"],
}

# ---------------------------------------------------------------------
# 5) PENGATURAN REPRODUCIBILITY
# ---------------------------------------------------------------------
# "Seed" adalah angka awal untuk pengacakan. Dengan seed yang sama,
# hasil sampling acak akan SELALU sama setiap dijalankan -> bisa diulang
# oleh penguji/peneliti lain. Wajib untuk skripsi/tesis.
RANDOM_SEED = 42

# Ambang batas (threshold) referensi, sejalan dengan SonarQube default.
THRESHOLDS = {
    "long_method_lines":        150,  # java:S138 default
    "long_parameter_list_count": 7,   # java:S107 / python:S107 default
}

# ---------------------------------------------------------------------
# 6) FUNGSI BANTU: pastikan semua folder ada
# ---------------------------------------------------------------------
def ensure_dirs():
    """Membuat semua folder data/hasil bila belum ada (aman dipanggil
    berulang kali)."""
    for d in [MLCQ_DIR, RAW_DIR, PROCESSED_DIR, LABELS_DIR,
              PREDICTIONS_DIR, METRICS_DIR, FIGURES_DIR]:
        for lang in LANGUAGES:
            # buat subfolder per bahasa di dalam raw/ dan processed/
            if d in (RAW_DIR, PROCESSED_DIR):
                (d / lang).mkdir(parents=True, exist_ok=True)
        d.mkdir(parents=True, exist_ok=True)


# Bila file ini dijalankan langsung (python config.py), buat foldernya
# dan tampilkan ringkasan. Bila hanya di-"import" file lain, baris ini
# tidak dijalankan.
if __name__ == "__main__":
    ensure_dirs()
    print("Folder data & hasil siap.")
    print(f"Jumlah kelas target : {len(CLASSES)}")
    print(f"Target total berkas : {TOTAL_FILES}")
