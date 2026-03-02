import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import re
from datetime import datetime
from collections import Counter
from utils.api import get_history

st.set_page_config(
    page_title="ProtoCare — Historique",
    page_icon="⊕",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("token"):
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #F7F4EF !important;
    font-family: 'Outfit', sans-serif; color: #1C1C1C;
}
#MainMenu, footer, [data-testid="stHeader"] { display:none !important; visibility:hidden !important; }
.block-container { padding: 0 2.5rem 2rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] { background: #17202A !important; border-right:none !important; box-shadow: 6px 0 30px rgba(0,0,0,0.15) !important; }
[data-testid="stSidebar"] * { color: #B8B0A0 !important; }
[data-testid="stSidebarNav"] { display: none !important; }
.sb-brand { font-family:'Cormorant Garamond',serif; font-size:13px; font-weight:400;
    letter-spacing:5px; text-transform:uppercase; color:#F0EAE0 !important;
    padding-bottom:20px; border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:22px; }
.sb-username { font-size:15px; font-weight:500; color:#F0EAE0 !important; }
.sb-role { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:#425A6A !important; margin-top:3px; }
.sb-sep { height:1px; background:rgba(255,255,255,0.05); margin:20px 0; }
.sb-label { font-size:9.5px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
    color:#304050 !important; margin-bottom:10px; display:block; }
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background:transparent !important; border:1px solid rgba(255,255,255,0.06) !important;
    color:#7A9AAA !important; border-radius:7px !important; font-size:13px !important;
    font-family:'Outfit',sans-serif !important; font-weight:400 !important;
    padding:10px 16px !important; width:100% !important; text-align:left !important;
    transition:all 0.18s !important; margin-bottom:6px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background:rgba(255,255,255,0.07) !important; color:#F0EAE0 !important;
    border-color:rgba(255,255,255,0.15) !important;
}
/* Assistant button — first = highlighted gold */
[data-testid="stSidebar"] [data-testid="stButton"]:nth-of-type(1) button {
    background: rgba(212,168,83,0.12) !important;
    border: 1px solid rgba(212,168,83,0.3) !important;
    color: #D4A853 !important; font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"]:nth-of-type(1) button:hover {
    background: rgba(212,168,83,0.22) !important;
    border-color: rgba(212,168,83,0.5) !important; color: #E8C070 !important;
}
/* Logout — last button = red */
[data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button {
    background: transparent !important;
    border: 1px solid rgba(220,80,60,0.2) !important;
    color: rgba(220,80,60,0.55) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button:hover {
    background: rgba(220,80,60,0.1) !important;
    border-color: rgba(220,80,60,0.45) !important; color: #DC503C !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] label {
    font-size:9.5px !important; letter-spacing:2px !important;
    text-transform:uppercase !important; color:#304050 !important; font-weight:700 !important;
}

/* PAGE HEADER */
.page-top {
    display:flex; align-items:center; justify-content:space-between;
    padding: 24px 0 20px;
    border-bottom: 1px solid rgba(28,28,28,0.07);
    margin-bottom: 32px;
}
.page-h { font-family:'Cormorant Garamond',serif; font-size:30px; font-weight:300;
    color:#1C1C1C; letter-spacing:-0.3px; }
.page-sub { font-size:11.5px; color:#9A9080; margin-top:4px; letter-spacing:0.3px; }
.page-date { font-size:12px; color:#B0A890; font-weight:400; }

/* KPIs */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:36px; }
.kpi {
    background:#fff; border:1px solid #EAE4DA; border-radius:10px;
    padding:22px 24px; position:relative; overflow:hidden;
    box-shadow:0 2px 12px rgba(0,0,0,0.04);
}
.kpi-accent { position:absolute; top:0; left:0; right:0; height:2.5px; border-radius:10px 10px 0 0; }
.kpi-label { font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase;
    color:#A09880; margin-bottom:10px; }
.kpi-val { font-family:'Cormorant Garamond',serif; font-size:44px; font-weight:300;
    color:#1C1C1C; line-height:1; letter-spacing:-1px; }
.kpi-sub { font-size:11.5px; color:#C0B8A8; margin-top:6px; }

/* SECTION TITLES */
.sec-h { font-size:10px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
    color:#9A9080; display:flex; align-items:center; gap:12px; margin-bottom:16px; }
.sec-h::after { content:''; flex:1; height:1px; background:#EAE4DA; }

/* HISTORY */
.hist-wrap { background:#fff; border:1px solid #EAE4DA; border-radius:10px;
    overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.04); }
.hist-row { padding:18px 24px; border-bottom:1px solid #F5F0EA; transition:background 0.15s; }
.hist-row:last-child { border-bottom:none; }
.hist-row:hover { background:#FDFAF6; }
.hist-q { font-size:14px; font-weight:500; color:#1C1C1C; margin-bottom:6px; }
.hist-preview { font-size:13px; color:#7A7060; line-height:1.65;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.hist-meta { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:10px; }
.hist-date { font-size:11px; color:#C0B8A8; }
.hist-tag { font-size:11px; background:#F5F0EA; color:#5A5040; border-radius:4px;
    padding:2px 9px; font-weight:500; }

/* TOPIC PILLS */
.topic { display:inline-block; border-radius:6px; padding:5px 12px;
    font-size:12px; font-weight:500; margin:3px 3px 0 0; }
.topic.hot { background:#17202A; color:#F0EAE0; }
.topic.warm { background:#F5F0EA; color:#4A4030; border:1px solid #EAE4DA; }
.topic.cool { background:#EEF2F7; color:#2A4060; border:1px solid #D8E4F0; }

.empty-state { text-align:center; padding:80px 20px; }
.empty-icon { font-family:'Cormorant Garamond',serif; font-size:56px; color:rgba(28,28,28,0.06);
    margin-bottom:20px; }
.empty-h { font-family:'Cormorant Garamond',serif; font-size:24px; font-weight:300;
    color:#5A5040; margin-bottom:8px; }
.empty-p { font-size:13px; color:#A09880; line-height:1.7; }

[data-testid="stTextInput"] input { background:#fff !important; border:1.5px solid #E4DED4 !important;
    border-radius:8px !important; padding:11px 15px !important; font-size:14px !important;
    font-family:'Outfit',sans-serif !important; }
[data-testid="stTextInput"] input:focus { border-color:#17202A !important; box-shadow:none !important; }
[data-testid="stSelectbox"] > div > div { background:#fff !important;
    border:1.5px solid #E4DED4 !important; border-radius:8px !important; }
[data-testid="stButton"] button { font-family:'Outfit',sans-serif !important;
    font-size:13px !important; border-radius:7px !important; }
[data-testid="stExpander"] { background:#FDFAF6 !important;
    border:1px solid #EAE4DA !important; border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)

user     = st.session_state.get("user") or {}
username = user.get("username", "Médecin")

with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">ProtoCare</div>
    <div class="sb-username">{username}</div>
    <div class="sb-role">Personnel médical</div>
    <div class="sb-sep"></div>
    <span class="sb-label">Navigation</span>
    """, unsafe_allow_html=True)
    if st.button("↗  Assistant RAG", key="nav_chat"):
        st.switch_page("pages/chat.py")
    if st.button("⊕  Historique & Dashboard", key="nav_history"):
        pass
    st.markdown('<div class="sb-sep"></div><span class="sb-label">Affichage</span>', unsafe_allow_html=True)
    limit = st.slider("Requêtes à charger", 10, 100, 50)
    st.markdown('<div class="sb-sep"></div>', unsafe_allow_html=True)
    if st.button("⎋  Déconnexion", key="logout"):
        st.session_state.token = None
        st.session_state.user  = None
        st.switch_page("app.py")

@st.cache_data(ttl=30, show_spinner=False)
def load(token_hash, lim):
    return get_history(limit=lim)

with st.spinner(""):
    raw, err = load(hash(st.session_state.token), limit)

if err == "SESSION_EXPIRED":
    st.session_state.token = None
    st.switch_page("app.py")

records = []
if raw:
    if isinstance(raw, list): records = raw
    elif isinstance(raw, dict): records = raw.get("items", raw.get("history", raw.get("queries", [])))

today = datetime.now().strftime("%d %B %Y")
st.markdown(f"""
<div class="page-top">
  <div>
    <div class="page-h">Historique & Dashboard</div>
    <div class="page-sub">Table query · GET /history/ · Base PostgreSQL</div>
  </div>
  <div class="page-date">{today}</div>
</div>
""", unsafe_allow_html=True)

total        = len(records)
today_s      = datetime.now().strftime("%Y-%m-%d")
today_n      = sum(1 for r in records if today_s in str(r.get("created_at", "")))
total_src    = sum(len(r.get("sources", [])) for r in records)
total_chunks = sum(r.get("chunks_used", 0) for r in records)

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi"><div class="kpi-accent" style="background:#17202A;"></div>
    <div class="kpi-label">Total requêtes</div>
    <div class="kpi-val">{total}</div>
    <div class="kpi-sub">enregistrées en base</div>
  </div>
  <div class="kpi"><div class="kpi-accent" style="background:#4CAF82;"></div>
    <div class="kpi-label">Aujourd'hui</div>
    <div class="kpi-val">{today_n}</div>
    <div class="kpi-sub">requêtes du jour</div>
  </div>
  <div class="kpi"><div class="kpi-accent" style="background:#D4A853;"></div>
    <div class="kpi-label">Sources citées</div>
    <div class="kpi-val">{total_src}</div>
    <div class="kpi-sub">fichiers récupérés</div>
  </div>
  <div class="kpi"><div class="kpi-accent" style="background:#6B8CBE;"></div>
    <div class="kpi-label">Chunks utilisés</div>
    <div class="kpi-val">{total_chunks}</div>
    <div class="kpi-sub">passages traités</div>
  </div>
</div>
""", unsafe_allow_html=True)

if records:
    col_g, col_t = st.columns([3, 2])
    with col_g:
        st.markdown('<div class="sec-h">Activité quotidienne</div>', unsafe_allow_html=True)
        date_counts: Counter = Counter()
        for r in records:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", str(r.get("created_at", "")))
            if m: date_counts[m.group(1)] += 1
        if date_counts:
            df = pd.DataFrame(sorted(date_counts.items()), columns=["Date", "Requêtes"])
            df["Date"] = pd.to_datetime(df["Date"])
            st.area_chart(df.set_index("Date"), height=160, use_container_width=True)

    with col_t:
        st.markdown('<div class="sec-h">Sujets fréquents</div>', unsafe_allow_html=True)
        KEYWORDS = ["diarrhée","toux","fièvre","détresse","douleur","agitation","méduse","violence",
                    "urgence","traitement","diagnostic","protocole","posologie","infection","allergie"]
        kw_c: Counter = Counter()
        for r in records:
            q = str(r.get("query", "")).lower()
            for kw in KEYWORDS:
                if kw in q: kw_c[kw] += 1
        top = kw_c.most_common(12)
        if top:
            mx = top[0][1]
            chips = "".join(
                f'<span class="topic {"hot" if c >= mx*0.7 else "warm" if c >= mx*0.4 else "cool"}">'
                f'{kw} ({c})</span>' for kw, c in top
            )
            st.markdown(f'<div style="margin-top:8px;">{chips}</div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)
st.markdown('<div class="sec-h">Interactions</div>', unsafe_allow_html=True)

s_col, f_col = st.columns([4, 1])
with s_col:
    search = st.text_input("", placeholder="Rechercher dans les requêtes…", label_visibility="collapsed")
with f_col:
    order = st.selectbox("", ["Plus récent", "Plus ancien"], label_visibility="collapsed")

filtered = records
if search:
    filtered = [r for r in records if
        search.lower() in str(r.get("query", "")).lower()
        or search.lower() in str(r.get("reponse", "")).lower()]
if order == "Plus ancien":
    filtered = list(reversed(filtered))

if not filtered:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">∅</div>
      <div class="empty-h">Aucune interaction trouvée</div>
      <div class="empty-p">Vos échanges avec l'assistant apparaîtront ici.</div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='font-size:12px;color:#A09880;margin-bottom:14px;'>{len(filtered)} résultat{'s' if len(filtered)!=1 else ''}</div>", unsafe_allow_html=True)
    st.markdown('<div class="hist-wrap">', unsafe_allow_html=True)
    for i, rec in enumerate(filtered):
        question = str(rec.get("query", "—"))
        reponse  = str(rec.get("reponse", ""))
        sources  = rec.get("sources", [])
        chunks   = rec.get("chunks_used", 0)
        raw_date = str(rec.get("created_at", ""))
        try:
            dt    = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            fdate = dt.strftime("%d/%m/%Y · %H:%M")
        except: fdate = raw_date[:16] or "—"

        preview   = reponse[:180] + "…" if len(reponse) > 180 else reponse
        src_tag   = f'<span class="hist-tag">{len(sources)} source{"s" if len(sources)!=1 else ""}</span>' if sources else ""
        chunk_tag = f'<span class="hist-tag">{chunks} chunk{"s" if chunks!=1 else ""}</span>' if chunks else ""

        st.markdown(f"""
        <div class="hist-row">
          <div class="hist-q">{question}</div>
          <div class="hist-preview">{preview}</div>
          <div class="hist-meta">
            <span class="hist-date">{fdate}</span>
            {src_tag}{chunk_tag}
          </div>
        </div>""", unsafe_allow_html=True)

        with st.expander(f"Réponse complète"):
            st.markdown(f"**Question :** {question}\n\n---\n\n{reponse}")
            if sources:
                st.markdown("**Sources :**")
                for s in sources: st.markdown(f"- `{s}`")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("⬇  Exporter en CSV"):
        df_exp = pd.DataFrame([{
            "Date": str(r.get("created_at", "")),
            "Question": str(r.get("query", "")),
            "Réponse": str(r.get("reponse", "")),
            "Sources": ", ".join(r.get("sources", [])),
            "Chunks": r.get("chunks_used", 0),
        } for r in filtered])
        st.download_button("Télécharger",
            data=df_exp.to_csv(index=False, encoding="utf-8-sig"),
            file_name=f"protocare_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv")