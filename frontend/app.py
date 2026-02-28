import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.api import login, register, get_me

st.set_page_config(
    page_title="MediAssist – Connexion",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #F4F1EC !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="collapsedControl"], #MainMenu, footer, header { display:none !important; visibility:hidden; }

/* Carte centrale */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    background: #fff;
    border: 1px solid #E2DDD5;
    border-radius: 20px;
    padding: 40px 48px !important;
    box-shadow: 0 4px 32px rgba(0,0,0,0.07);
    max-width: 460px;
    margin: 40px auto;
}

/* Brand */
.brand { display:flex; align-items:center; gap:12px; margin-bottom:32px; }
.brand-icon { width:46px; height:46px; background:#1A3A5C; border-radius:12px;
    display:flex; align-items:center; justify-content:center; font-size:22px; }
.brand-name { font-family:'Lora',serif; font-size:21px; font-weight:600; color:#1A3A5C; }
.brand-sub { font-size:10px; color:#9A9080; letter-spacing:1.8px; text-transform:uppercase; }

.page-title { font-family:'Lora',serif; font-size:22px; font-weight:600; color:#1A3A5C; margin-bottom:4px; }
.page-sub { font-size:13px; color:#7A7060; margin-bottom:24px; }

/* Inputs */
[data-testid="stTextInput"] label { font-size:12.5px !important; font-weight:600 !important; color:#3A3A3A !important; }
[data-testid="stTextInput"] input {
    background:#FAFAF8 !important; border:1.5px solid #DDD8CF !important;
    border-radius:10px !important; padding:11px 15px !important;
    font-size:14px !important; font-family:'DM Sans',sans-serif !important; color:#1A1A1A !important;
}
[data-testid="stTextInput"] input:focus { border-color:#1A3A5C !important; box-shadow:0 0 0 3px rgba(26,58,92,0.08) !important; }

/* Selectbox */
[data-testid="stSelectbox"] label { font-size:12.5px !important; font-weight:600 !important; color:#3A3A3A !important; }
[data-testid="stSelectbox"] > div > div {
    background:#FAFAF8 !important; border:1.5px solid #DDD8CF !important; border-radius:10px !important;
}

/* Bouton submit */
[data-testid="stFormSubmitButton"] button {
    width:100% !important; background:#1A3A5C !important; color:#fff !important;
    border:none !important; border-radius:10px !important; padding:13px !important;
    font-size:14px !important; font-weight:600 !important; font-family:'DM Sans',sans-serif !important;
    cursor:pointer; transition: background 0.2s !important;
}
[data-testid="stFormSubmitButton"] button:hover { background:#0F2540 !important; }

/* Tabs */
[data-baseweb="tab-list"] {
    background:#F0EDE7 !important; border-radius:10px !important;
    padding:4px !important; gap:4px !important; border-bottom:none !important; margin-bottom:22px;
}
[data-baseweb="tab"] {
    border-radius:8px !important; font-family:'DM Sans',sans-serif !important;
    font-size:13px !important; font-weight:500 !important; color:#7A7060 !important; padding:8px 22px !important;
}
[aria-selected="true"] {
    background:#fff !important; color:#1A3A5C !important;
    font-weight:600 !important; box-shadow:0 1px 4px rgba(0,0,0,0.1) !important;
}
[data-testid="stAlert"] { border-radius:10px !important; font-size:13px !important; }

.footer { text-align:center; font-size:11.5px; color:#B0A898; margin-top:24px; line-height:1.7; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("token", None), ("user", None), ("chat_messages", []), ("query_count", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Déjà connecté → on redirige directement vers le chat
if st.session_state.token:
    st.switch_page("pages/chat.py")

# ── Contenu ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand">
  <div class="brand-icon">🏥</div>
  <div>
    <div class="brand-name">MediAssist</div>
    <div class="brand-sub">Assistant Médical RAG</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab_login, tab_register = st.tabs(["Connexion", "Créer un compte"])

# ── Onglet CONNEXION ──────────────────────────────────────────────────────────
with tab_login:
    st.markdown('<p class="page-title">Bon retour 👋</p><p class="page-sub">Connectez-vous à votre espace médical.</p>', unsafe_allow_html=True)

    with st.form("form_login"):
        # Votre backend accepte email OU username dans le champ "username" de OAuth2
        username = st.text_input("Email ou identifiant", placeholder="dr.dupont  ou  dr@hopital.fr")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
        submit   = st.form_submit_button("Se connecter →")

    if submit:
        if not username or not password:
            st.error("Remplissez tous les champs.")
        else:
            with st.spinner("Connexion…"):
                data, err = login(username, password)
            if err:
                st.error(f"❌ {err}")
            else:
                # Stocke le token JWT
                st.session_state.token = data["access_token"]
                # Récupère le profil utilisateur via GET /auth/me
                user, _ = get_me()
                st.session_state.user = user or {"username": username}
                st.success("✅ Connecté !")
                st.switch_page("pages/chat.py")

# ── Onglet INSCRIPTION ────────────────────────────────────────────────────────
with tab_register:
    st.markdown('<p class="page-title">Créer un compte</p><p class="page-sub">Accès réservé au personnel médical autorisé.</p>', unsafe_allow_html=True)

    with st.form("form_register"):
        # Champs exacts de votre UserCreate : username, email, password, role
        reg_username = st.text_input("Identifiant",           placeholder="dr.dupont")
        reg_email    = st.text_input("Email professionnel",   placeholder="dr@hopital.fr")
        reg_password = st.text_input("Mot de passe",          type="password", placeholder="Min. 8 caractères")
        reg_confirm  = st.text_input("Confirmer mot de passe",type="password", placeholder="••••••••")
        # Votre modèle User a un champ "role"
        reg_role     = st.selectbox("Rôle", ["medecin", "admin"],
                                    format_func=lambda x: "Médecin" if x == "medecin" else "Administrateur")
        submit_reg   = st.form_submit_button("Créer mon compte →")

    if submit_reg:
        if not all([reg_username, reg_email, reg_password]):
            st.error("Remplissez tous les champs.")
        elif reg_password != reg_confirm:
            st.error("Les mots de passe ne correspondent pas.")
        elif len(reg_password) < 8:
            st.error("Mot de passe trop court (min. 8 caractères).")
        else:
            with st.spinner("Création du compte…"):
                # Appel POST /auth/register avec { username, email, password, role }
                data, err = register(reg_username, reg_email, reg_password, role=reg_role)
            if err:
                st.error(f"❌ {err}")
            else:
                st.success("✅ Compte créé ! Connectez-vous dans l'onglet Connexion.")

st.markdown('<div class="footer">Données sécurisées · Conformité RGPD<br>© 2025 MediAssist</div>', unsafe_allow_html=True)