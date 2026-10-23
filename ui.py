"""Skin tampilan (4 pilihan), komponen HTML, dan helper kompatibilitas Streamlit."""
import html

import streamlit as st

from config import BINS

SKINS = {
    "A · Eco Clean": dict(bg="#F4FAF5", card="#FFFFFF", text="#173326", muted="#5E7A69",
                          accent="#2E9D5B", hero="linear-gradient(135deg,#2E9D5B,#8BD3A0)",
                          hero_text="#FFFFFF", radius="18px", font="'Poppins','Segoe UI',sans-serif",
                          border="1px solid #D9EBDD", shadow="0 6px 20px rgba(46,157,91,.12)"),
    "B · Night Ops": dict(bg="#0E1217", card="#171D26", text="#E7ECF3", muted="#8D98A8",
                          accent="#3DF2A0", hero="linear-gradient(135deg,#131A24,#1F2B3A)",
                          hero_text="#E7ECF3", radius="10px", font="'JetBrains Mono','Consolas',monospace",
                          border="1px solid #263041", shadow="0 0 0 1px #263041"),
    "C · Bin Cards": dict(bg="#FFF9EC", card="#FFFFFF", text="#2B2417", muted="#7A6C52",
                          accent="#E0A100", hero="linear-gradient(135deg,#FFD65A,#FF9F45)",
                          hero_text="#2B2417", radius="26px", font="'Nunito','Trebuchet MS',sans-serif",
                          border="3px solid #2B2417", shadow="6px 6px 0 #2B2417"),
    "D · Minimal Lab": dict(bg="#FFFFFF", card="#FFFFFF", text="#111111", muted="#6B6B6B",
                            accent="#111111", hero="#F2F2F2", hero_text="#111111", radius="4px",
                            font="'Inter','Helvetica Neue',sans-serif",
                            border="1px solid #DDDDDD", shadow="none"),
}
DEFAULT_SKIN = "A · Eco Clean"


def apply_skin(name):
    s = SKINS.get(name, SKINS[DEFAULT_SKIN])
    st.markdown(f"""
<style>
.stApp {{ background:{s['bg']}; color:{s['text']}; font-family:{s['font']}; }}
.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp span,.stApp li {{ color:{s['text']}; }}
[data-testid="stSidebar"] {{ background:{s['card']}; border-right:{s['border']}; }}
.pl-hero {{ background:{s['hero']}; color:{s['hero_text']}; padding:28px 30px; border-radius:{s['radius']};
           border:{s['border']}; box-shadow:{s['shadow']}; margin-bottom:18px; }}
.pl-hero h1 {{ color:{s['hero_text']} !important; margin:0 0 4px 0; font-size:2rem; }}
.pl-hero p {{ color:{s['hero_text']} !important; margin:0; opacity:.9; }}
.pl-card {{ background:{s['card']}; border:{s['border']}; border-radius:{s['radius']};
           box-shadow:{s['shadow']}; padding:18px 20px; margin-bottom:14px; }}
.pl-muted {{ color:{s['muted']} !important; font-size:.9rem; }}
.pl-badge {{ display:inline-block; padding:4px 12px; border-radius:999px; color:#fff !important;
            font-weight:700; font-size:.85rem; }}
.pl-result {{ border-left:10px solid var(--bin); }}
.pl-result h2 {{ margin:6px 0 2px 0; }}
.stButton>button,.stDownloadButton>button {{ border-radius:{s['radius']}; border:{s['border']};
            background:{s['accent']}; color:#fff; font-weight:700; }}
.stButton>button:hover,.stDownloadButton>button:hover {{ filter:brightness(1.1); color:#fff; }}
</style>""", unsafe_allow_html=True)


def hero(title, subtitle, mode):
    chip = "Model terlatih" if mode == "terlatih" else "Mode demo (model COCO)"
    st.markdown(f"""<div class="pl-hero"><h1>♻️ {html.escape(title)}</h1>
<p>{html.escape(subtitle)}</p><p style="margin-top:8px"><b>{chip}</b></p></div>""",
                unsafe_allow_html=True)


def bin_badge(bin_key):
    b = BINS[bin_key]
    return (f'<span class="pl-badge" style="background:{b["color"]}">'
            f'{b["emoji"]} {html.escape(b["name"])}</span>')


def result_card(res, filename=""):
    b = BINS[res["bin_key"]]
    note = "Di bawah ambang keyakinan." if res["low_confidence"] else ""
    st.markdown(f"""<div class="pl-card pl-result" style="--bin:{b['color']}">
{bin_badge(res['bin_key'])}
<h2>{html.escape(res['label'])} · {res['confidence']:.0%}</h2>
<div class="pl-muted">{html.escape(filename)} {note}</div>
<p style="margin-top:10px">{html.escape(b['tip'])}</p></div>""", unsafe_allow_html=True)


# --- kompatibilitas antar versi Streamlit (use_container_width vs width="stretch") ---
def show_image(img, **kw):
    try:
        st.image(img, width="stretch", **kw)
    except TypeError:
        st.image(img, use_container_width=True, **kw)


def show_df(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)
