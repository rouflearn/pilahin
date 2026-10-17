"""Pembungkus model: klasifikasi sampah (model terlatih) atau mode demo (YOLO COCO)."""
from pathlib import Path

from config import (COCO_TO_BIN, BINS, DEFAULT_THRESHOLD, DEMO_WEIGHTS, TRAINED_WEIGHTS,
                    bin_for_class, display_label)


def make_result(pairs, threshold=DEFAULT_THRESHOLD, mapper=bin_for_class, mode="terlatih"):
    """Ubah daftar [(label, confidence)] (urut menurun) menjadi hasil standar.

    Fungsi murni sehingga bisa diuji tanpa model.
    """
    if not pairs:
        return {"label": "Tidak terdeteksi", "raw_label": "", "confidence": 0.0,
                "bin_key": "verifikasi", "top3": [], "mode": mode, "low_confidence": True}
    pairs = sorted(pairs, key=lambda p: -p[1])
    label, conf = pairs[0]
    low = conf < threshold
    return {
        "label": display_label(label), "raw_label": label, "confidence": float(conf),
        "bin_key": "verifikasi" if low else mapper(label),
        "top3": [(display_label(l), float(c)) for l, c in pairs[:3]],
        "mode": mode, "low_confidence": low,
    }


class WasteClassifier:
    def __init__(self, trained=TRAINED_WEIGHTS, demo=DEMO_WEIGHTS):
        from ultralytics import YOLO  # impor lambat: hanya saat model dimuat
        if Path(trained).exists():
            self.model, self.mode = YOLO(trained), "terlatih"
        else:
            self.model, self.mode = YOLO(demo), "demo"

    def predict(self, image, threshold=DEFAULT_THRESHOLD):
        r = self.model.predict(source=image, verbose=False,
                               **({} if self.mode == "terlatih" else {"conf": 0.25}))[0]
        names = r.names
        if self.mode == "terlatih":
            ids, confs = r.probs.top5, r.probs.top5conf.tolist()
            pairs = [(names[i], c) for i, c in zip(ids, confs)]
            return make_result(pairs, threshold)
        pairs = []
        if r.boxes is not None:
            pairs = [(names[int(b.cls[0])], float(b.conf[0])) for b in r.boxes]
        return make_result(pairs, threshold, mapper=lambda l: COCO_TO_BIN.get(l.lower(), "verifikasi"),
                           mode="demo")
