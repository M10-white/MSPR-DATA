import requests
import streamlit as st
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URL de l'API depuis les variables d'environnement
API_URL = os.getenv('API_URL', 'http://localhost:8001/api')

def register(username, email, password, country, is_admin=False):
    payload = {"username": username, "email": email, "password": password, "country": country, "is_admin": is_admin}
    r = requests.post(f"{API_URL}/register", json=payload)
    if r.status_code == 200:
        st.success("Inscription réussie ! Veuillez vous connecter.")
        return True
    else:
        st.error(f"Erreur d'inscription : {r.text}")
        return False

def login(username, password):
    data = {"username": username, "password": password}
    r = requests.post(f"{API_URL}/token", data=data)
    if r.status_code == 200:
        st.session_state["token"] = r.json()["access_token"]
        st.session_state["username"] = username
        st.success("Connexion réussie !")
        return True
    else:
        st.error(f"Erreur de connexion : {r.text}")
        return False

def get_token():
    return st.session_state.get("token")

def logout():
    if "token" in st.session_state:
        del st.session_state["token"]
    if "username" in st.session_state:
        del st.session_state["username"]
    st.success("Déconnexion réussie !")

def get_with_auth(path, params=None):
    token = get_token()
    if not token:
        st.error("Utilisateur non connecté")
        return None
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}{path}", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur {response.status_code} : {response.text}")
        return None

def post_with_auth(path, payload):
    token = get_token()
    if not token:
        st.error("Utilisateur non connecté")
        return None
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}{path}", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur {response.status_code} : {response.text}")
        return None

def is_authenticated() -> bool:
    """
    Vérifie si l'utilisateur est authentifié.
    
    Returns:
        bool: True si l'utilisateur est authentifié, False sinon
    """
    return 'token' in st.session_state 