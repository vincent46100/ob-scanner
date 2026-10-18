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

    notes_utilisateur = st.text_area(
        "Remarques (facultatives) :",
        placeholder="Ex : Période 1H, contexte macro...",
        height=80,
    )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # Bouton d'analyse pleine largeur stylisé en violet
    st.markdown('<div class="btn-analyser">', unsafe_allow_html=True)
    lancer_analyse = st.button("🔍 Analyser le graphique")
    st.markdown('</div>', unsafe_allow_html=True)

    if lancer_analyse:
      with st.spinner("🧠 Analyse approfondie des bougies, des Order Blocks et de la structure SMC en cours..."):
        try:
          modele = genai.GenerativeModel("gemini-1.5-flash")

          prompt_systeme = (
              "Agis en tant qu'analyste quantitatif expert en Smart Money Concepts (SMC) et Price Action. "
              "Analyse précisément le graphique de trading fourni en image. Fournis une analyse détaillée au format Markdown/HTML structuré comprenant exactement ces 6 sections :\n"
              "1. <h3 style='color: #38bdf8; font-weight: bold;'>1. VUE D'ENSEMBLE</h3> (description de l'actif, unité de temps apparente si visible, dynamique générale et phases).\n"
              "2. <h3 style='color: #38bdf8; font-weight: bold;'>2. STRUCTURE DE MARCHÉ</h3> (Biais directionnel, phase, dernier événement type BOS ou ChoCH, et points clés HH, LH, HL, LL relevés sur l'axe des prix).\n"
              "3. <h3 style='color: #38bdf8; font-weight: bold;'>3. ANALYSE DE LA LIQUIDITÉ</h3> (Buy-Side et Sell-Side Liquidity BSL/SSL identifiées).\n"
              "4. <h3 style='color: #38bdf8; font-weight: bold;'>4. POINTS D'INTÉRÊT / ORDER BLOCKS</h3> (Liste des Demand OB et Supply OB avec leur force en étoiles et leurs niveaux de prix exacts estimés).\n"
              "5. <h3 style='color: #38bdf8; font-weight: bold;'>5. SCÉNARIOS TACTIQUES</h3>\n"
              "6. <h3 style='color: #38bdf8; font-weight: bold;'>6. CONCLUSION</h3> (Résumé opérationnel et niveau de confiance global /10).\n\n"
              "RÈGLE STRICTE POUR LE CHAPITRE 4 (Order Blocks) :\n"
              "- Place OBLIGATOIREMENT une pastille rouge 🔴 devant chaque titre ou élément de Supply Order Block / Vente.\n"
              "- Place OBLIGATOIREMENT une pastille verte 🟢 devant chaque titre ou élément de Demand Order Block / Achat.\n\n"
              "RÈGLE STRICTE POUR LE CHAPITRE 5 (Scénarios Tactiques) :\n"
              "Le chapitre 5 DOIT obligatoirement utiliser ce format HTML stylisé avec des cartes sur fond sombre :\n"
              "<h4 style='color: #60a5fa;'>📈 SCÉNARIO PRINCIPAL — [Titre du scénario]</h4>\n"
              "<p><strong>Probabilité estimée :</strong> <span style='color: #fbbf24; font-weight: bold;'>[XX]%</span></p>\n"
              "<div style='background-color: #111827; border: 1px solid #374151; padding: 15px; border-radius: 8px; color: #4ade80; margin-bottom: 15px;'>\n"
              "<p style='color: #e2e8f0; margin-bottom: 8px;'>Prix actuel : <span style='color: #c084fc; font-weight: bold;'>[Prix]</span></p>\n"
              "→ [Étape 1]<br>→ [Étape 2]<br>→ [Étape 3]\n"
              "</div>\n"
              "<p style='margin-bottom: 20px;'><strong>Logique :</strong> [Explication détaillée de la structure]</p>\n\n"
              "<h4 style='color: #f43f5e;'>📉 SCÉNARIO ALTERNATIF — [Titre du scénario]</h4>\n"
              "<p><strong>Probabilité estimée :</strong> <span style='color: #fbbf24; font-weight: bold;'>[XX]%</span></p>\n"
              "<div style='background-color: #111827; border: 1px solid #374151; padding: 15px; border-radius: 8px; color: #4ade80; margin-bottom: 15px;'>\n"
              "→ [Étape alternative 1]<br>→ [Étape alternative 2]\n"
              "</div>\n\n"
              "RÈGLE STRICTE POUR LA LISTE DE CONTRÔLE (À mettre tout à la fin, après la Conclusion) :\n"
              "Inclus systématiquement cet encadré HTML de vérification de la capture :\n"
              "<div style='background-color: #0b0d1b; border: 1px solid #1e293b; border-radius: 10px; padding: 20px; margin-top: 25px;'>\n"
              "<h4 style='color: #ffffff; font-weight: bold; margin-bottom: 15px
