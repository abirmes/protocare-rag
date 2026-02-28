import streamlit as st
import sys, os, time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api import query_rag, get_me

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediAssist – Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth guard ────────────────────────────────────────────────────────────────
if not st.session_state.get("token"):
    st.switch_page("app.py")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background: #F4F1EC !important;
        font-family: 'DM Sans', sans-serif;
    }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stHeader"] { background: transparent !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #1A3A5C !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * { color: #E8E4DC !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
    [data-testid="stSidebarNav"] a {
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13.5px !important; font-weight: 500 !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,0.1) !important;
    }
    [data-testid="stSidebarNav"] [aria-selected="true"] a {
        background: rgba(255,255,255,0.15) !important;
    }

    /* ── Chat container ── */
    .chat-header {
        background: #FFFFFF;
        border-bottom: 1px solid #E2DDD5;
        padding: 18px 32px;
        display: flex; align-items: center; justify-content: space-between;
        border-radius: 16px 16px 0 0;
        margin-bottom: 0;
    }
    .chat-title {
        font-family: 'Lora', serif; font-size: 20px;
        font-weight: 600; color: #1A3A5C;
    }
    .chat-subtitle { font-size: 12.5px; color: #8A8070; margin-top: 2px; }

    .status-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #22C55E; display: inline-block;
        margin-right: 6px; animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; } 50% { opacity: 0.4; }
    }
    .status-label { font-size: 12px; color: #22C55E; font-weight: 600; }

    /* ── Messages ── */
    .msg-container { padding: 8px 0; }

    .msg-user-wrap {
        display: flex; justify-content: flex-end; margin: 12px 0;
    }
    .msg-user {
        background: #1A3A5C; color: #FFFFFF;
        border-radius: 18px 18px 4px 18px;
        padding: 13px 18px; max-width: 70%;
        font-size: 14px; line-height: 1.6;
        box-shadow: 0 2px 8px rgba(26,58,92,0.25);
        word-wrap: break-word; overflow-wrap: break-word;
        white-space: normal;
    }

    .msg-assistant-wrap {
        display: flex; justify-content: flex-start; gap: 12px; margin: 12px 0;
        max-width: 82%;
    }
    .msg-avatar {
        width: 36px; height: 36px; min-width: 36px;
        background: #E8F0F7; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }
    .msg-assistant {
        background: #FFFFFF;
        border: 1px solid #E8E4DC;
        border-radius: 4px 18px 18px 18px;
        padding: 14px 20px; max-width: 100%;
        font-size: 14px; line-height: 1.7;
        color: #2A2A2A;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .msg-assistant p { margin: 0 0 8px; }
    .msg-assistant p:last-child { margin-bottom: 0; }

    .msg-time {
        font-size: 11px; color: #B0A898; margin-top: 5px;
        text-align: right;
    }

    /* ── Sources ── */
    .sources-section {
        margin-top: 14px; padding-top: 12px;
        border-top: 1px solid #F0EDE7;
    }
    .sources-label {
        font-size: 11px; font-weight: 600; color: #8A8070;
        letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;
    }
    .source-chip {
        display: inline-flex; align-items: center; gap: 5px;
        background: #F0EDE7; border-radius: 20px;
        padding: 4px 12px; font-size: 11.5px;
        color: #4A6080; font-weight: 500; margin: 3px 3px 0 0;
        border: 1px solid #E2DDD5;
    }

    /* ── Suggestions ── */
    .suggestions-wrap { margin: 20px 0 8px; }
    .suggestions-title {
        font-size: 12px; color: #8A8070; font-weight: 500;
        margin-bottom: 10px; letter-spacing: 0.3px;
    }

    /* ── Input area ── */
    .input-area {
        background: #FFFFFF;
        border-top: 1px solid #E2DDD5;
        padding: 16px 24px;
        border-radius: 0 0 16px 16px;
    }
    [data-testid="stChatInput"] {
        border: 1.5px solid #DDD8CF !important;
        border-radius: 12px !important;
        background: #FAFAF8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #1A3A5C !important;
        box-shadow: 0 0 0 3px rgba(26,58,92,0.08) !important;
    }

    /* ── Sidebar cards ── */
    .sidebar-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 12px; padding: 14px 16px; margin-bottom: 12px;
    }
    .sidebar-card-title {
        font-size: 10.5px; letter-spacing: 1.5px;
        text-transform: uppercase; font-weight: 600;
        color: rgba(255,255,255,0.5) !important; margin-bottom: 8px;
    }
    .sidebar-stat {
        font-size: 26px; font-weight: 700;
        font-family: 'Lora', serif; color: #FFFFFF !important;
    }
    .sidebar-stat-label {
        font-size: 12px; color: rgba(255,255,255,0.6) !important;
    }

    /* Buttons */
    [data-testid="stButton"] button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important; font-weight: 500 !important;
        border-radius: 8px !important;
    }
    .clear-btn [data-testid="stButton"] button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #fff !important; width: 100%;
    }
    .clear-btn [data-testid="stButton"] button:hover {
        background: rgba(255,255,255,0.18) !important;
    }

    /* Slider */
    [data-testid="stSlider"] label {
        color: rgba(255,255,255,0.8) !important;
        font-size: 12.5px !important;
    }
    [data-testid="stSlider"] [data-testid="stTickBar"] span {
        color: rgba(255,255,255,0.5) !important; font-size: 11px !important;
    }

    /* Welcome card */
    .welcome-card {
        background: #FFFFFF; border: 1px solid #E8E4DC;
        border-radius: 16px; padding: 32px;
        text-align: center; margin: 24px auto; max-width: 600px;
    }
    .welcome-icon { font-size: 48px; margin-bottom: 16px; }
    .welcome-title {
        font-family: 'Lora', serif; font-size: 22px;
        font-weight: 600; color: #1A3A5C; margin-bottom: 8px;
    }
    .welcome-text { font-size: 14px; color: #7A7060; line-height: 1.7; }

    /* Typing indicator */
    .typing-dots {
        display: flex; gap: 5px; align-items: center; padding: 4px 0;
    }
    .typing-dots span {
        width: 7px; height: 7px; background: #A0AEC0;
        border-radius: 50%; animation: bounce 1.2s infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-6px); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session init ──────────────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

user = st.session_state.get("user", {})
username = user.get("username", "Médecin") if user else "Médecin"
full_name = user.get("full_name", username) if user else username

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown(
        f"""
        <div style="padding: 8px 0 24px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
            <div style="font-family:'Lora',serif; font-size:20px; font-weight:600; color:#fff; margin-bottom:4px;">🏥 MediAssist</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.4); letter-spacing:1.5px; text-transform:uppercase;">Assistant Médical RAG</div>
        </div>
        <div style="font-size:13px; color:rgba(255,255,255,0.7); margin-bottom:20px;">
            Bonjour, <strong style="color:#fff;">{full_name}</strong> 👋
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stats card
    st.markdown(
        f"""
        <div class="sidebar-card">
            <div class="sidebar-card-title">Session actuelle</div>
            <div class="sidebar-stat">{st.session_state.query_count}</div>
            <div class="sidebar-stat-label">requête{'s' if st.session_state.query_count != 1 else ''} effectuée{'s' if st.session_state.query_count != 1 else ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Navigation
    st.markdown(
        '<div style="font-size:10.5px; letter-spacing:1.5px; text-transform:uppercase; color:rgba(255,255,255,0.4); font-weight:600; margin-bottom:10px;">Navigation</div>',
        unsafe_allow_html=True,
    )
    if st.button("💬  Assistant RAG", use_container_width=True):
        pass  # already here
    if st.button("📊  Tableau de bord", use_container_width=True):
        st.switch_page("pages/history.py")

    st.markdown("---")

    # RAG settings
    st.markdown(
        '<div style="font-size:10.5px; letter-spacing:1.5px; text-transform:uppercase; color:rgba(255,255,255,0.4); font-weight:600; margin-bottom:10px;">Paramètres RAG</div>',
        unsafe_allow_html=True,
    )
    k_results = st.slider("Nombre de sources", min_value=1, max_value=10, value=5, help="Nombre de passages à récupérer")

    st.markdown("---")

    # Logout + clear
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️  Effacer la conversation", use_container_width=True):
        st.session_state.chat_messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if st.button("🚪  Se déconnecter", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.chat_messages = []
        st.session_state.query_count = 0
        st.switch_page("app.py")

# ── MAIN CONTENT ──────────────────────────────────────────────────────────────
# Header bar
st.markdown(
    """
    <div class="chat-header">
        <div>
            <div class="chat-title">Assistant Médical</div>
            <div class="chat-subtitle">Guide des protocoles cliniques · Base vectorielle ChromaDB</div>
        </div>
        <div>
            <span class="status-dot"></span>
            <span class="status-label">En ligne</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Suggestions rapides
SUGGESTIONS = [
    "📋 Protocole hypertension artérielle",
    "💊 Interaction médicamenteuse warfarine",
    "🚨 Prise en charge choc anaphylactique",
    "🩺 Critères diagnostic diabète type 2",
    "🏥 Protocole AVC en urgence",
]

# Welcome state
if not st.session_state.chat_messages:
    st.markdown(
        f"""
        <div class="welcome-card">
            <div class="welcome-icon">🩺</div>
            <div class="welcome-title">Bonjour, Dr. {full_name.split()[-1] if full_name else username}</div>
            <div class="welcome-text">
                Je suis votre assistant médical RAG. Posez-moi vos questions sur les protocoles cliniques,
                les interactions médicamenteuses, ou les guidelines thérapeutiques.<br><br>
                <strong>Commencez par une suggestion ou tapez votre question.</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="suggestions-wrap"><div class="suggestions-title">💡 Suggestions fréquentes</div></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(SUGGESTIONS))
    for i, (col, suggestion) in enumerate(zip(cols, SUGGESTIONS)):
        with col:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                # Extract clean text (remove emoji prefix)
                clean_q = suggestion.split(" ", 1)[1] if " " in suggestion else suggestion
                st.session_state.chat_messages.append({"role": "user", "content": clean_q, "time": datetime.now().strftime("%H:%M")})
                with st.spinner("Recherche en cours…"):
                    result, err = query_rag(clean_q)
                if err == "SESSION_EXPIRED":
                    st.session_state.token = None
                    st.switch_page("app.py")
                elif err:
                    answer = f"❌ Erreur : {err}"
                    sources = []
                else:
                    answer = result.get("answer", result.get("response", str(result)))
                    sources = result.get("sources", result.get("contexts", []))
                st.session_state.query_count += 1
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "time": datetime.now().strftime("%H:%M"),
                })
                st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    role = msg["role"]
    content = msg["content"]
    ts = msg.get("time", "")

    if role == "user":
        st.markdown(
            f"""
            <div class="msg-user-wrap">
                <div>
                    <div class="msg-user">{content}</div>
                    <div class="msg-time">{ts}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        sources = msg.get("sources", [])

        # Nettoyer le contenu de tout HTML résiduel
        import re
        clean_content = re.sub(r'<[^>]+>', '', content).strip()
        # Supprimer les </div> orphelins et balises résiduelles
        clean_content = re.sub(r'</?\w+[^>]*>', '', clean_content).strip()

        sources_html = ""
        if sources:
            chips = "".join(
                f'<span class="source-chip">📄 {s.get("source", s.get("metadata", {}).get("source", f"Source {i+1}")) if isinstance(s, dict) else s}</span>'
                for i, s in enumerate(sources[:5])
            )
            sources_html = f"""
            <div class="sources-section">
                <div class="sources-label">📚 Sources consultées</div>
                {chips}
            </div>
            """

        st.markdown(
            f"""
            <div class="msg-assistant-wrap">
                <div class="msg-avatar">🤖</div>
                <div style="max-width:82%;">
                    <div class="msg-assistant" style="max-width:100%;">
                        {clean_content}
                        {sources_html}
                    </div>
                    <div class="msg-time">{ts}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Input ─────────────────────────────────────────────────────────────────────
question = st.chat_input("Posez votre question médicale…")

if question:
    now = datetime.now().strftime("%H:%M")
    st.session_state.chat_messages.append({"role": "user", "content": question, "time": now})

    with st.spinner("🔍 Recherche dans la base de connaissances…"):
        result, err = query_rag(question)

    if err == "SESSION_EXPIRED":
        st.error("Session expirée. Reconnexion…")
        st.session_state.token = None
        time.sleep(1)
        st.switch_page("app.py")
    elif err:
        answer = f"❌ Une erreur est survenue : {err}"
        sources = []
    else:
        answer = result.get("answer", result.get("response", str(result)))
        sources = result.get("sources", result.get("contexts", []))

    st.session_state.query_count += 1
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "time": datetime.now().strftime("%H:%M"),
    })
    st.rerun()