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
              " format Markdown/HTML structuré comprenant exactement ces 6 paragraphes :"
              " 1. <h3 style='color: #38bdf8; font-weight: bold;'>1. VUE D'ENSEMBLE</h3> (description de l'actif, unité de temps apparente si visible, dynamique générale et phases)."
              " 2. <h3 style='color: #38bdf8; font-weight: bold;'>2. STRUCTURE DE MARCHÉ</h3> (Biais directionnel, phase, dernier événement type BOS ou ChoCH, et points clés HH, LH, HL, LL relevés sur l'axe des prix)."
              " 3. <h3 style='color: #38bdf8; font-weight: bold;'>3. ANALYSE DE LA LIQUIDITÉ</h3> (Buy-Side et Sell-Side Liquidity BSL/SSL identifiées)."
              " 4. <h3 style='color: #38bdf8; font-weight: bold;'>4. POINTS D'INTÉRÊT / ORDER BLOCKS</h3> (Liste des Demand OB et Supply OB avec leur force en étoiles et leurs niveaux de prix exacts estimés)."
              " 5. <h3 style='color: #38bdf8; font-weight: bold;'>5. SCÉNARIOS TACTIQUES</h3> (Scénario principal et scénario alternatif avec probabilités estimées et cibles chiffrées)."
              " 6. <h3 style='color: #38bdf8; font-weight: bold;'>6. CONCLUSION</h3> (Résumé opérationnel et niveau de confiance global /10)."
              " IMPÉRATIFS DE MISE EN FORME COULEUR (HTML) :"
              " - Les titres des 6 sections ci-dessus DOIVENT être impérativement écrits avec des balises HTML en bleu clair <h3 style='color: #38bdf8; font-weight: bold;'>...</h3>."
              " - Pour TOUS les points clés importants, niveaux de prix (ex: 4163.00), unités de temps (ex: M3, H1), et termes SMC majeurs (BOS, ChoCH, BSL, SSL, Order Block, HH, LH, HL, LL), entoure-les obligatoirement d'une balise HTML violette : <span style='color: #c084fc; font-weight: bold;'>...</span>."
              " - Pour toutes les étoiles de notation de force (ex: ★★★★★ ou ★★★★☆), entoure-les impérativement d'une balise HTML dorée : <span style='color: #fbbf24; font-weight: bold;'>★★★★★</span>."
          )

          contents = [prompt_systeme, image_originale]
          if notes_utilisateur:
            contents.append(f"Notes complémentaires du trader : {notes_utilisateur}")

          reponse = modele.generate_content(contents)
          st.session_state.resultat_analyse = reponse.text
          st.success("Analyse SMC approfondie terminée avec succès !")

        except Exception as e:
          st.error(
              "Erreur lors de l'analyse avec l'IA. Vérifiez votre clé API"
              f" Gemini dans les secrets Streamlit : {e}"
          )

    if st.session_state.resultat_analyse:
      st.markdown("---")
      st.markdown("### 📊 Résultat de l'Analyse Détaillée")
      st.markdown(st.session_state.resultat_analyse, unsafe_allow_html=True)

  else:
    st.info(
        "👆 Veuillez déposer une capture d'écran de votre graphique pour lancer"
        " l'analyse personnalisée."
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
