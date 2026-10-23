"""Rangkum hasil proyek jadi satu teks untuk laporan/presentasi.

Membaca (yang ada saja):
  dataset/{train,val,test}/<kelas>/   -> jumlah foto per kelas
  runs/pilahin/results.csv            -> akurasi tiap epoch (dari train.py)
  confusion_matrix.csv                -> akurasi per kelas (dari evaluate.py)

Jalankan:  python ringkas_hasil.py
Hasil dicetak dan disimpan di hasil_ringkas.md. Kirim isi file itu untuk mengisi laporan.
"""
import argparse
from pathlib import Path

import pandas as pd

EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def count_dataset(root):
    root = Path(root)
    rows = {}
    for split in ("train", "val", "test"):
        for cls_dir in sorted(p for p in (root / split).glob("*") if p.is_dir()):
            n = sum(1 for f in cls_dir.iterdir() if f.suffix.lower() in EXT)
            rows.setdefault(cls_dir.name, {})[split] = n
    if not rows:
        return None
    df = pd.DataFrame(rows).T.fillna(0).astype(int)
    for s in ("train", "val", "test"):
        if s not in df:
            df[s] = 0
    df = df[["train", "val", "test"]]
    df["total"] = df.sum(axis=1)
    return df


def read_training(path):
    p = Path(path)
    if not p.exists():
        return None
    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]
    col = "metrics/accuracy_top1"
    if col not in df:
        return None
    best = df.loc[df[col].idxmax()]
    return {"epochs": int(len(df)), "best_epoch": int(best["epoch"]),
            "best_top1": float(best[col]), "last_top1": float(df[col].iloc[-1])}


def read_confusion(path):
    p = Path(path)
    if not p.exists():
        return None
    cm = pd.read_csv(p, index_col=0)
    cm = cm.reindex(columns=sorted(set(cm.columns) | set(cm.index)), fill_value=0)
    cm = cm.reindex(index=cm.index, fill_value=0)
    total = int(cm.values.sum())
    correct = int(sum(cm.loc[c, c] for c in cm.index if c in cm.columns))
    per_class = {c: (cm.loc[c, c] / cm.loc[c].sum() if cm.loc[c].sum() else 0.0) for c in cm.index}
    confusions = []
    for a in cm.index:
        for b in cm.columns:
            if a != b and cm.loc[a, b] > 0:
                confusions.append((a, b, int(cm.loc[a, b])))
    confusions.sort(key=lambda t: -t[2])
    return {"total": total, "accuracy": correct / total if total else 0.0,
            "per_class": per_class, "top_confusions": confusions[:5]}


def build_summary(dataset, results, confusion):
    out = ["# Ringkasan hasil PILAHIN", ""]
    ds = count_dataset(dataset)
    out.append("## Dataset")
    if ds is None:
        out.append("(folder dataset tidak ditemukan)")
    else:
        out.append(f"Jumlah kelas: {len(ds)}; total foto: {int(ds['total'].sum())}")
        out.append("")
        out.append("| Kelas | Train | Val | Test | Total |")
        out.append("|---|---|---|---|---|")
        for cls, r in ds.iterrows():
            out.append(f"| {cls} | {r['train']} | {r['val']} | {r['test']} | {r['total']} |")
    out += ["", "## Pelatihan"]
    tr = read_training(results)
    if tr is None:
        out.append("(runs/pilahin/results.csv tidak ditemukan)")
    else:
        out.append(f"Jumlah epoch berjalan: {tr['epochs']}; akurasi validasi terbaik: "
                   f"{tr['best_top1']:.2%} (epoch {tr['best_epoch']}); epoch terakhir: {tr['last_top1']:.2%}")
    out += ["", "## Evaluasi pada data test"]
    cf = read_confusion(confusion)
    if cf is None:
        out.append("(confusion_matrix.csv tidak ditemukan; jalankan evaluate.py)")
    else:
        out.append(f"Akurasi total: {cf['accuracy']:.2%} dari {cf['total']} foto test")
        out.append("")
        out.append("| Kelas | Akurasi |")
        out.append("|---|---|")
        for c, a in cf["per_class"].items():
            out.append(f"| {c} | {a:.1%} |")
        if cf["top_confusions"]:
            out += ["", "Kesalahan tersering (benar -> diprediksi: jumlah):"]
            out += [f"- {a} -> {b}: {n}" for a, b, n in cf["top_confusions"]]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="dataset")
    ap.add_argument("--results", default="runs/pilahin/results.csv")
    ap.add_argument("--confusion", default="confusion_matrix.csv")
    ap.add_argument("--out", default="hasil_ringkas.md")
    a = ap.parse_args()
    text = build_summary(a.dataset, a.results, a.confusion)
    Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    print(f"Tersimpan: {a.out}")
