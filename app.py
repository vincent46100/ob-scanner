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
    </style>
""", unsafe_allow_html=True)

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

# --- GESTION DE L'ÉTAT ---
if "dernier_fichier" not in st.session_state:
  st.session_state.dernier_fichier = None
if "resultat_analyse" not in st.session_state:
  st.session_state.resultat_analyse = None
if "file_uploader_key" not in st.session_state:
  st.session_state.file_uploader_key = 0

# --- NAVIGATION ---
onglet_choisi = st.radio(
    "Navigation", ["🔍 Analyste", "🧠 Coach"], horizontal=True, label_visibility="collapsed"
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
    st.session_state.resultat_analyse = None

  notes_utilisateur = st.text_area(
      "Remarques (facultatives) :",
      placeholder="Ex : Période 1H, contexte macro...",
      height=80,
  )

  if fichier_telecharge is not None:
    image_originale = Image.open(fichier_telecharge)
    st.image(image_originale, caption="Capture soumise à l'analyse", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
      if st.button("🗑️ Supprimer"):
        st.session_state.dernier_fichier = None
        st.session_state.resultat_analyse = None
        st.rerun()
    with col2:
      if st.button("🔄 Remplacer"):
        st.session_state.dernier_fichier = None
        st.session_state.resultat_analyse = None
        st.session_state.file_uploader_key += 1
        st.rerun()

    st.markdown("---")

    if st.button("🔍 Analyser le graphique"):
      with st.spinner(
          "🧠 Analyse approfondie des bougies, des Order Blocks et de la"
          " structure SMC en cours..."
      ):
        try:
          modele = genai.GenerativeModel("gemini-3.8-flash")

          prompt_systeme = (
              "Agis en tant qu'analyste quantitatif expert en Smart Money"
              " Concepts (SMC) et Price Action. Analyse précisément le graphique"
              " de trading fourni en image. Fournis une analyse détaillée au"
              " format Markdown/HTML structuré comprenant exactement ces 6 sections :"
              " 1. <h3 style='color: #38bdf8; font-weight: bold;'>1. VUE D'ENSEMBLE</h3> (description de l'actif, unité de temps apparente si visible, dynamique générale et phases)."
              " 2. <h3 style='color: #38bdf8; font-weight: bold;'>2. STRUCTURE DE MARCHÉ</h3> (Biais directionnel, phase, dernier événement type BOS ou ChoCH, et points clés HH, LH, HL, LL relevés sur l'axe des prix)."
              " 3. <h3 style='color: #38bdf8; font-weight: bold;'>3. ANALYSE DE LA LIQUIDITÉ</h3> (Buy-Side et Sell-Side Liquidity BSL/SSL identifiées)."
              " 4. <h3 style='color: #38bdf8; font-weight: bold;'>4. POINTS D'INTÉRÊT / ORDER BLOCKS</h3> (Liste des Demand OB et Supply OB avec leur force en étoiles et leurs niveaux de prix exacts estimés)."
              " 5. <h3 style='color: #38bdf8; font-weight: bold;'>5. SCÉNARIOS TACTIQUES</h3>"
              " 6. <h3 style='color: #38bdf8; font-weight: bold;'>6. CONCLUSION</h3> (Résumé opérationnel et niveau de confiance global /10)."
              " "
              " RÈGLE STRICTE POUR LE CHAPITRE 4 (Order Blocks) :"
              " - Place OBLIGATOIREMENT une pastille rouge 🔴 devant chaque titre ou élément de Supply Order Block / Vente (ex: 🔴 Supply Order Blocks)."
              " - Place OBLIGATOIREMENT une pastille verte 🟢 devant chaque titre ou élément de Demand Order Block / Achat (ex: 🟢 Demand Order Blocks)."
              " "
              " RÈGLE STRICTE POUR LE CHAPITRE 5 (Scénarios Tactiques) :"
              " Le chapitre 5 DOIT obligatoirement utiliser ce format HTML stylisé avec des cartes sur fond sombre :"
              " <h4 style='color: #60a5fa;'>📈 SCÉNARIO PRINCIPAL — [Titre du scénario]</h4>"
              " <p><strong>Probabilité estimée :</strong> <span style='color: #fbbf24; font-weight: bold;'>[XX]%</span></p>"
              " <div style='background-color: #111827; border: 1px solid #374151; padding: 15px; border-radius: 8px; color: #4ade80; margin-bottom: 15px;'>"
              " <p style='color: #e2e8f0; margin-bottom: 8px;'>Prix actuel : <span style='color: #c084fc; font-weight: bold;'>[Prix]</span></p>"
              " → [Étape 1]<br>→ [Étape 2]<br>→ [Étape 3]"
              " </div>"
              " <p style='margin-bottom: 20px;'><strong>Logique :</strong> [Explication détaillée de la structure]</p>"
              " "
              " <h4 style='color: #f43f5e;'>📉 SCÉNARIO ALTERNATIF — [Titre du scénario]</h4>"
              " <p><strong>Probabilité estimée :</strong> <span style='color: #fbbf24; font-weight: bold;'>[XX]%</span></p>"
              " <div style='background-color: #111827; border: 1px solid #374151; padding: 15px; border-radius: 8px; color: #4ade80; margin-bottom: 15px;'>"
              " → [Étape alternative 1]<br>→ [Étape alternative 2]"
              " </div>"
              " "
              " RÈGLE STRICTE POUR LA LISTE DE CONTRÔLE (À mettre tout à la fin, après la Conclusion) :"
              " Inclus systématiquement cet encadré HTML de vérification de la capture :"
              " <div style='background-color: #0b0d1b; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; margin-top: 25px;'>"
              " <h4 style='color: #ffffff; font-weight: bold; margin-bottom: 15px;'>✅ Liste de contrôle — Bonne capture</h4>"
              " <p style='color: #c084fc; margin: 6px 0;'>✓ Période visible</p>"
              " <p style='color: #c084fc; margin: 6px
