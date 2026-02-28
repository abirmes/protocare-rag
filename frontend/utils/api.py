
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002")
API_PREFIX   = os.getenv("API_PREFIX", "")   


def _url(path: str) -> str:
    return f"{API_BASE_URL}{API_PREFIX}{path}"


def _auth_headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}



def login(username: str, password: str):
    try:
        r = requests.post(
            _url("/auth/login"),
            data={"username": username, "password": password},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Identifiants incorrects")
    except requests.exceptions.ConnectionError:
        return None, "Impossible de joindre le serveur."
    except requests.exceptions.Timeout:
        return None, "Serveur ne répond pas."
    except Exception as e:
        return None, str(e)


def register(username: str, email: str, password: str, role: str = "medecin"):
    try:
        r = requests.post(
            _url("/auth/register"),
            json={"username": username, "email": email, "password": password, "role": role},
            timeout=10,
        )
        if r.status_code in (200, 201):
            return r.json(), None
        return None, r.json().get("detail", "Erreur inscription")
    except requests.exceptions.ConnectionError:
        return None, "Impossible de joindre le serveur."
    except Exception as e:
        return None, str(e)


def get_me():
    try:
        r = requests.get(_url("/auth/me"), headers=_auth_headers(), timeout=10)
        if r.status_code == 200:
            return r.json(), None
        return None, "Token invalide"
    except Exception as e:
        return None, str(e)



def query_rag(question: str):

    try:
        r = requests.post(
            _url("/query/ask"),
            json={"question": question},
            headers=_auth_headers(),
            timeout=180,
        )
        if r.status_code == 200:
            return r.json(), None
        if r.status_code == 401:
            return None, "SESSION_EXPIRED"
        if r.status_code == 400:
            return None, r.json().get("detail", "Question invalide")
        return None, r.json().get("detail", f"Erreur {r.status_code}")
    except requests.exceptions.ConnectionError:
        return None, "Impossible de joindre le serveur."
    except requests.exceptions.Timeout:
        return None, "RAG timeout (> 60s). Réessayez."
    except Exception as e:
        return None, str(e)


def health_check() -> bool:
    try:
        r = requests.get(_url("/query/health"), timeout=5)
        return r.status_code == 200
    except Exception:
        return False



def get_history(skip: int = 0, limit: int = 50):

    try:
        r = requests.get(
            _url(f"/history/?skip={skip}&limit={limit}"),
            headers=_auth_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            return r.json(), None
        if r.status_code == 401:
            return None, "SESSION_EXPIRED"
        return None, r.json().get("detail", "Erreur chargement historique")
    except requests.exceptions.ConnectionError:
        return None, "Impossible de joindre le serveur."
    except Exception as e:
        return None, str(e)