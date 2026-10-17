"""Latih YOLO11n-cls pada dataset sampah.

Contoh:  python train.py --data dataset --epochs 20
Di CPU lambat; disarankan Google Colab (GPU gratis) lalu unduh weights/best.pt.
"""
import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="dataset", help="folder berisi train/ val/ (test/ opsional)")
ap.add_argument("--epochs", type=int, default=20)
ap.add_argument("--imgsz", type=int, default=224)
ap.add_argument("--batch", type=int, default=32)
ap.add_argument("--device", default=None, help="mis. 0 untuk GPU, cpu untuk CPU")
a = ap.parse_args()

model = YOLO("yolo11n-cls.pt")  # bobot awal (diunduh otomatis)
model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, batch=a.batch, device=a.device,
            project="runs", name="pilahin", exist_ok=True, patience=8)
best = Path("runs/pilahin/weights/best.pt")
Path("weights").mkdir(exist_ok=True)
shutil.copy2(best, "weights/best.pt")
print("Tersimpan: weights/best.pt")
