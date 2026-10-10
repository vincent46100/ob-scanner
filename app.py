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
  periode = "60d" if intervalle in ["1h", "30m", "15m"] else "1y"
  df = yf.download(symbole, period=periode, interval=intervalle, progress=False)

  if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.droplevel(1)

  df = df.dropna()
  return df


# --- ALGORITHME DE DÉTECTION AVEC FILTRE DE MITIGATION ---
def calculer_order_blocks(df, atr_len=14, lookback=20, max_obs=2):
  high_low = df["High"] - df["Low"]
  high_close = np.abs(df["High"] - df["Close"].shift())
  low_close = np.abs(df["Low"] - df["Close"].shift())
  tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
  df["ATR"] = tr.rolling(window=atr_len).mean()

  bullish_obs = []
  bearish_obs = []

  # 1. Détection initiale de tous les OB
  for i in range(lookback, len(df) - 1):
    # OB Haussier (Demand OB)
    if df["Close"].iloc[i] < df["Open"].iloc[i]:
      if df["Close"].iloc[i + 1] > df["High"].iloc[i]:
        move_size = df["Close"].iloc[i + 1] - df["Low"].iloc[i]
        if move_size >= (1.5 * df["ATR"].iloc[i]):
          bullish_obs.append({
              "index": i,
              "top": df["High"].iloc[i],
              "bottom": df["Low"].iloc[i],
              "date": df.index[i],
          })

    # OB Baissier (Supply OB)
    if df["Close"].iloc[i] > df["Open"].iloc[i]:
      if df["Close"].iloc[i + 1] < df["Low"].iloc[i]:
        move_size = df["High"].iloc[i] - df["Close"].iloc[i + 1]
        if move_size >= (1.5 * df["ATR"].iloc[i]):
          bearish_obs.append({
              "index": i,
              "top": df["High"].iloc[i],
              "bottom": df["Low"].iloc[i],
              "date": df.index[i],
          })

  # 2. Filtrage de Mitigation (Supprime les zones déjà testées/cassées par le prix)
  active_bulls = []
  for ob in bullish_obs:
    mitigated = False
    for j in range(ob["index"] + 1, len(df)):
      # Si le prix descend sous le haut de l'OB, il est mitigé
      if df["Low"].iloc[j] <= ob["top"]:
        mitigated = True
        break
    if not mitigated:
      active_bulls.append(ob)

  active_bears = []
  for ob in bearish_obs:
    mitigated = False
    for j in range(ob["index"] + 1, len(df)):
      # Si le prix monte au-dessus du bas de l'OB, il est mitigé
      if df["High"].iloc[j] >= ob["bottom"]:
        mitigated = True
        break
    if not mitigated:
      active_bears.append(ob)

  # On ne garde que les plus récents non mitigés (ex: max 2 de chaque côté pour la lisibilité)
  return active_bulls[-max_obs:], active_bears[-max_obs:]


# --- SYSTÈME DE MOT DE PASSE ---
entree_mot_de_passe = st.text_input(
    "🔑 Entrez le mot de passe pour OB Scanner AI :", type="password"
)

if entree_mot_de_passe != "Cecile46*":
  st.warning(
      "Veuillez entrer le mot de passe valide pour afficher l'application."
  )
  st.stop()


# --- BARRE LATÉRALE ---
st.sidebar.header("⚙️ Configuration du Marché")

actif_choisi = st.sidebar.selectbox(
    "Sélectionner l'Actif",
    options=[
        "Or / XAUUSD (GC=F)",
        "DAX / Germany 40 (^GDAXI)",
        "EURUSD (EURUSD=X)",
        "Bitcoin (BTC-USD)",
    ],
    index=0,
)

ticker_map = {
    "Or / XAUUSD (GC=F)": "GC=F",
    "DAX / Germany 40 (^GDAXI)": "^GDAXI",
    "EURUSD (EURUSD=X)": "EURUSD=X",
    "Bitcoin (BTC-USD)": "BTC-USD",
}
ticker = ticker_map[actif_choisi]

intervalle_choisi = st.sidebar.selectbox(
    "Unité de Temps", options=["15m", "1h", "4h", "1d"], index=1
)

