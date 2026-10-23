
import argparse
import shutil
from pathlib import Path

from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()

    data_dir = Path(args.data)
    if not (data_dir / "train").is_dir():
        raise FileNotFoundError(
            f"Folder {data_dir / 'train'} tidak ditemukan."
        )
    if not (data_dir / "val").is_dir():
        raise FileNotFoundError(
            f"Folder {data_dir / 'val'} tidak ditemukan."
        )

    # Transfer learning dari bobot awal YOLO11n untuk klasifikasi.
    model = YOLO("yolo11n-cls.pt")

    results = model.train(
        data=str(data_dir.resolve()),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project="runs",
        name="pilahin_training",
        exist_ok=True,
        patience=10,
        workers=0
    )

    # Ambil lokasi keluaran aktual, bukan menebak nama foldernya.
    save_dir = Path(results.save_dir)
    best = save_dir / "weights" / "best.pt"

    if not best.exists():
        raise FileNotFoundError(
            f"Model terbaik tidak ditemukan: {best}"
        )

    target = Path("weights")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best, target / "best.pt")

    print("\nTRAINING SELESAI")
    print(f"Model sumber : {best.resolve()}")
    print(f"Model aplikasi: {(target / 'best.pt').resolve()}")
    print("Aplikasi siap diarahkan ke model hasil training.")

if __name__ == "__main__":
    main()
