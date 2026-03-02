import streamlit as st
import sys, os, re
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api import query_rag

st.set_page_config(
    page_title="ProtoCare — Assistant",
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
#MainMenu, footer { display:none !important; visibility:hidden !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="collapsedControl"] { display:flex !important; visibility:visible !important; color: #17202A !important; }
.block-container { padding: 0 2.5rem 2rem !important; max-width: 100% !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #17202A !important;
    border-right: none !important;
    box-shadow: 6px 0 30px rgba(0,0,0,0.15) !important;
}
[data-testid="stSidebar"] * { color: #B8B0A0 !important; }
[data-testid="stSidebarNav"] { display: none !important; }

.sb-brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: 13px; font-weight: 400;
    letter-spacing: 5px; text-transform: uppercase;
    color: #F0EAE0 !important;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 22px;
}
.sb-username { font-size: 15px; font-weight: 500; color: #F0EAE0 !important; }
.sb-role { font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: #425A6A !important; margin-top: 3px; }
.sb-sep { height: 1px; background: rgba(255,255,255,0.05); margin: 20px 0; }
.sb-label { font-size: 9.5px; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: #304050 !important; margin-bottom: 10px; display: block; }
.sb-big-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 56px; font-weight: 300;
    color: #F0EAE0 !important; line-height: 1; letter-spacing: -2px;
}
.sb-num-sub { font-size: 11px; color: #425A6A !important; margin-top: 4px; }

/* Nav buttons — base */
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #7A9AAA !important; border-radius: 7px !important;
    font-size: 13px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 400 !important; padding: 10px 16px !important;
    width: 100% !important; text-align: left !important;
    transition: all 0.18s !important; margin-bottom: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: rgba(255,255,255,0.07) !important;
    color: #F0EAE0 !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* History button — nth-child(2) in nav section = highlighted gold */
[data-testid="stSidebar"] [data-testid="stButton"]:nth-of-type(2) button {
    background: rgba(212,168,83,0.12) !important;
    border: 1px solid rgba(212,168,83,0.3) !important;
    color: #D4A853 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"]:nth-of-type(2) button:hover {
    background: rgba(212,168,83,0.22) !important;
    border-color: rgba(212,168,83,0.5) !important;
    color: #E8C070 !important;
}

/* Logout button — last button = red */
[data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button {
    background: transparent !important;
    border: 1px solid rgba(220,80,60,0.2) !important;
    color: rgba(220,80,60,0.55) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"]:last-of-type button:hover {
    background: rgba(220,80,60,0.1) !important;
    border-color: rgba(220,80,60,0.45) !important;
    color: #DC503C !important;
}

[data-testid="stSidebar"] [data-testid="stSlider"] label {
    font-size: 9.5px !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; color: #304050 !important; font-weight: 700 !important;
}

/* ── TOPBAR ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 24px 0 20px;
    border-bottom: 1px solid rgba(28,28,28,0.07);
    margin-bottom: 36px;
}
.topbar-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 30px; font-weight: 300; color: #1C1C1C; letter-spacing: -0.3px;
}
.topbar-sub { font-size: 11.5px; color: #9A9080; margin-top: 4px; letter-spacing: 0.3px; }
.status-pill {
    display: flex; align-items: center; gap: 8px;
    background: #fff; border: 1px solid #EAE4DA;
    border-radius: 24px; padding: 8px 18px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}
.s-dot { width: 7px; height: 7px; border-radius: 50%; background: #4CAF82;
    animation: sp 2.5s infinite; }
@keyframes sp { 0%,100%{opacity:1}50%{opacity:0.4} }
.s-txt { font-size: 12px; font-weight: 500; color: #4CAF82; }

/* ── WELCOME ── */
.welcome-center { max-width: 680px; margin: 24px auto 0; text-align: center; }
.welcome-mark {
    width: 64px; height: 64px; background: #17202A; border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 24px;
    box-shadow: 0 8px 28px rgba(23,32,42,0.25);
}
.welcome-mark-txt {
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px; color: #F0EAE0; letter-spacing: 3px;
}
.welcome-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 36px; font-weight: 300; color: #1C1C1C;
    letter-spacing: -0.8px; margin-bottom: 12px;
}
.welcome-sub {
    font-size: 14px; color: #7A7060; line-height: 1.8; margin-bottom: 40px;
}
.sug-header {
    font-size: 10px; font-weight: 700; letter-spacing: 2.5px;
    text-transform: uppercase; color: #9A9080;
    display: flex; align-items: center; gap: 12px; margin-bottom: 12px;
    margin-top: 20px;
}
.sug-header::after { content:''; flex:1; height:1px; background:#EAE4DA; }

/* Suggestion buttons */
[data-testid="stButton"] button {
    background: #fff !important;
    border: 1px solid #EAE4DA !important;
    border-radius: 100px !important;
    padding: 9px 20px !important;
    font-size: 13px !important;
    color: #3A3020 !important;
    font-weight: 400 !important;
    font-family: 'Outfit', sans-serif !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    transition: all 0.18s !important;
}
[data-testid="stButton"] button:hover {
    background: #17202A !important; color: #F0EAE0 !important;
    border-color: #17202A !important;
    box-shadow: 0 4px 14px rgba(23,32,42,0.2) !important;
}

/* ── MESSAGES ── */
.msg-user-row { display:flex; justify-content:flex-end; margin:22px 0; }
.msg-user-bbl {
    background: #17202A; color: #F0EAE0;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 22px; max-width: 60%;
    font-size: 14px; line-height: 1.72;
    box-shadow: 0 4px 18px rgba(23,32,42,0.22);
}
.msg-ai-row {
    display: flex; align-items: flex-start;
    gap: 14px; margin: 22px 0; max-width: 74%;
}
.msg-ai-icon {
    width: 38px; height: 38px; min-width: 38px;
    background: #fff; border: 1px solid #EAE4DA;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px; color: #17202A;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.msg-ai-bbl {
    background: #fff; border: 1px solid #EAE4DA;
    border-radius: 4px 18px 18px 18px;
    padding: 16px 24px;
    font-size: 14px; line-height: 1.82; color: #2A2218;
    box-shadow: 0 2px 14px rgba(0,0,0,0.04);
}

/* ── INPUT ── */
[data-testid="stChatInput"] textarea {
    border: 1.5px solid #DDD8CE !important;
    border-radius: 12px !important;
    background: #fff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 14px !important; color: #1C1C1C !important;
    box-shadow: 0 2px 14px rgba(0,0,0,0.06) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #17202A !important;
    box-shadow: 0 0 0 3px rgba(23,32,42,0.07), 0 2px 14px rgba(0,0,0,0.06) !important;
}
</style>
""", unsafe_allow_html=True)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

user     = st.session_state.get("user", {})
username = user.get("username", "Médecin") if user else "Médecin"

SUGGESTIONS = [
    "Comment reconnaître une déshydratation chez un enfant ?",
    "Quels sont les signes de gravité d'une gastro-entérite ?",
    "Comment évaluer le score de Silverman ?",
    "Quand faut-il consulter pour un nourrisson fébrile ?",
    "Que faire en cas de convulsion fébrile ?",
    "Que faire immédiatement après une piqûre de méduse ?",
]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-brand">ProtoCare</div>
    <div class="sb-username">{username}</div>
    <div class="sb-role">Personnel médical</div>
    <div class="sb-sep"></div>
    <span class="sb-label">Session en cours</span>
    <div class="sb-big-num">{st.session_state.query_count}</div>
    <div class="sb-num-sub">requête{'s' if st.session_state.query_count != 1 else ''}</div>
    <div class="sb-sep"></div>
    <span class="sb-label">Navigation</span>
    """, unsafe_allow_html=True)

    if st.button("⊕  Assistant RAG", key="nav_chat"):
        pass
    if st.button("↗  Historique & Dashboard", key="nav_history"):
        st.switch_page("pages/history.py")

    st.markdown('<div class="sb-sep"></div><span class="sb-label">Paramètres RAG</span>', unsafe_allow_html=True)
    st.slider("Sources récupérées", 1, 10, 5)

    st.markdown('<div class="sb-sep"></div><span class="sb-label">Actions</span>', unsafe_allow_html=True)
    if st.button("↺  Nouvelle conversation", key="clear"):
        st.session_state.chat_messages = []
        st.rerun()
    if st.button("⎋  Déconnexion", key="logout"):
        for k in ["token", "user", "chat_messages", "query_count"]:
            st.session_state[k] = None if k in ["token", "user"] else ([] if k == "chat_messages" else 0)
        st.switch_page("app.py")

# ── TOPBAR ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div>
    <div class="topbar-title">Assistant Médical</div>
    <div class="topbar-sub">Protocoles cliniques · ChromaDB · Mistral 7B · Self-RAG</div>
  </div>
  <div class="status-pill">
    <div class="s-dot"></div>
    <span class="s-txt">Système actif</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── WELCOME ───────────────────────────────────────────────────────────────────
if not st.session_state.chat_messages:
    st.markdown(f"""
    <div class="welcome-center">
      <div class="welcome-mark"><div class="welcome-mark-txt">P</div></div>
      <div class="welcome-title">Bonjour, Dr. {username}</div>
      <div class="welcome-sub">
        Posez vos questions sur les protocoles cliniques, les conduites à tenir<br>
        ou les interactions médicamenteuses.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sug-header">Questions fréquentes</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": q})
                with st.spinner(""):
                    result, err = query_rag(q)
                if err == "SESSION_EXPIRED":
                    st.session_state.token = None
                    st.switch_page("app.py")
                answer = result.get("answer", str(result)) if not err else f"Erreur : {err}"
                st.session_state.query_count += 1
                st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                st.rerun()

# ── MESSAGES ──────────────────────────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    content = re.sub(r'<[^>]+>', '', msg["content"]).strip()
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user-row">
          <div class="msg-user-bbl">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-ai-row">
          <div class="msg-ai-icon">P</div>
          <div class="msg-ai-bbl">{content}</div>
        </div>""", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
question = st.chat_input("Posez votre question médicale…")
if question:
    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.spinner(""):
        result, err = query_rag(question)
    if err == "SESSION_EXPIRED":
        st.session_state.token = None
        st.switch_page("app.py")
    elif err:
        answer = f"Erreur : {err}"
    else:
        answer = result.get("answer", str(result))
    st.session_state.query_count += 1
    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    st.rerun()