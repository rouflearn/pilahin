"""Deteksi real-time dari webcam / kamera tambahan.

Contoh:
    python live.py                  # kamera 0 (bawaan laptop)
    python live.py --cam 1          # kamera tambahan (USB) biasanya indeks 1
    python live.py --list           # cek indeks kamera yang tersedia
Tombol: q / Esc = keluar, s = simpan foto, + / - = ubah ambang keyakinan.
"""
import argparse
import time
from collections import Counter, deque
from pathlib import Path

from config import BINS, DEFAULT_THRESHOLD


def smooth(history):
    """Gabungkan beberapa prediksi terakhir agar label tidak berkedip.

    history: deque berisi hasil make_result. Mengembalikan (bin_key, label, keyakinan_rata2),
    memakai suara terbanyak untuk tong lalu rata-rata keyakinan pada tong itu.
    """
    if not history:
        return None
    bin_key = Counter(r["bin_key"] for r in history).most_common(1)[0][0]
    same = [r for r in history if r["bin_key"] == bin_key]
    label = Counter(r["label"] for r in same).most_common(1)[0][0]
    conf = sum(r["confidence"] for r in same) / len(same)
    return bin_key, label, conf


def hex_to_bgr(hex_color):
    h = hex_color.lstrip("#")
    return int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)


def list_cameras(cv2, limit=5):
    found = []
    for i in range(limit):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) if hasattr(cv2, "CAP_DSHOW") else cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
        cap.release()
    return found


def draw_banner(cv2, frame, text, sub, color, ink):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 78), color, -1)
    cv2.putText(frame, text, (16, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.95, ink, 2, cv2.LINE_AA)
    cv2.putText(frame, sub, (16, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ink, 1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", type=int, default=0, help="indeks kamera (0, 1, 2, ...)")
    ap.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    ap.add_argument("--every", type=int, default=3, help="prediksi tiap N frame (lebih besar = lebih ringan)")
    ap.add_argument("--smooth", type=int, default=5, help="jumlah prediksi yang dirata-rata")
    ap.add_argument("--width", type=int, default=960, help="lebar jendela tampilan")
    ap.add_argument("--list", action="store_true", help="tampilkan indeks kamera yang tersedia lalu keluar")
    args = ap.parse_args()

    import cv2
    from PIL import Image
    from classifier import WasteClassifier

    if args.list:
        print("Kamera tersedia (indeks):", list_cameras(cv2) or "tidak ada")
        return

    cap = cv2.VideoCapture(args.cam, cv2.CAP_DSHOW) if hasattr(cv2, "CAP_DSHOW") else cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        raise SystemExit(f"Kamera {args.cam} tidak bisa dibuka. Coba: python live.py --list")

    clf = WasteClassifier()
    mode = "model terlatih" if clf.mode != "demo" else "MODE DEMO (COCO)"
    print(f"Memakai {mode}. Tekan q untuk keluar.")
    threshold = args.threshold
    history = deque(maxlen=max(1, args.smooth))
    out_dir = Path("snapshots")
    n, fps, t0, shown = 0, 0.0, time.time(), None

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal membaca frame dari kamera.")
            break
        n += 1
        if n % max(1, args.every) == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            history.append(clf.predict(Image.fromarray(rgb), threshold))
            shown = smooth(history)
            now = time.time()
            fps = args.every / max(now - t0, 1e-6)
            t0 = now

        view = frame
        if view.shape[1] > args.width:
            scale = args.width / view.shape[1]
            view = cv2.resize(view, (args.width, int(view.shape[0] * scale)))
        if shown:
            bin_key, label, conf = shown
            b = BINS[bin_key]
            draw_banner(cv2, view, f"{label}  {conf:.0%}", f"Tong: {b['name']}  |  ambang {threshold:.0%}  |  {fps:.1f} prediksi/dtk",
                        hex_to_bgr(b["color"]), hex_to_bgr(b["ink"]))
        else:
            draw_banner(cv2, view, "Menunggu...", "Arahkan benda ke kamera", (160, 160, 160), (30, 30, 30))
        cv2.putText(view, "q: keluar  s: simpan  +/-: ambang", (12, view.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("PILAHIN Live", view)

        k = cv2.waitKey(1) & 0xFF
        if k in (ord("q"), 27):
            break
        if k == ord("s"):
            out_dir.mkdir(exist_ok=True)
            p = out_dir / f"snap_{time.strftime('%H%M%S')}.jpg"
            cv2.imwrite(str(p), frame)
            print("Disimpan:", p)
        if k in (ord("+"), ord("=")):
            threshold = min(0.95, round(threshold + 0.05, 2)); history.clear()
        if k in (ord("-"), ord("_")):
            threshold = max(0.30, round(threshold - 0.05, 2)); history.clear()
        if cv2.getWindowProperty("PILAHIN Live", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
