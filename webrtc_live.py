"""Deteksi real-time di dalam aplikasi Streamlit (streamlit-webrtc).

Video dari kamera browser diproses frame demi frame; hasil terakhir dibaca
tab Live di app.py. Impor `av`/`cv2` ditunda agar modul mudah diuji.
"""
import threading
from collections import deque

import numpy as np
from PIL import Image

from components import thumb_b64
from config import BINS, DEFAULT_THRESHOLD
from live import draw_banner, hex_to_bgr, smooth


class LiveProcessor:
    """Prediksi tiap N frame, haluskan beberapa hasil terakhir, simpan hasil terbaru."""

    def __init__(self, clf, threshold=DEFAULT_THRESHOLD, every=5, smooth_n=5):
        self.clf, self.threshold, self.every = clf, threshold, max(1, every)
        self.history = deque(maxlen=max(1, smooth_n))
        self.lock = threading.Lock()
        self.n = 0
        self.shown = None   # (bin_key, label, conf)
        self.latest = None  # hasil make_result terakhir (untuk panel di app.py)
        self.thumb = ""

    def set_threshold(self, value):
        if abs(value - self.threshold) > 1e-9:
            with self.lock:
                self.threshold = value
                self.history.clear()

    def analyze(self, rgb):
        """rgb: array HxWx3 uint8. Mengembalikan hasil tersaring atau None bila frame dilewati."""
        self.n += 1
        if self.n % self.every:
            return self.shown
        img = Image.fromarray(np.ascontiguousarray(rgb))
        res = self.clf.predict(img, self.threshold)
        with self.lock:
            self.history.append(res)
            self.shown = smooth(self.history)
            self.latest = res
            self.thumb = thumb_b64(img, max_side=320)
        return self.shown

    def snapshot(self):
        with self.lock:
            return self.shown, self.latest, self.thumb

    def recv(self, frame):  # dipanggil streamlit-webrtc di thread lain
        import av
        import cv2

        bgr = frame.to_ndarray(format="bgr24")
        shown = self.analyze(bgr[:, :, ::-1])
        if shown:
            key, label, conf = shown
            b = BINS[key]
            draw_banner(cv2, bgr, f"{label}  {conf:.0%}", f"Tong: {b['name']}  |  ambang {self.threshold:.0%}",
                        hex_to_bgr(b["color"]), hex_to_bgr(b["ink"]))
        else:
            draw_banner(cv2, bgr, "Menunggu...", "Arahkan benda ke kamera", (160, 160, 160), (30, 30, 30))
        return av.VideoFrame.from_ndarray(bgr, format="bgr24")
