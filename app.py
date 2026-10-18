from datetime import date
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import requests
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Scanner AI Vincent — Smart Money Concepts",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .main-header {
        text-align: center;
        padding: 10px;
    }
    .main-header h1 {
        color: #a855f7;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #9333ea 0%, #c084fc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        padding: 12px;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }

    /* Style des encadrés principaux */
    .custom-card {
        background-color: #0b0d1b;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- GESTION DE L'ÉTAT (INITIALISATION) ---
if "dernier_fichier" not in st.session_state:
  st.session_state.dernier_fichier = None
if "resultat_analyse" not in st.session_state:
  st.session_state.resultat_analyse = None
if "file_uploader_key" not in st.session_state:
  st.session_state.file_uploader_key = 0

# --- EN-TÊTE DE LA PAGE ---
st.markdown("""
    <div class="main-header">
        <h1>Scanner AI Vincent</h1>
        <p>Smart Money Concepts — Terminal d'Analyse Avancée</p>
    </div>
""", unsafe_allow_html=True)

# --- SYSTÈME DE MOT DE PASSE ---
entree_mot_de_passe = st.text_input(
    "🔑 Entrez le mot de passe pour accéder à l'analyste :", type="password"
)

if entree_mot_de_passe != "Cecile46*":
  st.warning("Veuillez entrer le mot de passe valide.")
  st.stop()

# --- CONFIGURATION CLÉ API GEMINI ---
try:
  genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
  pass

# --- NAVIGATION ---
onglet_choisi = st.radio(
    "Navigation", ["🔍 Analyste", "🧠 Coach"], horizontal=True, label_visibility="collapsed"
)

st.markdown("---")

if onglet_choisi == "🔍 Analyste":
  
  # --- ENCADRÉ 1 : DÉPOSE TA CAPTURE (Haut) ---
  st.markdown('<div class="custom-card">', unsafe_allow_html=True)
  
  st.markdown("### 🖼️ Dépose ta capture d'écran")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 0.9rem;'>Glisse ou sélectionne la capture de ton graphique</p>",
      unsafe_allow_html=True,
  )

  fichier_telecharge = st.file_uploader(
      "Dépose ta capture ici",
