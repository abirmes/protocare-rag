import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.api import login, register, get_me

st.set_page_config(
    page_title="ProtoCare",
    page_icon="⊕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin:0; padding:0; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #F7F4EF !important;
    font-family: 'Outfit', sans-serif;
}
[data-testid="collapsedControl"], #MainMenu, footer, header,
[data-testid="stHeader"] { display:none !important; visibility:hidden !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMain"] > div { padding: 0 !important; }

/* LEFT PANEL */
.left-panel {
    background: #17202A;
    min-height: 100vh;
    padding: 56px 52px;
    display: flex; flex-direction: column; justify-content: space-between;
    position: relative; overflow: hidden;
}
.left-circle-1 {
    position: absolute; top: -120px; right: -120px;
    width: 420px; height: 420px; border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.04);
}
.left-circle-2 {
    position: absolute; bottom: -80px; left: -60px;
    width: 280px; height: 280px; border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.03);
}
.left-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 13px; letter-spacing: 6px;
    text-transform: uppercase; font-weight: 400;
    color: rgba(240,234,224,0.9);
}
.left-headline {
    font-family: 'Cormorant Garamond', serif;
    font-size: 52px; font-weight: 300; line-height: 1.12;
    color: #F0EAE0; letter-spacing: -1px;
}
.left-headline em { color: rgba(240,234,224,0.28); font-style: italic; }
.left-caption {
    font-size: 13px; color: rgba(255,255,255,0.25);
    line-height: 1.8; max-width: 300px;
}
.left-footer {
    font-size: 10.5px; color: rgba(255,255,255,0.12);
    letter-spacing: 1.5px; text-transform: uppercase;
}

/* INPUTS */
[data-testid="stTextInput"] label {
    font-size: 10.5px !important; font-weight: 600 !important;
    letter-spacing: 1.8px !important; text-transform: uppercase !important;
    color: #888070 !important; margin-bottom: 6px !important;
}
[data-testid="stTextInput"] input {
    background: #fff !important;
    border: 1.5px solid #E4DED4 !important;
    border-radius: 8px !important;
    padding: 13px 18px !important;
    font-size: 14px !important;
    font-family: 'Outfit', sans-serif !important;
    color: #1C1C1C !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    transition: all 0.18s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #17202A !important;
    box-shadow: 0 0 0 3px rgba(23,32,42,0.08) !important;
}
[data-testid="stSelectbox"] label {
    font-size: 10.5px !important; font-weight: 600 !important;
    letter-spacing: 1.8px !important; text-transform: uppercase !important;
    color: #888070 !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #fff !important;
    border: 1.5px solid #E4DED4 !important;
    border-radius: 8px !important;
}

[data-testid="stFormSubmitButton"] button {
    width: 100% !important;
    background: #17202A !important; color: #F0EAE0 !important;
    border: none !important; border-radius: 8px !important;
    padding: 14px !important; font-size: 14px !important;
    font-weight: 500 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.5px !important;
    transition: opacity 0.18s !important;
    box-shadow: 0 4px 16px rgba(23,32,42,0.22) !important;
}
[data-testid="stFormSubmitButton"] button:hover { opacity: 0.88 !important; }

/* TABS */
[data-baseweb="tab-list"] {
    background: #EEEAE3 !important;
    border-radius: 8px !important; padding: 3px !important;
    gap: 3px !important; border-bottom: none !important;
    margin-bottom: 32px !important;
}
[data-baseweb="tab"] {
    border-radius: 6px !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 13px !important; font-weight: 400 !important;
    color: #8A8070 !important; padding: 9px 22px !important;
}
[aria-selected="true"] {
    background: #fff !important; color: #1C1C1C !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

.form-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 34px; font-weight: 300; color: #1C1C1C;
    letter-spacing: -0.5px; margin-bottom: 8px;
}
.form-sub { font-size: 13.5px; color: #8A8070; margin-bottom: 32px; line-height: 1.6; }
[data-testid="stAlert"] { border-radius: 8px !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)

for k, v in [("token", None), ("user", None), ("chat_messages", []), ("query_count", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.token:
    st.switch_page("pages/chat.py")

col_left, col_right = st.columns([9, 11])

with col_left:
    st.markdown("""
    <div class="left-panel">
      <div class="left-circle-1"></div>
      <div class="left-circle-2"></div>
      <div class="left-logo">ProtoCare</div>
      <div>
        <div class="left-headline">
          L'assistant qui<br>
          <em>connaît</em> vos<br>
          protocoles.
        </div>
        <div style="margin-top: 28px;">
          <div class="left-caption">
            Accès sécurisé · Données chiffrées<br>
            Réservé au personnel médical autorisé.<br><br>
            Base vectorielle ChromaDB · Mistral 7B<br>
            Self-RAG · MLFlow · ProtoCare v1.0
          </div>
        </div>
      </div>
      <div class="left-footer">© 2025 ProtoCare · Confidentiel</div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='padding: 56px 64px 56px 52px;'>", unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Connexion", "Créer un compte"])

    with tab_login:
        st.markdown('<div class="form-title">Bon retour.</div><div class="form-sub">Identifiez-vous pour accéder à l\'assistant médical.</div>', unsafe_allow_html=True)
        with st.form("login"):
            email    = st.text_input("Identifiant ou email", placeholder="dr.dupont ou dr@hopital.fr")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Accéder à ProtoCare →")
        if submit:
            if not email or not password:
                st.error("Veuillez remplir tous les champs.")
            else:
                with st.spinner(""):
                    data, err = login(email, password)
                if err:
                    st.error("Identifiants incorrects.")
                else:
                    st.session_state.token = data["access_token"]
                    user, _ = get_me()
                    st.session_state.user = user or {"username": email}
                    st.switch_page("pages/chat.py")

    with tab_register:
        st.markdown('<div class="form-title">Créer un compte.</div><div class="form-sub">Accès réservé au personnel médical autorisé.</div>', unsafe_allow_html=True)
        with st.form("register"):
            reg_user = st.text_input("Identifiant", placeholder="dr.dupont")
            reg_mail = st.text_input("Email professionnel", placeholder="dr@hopital.fr")
            reg_pwd  = st.text_input("Mot de passe", type="password", placeholder="Minimum 8 caractères")
            reg_conf = st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••")
            reg_role = st.selectbox("Rôle", ["medecin", "admin"],
                                    format_func=lambda x: "Médecin" if x == "medecin" else "Administrateur")
            submit_r = st.form_submit_button("Créer mon compte →")
        if submit_r:
            if not all([reg_user, reg_mail, reg_pwd]):
                st.error("Veuillez remplir tous les champs.")
            elif reg_pwd != reg_conf:
                st.error("Les mots de passe ne correspondent pas.")
            elif len(reg_pwd) < 8:
                st.error("Minimum 8 caractères requis.")
            else:
                with st.spinner(""):
                    data, err = register(reg_user, reg_mail, reg_pwd, role=reg_role)
                if err:
                    st.error(f"Erreur : {err}")
                else:
                    st.success("Compte créé avec succès. Connectez-vous.")

    st.markdown("</div>", unsafe_allow_html=True)