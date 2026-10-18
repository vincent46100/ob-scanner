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
st.markdown(
    """
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
    
    /* Style général des boutons secondaires (Supprimer / Remplacer) */
    .stButton>button {
        background-color: #27272a;
        color: white;
        border: 1px solid #3f3f46;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #3f3f46;
    }

    /* Style spécifique pour le bouton principal "Analyser le graphique" */
    .btn-analyser div.stButton>button {
        background: linear-gradient(135deg, #a855f7 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        padding: 14px 20px !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4) !important;
    }
    .btn-analyser div.stButton>button:hover {
        opacity: 0.92 !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- EN-TÊTE DE LA PAGE ---
st.markdown(
    """
    <div class="main-header">
        <h1>Scanner AI Vincent</h1>
        <p>Smart Money Concepts — Terminal d'Analyse Avancée</p>
    </div>
""",
    unsafe_allow_html=True,
)

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

# --- GESTION DE L'ÉTAT ---
if "dernier_fichier" not in st.session_state:
  st.session_state.dernier_fichier = None
if "resultat_analyse" not in st.session_state:
  st.session_state.resultat_analyse = None
if "file_uploader_key" not in st.session_state:
  st.session_state.file_uploader_key = 0

# --- NAVIGATION ---
onglet_choisi = st.radio(
    "Navigation",
    ["🔍 Analyste", "🧠 Coach"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")

if onglet_choisi == "🔍 Analyste":
  st.markdown("### 🖼️ Dépose ta capture d'écran")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 0.9rem;'>Glisse ou sélectionne"
      " la capture de ton graphique</p>",
      unsafe_allow_html=True,
  )

  fichier_telecharge = st.file_uploader(
      "Dépose ta capture ici",
      type=["png", "jpg", "jpeg"],
      label_visibility="collapsed",
      key=f"uploader_{st.session_state.file_uploader_key}",
  )

  if fichier_telecharge != st.session_state.dernier_fichier:
    st.session_state.dernier_fichier = fichier_telecharge
    st.session_state.resultat_
      
