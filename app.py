import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configurazione pagina
st.set_page_config(page_title="Radar Scenari Macro Dashboard", layout="wide", initial_sidebar_state="expanded")

# CSS personalizzato stile dark dashboard
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    h1, h2, h3 {color: #ffffff;}
    .tab-container {display: flex; gap: 10px; margin: 20px 0;}
    .tab-btn {padding: 10px 20px; background: #262730; color: #fff; border: none; cursor: pointer; border-radius: 5px;}
    .tab-btn.active {background: #1f77b4;}
    .kpi-box {background: #1e1e2e; padding: 20px; border-radius: 10px; text-align: center;}
    .kpi-value {font-size: 2em; font-weight: bold;}
    .positive {color: #00ff41;}
    .negative {color: #ff4136;}
</style>
""", unsafe_allow_html=True)

# Dati ETF per scenario
scenari_data = {
    "Goldilocks": [
        {"ticker": "SPY", "nome": "SPDR S&P 500 ETF"},
        {"ticker": "QQQ", "nome": "Invesco QQQ Trust"},
        {"ticker": "IWM", "nome": "iShares Russell 2000 ETF"},
        {"ticker": "EEM", "nome": "iShares MSCI Emerging Markets ETF"},
        {"ticker": "VNQ", "nome": "Vanguard Real Estate ETF"}
    ],
    "Recession": [
        {"ticker": "TLT", "nome": "iShares 20+ Year Treasury Bond ETF"},
        {"ticker": "GLD", "nome": "SPDR Gold Trust"},
        {"ticker": "UUP", "nome": "Invesco DB US Dollar Index Bullish Fund"},
        {"ticker": "SHY", "nome": "iShares 1-3 Year Treasury Bond ETF"},
        {"ticker": "AGG", "nome": "iShares Core US Aggregate Bond ETF"}
    ],
    "Stagflation": [
        {"ticker": "GLD", "nome": "SPDR Gold Trust"},
        {"ticker": "DBC", "nome": "Invesco DB Commodity Index Tracking Fund"},
        {"ticker": "TIP", "nome": "iShares TIPS Bond ETF"},
        {"ticker": "XLE", "nome": "Energy Select Sector SPDR Fund"},
        {"ticker": "PDBC", "nome": "Invesco Optimum Yield Diversified Commodity"}
    ]
}

# Funzione per calcolare variazioni percentuali
def calcola_variazioni(ticker):
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=100)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return None
        
        prezzo_attuale = hist['Close'].iloc[-1]
        
        # Calcolo variazioni
        var_1d = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100 if len(hist) > 1 else 0
        var_1w = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-6]) - 1) * 100 if len(hist) > 5 else 0
        var_1m = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-22]) - 1) * 100 if len(hist) > 21 else 0
        var_3m = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-66]) - 1) * 100 if len(hist) > 65 else 0
        
        return {
            "prezzo": prezzo_attuale,
            "var_1d": var_1d,
            "var_1w": var_1w,
            "var_1m": var_1m,
            "var_3m": var_3m
        }
    except:
        return None

# Sidebar: selezione scenario
st.sidebar.title("📊 Scenari Macro")
scenario = st.sidebar.radio("Seleziona Scenario", list(scenari_data.keys()))

# Titolo principale
st.title(f"Dashboard: {scenario}")

# Recupero dati
with st.spinner("Caricamento dati da Yahoo Finance..."):
    etf_list = scenari_data[scenario]
    dati_etf = []
    
    for etf in etf_list:
        var = calcola_variazioni(etf["ticker"])
        if var:
            dati_etf.append({
                "Ticker": etf["ticker"],
                "Nome ETF": etf["nome"],
                "Prezzo": f"${var['prezzo']:.2f}",
                "1 Giorno %": var['var_1d'],
                "1 Settimana %": var['var_1w'],
                "1 Mese %": var['var_1m'],
                "3 Mesi %": var['var_3m']
            })

if not dati_etf:
    st.error("⚠️ Impossibile recuperare i dati. Verifica la connessione.")
    st.stop()

df = pd.DataFrame(dati_etf)

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Tabella Performance ETF")
    st.dataframe(df.style.format({
        "1 Giorno %": "{:.2f}",
        "1 Settimana %": "{:.2f}",
        "1 Mese %": "{:.2f}",
        "3 Mesi %": "{:.2f}"
    }).applymap(lambda x: 'color: #00ff41' if isinstance(x, (int, float)) and x > 0 else ('color: #ff4136' if isinstance(x, (int, float)) and x < 0 else ''), subset=['1 Giorno %', '1 Settimana %', '1 Mese %', '3 Mesi %']), use_container_width=True)

with col2:
    st.subheader("📊 KPI Medi")
    avg_1d = df["1 Giorno %"].mean()
    avg_1w = df["1 Settimana %"].mean()
    avg_1m = df["1 Mese %"].mean()
    avg_3m = df["3 Mesi %"].mean()
    
    col_kpi1, col_kpi2 = st.columns(2)
    with col_kpi1:
        st.metric("Avg 1 Giorno", f"{avg_1d:.2f}%", delta=None)
        st.metric("Avg 1 Mese", f"{avg_1m:.2f}%", delta=None)
    with col_kpi2:
        st.metric("Avg 1 Settimana", f"{avg_1w:.2f}%", delta=None)
        st.metric("Avg 3 Mesi", f"{avg_3m:.2f}%", delta=None)

# Grafico a linee interattivo
st.subheader("📉 Grafico Variazioni per Periodo")
fig = go.Figure()

for idx, row in df.iterrows():
    fig.add_trace(go.Scatter(
        x=["1 Giorno", "1 Settimana", "1 Mese", "3 Mesi"],
        y=[row["1 Giorno %"], row["1 Settimana %"], row["1 Mese %"], row["3 Mesi %"]],
        mode='lines+markers',
        name=row["Ticker"],
        line=dict(width=3),
        marker=dict(size=8)
    ))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Periodo",
    yaxis_title="Variazione %",
    hovermode="x unified",
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption(f"📅 Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Dati: Yahoo Finance via yfinance")
