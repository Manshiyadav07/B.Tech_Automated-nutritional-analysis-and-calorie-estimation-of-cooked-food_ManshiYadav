import sys
import os
import tempfile
import base64
from io import BytesIO

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Import real backend ───────────────────────────────────────────────────────
BACKEND_OK   = False
IMPORT_ERROR = ""

try:
    from app.detect      import detect_food
    from app.calorie     import calculate_calories
    from utils.nutrition import nutrition
    BACKEND_OK = True
except Exception as e:
    IMPORT_ERROR = str(e)

import streamlit as st
import plotly.graph_objects as go
from PIL import Image

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Calorie Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

:root{
  --bg:     #0A0A0A;
  --s2:     #181818;
  --border: #2A2A2A;
  --amber:  #F0A500;
  --orange: #E05A1A;
  --green:  #3D8B40;
  --cream:  #F0E8DC;
  --muted:  #666666;
  --r:      14px;
  --sh:     0 2px 20px rgba(0,0,0,.6);
}

html,body,[class*="css"]{
  font-family:'Plus Jakarta Sans',sans-serif;
  background:var(--bg)!important;
  color:var(--cream);
}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:1.75rem 2.5rem 5rem!important;max-width:1320px}

/* ── hero ── */
.hero{
  background:linear-gradient(120deg,#111 0%,#1A1005 55%,#2A1005 100%);
  border:1px solid var(--border);border-radius:20px;
  padding:2.5rem 3rem 2rem;margin-bottom:1.75rem;
  position:relative;overflow:hidden;
}
.hero::before{
  content:'';position:absolute;top:-80px;right:-80px;
  width:320px;height:320px;
  background:radial-gradient(circle,rgba(240,165,0,.10) 0%,transparent 68%);
  pointer-events:none;
}
.hero-tag{
  display:inline-flex;align-items:center;gap:.35rem;
  background:rgba(240,165,0,.12);border:1px solid rgba(240,165,0,.28);
  color:var(--amber);font-size:.68rem;font-weight:600;letter-spacing:2px;
  text-transform:uppercase;padding:.28rem .8rem;border-radius:999px;
  margin-bottom:.9rem;
}
.hero h1{
  font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;
  color:var(--cream);margin:0 0 .35rem;letter-spacing:-.5px;line-height:1.05;
}
.hero p{font-size:.95rem;color:var(--muted);margin:0;font-weight:300}

/* ── section label ── */
.slabel{
  font-family:'Syne',sans-serif;font-size:.7rem;font-weight:700;
  letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);
  margin-bottom:.7rem;display:flex;align-items:center;gap:.4rem;
}
.slabel b{color:var(--amber)}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"]{
  gap:.3rem;background:transparent;
  border-bottom:1px solid var(--border);padding-bottom:0;
}
.stTabs [data-baseweb="tab"]{
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  font-size:.78rem!important;color:var(--muted)!important;
  background:transparent!important;border:none!important;
  padding:.5rem .95rem!important;border-radius:8px 8px 0 0!important;
  letter-spacing:.5px;text-transform:uppercase;
}
.stTabs [aria-selected="true"]{
  color:var(--amber)!important;border-bottom:2px solid var(--amber)!important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"]{
  background:var(--s2)!important;
  border:2px dashed var(--border)!important;
  border-radius:var(--r)!important;
}
[data-testid="stFileUploader"]:hover{border-color:var(--amber)!important}

