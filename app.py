"""PILAHIN v2 (tampilan Jalur Sampah). Jalankan: streamlit run app.py"""
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from algorithms import count_by, merge_sort
from classifier import WasteClassifier
from components import (CSS, NOTE_HTML, empty_html, hero_html, queue_html, recap_html,
                        steps_panel, thumb_b64, top3_panel, topbar_html, wrap)
from config import BINS, DEFAULT_THRESHOLD, IMAGE_TYPES, bin_priority

st.set_page_config(page_title="PILAHIN", page_icon="♻️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


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
    rows, thumbs = [], {}
    bar = st.progress(0.0, text="Menganalisis...")
    for i, f in enumerate(files, start=1):
        name = getattr(f, "name", None) or "foto.jpg"
        try:
            img = load_image(f)
            res = clf.predict(img, threshold)
        except Exception as e:  # satu file rusak tidak menghentikan semuanya
            st.warning(f"Lewati {name}: {e}")
            continue
        res.update(file=name, id=f"{i}_{name}", waktu=datetime.now().strftime("%H:%M:%S"),
                   sig=(getattr(f, "file_id", None) or f"{i}_{name}", threshold))
        rows.append(res)
        thumbs[res["id"]] = thumb_b64(img)
        bar.progress(i / len(files), text=f"Menganalisis {i}/{len(files)}")
    bar.empty()
    return rows, thumbs


def remember(rows):
    """Simpan ke riwayat sekali saja (Streamlit menjalankan ulang skrip tiap interaksi)."""
    seen = {r["sig"] for r in st.session_state.history}
    st.session_state.history.extend(r for r in rows if r["sig"] not in seen)


def to_table(rows):
    return pd.DataFrame([{
        "Urutan": i, "File": r["file"], "Objek": r["label"],
        "Tong": BINS[r["bin_key"]]["name"], "Keyakinan (%)": round(r["confidence"] * 100, 1),
        "Waktu": r["waktu"]} for i, r in enumerate(rows, start=1)])


def show_df(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:  # Streamlit versi lama
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_results(rows, thumbs, sort_mode, threshold, mode):
    key = {"Prioritas penanganan": lambda r: (bin_priority(r["bin_key"]), -r["confidence"]),
           "Keyakinan tertinggi": lambda r: -r["confidence"],
           "Nama file": lambda r: r["file"].lower()}[sort_mode]
    ordered = merge_sort(rows, key)  # Merge Sort

    st.markdown(wrap(topbar_html(len(rows), threshold, mode)), unsafe_allow_html=True)
    if len(ordered) > 1:
        labels = {r["id"]: f"{i}. {r['file']}  ·  {r['label']}" for i, r in enumerate(ordered, 1)}
        chosen = st.selectbox("Foto yang ditampilkan di jalur", list(labels), format_func=labels.get)
        res = next(r for r in ordered if r["id"] == chosen)
    else:
        res = ordered[0]

    body = wrap(
        hero_html(res, thumbs[res["id"]], threshold),
        '<div class="pl-row">' + top3_panel(res) + steps_panel(res) + "</div>",
        recap_html(ordered),   # Counter
        queue_html(ordered),   # Priority Queue (heap)
        NOTE_HTML,
    )
    st.markdown(body, unsafe_allow_html=True)
    with st.expander("Tabel hasil (diurutkan dengan Merge Sort)"):
        show_df(to_table(ordered))


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Pengaturan")
    threshold = st.slider("Ambang keyakinan", 0.30, 0.95, DEFAULT_THRESHOLD, 0.05,
                          help="Di bawah ambang -> 'Perlu Verifikasi' (tidak menebak).")
    sort_mode = st.selectbox("Urutkan hasil", ["Prioritas penanganan", "Keyakinan tertinggi", "Nama file"])

clf = get_classifier()
if clf.mode == "demo":
    st.warning("Model terlatih (weights/best.pt) belum ada, jadi memakai model umum COCO. "
               "Hasil hanya demonstrasi. Jalankan train.py untuk hasil yang valid.")

st.session_state.setdefault("history", [])
tab_up, tab_cam, tab_live, tab_hist, tab_about = st.tabs(
    ["📤 Unggah", "📷 Kamera", "🎥 Live", "📊 Riwayat", "ℹ️ Tentang"])


def empty_state():
    st.markdown(wrap(topbar_html(0, threshold, clf.mode), empty_html()), unsafe_allow_html=True)


with tab_up:
    files = st.file_uploader("Pilih satu atau banyak gambar", type=IMAGE_TYPES, accept_multiple_files=True)
    if files:
        rows, thumbs = analyze(files, threshold)
        if rows:
            remember(rows)
            render_results(rows, thumbs, sort_mode, threshold, clf.mode)
    else:
        empty_state()

with tab_cam:
    shot = st.camera_input("Ambil foto sampah")
    if shot:
        rows, thumbs = analyze([shot], threshold)
        if rows:
            remember(rows)
            render_results(rows, thumbs, sort_mode, threshold, clf.mode)

with tab_live:
    st.caption("Arahkan benda ke kamera; hasil muncul otomatis tanpa perlu jepret foto. "
               "Klik START dan izinkan kamera di browser.")
    try:
        from streamlit_webrtc import WebRtcMode, webrtc_streamer
        from webrtc_live import LiveProcessor
    except ImportError:
        st.info("Fitur ini butuh paket tambahan. Jalankan: pip install streamlit-webrtc lalu mulai ulang aplikasi. "
                "Alternatif tanpa paket: python live.py (jendela terpisah).")
    else:
        every = st.select_slider("Seberapa sering memprediksi", options=[2, 3, 5, 8, 12], value=5,
                                 help="Angka kecil = lebih responsif tapi lebih berat. Naikkan bila video patah-patah.")
        ctx = webrtc_streamer(
            key="pilahin-live", mode=WebRtcMode.SENDRECV,
            video_processor_factory=lambda: LiveProcessor(clf, threshold, every),
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            async_processing=True,
        )
        box = st.empty()
        while ctx.state.playing:
            proc = ctx.video_processor
            if proc is not None:
                proc.set_threshold(threshold)
                shown, latest, thumb = proc.snapshot()
                if shown and latest:
                    key, label, conf = shown
                    res = dict(latest, bin_key=key, label=label, confidence=conf)
                    box.markdown(wrap(hero_html(res, thumb, threshold), steps_panel(res)), unsafe_allow_html=True)
            time.sleep(0.4)
        if not ctx.state.playing:
            box.empty()

with tab_hist:
    hist = st.session_state.history
    if not hist:
        st.info("Belum ada riwayat sesi ini.")
    else:
        st.markdown(wrap(recap_html(hist)), unsafe_allow_html=True)
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
**Alur:** foto → klasifikasi (YOLO11n-cls) → jika keyakinan ≥ ambang, kelas dipetakan ke tong
(Organik / Anorganik Daur Ulang / B3 / Residu), jika tidak → *Perlu Verifikasi*.

**Algoritma:** Merge Sort (urut hasil), Counter (rekap), Priority Queue/heap (antrean penanganan).

**Batasan:** model hanya mengenal kelas dataset latihnya, akurasi bergantung pada kualitas foto,
dan aturan prioritas/tong adalah penyederhanaan. Aturan pemilahan resmi dapat berbeda di tiap daerah.
""")
