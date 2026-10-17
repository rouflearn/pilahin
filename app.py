"""PILAHIN v2 — klasifikasi sampah -> tong yang tepat. Jalankan: streamlit run app.py"""
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from algorithms import PriorityQueue, count_by, merge_sort
from classifier import WasteClassifier
from config import BINS, DEFAULT_THRESHOLD, IMAGE_TYPES, bin_priority
from ui import (DEFAULT_SKIN, SKINS, apply_skin, bin_badge, hero, result_card,
                show_df, show_image)

st.set_page_config(page_title="PILAHIN", page_icon="♻️", layout="wide")


@st.cache_resource(show_spinner="Memuat model...")
def get_classifier():
    return WasteClassifier()


def load_image(file):
    """Buka gambar, perbaiki rotasi EXIF, dan kecilkan agar cepat diproses."""
    img = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
    img.thumbnail((1280, 1280))
    return img


def analyze(files, threshold):
    clf = get_classifier()
    rows, images = [], {}
    bar = st.progress(0.0, text="Menganalisis...")
    for i, f in enumerate(files, start=1):
        name = getattr(f, "name", None) or "foto.jpg"
        try:
            img = load_image(f)
            res = clf.predict(img, threshold)
        except Exception as e:  # satu file rusak tidak boleh menghentikan semuanya
            st.warning(f"Lewati {name}: {e}")
            continue
        res.update(file=name, id=f"{i}_{name}", waktu=datetime.now().strftime("%H:%M:%S"),
                   sig=(getattr(f, "file_id", None) or f"{i}_{name}", threshold))
        rows.append(res); images[res["id"]] = img
        bar.progress(i / len(files), text=f"Menganalisis {i}/{len(files)}")
    bar.empty()
    return rows, images


def remember(rows):
    """Simpan ke riwayat sekali saja (Streamlit menjalankan ulang skrip tiap interaksi)."""
    seen = {r["sig"] for r in st.session_state.history}
    st.session_state.history.extend(r for r in rows if r["sig"] not in seen)


def to_table(rows):
    return pd.DataFrame([{
        "Urutan": i, "File": r["file"], "Objek": r["label"],
        "Tong": BINS[r["bin_key"]]["name"], "Keyakinan (%)": round(r["confidence"] * 100, 1),
        "Waktu": r["waktu"]} for i, r in enumerate(rows, start=1)])


def render_results(rows, images, sort_mode):
    key = {"Prioritas penanganan": lambda r: (bin_priority(r["bin_key"]), -r["confidence"]),
           "Keyakinan tertinggi": lambda r: -r["confidence"],
           "Nama file": lambda r: r["file"].lower()}[sort_mode]
    ordered = merge_sort(rows, key)  # Merge Sort

    if len(ordered) == 1:
        r = ordered[0]
        c1, c2 = st.columns([1, 1])
        with c1:
            show_image(images[r["id"]])
        with c2:
            result_card(r, r["file"])
            st.markdown("**3 kemungkinan teratas**")
            st.bar_chart(pd.DataFrame(r["top3"], columns=["Kelas", "Keyakinan"]).set_index("Kelas"))
    else:
        counts = count_by(rows, "bin_key")  # Counter
        cols = st.columns(len(BINS))
        for col, (k, b) in zip(cols, BINS.items()):
            col.metric(f"{b['emoji']} {b['name']}", counts.get(k, 0))
        st.markdown("#### Antrean penanganan (Priority Queue)")
        pq = PriorityQueue()
        for r in rows:
            pq.push(r, bin_priority(r["bin_key"]))
        for pos, r in enumerate(pq.to_list(), start=1):
            st.markdown(f"**{pos}.** {bin_badge(r['bin_key'])} &nbsp; {r['label']} "
                        f"<span class='pl-muted'>({r['file']}, {r['confidence']:.0%})</span>",
                        unsafe_allow_html=True)
        st.markdown("#### Galeri")
        gcols = st.columns(4)
        for i, r in enumerate(ordered):
            with gcols[i % 4]:
                show_image(images[r["id"]])
                st.markdown(f"{bin_badge(r['bin_key'])}<br><b>{r['label']}</b> {r['confidence']:.0%}",
                            unsafe_allow_html=True)
    with st.expander("Tabel hasil"):
        show_df(to_table(ordered))


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Pengaturan")
    skin = st.selectbox("Tampilan", list(SKINS), index=list(SKINS).index(DEFAULT_SKIN))
    threshold = st.slider("Ambang keyakinan", 0.30, 0.95, DEFAULT_THRESHOLD, 0.05,
                          help="Di bawah ambang -> 'Perlu Verifikasi' (tidak menebak).")
    sort_mode = st.selectbox("Urutkan hasil", ["Prioritas penanganan", "Keyakinan tertinggi", "Nama file"])
    st.caption("Tip: mode gelap Streamlit bisa dipilih lewat menu ⋮ → Settings → Theme.")

apply_skin(skin)
clf = get_classifier()
hero("PILAHIN", "Foto sampahmu, dapatkan tong yang tepat.", clf.mode)
if clf.mode == "demo":
    st.warning("Model terlatih (weights/best.pt) belum ada, jadi memakai model umum COCO. "
               "Hasil hanya demonstrasi. Jalankan train.py untuk hasil yang valid.")

st.session_state.setdefault("history", [])
tab_up, tab_cam, tab_hist, tab_about = st.tabs(["📤 Unggah", "📷 Kamera", "📊 Riwayat", "ℹ️ Tentang"])

with tab_up:
    files = st.file_uploader("Pilih satu atau banyak gambar", type=IMAGE_TYPES, accept_multiple_files=True)
    if files:
        rows, images = analyze(files, threshold)
        if rows:
            remember(rows)
            render_results(rows, images, sort_mode)
    else:
        st.info("Unggah gambar untuk memulai.")

with tab_cam:
    shot = st.camera_input("Ambil foto sampah")
    if shot:
        rows, images = analyze([shot], threshold)
        if rows:
            remember(rows)
            render_results(rows, images, sort_mode)

with tab_hist:
    hist = st.session_state.history
    if not hist:
        st.info("Belum ada riwayat sesi ini.")
    else:
        counts = count_by(hist, "bin_key")
        st.bar_chart(pd.DataFrame({"Jumlah": {BINS[k]["name"]: v for k, v in counts.items()}}))
        df = to_table(hist)
        show_df(df)
        c1, c2 = st.columns(2)
        c1.download_button("Unduh CSV", df.to_csv(index=False).encode("utf-8-sig"),
                           "riwayat_pilahin.csv", "text/csv")
        if c2.button("Hapus riwayat"):
            st.session_state.history = []
            st.rerun()

with tab_about:
    st.markdown("""
**Alur:** gambar → klasifikasi (YOLO11n-cls) → jika keyakinan ≥ ambang, kelas dipetakan ke tong
(Organik / Anorganik Daur Ulang / B3 / Residu), jika tidak → *Perlu Verifikasi*.

**Algoritma:** Merge Sort (urut hasil), Counter (rekap), Priority Queue/heap (antrean penanganan).

**Batasan:** model hanya mengenal kelas dataset latihnya, akurasi bergantung pada kualitas foto,
dan aturan prioritas/tong adalah penyederhanaan. Aturan pemilahan resmi dapat berbeda di tiap daerah.
""")
