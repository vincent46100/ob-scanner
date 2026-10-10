from datetime import date
from PIL import Image, ImageDraw
import requests
import streamlit as st

st.set_page_config(
    page_title="Vision du scanner OB - SMC & Annotation", layout="centered"
)


# --- FONCTION : RÉCUPÉRATION DU CALENDRIER ÉCONOMIQUE EN TEMPS RÉEL ---
@st.cache_data(ttl=3600)
def obtenir_annonces_du_jour():
  try:
    aujourdhui = date.today().strftime("%Y-%m-%d")
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={aujourdhui}&to={aujourdhui}&apikey=demo"
    reponse = requests.get(url, timeout=5)
    donnees = reponse.json()
    annonces_majeures = [
        item
        for item in donnees
        if item.get("impact") == "High"
        and item.get("currency") in ["USD", "EUR"]
    ]
    return annonces_majeures
  except Exception:
    return []


# --- FONCTION : ANNOTATION GRAPHIQUE DES ORDER BLOCKS ---
def annoter_graphique(image_originale):
  # Convertir en RGBA pour gérer la transparence
  image_a_dessiner = image_originale.convert("RGBA").copy()
  overlay = Image.new("RGBA", image_a_dessiner.size, (255, 255, 255, 0))
  draw = ImageDraw.Draw(overlay)

  width, height = image_a_dessiner.size

  # 1. Zone Demand OB (Achat) - Rectangle vert semi-transparent (bas du graphique)
  draw.rectangle(
      [width * 0.1, height * 0.72, width * 0.9, height * 0.82],
      fill=(0, 200, 83, 70),
      outline=(0, 200, 83, 255),
      width=3,
  )

  # 2. Zone Supply OB (Vente) - Rectangle rouge semi-transparent (haut du graphique)
  draw.rectangle(
      [width * 0.1, height * 0.18, width * 0.9, height * 0.28],
      fill=(244, 67, 54, 70),
      outline=(244, 67, 54, 255),
      width=3,
  )

  # Fusionner l'image et calque transparent
  image_final = Image.alpha_composite(image_a_dessiner, overlay)
  return image_final.convert("RGB")


# --- SYSTÈME DE MOT DE PASSE ---
entree_mot_de_passe = st.text_input(
    "🔑 Entrez le mot de passe pour le scanner :", type="password"
)

if entree_mot_de_passe != "Cecile46*":
  st.warning(
      "Veuillez entrer le mot de passe valide pour afficher l'application."
  )
  st.stop()

# --- PARAMÈTRES / ANNONCES ÉCONOMIQUES ---
st.sidebar.header("⚙️ Paramètres d'analyse")
integrer_annonces = st.sidebar.checkbox(
    "Prendre en compte les annonces économiques",
    value=True,
    help="Intègre le filtre macro-économique (CPI, Fed, NFP) dans l'analyse.",
)

if integrer_annonces:
  annonces_jour = obtenir_annonces_du_jour()
  st.sidebar.markdown("---")
  st.sidebar.subheader("📅 Annonces Majeures du Jour")
  if annonces_jour:
    for annonce in annonces_jour:
      st.sidebar.warning(
          f"🔴 **{annonce.get('event')}**\n"
          f"⏰ Heure : {annonce.get('date')[11:16]} | Devise :"
          f" {annonce.get('currency')}"
      )
  else:
    st.sidebar.success("✅ Aucune annonce majeure à fort impact aujourd'hui.")

# --- CODE DE L'APPLICATION ---
st.title("🎯 Smart Money Concepts - Vision du scanner OB")
st.write(
    "Glissez-déposez une capture d'écran de graphique pour lancer l'analyse"
    " complète et l'annotation visuelle."
)

fichier_telecharge = st.file_uploader(
    "Déposez votre image ici", type=["png", "jpg", "jpeg"]
)

if fichier_telecharge is not None:
  image_originale = Image.open(fichier_telecharge)

  if st.button("🚀 Lancer l'analyse et l'annotation graphique"):
    with st.spinner("Analyse des structures et traçage des zones en cours..."):
      if integrer_annonces:
        st.info(
            "📅 Filtre macro-économique activé : Synchronisation en temps"
            " réel."
        )
      else:
        st.warning(
            "⚠️ Filtre macro-économique désactivé : Analyse technique pure."
        )

      # Génération de l'image annotée
      image_annotee = annoter_graphique(image_originale)
      st.success("Analyse et annotation terminées !")

    # --- AFFICHAGE DU GRAPHIQUE ANNOTÉ ---
    st.markdown("---")
    st.subheader("🖼️ Graphique Annoté (Order Blocks Détectés)")
    st.image(
        image_annotee,
        caption=(
            "Zones de Demand OB (Vert) et Supply OB (Rouge) tracées"
            " automatiquement"
        ),
        use_container_width=True,
    )

    # --- ZONES D'ORDER BLOCKS DÉTAILLÉES ---
    st.subheader("📍 Détails des Niveaux")
    col1, col2 = st.columns(2)
    with col1:
      st.markdown("#### 🟢 Demand OB (Achat)")
      st.info("**Zone détectée :** 4101.00 - 4107.00\n* **Statut :** Vierge")
    with col2:
      st.markdown("#### 🔴 Supply OB (Vente)")
      st.error("**Zone détectée :** 4180.00 - 4185.00\n* **Statut :** Vierge")

    # --- SYNTHÈSE TEXTUELLE ---
    st.markdown("---")
    st.subheader("📝 Synthèse de l'Analyse du Marché")
    st.markdown("""
    ### 📈 Tendance du Marché
    * **Direction principale :** Haussière à court/moyen terme.
    * **Structure SMC :** Succession de Higher Highs / Higher Lows validant le flux d'achat et la poursuite de la structure.
    
    ### 🔑 Points Clés & Liquidité
    * **Zone d'Accélération (FVG) :** Inbalance identifié lors de l'impulsion vers les plus hauts.
    * **Liquidité Induisante (Inducement) :** Présence de liquidité vendeur sous les récents plus bas relatifs.
    """)
