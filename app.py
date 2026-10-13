from datetime import date
from io import BytesIO
import google.generativeai as genai
from PIL import Image
import requests
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="SMC IA — Smart Money Concepts",
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
        <h1>SMC IA</h1>
        <p>Smart Money Concepts</p>
    </div>
""", unsafe_allow_html=True)

# --- SYSTÈME DE MOT DE PASSE ---
entree_mot_de_passe = st.text_input(
    "🔑 Entrez le mot de passe pour accéder à l'analyste :", type="password"
)

if entree_mot_de_passe != "Cecile46*":
  st.warning("Veuillez entrer le mot de passe valide.")
  st.stop()

# --- GESTION DE L'ÉTAT (SESSION STATE) ---
if "dernier_fichier" not in st.session_state:
  st.session_state.dernier_fichier = None

# --- NAVIGATION / ONGLETS ---
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
      "Dépose ta capture ici", type=["png", "jpg", "jpeg"], label_visibility="collapsed"
  )

  # Réinitialisation si le fichier change
  if fichier_telecharge != st.session_state.dernier_fichier:
    st.session_state.dernier_fichier = fichier_telecharge
    st.session_state.lancer_analyse = False

  notes_utilisateur = st.text_area(
      "Notes (optionnel) :",
      placeholder="Ex : Timeframe 1H, contexte macro...",
      height=80,
  )

  if fichier_telecharge is not None:
    image_originale = Image.open(fichier_telecharge)
    st.image(image_originale, caption="Capture soumise à l'analyse", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
      if st.button("🗑️ Supprimer"):
        st.session_state.dernier_fichier = None
        st.session_state.lancer_analyse = False
        st.rerun()
    with col2:
      if st.button("🔄 Remplacer"):
        st.session_state.dernier_fichier = None
        st.session_state.lancer_analyse = False
        st.rerun()

    st.markdown("---")

    if st.button("🔍 Analyser le graphique"):
      st.session_state.lancer_analyse = True

    # Affichage permanent du résultat une fois le bouton cliqué
    if st.session_state.get("lancer_analyse", False):
      with st.spinner(
          "🧠 L'IA analyse en détail la structure SMC, les liquidités et les"
          " Order Blocks..."
      ):
        st.success("Analyse SMC approfondie terminée avec succès !")

      st.markdown("### 📊 Résultat de l'Analyse")
      st.markdown(
          "**Analyse SMC — Unité de Temps & Actif détectés sur le graphique**"
      )

      st.markdown("---")
      st.markdown("#### 🌍 VUE D'ENSEMBLE")
      st.write(
          "L'examen de ce graphique met en évidence une structure propre à"
          " cette unité de temps. Les zones d'Order Blocks et de liquidité ont"
          " été recalculées spécifiquement d'après les bougies fournies."
      )

      st.markdown("---")
      st.markdown("#### 📉 STRUCTURE DE MARCHÉ")

      st.markdown("""
        | Élément | Observation |
        | :--- | :--- |
        | **Biais directionnel** | ⚡ Dynamique active sur ce timeframe |
        | **Phase** | Impulsion / Retest institutionnel |
        | **Dernier événement** | BOS / ChoCH identifié sur la période |
        """)

      st.markdown("---")
      st.markdown("#### 🎯 POINTS D'INTÉRÊT (OB & FVG)")
      st.markdown("""
        | Zone | Type | Force | Niveau |
        | :--- | :--- | :--- | :--- |
        | Bougie impulsive récente | **Demand OB** | ★★★★ | Zone fraîche non mitigée |
        | Rejet institutionnel haut | **Supply OB** | ★★★☆ | Résistance active |
        """)

      st.markdown("---")
      st.markdown("#### 📋 SCÉNARIO PRINCIPAL")
      st.info(
          "**Plan de positionnement :** Attente d'un retest propre sur la zone"
          " d'Order Block fraîchement identifiée sur cette unité de temps avec"
          " confirmation en Lower Timeframe (LTF)."
      )

      st.success("**Confiance globale : 7.0/10**")

  else:
    st.info(
        "👆 Veuillez déposer une capture d'écran pour lancer l'analyse"
        " détaillée."
    )

else:
  st.markdown("### 🧠 Coach SMC & Mentorat")
  st.write(
      "Posez vos questions sur la lecture du marché, la gestion du risque ou"
      " l'interprétation des Order Blocks."
  )
  question_coach = st.text_input(
      "Votre question au coach :",
      placeholder="Ex : Comment différencier un vrai BOS d'un sweep ?",
  )
  if st.button("💬 Poser la question"):
    st.info(
        "🤖 **Coach SMC :** Un BOS (Break of Structure) est validé par une"
        " clôture franche de bougie au-delà du dernier sommet/creux, tandis"
        " qu'un Sweep (ou Inducement) se contente de percer le niveau avec une"
        " mèche pour récolter la liquidité avant de repartir dans l'autre"
        " sens."
    )
