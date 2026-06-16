# Evaluasi LLM untuk Deteksi Code Smells

Implementasi tesis: perbandingan **SonarQube**, **UniXcoder**, dan
**Qwen2.5-Coder** untuk mendeteksi 5 code smells pada 500 berkas
(250 Java + 250 Python), dengan skema klasifikasi 6 kelas.

## Cara memulai (sekali saja)

```bash
# 1) Buat struktur folder
python setup_project.py

# 2) Pasang library lokal (data prep + evaluasi)
pip install -r requirements.txt
```

## Peta jalan tahapan

| Tahap | Isi | Lingkungan |
|-------|-----|------------|
| 1 | Persiapan data + ground truth | Lokal |
| 2 | Baseline SonarQube | Lokal (Docker) |
| 3 | Qwen2.5-Coder (prompt engineering) | Google Colab (T4) |
| 4 | UniXcoder (fine-tuning) | Google Colab (T4) |
| 5 | Pipeline evaluasi (metrik + statistik) | Lokal |
| 6 | Visualisasi (8 grafik) | Lokal |
| 7 | Tulis Bab IV (jawab RM 1-4) | - |
| 8 | Tulis Bab V (simpulan & saran) | - |

## Struktur folder

- `data/`  — data mentah, olahan, dan label
- `src/`   — kode program (data_prep, detectors, evaluation)
- `results/` — prediksi, tabel metrik, dan gambar untuk Bab IV
- `notebooks/` — notebook Colab untuk menjalankan model
- `config.py` — semua pengaturan terpusat
