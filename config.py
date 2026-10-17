"""Konfigurasi pusat: kelas model, tong sampah, prioritas, dan tips."""
import re

# Urutan prioritas penanganan (angka kecil = didahulukan). Ini aturan demonstrasi.
BINS = {
    "verifikasi": {"name": "Perlu Verifikasi", "emoji": "❓", "color": "#8A8F98", "priority": 0,
                   "tip": "Keyakinan model rendah. Periksa objek secara manual sebelum dibuang."},
    "b3": {"name": "B3 (Berbahaya)", "emoji": "☣️", "color": "#D64545", "priority": 1,
           "tip": "Jangan dicampur dengan sampah lain. Serahkan ke titik pengumpulan B3."},
    "organik": {"name": "Organik", "emoji": "🥬", "color": "#2E9D5B", "priority": 2,
                "tip": "Bisa dikomposkan. Pisahkan dari sampah kering agar tidak membusukkan yang lain."},
    "daur_ulang": {"name": "Anorganik Daur Ulang", "emoji": "♻️", "color": "#E0A100", "priority": 3,
                   "tip": "Bersihkan dan keringkan, lalu setor ke bank sampah / pengepul."},
    "residu": {"name": "Residu", "emoji": "🗑️", "color": "#5B6575", "priority": 4,
               "tip": "Sulit didaur ulang. Buang ke tempat sampah umum / TPA."},
}

# Nama kelas (huruf kecil, spasi/underscore -> '-') -> tong.
# Mencakup dataset "Garbage Classification (5 classes)" dan TrashNet.
CLASS_TO_BIN = {
    "biological": "organik",
    "paper": "daur_ulang",
    "cardboard": "daur_ulang",
    "plastic": "daur_ulang",
    "trash": "residu",
}

CLASS_LABEL_ID = {
    "biological": "Sampah biologis", "cardboard": "Kardus",
    "paper": "Kertas", "plastic": "Plastik", "trash": "Sampah lain",
}

# Pemetaan label COCO (mode demo tanpa model terlatih). Hanya indikasi.
COCO_TO_BIN = {
    "bottle": "daur_ulang", "cup": "daur_ulang",
    "banana": "organik", "apple": "organik", "orange": "organik", "sandwich": "organik",
    "broccoli": "organik", "carrot": "organik", "pizza": "organik", "donut": "organik",
    "cake": "organik", "book": "daur_ulang", "wadah_plastik": "daur_ulang", "plastik": "daur_ulang",
}


def normalize_label(label: str) -> str:
    return re.sub(r"[\s_]+", "-", label.strip().lower())


def bin_for_class(label: str) -> str:
    """Kelas tak dikenal -> 'verifikasi' (aman, tidak menebak)."""
    return CLASS_TO_BIN.get(normalize_label(label), "verifikasi")


def display_label(label: str) -> str:
    key = normalize_label(label)
    return CLASS_LABEL_ID.get(key, label.replace("_", " ").capitalize())


def bin_priority(bin_key: str) -> int:
    return BINS.get(bin_key, BINS["verifikasi"])["priority"]


DEFAULT_THRESHOLD = 0.60
IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]
TRAINED_WEIGHTS = "weights/best.pt"
DEMO_WEIGHTS = "weights/yolo11n.pt"
