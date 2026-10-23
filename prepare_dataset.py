"""Bagi dataset berfolder-kelas menjadi train/val/test.

Contoh:  python prepare_dataset.py --src raw_data --dst dataset
raw_data/<kelas>/*.jpg  ->  dataset/{train,val,test}/<kelas>/*.jpg
"""
import argparse
import random
import shutil
from pathlib import Path

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def split_dataset(src, dst, ratios=(0.7, 0.15, 0.15), seed=42):
    src, dst = Path(src), Path(dst)
    if abs(sum(ratios) - 1) > 1e-6:
        raise ValueError("rasio harus berjumlah 1")
    rng = random.Random(seed)
    summary = {}
    for cls_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        files = sorted(f for f in cls_dir.iterdir() if f.suffix.lower() in EXT)
        rng.shuffle(files)
        n = len(files)
        n_train, n_val = int(n * ratios[0]), int(n * ratios[1])
        parts = {"train": files[:n_train], "val": files[n_train:n_train + n_val],
                 "test": files[n_train + n_val:]}
        for split, items in parts.items():
            out = dst / split / cls_dir.name
            out.mkdir(parents=True, exist_ok=True)
            for f in items:
                shutil.copy2(f, out / f.name)
        summary[cls_dir.name] = {k: len(v) for k, v in parts.items()}
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", default="dataset")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    for cls, c in split_dataset(a.src, a.dst, seed=a.seed).items():
        print(f"{cls:15s} train={c['train']:5d} val={c['val']:5d} test={c['test']:5d}")
