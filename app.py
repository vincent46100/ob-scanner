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
        background-color: #050811;
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

    /* Notre bel encadré bleu nuit sobre et harmonieux */
    .custom-card {
        background-color: #0b0f19;
        border: 1px solid #1e294b;
        border-radius: 12px;
        padding: 25px;
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
  
  lancer_analyse = False
  
  # --- ENCADRÉ GLOBAL BLEU NUIT SOBRE ---
  st.markdown('<div class="custom-card">', unsafe_allow_html=True)
  
  st.markdown("### 🖼️ Dépose ta capture d'écran")
  st.markdown(
      "<p style='color: #94a3b8; font-size: 0.9rem;'>Glisse ou sélectionne la capture de ton graphique</p>",
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
    st.session_state.resultat_analyse = None

  if fichier_telecharge is not None:
    image_originale = Image.open(fichier_telecharge)
    st.image(image_originale, caption="Capture soumise à l'analyse", use_container_width=True)

  notes_utilisateur = st.text_area(
      "Remarques (facultatives) :",
      placeholder="Ex : Période 1H, contexte macro...",
      height=80,
  )

  st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

  # Boutons "Remplacer" et "Analyser" côte à côte avec le beau design violet
  if fichier_telecharge is not None:
    col1, col2 = st.columns(2)
    with col1:
      if st.button("🔄 Remplacer la capture"):
        st.session_state.dernier_fichier = None
        st.session_state.resultat_analyse = None
        st.session_state.file_uploader_key += 1
        st.rerun()
    with col2:
      lancer_analyse = st.button("🔍 Analyser le graphique")
  else:
    col_g, col_c, col_d = st.columns([1, 2, 1])
    with col_c:
      lancer_analyse = st.button("🔍 Analyser le graphique")

  st.markdown('</div>', unsafe_allow_html=True)

  # --- TRAITEMENT GEMINI ---
  if lancer_analyse and fichier_telecharge is not None:
    with st.spinner("🧠 Analyse approfondie des bougies, des Order Blocks et de la structure SMC en cours..."):
      try:
        # Retour au modèle exigé par l'API Google
        modele = genai.GenerativeModel("gemini-3.8-flash")

        prompt_systeme = (
            "Agis en tant qu'analyste quantitatif expert en Smart Money Concepts (SMC) et Price Action. "
            "Analyse précisément le graphique de trading fourni en image. Fournis une analyse détaillée au format Markdown/HTML structuré comprenant exactement ces 6 sections :\n"
            "1. <h3 style='color: #38bdf8; font-weight: bold;'>1. VUE D'ENSEMBLE</h3> (description de l'actif, unité de temps apparente si visible, dynamique générale et phases).\n"
            "2. <h3 style='color: #38bdf8; font-weight: bold;'>2. STRUCTURE DE MARCHÉ</h3> (Biais directionnel, phase, dernier événement type BOS ou ChoCH, et points clés HH, LH, HL, LL relevés sur l'axe des prix).\n"
            "3. <h3 style='color: #38bdf8; font-weight: bold;'>3. ANALYSE DE LA LIQUID