st.sidebar.markdown("---")
st.sidebar.header("⭐ Paramètres OB Scanner 5★")
atr_period = st.sidebar.number_input(
    "Période ATR", value=14, min_value=5, max_value=50
)
lookback_period = st.sidebar.slider(
    "Fenêtre de recherche (Lookback)", min_value=5, max_value=50, value=20
)
max_zones = st.sidebar.slider(
    "Max zones affichées par côté", min_value=1, max_value=5, value=2
)

st.sidebar.markdown("---")
integrer_annonces = st.sidebar.checkbox(
    "Prendre en compte les annonces économiques", value=True
)

if integrer_annonces:
  annonces_jour = obtenir_annonces_du_jour()
  st.sidebar.markdown("---")
  st.sidebar.subheader("📅 Annonces Majeures du Jour")
  if annonces_jour:
    for annonce in annonces_jour:
      st.sidebar.warning(
          f"🔴 **{annonce.get('event')}**\n⏰ Heure :"
          f" {annonce.get('date')[11:16]}"
      )
  else:
    st.sidebar.success("✅ Aucune annonce majeure aujourd'hui.")


# --- APPLICATION PRINCIPALE ---
st.title("🎯 Smart Money Concepts - OB Scanner AI (Propre & Épuré)")
st.write(
    "Affichage exclusif des Order Blocks **non mitigés** (vierges) pour une"
    " lecture claire et nette."
)

if st.button("🚀 Charger le Marché et Analyser"):
  with st.spinner("Filtrage des zones actives et calculs en cours..."):
    df = charger_donnees_marche(ticker, intervalle_choisi)
    bull_obs, bear_obs = calculer_order_blocks(
        df,
        atr_len=atr_period,
        lookback=lookback_period,
        max_obs=max_zones,
    )

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Prix",
            )
        ]
    )

    # Ajout des zones Demand OB (Vertes) non mitigées
    for ob in bull_obs:
      fig.add_shape(
          type="rect",
          x0=df.index[ob["index"]],
          y0=ob["bottom"],
          x1=df.index[-1],
          y1=ob["top"],
          fillcolor="rgba(0, 200, 83, 0.2)",
          line=dict(color="rgba(0, 200, 83, 0.9)", width=1),
      )

    # Ajout des zones Supply OB (Rouges) non mitigées
    for ob in bear_obs:
      fig.add_shape(
          type="rect",
          x0=df.index[ob["index"]],
          y0=ob["bottom"],
          x1=df.index[-1],
          y1=ob["top"],
          fillcolor="rgba(255, 61, 0, 0.2)",
          line=dict(color="rgba(255, 61, 0, 0.9)", width=1),
      )

    debut_zoom = df.index[-100] if len(df) > 100 else df.index[0]

    fig.update_layout(
        title=f"SMC Pro Clean - {actif_choisi} ({intervalle_choisi})",
        xaxis_title="Date / Heure",
        yaxis_title="Prix",
        template="plotly_dark",
        height=700,
        xaxis_rangeslider_visible=False,
        xaxis=dict(range=[debut_zoom, df.index[-1]], type="date"),
    )

    st.success("Analyse épurée terminée !")

  st.markdown("---")
  st.subheader("🖼️ Graphique Propre (Zones Vierges Uniquement)")
  st.plotly_chart(fig, use_container_width=True)

  st.markdown("---")
  st.subheader("📍 Niveaux Actifs Exploitables")

  col1, col2 = st.columns(2)
  with col1:
    st.markdown("#### 🟢 Demand OB Actifs (Achat)")
    if bull_obs:
      for ob in bull_obs:
        st.info(
            f"**Zone :** {ob['bottom']:.2f} - {ob['top']:.2f} (Créé le"
            f" {ob['date']})"
        )
    else:
      st.success(
          "Aucun Demand OB actif (tous ont été testés ou prix au-dessus)."
      )

  with col2:
    st.markdown("#### 🔴 Supply OB Actifs (Vente)")
    if bear_obs:
      for ob in bear_obs:
        st.error(
            f"**Zone :** {ob['bottom']:.2f} - {ob['top']:.2f} (Créé le"
            f" {ob['date']})"
        )
    else:
      st.success("Aucun Supply OB actif (tous ont été testés ou prix en-dessous).")
