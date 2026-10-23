"""Pembuat HTML untuk tampilan "Jalur Sampah" (tanpa dependensi Streamlit, mudah diuji).

Semua fungsi mengembalikan string HTML satu baris (tanpa baris kosong dan tanpa
indentasi) agar tidak dibaca sebagai blok kode oleh pengurai Markdown Streamlit.
"""
import base64
import html
import io
import math

from algorithms import PriorityQueue, count_by
from config import BINS, bin_priority

# Tong yang digambar pada jalur (Perlu Verifikasi bukan tong, hanya status).
BIN_ORDER = ["organik", "daur_ulang", "b3", "residu"]
RING_LEN = 2 * math.pi * 80  # keliling cincin keyakinan (r = 80)
MUTED_BAR = "#B9C7BE"

CSS = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800"
    "&family=Figtree:wght@400;500;700&display=swap');"
    ".block-container{max-width:1240px;padding-top:2rem;}"
    ".pl-wrap{display:flex;flex-direction:column;gap:28px;font-family:'Figtree',system-ui,sans-serif;color:#11271B;}"
    ".pl-bar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;}"
    ".pl-brand{display:flex;align-items:center;gap:12px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:26px;}"
    ".pl-chips{display:flex;flex-wrap:wrap;gap:10px;}"
    ".pl-chip{background:#fff;border:1px solid #D7E2DA;border-radius:999px;padding:8px 16px;font-size:14px;color:#52665A;}"
    ".pl-chip.dark{background:#11271B;border-color:#11271B;color:#fff;font-weight:700;}"
    ".pl-hero{background:#fff;border-radius:32px;padding:36px;display:flex;flex-direction:column;gap:32px;box-shadow:0 1px 0 #D7E2DA;}"
    ".pl-head{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:16px;}"
    ".pl-title{min-width:0;}"
    ".pl-h1{margin:0;padding:0;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(40px,7vw,76px);"
    "line-height:1;letter-spacing:-.03em;overflow-wrap:anywhere;color:#11271B;}"
    ".pl-lead{margin:8px 0 0;font-size:20px;color:#52665A;max-width:52ch;line-height:1.5;}"
    ".pl-pill{font-weight:700;font-size:18px;border-radius:999px;padding:12px 22px;}"
    ".pl-flow{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:12px 8px;background:#F3F7F4;"
    "border-radius:24px;padding:28px 16px;}"
    ".pl-stage{display:flex;flex-direction:column;align-items:center;gap:12px;width:220px;}"
    ".pl-stage.wide{flex:1 1 360px;width:auto;min-width:0;}"
    ".pl-stage b{font-size:16px;}"
    ".pl-photo{width:200px;height:200px;border-radius:24px;background:#DCE8DF;overflow:hidden;display:flex;"
    "align-items:center;justify-content:center;color:#52665A;font-size:15px;}"
    ".pl-photo.empty{border:3px dashed #A9BDB0;background:transparent;}"
    ".pl-photo img{width:100%;height:100%;object-fit:cover;}"
    ".pl-gauge{position:relative;width:200px;height:200px;}"
    ".pl-gauge .c{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}"
    ".pl-gauge .n{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:54px;line-height:1;}"
    ".pl-gauge .s{font-size:15px;color:#52665A;max-width:130px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}"
    ".pl-bins{display:flex;align-items:flex-end;justify-content:center;gap:18px;height:200px;}"
    ".pl-bin{display:flex;flex-direction:column;align-items:center;gap:6px;}"
    ".pl-bin span{font-size:14px;font-weight:700;text-align:center;}"
    ".pl-row{display:flex;flex-wrap:wrap;gap:28px;}"
    ".pl-panel{flex:1 1 480px;min-width:0;background:#fff;border-radius:28px;padding:32px;display:flex;flex-direction:column;gap:20px;}"
    ".pl-panel h2{margin:0;padding:0;font-family:'Bricolage Grotesque',sans-serif;font-size:28px;font-weight:700;color:#11271B;}"
    ".pl-phead{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;}"
    ".pl-sub{color:#52665A;font-size:15px;}"
    ".pl-brow{display:flex;flex-direction:column;gap:8px;}"
    ".pl-btop{display:flex;justify-content:space-between;font-size:17px;}"
    ".pl-track{height:18px;background:#E6EEE8;border-radius:999px;overflow:hidden;}"
    ".pl-fill{height:100%;border-radius:999px;}"
    ".pl-steps{display:flex;flex-direction:column;gap:14px;}"
    ".pl-step{display:flex;align-items:center;gap:16px;font-size:18px;line-height:1.4;}"
    ".pl-step i{flex:0 0 auto;width:40px;height:40px;border-radius:50%;background:#11271B;color:#fff;display:flex;"
    "align-items:center;justify-content:center;font-weight:700;font-style:normal;}"
    ".pl-stack{display:flex;gap:4px;height:56px;border-radius:18px;overflow:hidden;}"
    ".pl-seg{display:flex;align-items:center;justify-content:center;font-weight:800;font-size:20px;}"
    ".pl-legend{display:flex;flex-wrap:wrap;gap:12px 28px;}"
    ".pl-legend span{display:flex;align-items:center;gap:8px;font-size:15px;}"
    ".pl-legend .sw{display:inline-block;width:14px;height:14px;border-radius:4px;}"
    ".pl-q{display:flex;align-items:center;gap:16px;padding:12px 0;border-top:1px solid #E6EEE8;}"
    ".pl-q .p{flex:0 0 32px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:22px;color:#52665A;}"
    ".pl-q .d{flex:0 0 auto;width:16px;height:16px;border-radius:50%;}"
    ".pl-q .t{flex:1 1 auto;min-width:0;font-size:18px;font-weight:700;overflow-wrap:anywhere;}"
    ".pl-q .t small{display:block;font-size:13px;font-weight:400;color:#52665A;}"
    ".pl-q .b{flex:0 1 220px;min-width:0;font-size:15px;color:#52665A;}"
    ".pl-q .c{flex:0 0 56px;text-align:right;font-size:16px;font-weight:700;}"
    ".pl-note{font-size:14px;color:#52665A;max-width:70ch;line-height:1.5;margin:0;}"
    "@media(max-width:700px){.pl-hero,.pl-panel{padding:22px;}.pl-q .b{display:none;}}"
    "</style>"
)

LOGO_SVG = (
    '<svg width="40" height="40" viewBox="0 0 40 40" role="img" aria-label="Logo PILAHIN">'
    '<circle cx="20" cy="20" r="20" fill="#1FA05A"/>'
    '<path d="M14 21l4-7h6M26 19l-4 7h-6M24 14l3 0-1.5 2.5M16 26l-3 0 1.5-2.5" fill="none" stroke="#fff" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)
ARROW_SVG = (
    '<svg width="84" height="28" viewBox="0 0 84 28" role="img" aria-label="menuju">'
    '<path d="M3 14h66" stroke="#11271B" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round" fill="none"/>'
    '<path d="M62 6l14 8-14 8" fill="none" stroke="#11271B" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def esc(text):
    return html.escape(str(text), quote=True)


def pct(x):
    return int(round(float(x) * 100))


def thumb_b64(img, max_side=420, quality=82):
    """Gambar PIL -> teks base64 JPEG kecil untuk disematkan di HTML."""
    small = img.copy().convert("RGB")
    small.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    small.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def bin_svg(color, w, h, label):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 64 80" role="img" aria-label="{esc(label)}">'
        f'<rect x="22" y="4" width="20" height="7" rx="2" fill="{color}"/>'
        f'<rect x="6" y="11" width="52" height="9" rx="3" fill="{color}"/>'
        f'<path d="M11 22h42l-3 49a5 5 0 0 1-5 4H19a5 5 0 0 1-5-4z" fill="{color}"/>'
        '<path d="M26 30v36M38 30v36" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.4"/></svg>'
    )


def ring_svg(conf, color, threshold):
    """Cincin keyakinan dengan penanda ambang (mulai dari atas, searah jarum jam)."""
    conf = max(0.0, min(1.0, float(conf)))
    t = max(0.0, min(1.0, float(threshold)))
    ang = -math.pi / 2 + 2 * math.pi * t
    x1, y1 = 100 + 68 * math.cos(ang), 100 + 68 * math.sin(ang)
    x2, y2 = 100 + 92 * math.cos(ang), 100 + 92 * math.sin(ang)
    fill = f"{conf * RING_LEN:.1f} {RING_LEN + 1:.1f}"
    return (
        f'<svg width="200" height="200" viewBox="0 0 200 200" role="img" '
        f'aria-label="Keyakinan model {pct(conf)} persen, ambang {pct(t)} persen">'
        '<circle cx="100" cy="100" r="80" fill="none" stroke="#DCE8DF" stroke-width="20"/>'
        f'<circle cx="100" cy="100" r="80" fill="none" stroke="{color}" stroke-width="20" stroke-linecap="round" '
        f'stroke-dasharray="{fill}" transform="rotate(-90 100 100)"/>'
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#11271B" stroke-width="4"/></svg>'
    )


def topbar_html(n_photos, threshold, mode):
    model = "Model terlatih" if mode == "terlatih" else "Mode demo (model COCO)"
    return (
        '<div class="pl-bar">'
        f'<div class="pl-brand">{LOGO_SVG}<span>PILAHIN</span></div>'
        '<div class="pl-chips">'
        f'<span class="pl-chip">{esc(model)}</span>'
        f'<span class="pl-chip">Sesi ini: {int(n_photos)} foto</span>'
        f'<span class="pl-chip dark">Ambang keyakinan {pct(threshold)}%</span>'
        "</div></div>"
    )


def _bins_row(selected, dim_all=False):
    parts = []
    for key in BIN_ORDER:
        b = BINS[key]
        picked = key == selected
        op = 1 if picked else (0.45 if dim_all else 0.28)
        w, h = (96, 120) if picked else (64, 80)
        parts.append(
            f'<div class="pl-bin" style="opacity:{op}">{bin_svg(b["color"], w, h, b["name"])}'
            f'<span>{esc(b["short"])}</span></div>'
        )
    return '<div class="pl-bins">' + "".join(parts) + "</div>"


def _flow(photo_html, ring_html, bins_html, bins_caption, photo_cls="pl-photo"):
    return (
        '<div class="pl-flow">'
        f'<div class="pl-stage"><div class="{photo_cls}">{photo_html}</div><b>Foto Anda</b></div>'
        f"{ARROW_SVG}"
        f'<div class="pl-stage">{ring_html}<b>Dibaca model</b></div>'
        f"{ARROW_SVG}"
        f'<div class="pl-stage wide">{bins_html}<b>{esc(bins_caption)}</b></div>'
        "</div>"
    )


def hero_html(res, thumb, threshold):
    b = BINS[res["bin_key"]]
    low = res["bin_key"] == "verifikasi"
    conf = res["confidence"]
    if low:
        lead = (f"Keyakinan model {pct(conf)}%, di bawah ambang {pct(threshold)}%. "
                "Periksa benda ini secara manual sebelum dibuang.")
    else:
        lead = f"Model yakin {pct(conf)}%. Benda ini masuk tong {b['name']}."
    photo = f'<img alt="Foto yang dianalisis" src="data:image/jpeg;base64,{thumb}">' if thumb else "Foto"
    ring_center = (
        f'<div class="c"><span class="n">{pct(conf)}%</span><span class="s">{esc(res["label"])}</span></div>'
    )
    ring = f'<div class="pl-gauge">{ring_svg(conf, b["color"], threshold)}{ring_center}</div>'
    caption = "Periksa manual" if low else "Tong tujuan"
    return (
        '<div class="pl-hero">'
        '<div class="pl-head"><div class="pl-title">'
        f'<h1 class="pl-h1">{esc(res["label"])}</h1><p class="pl-lead">{esc(lead)}</p></div>'
        f'<span class="pl-pill" style="background:{b["color"]};color:{b["ink"]}">{esc(b["name"])}</span></div>'
        + _flow(photo, ring, _bins_row(res["bin_key"], dim_all=low), caption)
        + "</div>"
    )


def empty_html():
    ring = (
        '<div class="pl-gauge">' + ring_svg(0, "#DCE8DF", 0.6)
        + '<div class="c"><span class="n">0%</span><span class="s">menunggu foto</span></div></div>'
    )
    return (
        '<div class="pl-hero"><div class="pl-head"><div class="pl-title">'
        '<h1 class="pl-h1">Foto sampahmu, dapatkan tong yang tepat</h1>'
        '<p class="pl-lead">Unggah satu atau banyak foto, atau ambil dari kamera. '
        "Aplikasi menunjukkan tong tujuan dan tidak menebak bila tidak yakin.</p></div></div>"
        + _flow("Belum ada foto", ring, _bins_row(None, dim_all=True), "Empat tong tujuan", photo_cls="pl-photo empty")
        + "</div>"
    )


def top3_panel(res):
    b = BINS[res["bin_key"]]
    rows = []
    for i, (name, conf) in enumerate(res["top3"]):
        p = pct(conf)
        color = b["color"] if i == 0 else MUTED_BAR
        rows.append(
            '<div class="pl-brow">'
            f'<div class="pl-btop"><b>{esc(name)}</b><span class="pl-sub">{p}%</span></div>'
            f'<div class="pl-track"><div class="pl-fill" style="width:{max(p, 1)}%;background:{color}"></div></div></div>'
        )
    return '<div class="pl-panel"><h2>Tiga kemungkinan teratas</h2>' + "".join(rows) + "</div>"


def steps_panel(res):
    b = BINS[res["bin_key"]]
    steps = "".join(f'<div class="pl-step"><i>{n}</i><span>{esc(t)}</span></div>' for n, t in enumerate(b["steps"], 1))
    return f'<div class="pl-panel"><h2>Cara membuangnya</h2><div class="pl-steps">{steps}</div></div>'


def recap_html(rows):
    counts = count_by(rows, "bin_key")  # Counter
    order = sorted(BINS, key=bin_priority)
    present = [k for k in order if counts.get(k, 0) > 0]
    segs = "".join(
        f'<div class="pl-seg" style="flex:{counts[k]} 1 0;background:{BINS[k]["color"]};color:{BINS[k]["ink"]}">{counts[k]}</div>'
        for k in present
    )
    legend = "".join(
        f'<span><i class="sw" style="background:{BINS[k]["color"]}"></i>{esc(BINS[k]["name"])}</span>' for k in present
    )
    return (
        '<div class="pl-panel"><div class="pl-phead"><h2>Rekap sesi</h2>'
        f'<span class="pl-sub">{len(rows)} foto</span></div>'
        f'<div class="pl-stack">{segs}</div><div class="pl-legend">{legend}</div></div>'
    )


def queue_html(rows):
    pq = PriorityQueue()  # Priority Queue (heap)
    for r in rows:
        pq.push(r, bin_priority(r["bin_key"]))
    items = []
    for pos, r in enumerate(pq.to_list(), start=1):
        b = BINS[r["bin_key"]]
        items.append(
            '<div class="pl-q">'
            f'<span class="p">{pos}</span><span class="d" style="background:{b["color"]}"></span>'
            f'<span class="t">{esc(r["label"])}<small>{esc(r["file"])}</small></span>'
            f'<span class="b">{esc(b["name"])}</span><span class="c">{pct(r["confidence"])}%</span></div>'
        )
    return (
        '<div class="pl-panel" style="gap:8px"><div class="pl-phead"><h2>Antrean penanganan</h2>'
        '<span class="pl-sub">Yang perlu dicek dan yang berbahaya lebih dulu</span></div>' + "".join(items) + "</div>"
    )


NOTE_HTML = (
    '<p class="pl-note">Pemetaan tong dan urutan prioritas adalah penyederhanaan; '
    "aturan pemilahan resmi dapat berbeda di tiap daerah.</p>"
)


def wrap(*sections):
    return '<div class="pl-wrap">' + "".join(sections) + "</div>"


def result_html(res, rows, thumb, threshold):
    """Satu foto terpilih (hero + dua panel) ditambah rekap dan antrean seluruh sesi."""
    return wrap(
        hero_html(res, thumb, threshold),
        '<div class="pl-row">' + top3_panel(res) + steps_panel(res) + "</div>",
        recap_html(rows),
        queue_html(rows),
        NOTE_HTML,
    )
