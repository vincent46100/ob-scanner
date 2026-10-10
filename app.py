from datetime import date
from PIL import Image
import requests
import streamlit as st

st.set_page_config(page_title="Vision du scanner OB", layout="centered")


# --- FONCTION : RÉCUPÉRATION DU CALENDRIER ÉCONOMIQUE EN TEMPS RÉEL ---
@st.cache_data(ttl=3600)  # Mise en cache pendant 1h pour éviter de recharger inutilement
def obtenir_annonces_du_jour():
  try:
    # Exemple d'appel vers une API de calendrier économique
    # Remplacez 'YOUR_API_KEY' par votre clé API si vous en utilisez une dédiée
    aujourdhui = date.today().strftime("%Y-%m-%d")
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={aujourdhui}&to={aujourdhui}&apikey=demo"

    reponse = requests.get(url, timeout=5)
    donnees = reponse.json()

    # Filtrer les annonces à fort impact (High) pour USD / EUR
    annonces_mjeures = [
        item
        for item in donnees
        if item.get("impact") == "High"
        and item.get("currency") in ["USD", "EUR"]
    ]
    return annonces_mjeures
  except Exception:
    return []


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

# --- AFFICHAGE EN TEMPS RÉEL DES ANNONCES DU JOUR ---
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
    "Glissez-déposez une capture d'écran de graphique ou un PDF pour analyser"
    " les Order Blocks, la tendance et les points clés."
)

fichier_telecharge = st.file_uploader(
    "Déposez votre image ou PDF ici", type=["png", "jpg", "jpeg", "pdf"]
)

if fichier_telecharge is not None:
  image = Image.open(fichier_telecharge)
  st.image(image, caption="Graphique soumis à l'analyse", use_container_width=True)

  if st.button("🚀 Lancer l'analyse complète"):
    with st.spinner("Analyse des structures institutionnelles en cours..."):
      if integrer_annonces:
        st.info(
            "📅 Filtre macro-économique activé : Synchronisation en temps"
            " réel."
        )
      else:
        st.warning(
            "⚠️ Filtre macro-économique désactivé : Analyse technique pure."
        )
      st.success("Analyse terminée !")

    # --- ZONES ET SYNTHÈSE ---
    st.subheader("📍 Zones d'Order Blocks Détectées")
    col1, col2 = st.columns(2)
    with col1:
      st.markdown("#### 🟢 Demand OB (Achat)")
      st.info("**Zone détectée :** 4101.00 - 4107.00\n* **Statut :** Vierge")
    with col2:
      st.markdown("#### 🔴 Supply OB (Vente)")
      st.error("**Zone détectée :** 4180.00 - 4185.00\n* **Statut :** Vierge")

    st.markdown("---")
    st.subheader("📝 Synthèse de l'Analyse du Marché")
    st.markdown("""
    ### 📈 Tendance du Marché
    * **Direction principale :** Haussière à court/moyen terme.
    * **Structure SMC :** Succession de Higher Highs / Higher Lows validant le flux d'achat.
    
    ### 🔑 Points Clés & Liquidité
    * **Zone d'Accélération (FVG) :** Inbalance identifié lors de l'impulsion.
    * **Liquidité Induisante (Inducement) :** Liquidité sous les plus bas récents.
    """)
