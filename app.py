from datetime import date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="OB Scanner AI - Moteur Algorithmique SMC", layout="wide"
)


# --- FONCTION : RÉCUPÉRATION DU CALENDRIER ÉCONOMIQUE ---
@st.cache_data(ttl=3600)
def obtenir_annonces_du_jour():
  try:
    aujourdhui = date.today().strftime("%Y-%m-%d")
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={aujourdhui}&to={aujourdhui}&apikey=demo"
    reponse = requests.get(url, timeout=5)
    donnees = reponse.json()
    return [
        item
        for item in donnees
        if item.get("impact") == "High"
        and item.get("currency") in ["USD", "EUR", "GBP", "JPY"]
    ]
  except Exception:
    return []


# --- TÉLÉCHARGEMENT DES DONNÉES DE MARCHÉ (OHLCV) ---
@st.cache_data(ttl=600)
def charger_donnees_marche(symbole, intervalle="1h"):
  # Gestion des périodes selon l'intervalle pour respecter les limites yfinance
    periode = "60d" if intervalle in ["1h", "30m", "15m"] else "1y"
    df = yf.download(symbole, period=periode, interval=intervalle, progress=False)
    
    # Correction multi-index éventuelle de yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    df = df.dropna()
    return df


# --- ALGORITHME DE DÉTECTION DES ORDER BLOCKS (Logique Pine Script) ---
def calculer_order_blocks(df, atr_len=14, lookback=20):
    # Calcul de l'ATR
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=atr_len).mean()

    # Listes pour stocker les zones OB détectées
    bullish_obs = []
    bearish_obs = []

    # Parcours des bougies pour détecter le Displacement et l'OB
    for i in range(lookback, len(df) - 1):
        # OB Haussier (Demand OB) : Dernière bougie baissière avant une forte impulsion haussière
        if df['Close'].iloc[i] < df['Open'].iloc[i]: # Bougie rouge
            # Vérification de l'impulsion (la bougie suivante casse le haut de la bougie i)
            if df['Close'].iloc[i+1] > df['High'].iloc[i]:
                move_size = df['Close'].iloc[i+1] - df['Low'].iloc[i]
                if move_size >= (1.5 * df['ATR'].iloc[i]):
                    bullish_obs.append({
                        'index': i,
                        'top': df['High'].iloc[i],
                        'bottom': df['Low'].iloc[i],
                        'date': df.index[i]
                    })

        # OB Baissier (Supply OB) : Dernière bougie haussière avant une forte impulsion baissière
        if df['Close'].iloc[i] > df['Open'].iloc[i]: # Bougie verte
            if df['Close'].iloc[i+1] < df['Low'].iloc[i]:
                move_size = df['High'].iloc[i] - df['Close'].iloc[i+1]
                if move_size >= (1.5 * df['ATR'].iloc[i]):
                    bearish_obs.append({
                        'index': i,
                        'top': df['High'].iloc[i],
                        'bottom': df['Low'].iloc[i],
                        'date': df.index[i]
                    })

    # Garder les 3 plus récents de chaque côté pour la clarté du graphique
    return bullish_obs[-3:], bearish_obs[-3:]


# --- SYSTÈME DE MOT DE PASSE ---
entree_mot_de_passe = st.text_input(
    "🔑 Entrez le mot de passe pour OB Scanner AI :", type="password"
)

if entree_mot_de_passe != "Cecile46*":
  st.warning("Veuillez entrer le mot de passe valide pour afficher l'application.")
  st.stop()


# --- BARRE LATÉRALE : PARAMÈTRES AVANCÉS ---
st.sidebar.header("⚙️ Configuration du Marché")

actif_choisi = st.sidebar.selectbox(
    "Sélectionner l'Actif",
    options=["Or / XAUUSD (GC=F)", "DAX / Germany 40 (^GDAXI)", "EURUSD (EURUSD=X)", "Bitcoin (BTC-USD)"],
    index=0
)

