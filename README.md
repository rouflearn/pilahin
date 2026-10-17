# PILAHIN — Klasifikasi Sampah Berbasis Citra

Aplikasi web Python + Streamlit untuk membantu mengenali sampah dari gambar.

## Jalankan secara lokal

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud

1. Unggah isi repository ini ke GitHub.
2. Buka https://share.streamlit.io dan hubungkan akun GitHub.
3. Pilih **Create app**, repository `pilahin`, branch `main`, file utama `app.py`.
4. Klik **Deploy**.

## Status model dan keterbatasan

Paket deploy menyertakan `weights/best.pt` dari proyek sumber agar aplikasi dapat menemukan model pada path yang diharapkan.
Dataset yang tersedia saat paket dibuat hanya memiliki satu kelas (`plastik`). Karena itu, model ini **belum menjadi model multi-kategori yang tervalidasi** untuk organik, B3, anorganik lain, dan residu. Verifikasi hasil secara manual dan jangan menjadikan hasil model sebagai satu-satunya dasar penanganan limbah berbahaya.

## Berkas utama

- `app.py`: antarmuka Streamlit
- `classifier.py`: pemuatan model dan inferensi
- `config.py`: kategori dan aturan pemetaan
- `algorithms.py`: pengurutan dan rekap
- `weights/best.pt`: bobot model yang disertakan
- `requirements.txt`: dependensi Python

## Tes unit

```bash
python tests/test_all.py
```