/* ── button ── */
.stButton>button{
  background:linear-gradient(135deg,#F0A500 0%,#E05A1A 100%)!important;
  color:#0A0A0A!important;
  font-family:'Syne',sans-serif!important;font-weight:800!important;
  font-size:.9rem!important;letter-spacing:.8px!important;
  text-transform:uppercase!important;border:none!important;
  border-radius:12px!important;padding:.85rem 2rem!important;width:100%!important;
  box-shadow:0 6px 28px rgba(224,90,26,.4)!important;
  transition:opacity .2s,transform .15s!important;
}
.stButton>button:hover{opacity:.88!important;transform:translateY(-1px)!important}
.stButton>button:disabled{opacity:.3!important;transform:none!important}

/* ── preview box ── */
.prev-wrap{
  background:var(--s2);
  border:1px solid var(--border);
  border-radius:var(--r);
  padding:1.2rem;
  display:flex;
  justify-content:center;
  align-items:center;
  min-height:300px;
  box-shadow:var(--sh);
}
.prev-wrap img{
  border-radius:10px;
  max-width:100%;
  max-height:360px;
  object-fit:contain;
  display:block;
}
.empty-prev{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:.6rem;
  min-height:260px;
}

/* ── food cards ── */
.fcard{
  background:var(--s2);border:1px solid var(--border);
  border-radius:var(--r);padding:1.3rem .9rem 1.1rem;
  text-align:center;box-shadow:var(--sh);
  transition:transform .22s,border-color .22s;height:100%;
}
.fcard:hover{transform:translateY(-4px);border-color:rgba(240,165,0,.45)}
.fcard .fc-icon{font-size:2.1rem;margin-bottom:.45rem;display:block}
.fcard .fc-name{
  font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;
  color:var(--cream);text-transform:capitalize;margin-bottom:.18rem;
}
.fcard .fc-qty{font-size:.72rem;color:var(--muted);margin-bottom:.6rem}
.fcard .fc-pill{
  display:inline-block;
  background:linear-gradient(135deg,rgba(240,165,0,.14),rgba(224,90,26,.14));
  border:1px solid rgba(240,165,0,.3);color:var(--amber);
  font-family:'Syne',sans-serif;font-weight:700;font-size:.85rem;
  padding:.28rem .8rem;border-radius:999px;
}
.fcard .fc-nodb{
  display:inline-block;
  background:rgba(102,102,102,.12);border:1px solid var(--border);
  color:var(--muted);font-size:.72rem;padding:.22rem .7rem;border-radius:999px;
}

/* ── total box ── */
.total-box{
  background:linear-gradient(120deg,#111 0%,#1A1005 60%,#2A1A05 100%);
  border:1px solid rgba(240,165,0,.22);border-radius:var(--r);
  padding:1.6rem 2.2rem;
  display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 8px 32px rgba(0,0,0,.5);margin-top:1.2rem;
}
.total-box .tl{
  font-family:'Syne',sans-serif;font-size:.68rem;font-weight:700;
  letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;
}
.total-box .tv{
  font-family:'Syne',sans-serif;font-size:3.4rem;font-weight:800;
  color:var(--amber);line-height:1;
}
.total-box .tu{font-size:.8rem;color:var(--muted);margin-top:.2rem}
.total-box .tc{font-size:.78rem;color:var(--muted)}

/* ── notice boxes ── */
.warn-box{
  background:rgba(224,90,26,.1);border:1px solid rgba(224,90,26,.3);
  border-radius:var(--r);padding:1rem 1.3rem;
  color:#E07050;font-size:.88rem;font-weight:500;
}
.info-box{
  background:rgba(61,139,64,.1);border:1px solid rgba(61,139,64,.3);
  border-radius:var(--r);padding:1rem 1.3rem;
  color:#6DBF70;font-size:.82rem;line-height:1.55;
}
.err-box{
  background:rgba(224,90,26,.1);border:1px solid rgba(224,90,26,.35);
  border-radius:var(--r);padding:1.2rem 1.5rem;
  color:#E07050;font-size:.86rem;line-height:1.6;
}

/* ── sidebar ── */
[data-testid="stSidebar"]{background:#0D0D0D!important}
[data-testid="stSidebar"] *{color:var(--cream)!important}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{
  font-family:'Syne',sans-serif!important;color:var(--amber)!important;
}
.sb-card{
  background:var(--s2);border:1px solid var(--border);
  border-radius:10px;padding:.7rem .95rem;
  font-size:.8rem;line-height:1.65;margin-bottom:.5rem;
}
.sb-div{border:none;border-top:1px solid var(--border);margin:1rem 0}
.dot{
  display:inline-block;width:8px;height:8px;
  border-radius:50%;margin-right:.35rem;vertical-align:middle;
}
.dot-g{background:#4CAF50;box-shadow:0 0 6px #4CAF50}
.dot-r{background:#F44336;box-shadow:0 0 6px #F44336}

hr{border-color:var(--border)!important}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
EMOJI_MAP = {
    "roti":"🫓","dal":"🥣","rice":"🍚","sabzi":"🥦","rayta":"🥛",
    "salad":"🥗","sweet":"🍮","paneer":"🧀","idli":"🍥","dosa":"🥞",
    "biryani":"🍛","samosa":"🥟","chole":"🫘","poha":"🍽️","upma":"🍲",
    "paratha":"🥙","khichdi":"🍜","rajma":"🫘",
}
COLORS = [
    "#F0A500","#E05A1A","#3D8B40","#C87D10","#A04020",
    "#2A6B2E","#805010","#904020","#508830","#B06010",
]

def get_emoji(name: str) -> str:
    return EMOJI_MAP.get(name.lower().strip(), "🍴")

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def pil_to_base64(img: Image.Image) -> str:
    """Convert PIL image to base64 string for embedding in HTML."""
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


def process_image(pil_img: Image.Image) -> str:
    """Save PIL image to a temp JPEG and return its path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
        pil_img.save(f.name, format="JPEG", quality=95)
        return f.name


def build_items(detected: list) -> list:
    """Count duplicates, look up calories. Returns list of dicts for display."""
    counts = {}
    for item in detected:
        key = item.lower().strip()
        counts[key] = counts.get(key, 0) + 1

    result = []
    for name, qty in counts.items():
        cal_each = nutrition.get(name, 0) if BACKEND_OK else 0
        result.append({
            "name":      name,
            "emoji":     get_emoji(name),
            "qty":       qty,
            "cal_each":  cal_each,
            "total_cal": cal_each * qty,
            "in_db":     cal_each > 0,
        })
    return result


def show_results(items: list) -> None:
    """Render food cards, total calories box, and distribution charts."""

    if not items:
        st.markdown("""
        <div class="warn-box">
             No food detected. Please try a clearer, well-lit photo of the thali.<br>
            <span style="font-size:.78rem;opacity:.7">
                Model accuracy will improve as more training data is added.
            </span>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Food cards ──────────────────────────────────────────────────────────
    st.markdown('<div class="slabel"><b>●</b> Detected Food Items</div>',
                unsafe_allow_html=True)

    n_cols = min(len(items), 4)
    cols   = st.columns(n_cols, gap="small")

    for i, item in enumerate(items):
        qty_label = f"{item['qty']} serving{'s' if item['qty'] > 1 else ''}"
        badge = (
            f'<div class="fc-pill"> {item["total_cal"]} kcal</div>'
            if item["in_db"]
            else '<div class="fc-nodb">Not in nutrition DB</div>'
        )
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="fcard">
                <span class="fc-icon">{item["emoji"]}</span>
                <div class="fc-name">{item["name"]}</div>
                <div class="fc-qty">{qty_label}</div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

    # ── Total calories ──────────────────────────────────────────────────────
    grand_total    = sum(i["total_cal"] for i in items)
    total_servings = sum(i["qty"]       for i in items)
    missing        = [i["name"]         for i in items if not i["in_db"]]

    st.markdown(f"""
    <div class="total-box">
        <div>
            <div class="tl"> Total Calories</div>
            <div class="tc">{len(items)} food type(s) · {total_servings} serving(s) detected</div>
        </div>
        <div style="text-align:right">
            <div class="tv">{grand_total}</div>
            <div class="tu">kcal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if missing:
        st.markdown(f"""
        <div class="info-box" style="margin-top:.8rem">
             Detected but <b>not in nutrition DB</b> (counted as 0 kcal):
            <b>{', '.join(missing)}</b><br>
            Add them to <code>utils/nutrition.py</code> to track their calories.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────────────
    chart_items = [i for i in items if i["in_db"]]

    if len(chart_items) < 2:
        st.markdown("""
        <div class="info-box">
             Need at least 2 items with calorie data to show charts.
            Add more foods to <code>utils/nutrition.py</code>.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown('<div class="slabel"><b>●</b> Calorie Distribution</div>',
                unsafe_allow_html=True)

    names = [i["name"].capitalize() for i in chart_items]
    cals  = [i["total_cal"]         for i in chart_items]
    clrs  = COLORS[:len(chart_items)]

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        fig_pie = go.Figure(go.Pie(
            labels=names, values=cals, hole=.46,
            marker=dict(colors=clrs, line=dict(color="#0A0A0A", width=2)),
            textfont=dict(family="Plus Jakarta Sans", size=12, color="#F0E8DC"),
            hovertemplate="<b>%{label}</b><br>%{value} kcal · %{percent}<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=10,l=10,r=10), height=300,
            legend=dict(font=dict(family="Plus Jakarta Sans", size=11, color="#F0E8DC"),
                        bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar":False})

    with col2:
        fig_bar = go.Figure(go.Bar(
            x=names, y=cals,
            marker=dict(color=clrs, line=dict(color="rgba(0,0,0,0)")),
            text=cals, textposition="outside",
            textfont=dict(family="Syne", size=11, color="#F0E8DC"),
            hovertemplate="<b>%{x}</b><br>%{y} kcal<extra></extra>",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(family="Plus Jakarta Sans", size=11, color="#666")),
            yaxis=dict(showgrid=True, gridcolor="#1E1E1E", zeroline=False,
                       tickfont=dict(family="Plus Jakarta Sans", size=10, color="#666"),
                       title=dict(text="kcal",
                                  font=dict(family="Plus Jakarta Sans", size=10, color="#666"))),
            margin=dict(t=35,b=10,l=10,r=10), height=300, bargap=0.32,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar":False})


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("##  Calorie Analyzer")
    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)

    dot   = "dot-g" if BACKEND_OK else "dot-r"
    label = "Backend connected" if BACKEND_OK else "Import error"
    st.markdown(
        f'<div class="sb-card"><span class="dot {dot}"></span><b>{label}</b></div>',
        unsafe_allow_html=True,
    )
    if not BACKEND_OK:
        st.markdown(
            f'<div class="sb-card" style="color:#E07050!important">{IMPORT_ERROR}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)
    st.markdown("###  Project Info")
    st.markdown(f"""
    <div class="sb-card">
        <b>Model:</b> thali-detection-clean/1<br>
        <b>Source:</b> Roboflow Serverless<br>
        <b>Confidence:</b> &gt; 0.2<br>
        <b>Foods in DB:</b> {len(nutrition) if BACKEND_OK else "—"}
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)
    st.markdown("###  How to Use")
    for step in [
        "1 Upload a thali photo or use camera",
        "2 Click <b>Analyze Food</b>",
        "3 See detected items &amp; kcal",
        "4 Check the distribution chart",
    ]:
        st.markdown(f'<div class="sb-card">{step}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)
    st.markdown("###  Nutrition Database")
    if BACKEND_OK:
        for food, cal in nutrition.items():
            st.markdown(
                f'<div class="sb-card" style="padding:.4rem .9rem">'
                f'{get_emoji(food)} <b>{food.capitalize()}</b> — {cal} kcal</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="sb-card">Unavailable</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-card" style="font-size:.74rem;color:#555!important">
         Model training is in progress. Detection accuracy will improve
        as more thali images are added to the Roboflow dataset.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ Minor Project · AI Powered</div>
    <h1> Food Calorie Analyzer</h1>
    <p>AI-powered Indian thali detection and calorie estimation using Roboflow</p>
</div>
""", unsafe_allow_html=True)

# Backend error banner
if not BACKEND_OK:
    st.markdown(f"""
    <div class="err-box">
        <b> Cannot import backend modules</b><br><br>
        <code>{IMPORT_ERROR}</code><br><br>
        <b>Fix checklist:</b><br>
        &nbsp;&nbsp;• This file must be inside <code>FoodCalorieAi/</code> (project root)<br>
        &nbsp;&nbsp;• Create empty <code>app/__init__.py</code><br>
        &nbsp;&nbsp;• Create empty <code>utils/__init__.py</code><br>
        &nbsp;&nbsp;• Run: <code>pip install inference-sdk streamlit plotly pillow</code>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Two-column layout ─────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown('<div class="slabel"><b>●</b> Input</div>', unsafe_allow_html=True)

    tab_upload, tab_camera = st.tabs(["    Upload Image  ", "    Camera  "])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Drop image here",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )

    with tab_camera:
        camera_photo = st.camera_input(
            "Point camera at your meal",
            label_visibility="collapsed",
        )

    # Resolve which image to use
    active_image = None
    if uploaded_file is not None:
        active_image = Image.open(uploaded_file).convert("RGB")
    elif camera_photo is not None:
        active_image = Image.open(camera_photo).convert("RGB")

    st.markdown("<br>", unsafe_allow_html=True)

    analyze_btn = st.button(
        "  Analyze Food",
        disabled=(active_image is None),
        help="Upload or capture an image first",
    )

# ── RIGHT COLUMN — Preview (base64 embedded, always inside the box) ───────────
with right_col:
    st.markdown('<div class="slabel"><b>●</b> Preview</div>', unsafe_allow_html=True)

    if active_image:
        # Resize for display
        preview = active_image.copy()
        preview.thumbnail((600, 400))
        # Convert to base64 so it renders INSIDE the HTML div
        b64 = pil_to_base64(preview)
        st.markdown(f"""
        <div class="prev-wrap">
            <img src="data:image/jpeg;base64,{b64}" alt="Food preview"/>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="prev-wrap">
            <div class="empty-prev">
                <div style="font-size:3rem">🍴</div>
                <div style="font-size:.85rem;color:#444;margin-top:.3rem">
                    Upload or capture a photo to preview
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Divider ───────────────────────────────────────────────────────────────────
st.markdown("<hr style='margin:1.6rem 0'>", unsafe_allow_html=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze_btn and active_image:
    with st.spinner(" Sending image to Roboflow model…"):
        try:
            img_path = process_image(active_image)

            # ── YOUR REAL BACKEND CALLS ──────────────────────────────────
            detected = detect_food(img_path)       # → list e.g. ["roti","dal"]
            calculate_calories(detected)           # prints breakdown to terminal
            # ─────────────────────────────────────────────────────────────

            try:
                os.unlink(img_path)
            except Exception:
                pass

        except Exception as exc:
            st.markdown(f"""
            <div class="err-box">
                 <b>Detection failed</b><br><br>
                <code>{exc}</code><br><br>
                Check your Roboflow API key and internet connection.
            </div>
            """, unsafe_allow_html=True)
            st.stop()

    display_items = build_items(detected)
    show_results(display_items)

elif not active_image:
    st.markdown("""
    <div style="text-align:center;padding:3.5rem 0">
        <div style="font-size:3.8rem;margin-bottom:1rem"></div>
        <div style="font-family:'Syne',sans-serif;font-size:1.15rem;
                    font-weight:800;color:#F0E8DC;margin-bottom:.4rem">
            Ready to Analyze
        </div>
        <div style="font-size:.85rem;color:#555">
            Upload a thali photo or use the camera,
            then click <b style="color:#F0A500">Analyze Food</b>
        </div>
    </div>
    """, unsafe_allow_html=True)