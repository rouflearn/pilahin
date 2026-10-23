"""Konfigurasi pusat: kelas model, tong sampah, prioritas, dan tips."""
import re

# Urutan prioritas penanganan (angka kecil = didahulukan). Ini aturan demonstrasi.
BINS = {
    "verifikasi": {
        "name": "Perlu Verifikasi", "short": "Verifikasi", "color": "#8A93A0", "ink": "#11271B", "priority": 0,
        "tip": "Keyakinan model rendah. Periksa objek secara manual sebelum dibuang.",
        "steps": ["Periksa bendanya langsung.", "Foto ulang dari dekat dengan cahaya cukup.", "Tentukan tong secara manual."],
    },
    "b3": {
        "name": "B3 (Berbahaya)", "short": "B3", "color": "#E5484D", "ink": "#FFFFFF", "priority": 1,
        "tip": "Jangan dicampur dengan sampah lain. Serahkan ke titik pengumpulan B3.",
        "steps": ["Jangan dibuka, dibakar, atau ditekan.", "Simpan terpisah dari sampah lain.", "Serahkan ke titik pengumpulan B3."],
    },
    "organik": {
        "name": "Organik", "short": "Organik", "color": "#1FA05A", "ink": "#FFFFFF", "priority": 2,
        "tip": "Bisa dikomposkan. Pisahkan dari sampah kering agar tidak membusukkan yang lain.",
        "steps": ["Pisahkan dari sampah kering.", "Tiriskan bila basah.", "Masukkan ke komposter atau tong organik."],
    },
    "daur_ulang": {
        "name": "Anorganik Daur Ulang", "short": "Daur ulang", "color": "#F2B705", "ink": "#11271B", "priority": 3,
        "tip": "Bersihkan dan keringkan, lalu setor ke bank sampah / pengepul.",
        "steps": ["Kosongkan dan bersihkan dari sisa isi.", "Keringkan, pipihkan bila bisa.", "Setor ke bank sampah atau pengepul."],
    },
    "residu": {
        "name": "Residu", "short": "Residu", "color": "#5A6577", "ink": "#FFFFFF", "priority": 4,
        "tip": "Sulit didaur ulang. Buang ke tempat sampah umum / TPA.",
        "steps": ["Pastikan sudah tidak bisa dipilah lagi.", "Bungkus agar tidak berceceran.", "Buang ke tempat sampah umum."],
    },
}

# Nama kelas (huruf kecil, spasi/underscore -> '-') -> tong.
# Mencakup dataset "Garbage Classification (12 classes)" dan TrashNet.
CLASS_TO_BIN = {
    "biological": "organik",
        "paper": "daur_ulang",
        "cardboard": "daur_ulang",
        "botol-plastik": "daur_ulang",
        "kantong-plastik": "residu",      # kantong kresek umumnya sulit didaur ulang
        "wadah-plastik": "daur_ulang",
        "cup-plastik": "daur_ulang",
        "trash": "residu",
    }
    
CLASS_LABEL_ID = {
        "biological": "Sampah biologis", "cardboard": "Kardus", "paper": "Kertas",
        "botol-plastik": "Botol plastik", "kantong-plastik": "Kantong plastik",
        "wadah-plastik": "Wadah plastik", "cup-plastik": "Cup plastik",
        "trash": "Sampah lain",
}

# Pemetaan label COCO (mode demo tanpa model terlatih). Hanya indikasi.
COCO_TO_BIN = {
    "bottle": "daur_ulang", "cup": "verifikasi", "wine glass": "verifikasi", "can": "daur_ulang",
    "banana": "organik", "apple": "organik", "orange": "organik", "sandwich": "organik",
    "broccoli": "organik", "carrot": "organik", "pizza": "organik", "donut": "organik",
    "cake": "organik", "book": "daur_ulang",
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