# Mapping du ticker yfinance
ticker_map = {
    "Or / XAUUSD (GC=F)": "GC=F",
    "DAX / Germany 40 (^GDAXI)": "^GDAXI",
    "EURUSD (EURUSD=X)": "EURUSD=X",
    "Bitcoin (BTC-USD)": "BTC-USD"
}
ticker = ticker_map[actif_choisi]

intervalle_choisi = st.sidebar.selectbox("Unité de Temps", options=["15m", "1h", "4h", "1d"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("⭐ Paramètres OB Scanner 5★")
atr_period = st.sidebar.number_input("Période ATR", value=14, min_value=5, max_value=50)
lookback_period = st.sidebar.slider("Fenêtre de recherche (Lookback)", min_value=5, max_value=50, value=20)

st.sidebar.markdown("---")
integrer_annonces = st.sidebar.checkbox("Prendre en compte les annonces économiques", value=True)

if integrer_annonces:
  annonces_jour = obtenir_annonces_du_jour()
  st.sidebar.markdown("---")
  st.sidebar.subheader("📅 Annonces Majeures du Jour")
  if annonces_jour:
    for annonce in annonces_jour:
      st.sidebar.warning(f"🔴 **{annonce.get('event')}**\n⏰ Heure : {annonce.get('date')[11:16]}")
  else:
    st.sidebar.success("✅ Aucune annonce majeure aujourd'hui.")


# --- APPLICATION PRINCIPALE ---
st.title("🎯 Smart Money Concepts - OB Scanner AI (Algorithmique)")
st.write("Analyse mathématique en direct des Order Blocks et des structures institutionnelles.")

if st.button("🚀 Charger le Marché et Calculer les Order Blocks"):
    with st.spinner("Récupération des bougies et calculs ATR / Displacement en cours..."):
        df = charger_donnees_marche(ticker, intervalle_choisi)
        bull_obs, bear_obs = calculer_order_blocks(df, atr_len=atr_period, lookback=lookback_period)
        
        # Création du graphique Plotly professionnel
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Prix"
        )])

        # Ajout des zones Demand OB (Vertes)
        for ob in bull_obs:
            fig.add_shape(
                type="rect",
                x0=df.index[ob['index']], y0=ob['bottom'],
                x1=df.index[-1], y1=ob['top'],
                fillcolor="rgba(0, 200, 83, 0.25)",
                line=dict(color="rgba(0, 200, 83, 1)", width=1),
            )

        # Ajout des zones Supply OB (Rouges)
        for ob in bear_obs:
            fig.add_shape(
                type="rect",
                x0=df.index[ob['index']], y0=ob['bottom'],
                x1=df.index[-1], y1=ob['top'],
                fillcolor="rgba(255, 61, 0, 0.25)",
                line=dict(color="rgba(255, 61, 0, 1)", width=1),
            )

        fig.update_layout(
            title=f"Analyse SMC - {actif_choisi} ({intervalle_choisi})",
            xaxis_title="Date / Heure",
            yaxis_title="Prix",
            template="plotly_dark",
            height=650,
            xaxis_rangeslider_visible=False
        )

        st.success("Calculs terminés avec succès !")

    # --- AFFICHAGE DU GRAPHIQUE INTERACTIF ---
    st.markdown("---")
    st.subheader("🖼️ Graphique Interactif & Zones Institutionnelles")
    st.plotly_chart(fig, use_container_width=True)

    # --- TABLEAU DE SYNTHÈSE ---
    st.markdown("---")
    st.subheader("📍 Niveaux Clés Détectés par l'Algorithme")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🟢 Derniers Demand OB (Achat)")
        if bull_obs:
            for ob in bull_obs:
                st.info(f"**Zone :** {ob['bottom']:.2f} - {ob['top']:.2f} (Détecté le {ob['date']})")
        else:
            st.warning("Aucun Demand OB valide trouvé sur cette période.")

    with col2:
        st.markdown("#### 🔴 Derniers Supply OB (Vente)")
        if bear_obs:
            for ob in bear_obs:
                st.error(f"**Zone :** {ob['bottom']:.2f} - {ob['top']:.2f} (Détecté le {ob['date']})")
        else:
            st.warning("Aucun Supply OB valide trouvé sur cette période.")
