# PILAHIN — Klasifikasi Sampah Berbasis Citra

Aplikasi web berbasis Python dan Streamlit untuk membantu mengenali sampah dari gambar menggunakan model kecerdasan buatan (AI).

## Fitur Utama

- Unggah dan analisis gambar sampah.
- Klasifikasi gambar menggunakan model AI.
- Antarmuka web berbasis Streamlit.
- Pemrosesan model melalui Python.

## Persyaratan

- Python 3.10 atau versi yang kompatibel dengan dependensi aplikasi.
- pip.
- Model AI pada `weights/best.pt`.

## Menjalankan Aplikasi Secara Lokal

1. Buat virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Aktifkan virtual environment.

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   Git Bash:

   ```bash
   source .venv/Scripts/activate
   ```

   macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Instal dependensi:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi:

   ```bash
   streamlit run app.py
   ```

## Deploy ke Streamlit Community Cloud

1. Unggah seluruh berkas aplikasi ke repository GitHub.
2. Buka https://share.streamlit.io.
3. Hubungkan akun GitHub.
4. Pilih **Create app**.
5. Pilih repository `rouflearn/pilahin`.
6. Pilih branch `main`.
7. Atur file utama menjadi `app.py`.
8. Klik **Deploy**.

## Struktur Berkas Utama

- `app.py`: antarmuka utama Streamlit.
- `classifier.py`: pemuatan model dan proses inferensi.
- `config.py`: konfigurasi kategori dan pemetaan.
- `algorithms.py`: fungsi pengurutan dan rekapitulasi.
- `ui.py`: komponen antarmuka.
- `weights/best.pt`: bobot model AI.
- `requirements.txt`: daftar dependensi Python.
- `tests/test_all.py`: pengujian aplikasi.

## Status Model dan Keterbatasan

Paket aplikasi menyertakan model pada `weights/best.pt` agar aplikasi dapat menemukan berkas model pada lokasi yang diharapkan.

Dataset yang tersedia saat paket dibuat hanya memiliki satu kelas, yaitu `plastik`. Oleh karena itu, model ini belum tervalidasi untuk mengklasifikasikan berbagai kategori sampah seperti organik, B3, anorganik lainnya, dan residu.

Hasil prediksi perlu diperiksa secara manual. Jangan menjadikan prediksi model sebagai satu-satunya dasar untuk menentukan penanganan limbah berbahaya.

## Menjalankan Tes

Jalankan perintah berikut dari direktori utama repository:

```bash
python tests/test_all.py
```

## Lisensi dan Pengembangan

Silakan tambahkan informasi lisensi dan kontribusi sesuai kebijakan pengembangan proyek PILAHIN.
