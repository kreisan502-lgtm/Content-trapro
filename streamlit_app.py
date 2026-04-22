import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

# 1. Konfigurasi Halaman & Injeksi CSS Premium
st.set_page_config(page_title="BizInvest Pro Suite", layout="wide", initial_sidebar_state="expanded")

# CSS Kustom untuk UI Premium (Efek Kartu, Tombol Presisi, dan Warna)
st.markdown("""
    <style>
    /* Menyembunyikan elemen bawaan Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Styling Tombol Premium */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.6rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Styling Metrik (Card Effect) */
    div[data-testid="metric-container"] {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border-left: 5px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sistem Login Sederhana
def check_password():
    def password_entered():
        if st.session_state["password"] == "AksesPremium123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("### 🔐 Login Akses BizInvest Pro")
        st.text_input("Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("### 🔐 Login Akses BizInvest Pro")
        st.text_input("Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        st.error("Password salah. Akses ditolak.")
        return False
    return True

# 3. Modul AI Trading Super Canggih
def menu_trading():
    st.markdown("## 📈 Terminal Analisis Kuantitatif")
    st.caption("Didukung oleh algoritma teknikal tingkat lanjut")
    
    # Kontrol Panel Atas
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            ticker_symbol = st.text_input("Kode Emiten (Contoh: LPKR.JK, BBCA.JK)", value="LPKR.JK")
        with col2:
            timeframe = st.selectbox("Rentang Waktu", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
        with col3:
            interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
        with col4:
            st.markdown("<br>", unsafe_allow_html=True) # Spasi agar tombol sejajar
            analyze_btn = st.button("Analisis Pasar")

    st.markdown("---")

    if analyze_btn:
        try:
            with st.spinner("Mengunduh data pasar dan memproses algoritma..."):
                ticker_data = yf.Ticker(ticker_symbol)
                df = ticker_data.history(period=timeframe, interval=interval)
                
                if df.empty:
                    st.error("Data tidak ditemukan. Pastikan kode emiten valid.")
                    return
                
                # Kalkulasi Indikator
                df.ta.macd(append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.bbands(append=True)
                df.ta.sma(length=20, append=True) # Simple Moving Average 20
                df.ta.ema(length=50, append=True) # Exponential Moving Average 50

                # TABS UI (Sangat Profesional)
                tab1, tab2, tab3 = st.tabs(["📊 Grafik & Indikator Utama", "🤖 Rekomendasi Sistem AI", "🏢 Profil Perusahaan"])
                
                with tab1:
                    # Metrik Harga Real-time
                    current_price = df['Close'].iloc[-1]
                    prev_price = df['Close'].iloc[-2]
                    price_change = current_price - prev_price
                    pct_change = (price_change / prev_price) * 100
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Harga Terakhir", f"Rp {current_price:,.0f}", f"{pct_change:.2f}%")
                    m2.metric("Volume Transaksi", f"{df['Volume'].iloc[-1]:,.0f}")
                    m3.metric("RSI (14)", f"{df['RSI_14'].iloc[-1]:.2f}")
                    m4.metric("Tren MACD", "Bullish" if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1] else "Bearish")

                    # Pembuatan Grafik Plotly (Candlestick + Volume)
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, subplot_titles=(f'Pergerakan Harga {ticker_symbol.upper()}', 'Volume'), 
                                        row_width=[0.2, 0.7])

                    # Plot Candlestick
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Harga'), row=1, col=1)
                    # Plot Moving Averages
                    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=1.5), name='SMA 20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='cyan', width=1.5), name='EMA 50'), row=1, col=1)
                    # Plot Volume
                    colors = ['green' if row['Open'] - row['Close'] >= 0 else 'red' for index, row in df.iterrows()]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

                    fig.update_layout(xaxis_rangeslider_visible=False, height=600, template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.markdown("### Kesimpulan Analisis Teknikal")
                    rsi_val = df['RSI_14'].iloc[-1]
                    macd_val = df['MACD_12_26_9'].iloc[-1]
                    signal_val = df['MACDs_12_26_9'].iloc[-1]
                    
                    rekomendasi = "HOLD (Pantau Ketat)"
                    alasan = "Pasar sedang dalam fase konsolidasi atau tidak menunjukkan momentum arah yang kuat."
                    
                    if rsi_val < 30 and macd_val > signal_val:
                        rekomendasi = "STRONG BUY 🟢"
                        alasan = "Aset berada di area jenuh jual (Oversold) dan indikator tren mulai menunjukkan pembalikan arah naik (Golden Cross)."
                    elif rsi_val > 70 or macd_val < signal_val:
                        rekomendasi = "TAKE PROFIT / SELL 🔴"
                        alasan = "Aset berada di area jenuh beli (Overbought) atau momentum tren mulai melemah (Death Cross)."
                        
                    st.success(f"**Rekomendasi Algoritma:** {rekomendasi}")
                    st.write(f"**Dasar Logika:** {alasan}")
                    
                    with st.expander("Lihat Data Tabel Mentah"):
                        st.dataframe(df.tail(10))

                with tab3:
                    info = ticker_data.info
                    st.write(f"**Nama:** {info.get('longName', 'Tidak tersedia')}")
                    st.write(f"**Sektor:** {info.get('sector', 'Tidak tersedia')}")
                    st.write(f"**Kapitalisasi Pasar:** Rp {info.get('marketCap', 0):,.0f}")
                    st.write(f"**Deskripsi Bisnis:**")
                    st.write(info.get('longBusinessSummary', 'Data deskripsi tidak tersedia untuk emiten ini.'))

        except Exception as e:
            st.error(f"Terjadi kesalahan saat mengambil data: {e}")

# 4. Navigasi Utama Aplikasi
if check_password():
    with st.sidebar:
        st.markdown("## ⚙️ Main Menu")
        pilihan = st.radio("Pilih Modul:", ["AI Trading Terminal", "Kalkulator HPP & Margin"])
        st.markdown("---")
        st.caption("BizInvest Pro Suite v2.0")
        st.caption("Licensed Copy")
    
    if pilihan == "AI Trading Terminal":
        menu_trading()
    elif pilihan == "Kalkulator HPP & Margin":
        st.title("📦 Modul Kalkulator HPP (Segera Hadir)")
        st.info("Modul HPP bisa kamu tempelkan dari kode sebelumnya di bagian ini.")
                    
