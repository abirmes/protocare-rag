import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import re
from datetime import datetime
from collections import Counter
from utils.api import get_history

st.set_page_config(page_title="MediAssist – Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("token"):
    st.switch_page("app.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [data-testid="stAppViewContainer"] { background:#F4F1EC !important; font-family:'DM Sans',sans-serif; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stHeader"] { background:transparent !important; }
[data-testid="stSidebar"] { background:#1A3A5C !important; border-right:none !important; }
[data-testid="stSidebar"] * { color:#E8E4DC !important; }
[data-testid="stButton"] button {
    font-family:'DM Sans',sans-serif !important; font-size:13px !important; font-weight:500 !important;
    border-radius:8px !important; background:rgba(255,255,255,0.1) !important;
    border:1px solid rgba(255,255,255,0.15) !important; color:#fff !important; width:100%;
}
[data-testid="stButton"] button:hover { background:rgba(255,255,255,0.2) !important; }
.page-header { background:#fff; border:1px solid #E2DDD5; border-radius:14px; padding:20px 28px;
    display:flex; align-items:center; justify-content:space-between; margin-bottom:22px;
    box-shadow:0 2px 12px rgba(0,0,0,0.04); }
.page-title { font-family:'Lora',serif; font-size:22px; font-weight:600; color:#1A3A5C; }
.page-sub { font-size:12.5px; color:#8A8070; margin-top:3px; }
.page-date { font-size:12px; color:#A09880; font-weight:500; }
.kpi { background:#fff; border:1px solid #E2DDD5; border-radius:12px; padding:20px 24px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04); position:relative; overflow:hidden; }
.kpi::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.kpi.blue::before  { background:#1A3A5C; }
.kpi.teal::before  { background:#0D9488; }
.kpi.amber::before { background:#D97706; }
.kpi.rose::before  { background:#E11D48; }
.kpi-label { font-size:10.5px; letter-spacing:1.4px; text-transform:uppercase; font-weight:600; color:#8A8070; margin-bottom:8px; }
.kpi-value { font-family:'Lora',serif; font-size:36px; font-weight:600; color:#1A3A5C; line-height:1; }
.kpi-sub   { font-size:11.5px; color:#A09880; margin-top:5px; }
.kpi-icon  { position:absolute; top:18px; right:20px; font-size:26px; opacity:.12; }
.sec { font-family:'Lora',serif; font-size:16px; font-weight:600; color:#1A3A5C;
    margin:24px 0 14px; display:flex; align-items:center; gap:8px; }
.sec hr { flex:1; border:none; border-top:1px solid #E2DDD5; margin-left:10px; }
.hist-card { background:#fff; border:1px solid #E2DDD5; border-radius:12px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.hist-row { padding:14px 20px; border-bottom:1px solid #F5F2EE; }
.hist-row:last-child { border-bottom:none; }
.hist-row:hover { background:#FAFAF8; }
.hist-q { font-size:14px; font-weight:500; color:#1A1A1A; margin-bottom:4px; }
.hist-preview { font-size:12.5px; color:#7A7060; margin-top:5px; line-height:1.5;
    display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.hist-meta { display:flex; gap:12px; align-items:center; margin-top:7px; flex-wrap:wrap; }
.hist-time { font-size:11px; color:#A09880; }
.tag  { font-size:11px; background:#EEF2F7; color:#2A4A6A; border-radius:16px; padding:2px 10px; font-weight:500; }
.chip { display:inline-block; background:#EEF2F7; border:1px solid #D8E0EB; border-radius:16px;
    padding:3px 10px; font-size:11px; color:#2A4A6A; margin:2px 2px 0 0; }
.topics { display:flex; flex-wrap:wrap; gap:7px; }
.topic      { background:#EEF2F7; border:1px solid #D8E0EB; border-radius:16px; padding:5px 12px; font-size:12.5px; color:#1A3A5C; font-weight:500; }
.topic.hot  { background:#FEF3C7; border-color:#FDE68A; color:#92400E; }
.topic.warm { background:#F0FDF4; border-color:#BBF7D0; color:#166534; }
.empty { text-align:center; padding:60px 20px; color:#A09880; }
.empty-icon  { font-size:44px; margin-bottom:14px; }
.empty-title { font-family:'Lora',serif; font-size:18px; color:#5A5040; margin-bottom:8px; }
.empty-text  { font-size:13px; line-height:1.6; }
[data-testid="stTextInput"] input { background:#fff !important; border:1.5px solid #DDD8CF !important;
    border-radius:10px !important; padding:10px 14px !important; font-size:14px !important; }
[data-testid="stSelectbox"] > div > div { background:#fff !important; border:1.5px solid #DDD8CF !important; border-radius:10px !important; }
[data-testid="stExpander"] { background:#FAFAF8 !important; border:1px solid #E8E4DC !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session ───────────────────────────────────────────────────────────────────
user     = st.session_state.get("user") or {}
username = user.get("username", "Médecin")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:0 0 20px;border-bottom:1px solid rgba(255,255,255,0.1);margin-bottom:20px;">
        <div style="font-family:'Lora',serif;font-size:19px;font-weight:600;color:#fff;margin-bottom:4px;">🏥 MediAssist</div>
        <div style="font-size:10px;color:rgba(255,255,255,0.4);letter-spacing:1.8px;text-transform:uppercase;">ProtoCare RAG</div>
    </div>
    <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-bottom:20px;">
        Connecté : <strong style="color:#fff;">{username}</strong>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,0.4);font-weight:600;margin-bottom:10px;">Navigation</div>', unsafe_allow_html=True)
    if st.button("💬  Assistant RAG"):
        st.switch_page("pages/chat.py")
    if st.button("📊  Tableau de bord"):
        pass
    st.markdown("---")
    limit = st.slider("Requêtes à charger", 10, 100, 50)
    st.markdown("---")
    if st.button("🚪  Se déconnecter"):
        st.session_state.token = None
        st.session_state.user  = None
        st.switch_page("app.py")

# ── Chargement  GET /history/ ─────────────────────────────────────────────────
@st.cache_data(ttl=30, show_spinner=False)
def load(token_hash, lim):
    return get_history(limit=lim)

with st.spinner("Chargement…"):
    raw, err = load(hash(st.session_state.token), limit)

if err == "SESSION_EXPIRED":
    st.session_state.token = None
    st.switch_page("app.py")

# Normalise en liste
records = []
if raw:
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        records = raw.get("items", raw.get("history", raw.get("queries", [])))

# ── Page header ───────────────────────────────────────────────────────────────
today = datetime.now().strftime("%A %d %B %Y")
st.markdown(f"""
<div class="page-header">
  <div>
    <div class="page-title">Tableau de bord</div>
    <div class="page-sub">Historique des requêtes · Table <code>query</code> · GET /history/</div>
  </div>
  <div class="page-date">📅 {today}</div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total    = len(records)
today_s  = datetime.now().strftime("%Y-%m-%d")
today_n  = sum(1 for r in records if today_s in str(r.get("created_at", "")))

# sources est déjà list[str] grâce à QueryOut.from_orm_custom dans le backend
total_src    = sum(len(r.get("sources", [])) for r in records)
total_chunks = sum(r.get("chunks_used", 0)   for r in records)

for col, (color, icon, label, val, sub) in zip(
    st.columns(4),
    [
        ("blue",  "📋", "Total requêtes",  total,        "enregistrées en base"),
        ("teal",  "🗓️",  "Aujourd'hui",    today_n,      "requêtes du jour"),
        ("amber", "📚", "Sources citées",  total_src,    "fichiers récupérés"),
        ("rose",  "🧩", "Chunks utilisés", total_chunks, "passages traités"),
    ]
):
    with col:
        st.markdown(f"""
        <div class="kpi {color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# ── Graphes ───────────────────────────────────────────────────────────────────
if records:
    col_g, col_t = st.columns([3, 2])

    with col_g:
        st.markdown('<div class="sec">📈 Activité quotidienne <hr></div>', unsafe_allow_html=True)
        date_counts: Counter = Counter()
        for r in records:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", str(r.get("created_at", "")))
            if m:
                date_counts[m.group(1)] += 1
        if date_counts:
            df = pd.DataFrame(sorted(date_counts.items()), columns=["Date", "Requêtes"])
            df["Date"] = pd.to_datetime(df["Date"])
            st.area_chart(df.set_index("Date"), height=180, use_container_width=True)
        else:
            st.info("Pas encore de données temporelles.")

    with col_t:
        st.markdown('<div class="sec">🏷️ Sujets fréquents <hr></div>', unsafe_allow_html=True)
        KEYWORDS = ["protocole","hypertension","diabète","antibiothérapie","douleur","urgence",
                    "posologie","interaction","traitement","diagnostic","cardio","pneumonie",
                    "sepsis","AVC","infarctus","allergie","anticoagulant","glycémie"]
        kw_c: Counter = Counter()
        for r in records:
            # colonne "query" dans la table (pas "question")
            q = str(r.get("query", "")).lower()
            for kw in KEYWORDS:
                if kw in q:
                    kw_c[kw] += 1
        top = kw_c.most_common(10)
        if top:
            mx = top[0][1]
            chips = "".join(
                f'<span class="topic {"hot" if c >= mx*0.7 else "warm" if c >= mx*0.4 else ""}">'
                f'#{kw} ({c})</span>' for kw, c in top
            )
            st.markdown(f'<div class="topics">{chips}</div>', unsafe_allow_html=True)
        else:
            st.info("Pas encore assez de données.")

# ── Liste historique ──────────────────────────────────────────────────────────
st.markdown('<div class="sec">🕐 Historique des interactions <hr></div>', unsafe_allow_html=True)

s_col, f_col = st.columns([4, 1])
with s_col:
    search = st.text_input("", placeholder="🔍  Rechercher dans les requêtes…", label_visibility="collapsed")
with f_col:
    order = st.selectbox("", ["Plus récent", "Plus ancien"], label_visibility="collapsed")

filtered = records
if search:
    filtered = [r for r in records if
        search.lower() in str(r.get("query",   "")).lower()   # colonne "query"
        or search.lower() in str(r.get("reponse", "")).lower() # colonne "reponse"
    ]
if order == "Plus ancien":
    filtered = list(reversed(filtered))

if not filtered:
    st.markdown("""
    <div class="empty">
      <div class="empty-icon">📭</div>
      <div class="empty-title">Aucune interaction trouvée</div>
      <div class="empty-text">
        Vos échanges avec l'assistant apparaîtront ici après chaque POST /query/ask.
      </div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='font-size:12.5px;color:#8A8070;margin-bottom:12px;'>{len(filtered)} résultat{'s' if len(filtered)!=1 else ''}</div>", unsafe_allow_html=True)
    st.markdown('<div class="hist-card">', unsafe_allow_html=True)

    for i, rec in enumerate(filtered):
        # Noms de colonnes exacts du brief : query, reponse
        question   = str(rec.get("query",      "—"))
        reponse    = str(rec.get("reponse",     ""))
        sources    = rec.get("sources",    [])   # list[str] converti par le backend
        chunks     = rec.get("chunks_used", 0)
        raw_date   = str(rec.get("created_at", ""))

        try:
            dt    = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            fdate = dt.strftime("%d/%m/%Y à %H:%M")
        except Exception:
            fdate = raw_date[:16] or "—"

        preview    = reponse[:200] + "…" if len(reponse) > 200 else reponse
        src_tag    = f'<span class="tag">📚 {len(sources)} source{"s" if len(sources)!=1 else ""}</span>' if sources else ""
        chunk_tag  = f'<span class="tag">🧩 {chunks} chunk{"s" if chunks!=1 else ""}</span>'             if chunks  else ""

        st.markdown(f"""
        <div class="hist-row">
          <div class="hist-q">❓ {question}</div>
          <div class="hist-preview">{preview}</div>
          <div class="hist-meta">
            <span class="hist-time">🕐 {fdate}</span>
            {src_tag}{chunk_tag}
          </div>
        </div>""", unsafe_allow_html=True)

        with st.expander(f"Réponse complète #{i+1}"):
            st.markdown(f"**Question :** {question}\n\n---\n\n{reponse}")
            if sources:
                st.markdown("**Sources :**")
                for s in sources:
                    st.markdown(f"- 📄 `{s}`")
            if chunks:
                st.markdown(f"*{chunks} chunks utilisés*")

    st.markdown("</div>", unsafe_allow_html=True)

    # Export CSV
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("⬇️  Exporter en CSV"):
        df_exp = pd.DataFrame([{
            "Date":         str(r.get("created_at", "")),
            "Question":     str(r.get("query",   "")),      # colonne "query"
            "Réponse":      str(r.get("reponse", "")),      # colonne "reponse"
            "Sources":      ", ".join(r.get("sources", [])),
            "Chunks":       r.get("chunks_used", 0),
        } for r in filtered])
        st.download_button(
            "📥 Télécharger",
            data=df_exp.to_csv(index=False, encoding="utf-8-sig"),
            file_name=f"protocare_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )