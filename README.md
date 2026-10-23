# PILAHIN v2 — Klasifikasi Sampah ke Tong yang Tepat

Foto sampah → model klasifikasi (YOLO11n-cls) → tong: **Organik / Anorganik Daur Ulang / B3 / Residu**.
Keyakinan rendah → **Perlu Verifikasi** (aplikasi tidak menebak).

Algoritma: Merge Sort (urut hasil), Counter (rekap), Priority Queue/heap (antrean penanganan).

## Struktur
| File | Fungsi |
|---|---|
| `app.py` | Aplikasi Streamlit (unggah, kamera, riwayat) |
| `live.py` | Deteksi real-time dari webcam / kamera tambahan (OpenCV) |
| `webrtc_live.py` | Pemroses video untuk tab Live di aplikasi web (streamlit-webrtc) |
| `components.py` | Pembuat HTML tampilan Jalur Sampah (cincin, tong, panel) |
| `config.py` | Kelas → tong, prioritas, tips |
| `classifier.py` | Model terlatih; otomatis mode demo (COCO) bila `weights/best.pt` belum ada |
| `algorithms.py` | Merge Sort, Counter, Priority Queue |
| `prepare_dataset.py` | Bagi dataset jadi train/val/test |
| `train.py`, `evaluate.py` | Latih dan evaluasi |
| `ringkas_hasil.py` | Merangkum jumlah dataset, akurasi, dan akurasi per kelas untuk laporan |
| `tests/test_all.py` | Tes (`python tests/test_all.py`) |

## Instalasi (Windows)
```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python tests\test_all.py
streamlit run app.py
```
Tanpa model terlatih, app berjalan di **mode demo** (model COCO) agar UI bisa dicoba dulu.

## Dataset
Disarankan *Garbage Classification (12 classes)* (Kaggle; berisi battery, biological, brown/green/white-glass,
cardboard, clothes, metal, paper, plastic, shoes, trash) atau TrashNet (6 kelas, tanpa baterai/organik).
Periksa lisensi dan unduh sendiri, lalu:
```
python prepare_dataset.py --src garbage_classification --dst dataset
python train.py --data dataset --epochs 20      # CPU lambat -> pakai Google Colab (GPU)
python evaluate.py --data dataset/test
```
`train.py` menyalin hasil terbaik ke `weights/best.pt`. Nama kelas baru cukup ditambahkan di `CLASS_TO_BIN` (`config.py`);
kelas tak dikenal otomatis menjadi *Perlu Verifikasi*.

## Rencana 4 hari
**Hari 1 — Fondasi & data**
- Instal Python + venv, jalankan `tests`, jalankan app mode demo (pastikan UI tampil).
- Unduh dataset, `prepare_dataset.py`, cek jumlah gambar per kelas dan beberapa gambar secara visual.
- Latih cepat 3–5 epoch sebagai uji alur. *Output:* `best.pt` awal.

**Hari 2 — Model**
- Latih penuh (15–30 epoch, Colab bila perlu). Jalankan `evaluate.py`.
- Baca confusion matrix: kelas mana yang tertukar (mis. paper↔cardboard, glass↔plastic)? Catat sebagai pembahasan.
- Tentukan ambang keyakinan (default 0.60) dengan melihat benar/salah di berbagai nilai. *Output:* `weights/best.pt`, tabel akurasi.

**Hari 3 — Aplikasi**
- Pasang `best.pt`, uji unggah satu/banyak gambar, kamera, riwayat, ekspor CSV.
- Tampilan sudah final (layout "Jalur Sampah", di `components.py`).
- Uji dengan foto sendiri (cahaya buruk, objek ganda, latar ramai) dan catat kegagalan.

**Hari 4 — Rapikan & presentasi**
- Perbaiki bug dari uji Hari 3, jalankan `tests`, bersihkan README.
- Siapkan laporan/slide: masalah, dataset, algoritma + alasan, hasil evaluasi, batasan, demo.
- Cadangan: latih ulang bila ada kelas lemah. *Jika hanya 3 hari:* gabungkan Hari 3 dan 4, lewati kamera dan skin.

## Batasan
- Satu gambar = satu objek utama; foto berisi banyak jenis sampah akan membingungkan model.
- Akurasi dataset publik ≠ akurasi di lapangan; selalu uji dengan foto sendiri.
- Pemetaan tong dan urutan prioritas adalah penyederhanaan; aturan pemilahan resmi berbeda tiap daerah.
- Aplikasi ini belum diuji menjalankan Streamlit/YOLO di lingkungan pembuatnya (hanya logika non-model yang diuji).
