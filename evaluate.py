"""Evaluasi pada split test: akurasi, akurasi per kelas, dan confusion matrix (CSV).

Contoh:  python evaluate.py --data dataset/test
"""
import argparse
from pathlib import Path

import pandas as pd
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="dataset/test")
ap.add_argument("--weights", default="weights/best.pt")
a = ap.parse_args()

model = YOLO(a.weights)
rows = []
for cls_dir in sorted(p for p in Path(a.data).iterdir() if p.is_dir()):
    files = [f for f in cls_dir.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    for f in files:
        r = model.predict(str(f), verbose=False)[0]
        rows.append({"benar": cls_dir.name, "prediksi": r.names[r.probs.top1], "conf": float(r.probs.top1conf)})
df = pd.DataFrame(rows)
print(f"Akurasi total: {(df.benar == df.prediksi).mean():.2%}  (n={len(df)})")
print(df.assign(ok=df.benar == df.prediksi).groupby("benar").ok.mean().map("{:.1%}".format))
cm = pd.crosstab(df.benar, df.prediksi)
cm.to_csv("confusion_matrix.csv")
print("Confusion matrix -> confusion_matrix.csv")
