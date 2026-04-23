import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

# ==========================================
# 1. KONFIGURASI & UI CSS
# ==========================================
st.set_page_config(page_title="BizInvest Pro Multi-Asset", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.6rem;
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"] {
        background-color: #0d1117;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE ASET DINAMIS
# ==========================================
DB_ASET = {
    "Saham Indonesia (BEI)": [
        "LPKR.JK - Lippo Karawaci", "BBCA.JK - Bank Central Asia", "BBRI.JK - Bank Rakyat Indonesia",
        "TLKM.JK - Telkom Indonesia", "ASII.JK - Astra International", "GOTO.JK - GoTo Tokopedia",
        "ADRO.JK - Adaro Energy", "ANTM.JK - Aneka Tambang", "BMRI.JK - Bank Mandiri", "BBNI.JK - Bank Negara Indonesia"
    ],
    "Saham Luar Negeri (US)": [
        "AAPL - Apple Inc.", "TSLA - Tesla Inc.", "NVDA - NVIDIA Corp", "MSFT - Microsoft",
        "AMZN - Amazon.com", "GOOGL - Alphabet (Google)", "META - Meta Platforms", "NFLX - Netflix"
    ],
    "Cryptocurrency": [
        "BTC-USD - Bitcoin", "ETH-USD - Ethereum", "SOL-USD - Solana", "BNB-USD - Binance Coin",
        "XRP-USD - Ripple", "ADA-USD - Cardano", "DOGE-USD - Dogecoin"
    ]
}

# ==========================================
# 3. SISTEM LOGIN
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == "AksesPremium123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 BizInvest Pro Login</h2>", unsafe_allow_html=True)
        st.text_input("Password Akses:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password Akses:", type="password", on_change=password_entered, key="password")
        st.error("❌ Password salah.")
        return False
    return True

# ==========================================
# 4. TERMINAL ANALISIS MULTI-ASET
# ==========================================
def menu_trading():
    st.markdown("## 🌐 Multi-Asset Intelligence Terminal")
    
    with st.container():
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            kategori = st.selectbox("Pilih Jenis Aset & Pasar", list(DB_ASET.keys()))
        with c2:
            pilihan = st.selectbox("Cari Nama Aset", DB_ASET[kategori] + ["➕ Input Manual Kode..."])
        with c3:
            if pilihan == "➕ Input Manual Kode...":
                ticker_symbol = st.text_input("Ketik Kode (Contoh: BUMI.JK atau DOGE-USD)", "").upper()
            else:
                ticker_symbol = pilihan.split(" - ")[0]

        # Row 2 untuk Parameter
        p1, p2, p3 = st.columns([1, 1, 1])
        with p1:
            timeframe = st.selectbox("Rentang Waktu", ["1mo", "3mo", "6mo", "1y", "5y"], index=1)
        with p2:
            interval = st.selectbox("Interval Lilin", ["1d", "1wk", "1mo"], index=0)
        with p3:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_btn = st.button("🚀 Jalankan Analisis")

    st.markdown("---")

    if analyze_btn and ticker_symbol:
        try:
            with st.spinner(f"Menghubungkan ke Bursa Pasar untuk {ticker_symbol}..."):
                data_raw = yf.Ticker(ticker_symbol)
                df = data_raw.history(period=timeframe, interval=interval)
                
                if df.empty:
                    st.error("⚠️ Data tidak ditemukan. Pastikan kode ticker benar.")
                    return

                # Advanced Indicators
                df.ta.macd(append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.bbands(append=True)
                df.ta.ema(length=20, append=True)
                df.ta.ema(length=50, append=True)

                tab1, tab2, tab3 = st.tabs(["📈 Chart Pro", "🧠 AI Analysis", "📋 Market Info"])
                
                with tab1:
                    # Metrik Utama
                    last_price = df['Close'].iloc[-1]
                    change = last_price - df['Close'].iloc[-2]
                    pct = (change / df['Close'].iloc[-2]) * 100
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Harga Terakhir", f"{last_price:,.2f}", f"{pct:.2f}%")
                    m2.metric("Volatilitas (RSI)", f"{df['RSI_14'].iloc[-1]:.2f}")
                    m3.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
                    m4.metric("Status EMA", "Bullish" if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1] else "Bearish")

                    # Candlestick + Volume + Indikator
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
                    
                    # Candlestick & EMA
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Harga'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='yellow', width=1), name='EMA 20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='cyan', width=1), name='EMA 50'), row=1, col=1)
                    
                    # Volume
                    v_colors = ['green' if df.iloc[i]['Close'] >= df.iloc[i]['Open'] else 'red' for i in range(len(df))]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)

                    fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.subheader("💡 Intelligence Sinyal")
                    rsi = df['RSI_14'].iloc[-1]
                    macd = df['MACD_12_26_9'].iloc[-1]
                    signal = df['MACDs_12_26_9'].iloc[-1]
                    
                    if rsi < 35 and macd > signal:
                        st.success("### REKOMENDASI: BUY 🟢")
                        st.write("Alasan: Kondisi Jenuh Jual (Oversold) terdeteksi dan momentum MACD mulai menguat.")
                    elif rsi > 65 or macd < signal:
                        st.error("### REKOMENDASI: SELL / TAKE PROFIT 🔴")
                        st.write("Alasan: Kondisi Jenuh Beli (Overbought) atau momentum tren mulai melemah.")
                    else:
                        st.warning("### REKOMENDASI: HOLD / WAIT 🟡")
                        st.write("Alasan: Pasar belum memberikan konfirmasi arah yang kuat.")

                with tab3:
                    info = data_raw.info
                    st.write(f"**Nama Resmi:** {info.get('longName', ticker_symbol)}")
                    st.write(f"**Mata Uang:** {info.get('currency', 'N/A')}")
                    st.write(f"**Bursa:** {info.get('exchange', 'N/A')}")
                    st.write("**Deskripsi:**")
                    st.write(info.get('longBusinessSummary', 'Informasi profil tidak tersedia.'))

        except Exception as e:
            st.error(f"Koneksi Gagal: {e}")

# ==========================================
# 5. MODUL HPP
# ==========================================
def menu_hpp():
    st.markdown("## 📦 Business Margin Optimizer")
    col_a, col_b = st.columns(2)
    with col_a:
        bahan = st.number_input("Biaya Bahan Baku", value=500000)
        tenaga = st.number_input("Biaya Tenaga", value=200000)
        lain = st.number_input("Biaya Lainnya", value=50000)
    with col_b:
        qty = st.number_input("Jumlah Produksi", value=100)
        margin = st.slider("Target Margin (%)", 0, 100, 30)
        
    if st.button("Hitung Profitabilitas"):
        total = bahan + tenaga + lain
        hpp = total / qty
        jual = hpp * (1 + margin/100)
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("HPP per Unit", f"Rp {hpp:,.0f}")
        c2.metric("Harga Jual", f"Rp {jual:,.0f}")
        c3.metric("Laba per Unit", f"Rp {jual-hpp:,.0f}")

# ==========================================
# 6. NAVIGASI UTAMA
# ==========================================
if check_password():
    st.markdown("<h1 style='text-align: center;'>⚡ BizInvest Suite v3.0</h1>", unsafe_allow_html=True)
    mode = st.radio("Pilih Layanan", ["Analisis Pasar (Multi-Asset)", "Kalkulator Bisnis (HPP)"], horizontal=True, label_visibility="collapsed")
    st.divider()
    
    if "Analisis Pasar" in mode:
        menu_trading()
    else:
        menu_hpp()
                    
