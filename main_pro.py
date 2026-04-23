import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta
import time

# ==========================================
# 1. KONFIGURASI TEMA "DARK GOLD PREMIUM"
# ==========================================
st.set_page_config(page_title="BizInvest Pro v5.0", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Sembunyikan elemen Streamlit bawaan */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Background Premium */
    .stApp { background-color: #0b0f19; color: #ffffff; }
    
    /* Desain Tombol Utama (Emas/Biru Tua) */
    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        color: #fbbf24; /* Warna Emas */
        font-weight: 800; font-size: 16px; border: 1px solid #d97706;
        padding: 0.8rem; transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(217, 119, 6, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-3px); box-shadow: 0 6px 20px rgba(217, 119, 6, 0.5);
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: white;
    }
    
    /* Kartu Metrik */
    div[data-testid="metric-container"] {
        background: #1f2937; border-radius: 12px; padding: 15px;
        border-left: 4px solid #fbbf24; box-shadow: 0 4px 6px rgba(0,0,0,0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE NAVIGASI & LOGIN
# ==========================================
if 'page' not in st.session_state: st.session_state['page'] = 'home'
def navigate(page_name): st.session_state['page'] = page_name

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: #fbbf24; margin-top: 10vh;'>👑 Akses VIP BizInvest Pro</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Masukkan Lisensi:", type="password", key="pwd_input")
            if st.button("Masuk"):
                if st.session_state.pwd_input == "AksesPremium123":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else: st.error("❌ Lisensi tidak valid.")
        return False
    return st.session_state["password_correct"]

# ==========================================
# 3. KECERDASAN BUATAN (AI ADVISOR ENGINE)
# ==========================================
def generate_ai_report(ticker, df, info):
    """Menghasilkan laporan naratif AI layaknya analis profesional"""
    rsi = df['RSI_14'].iloc[-1]
    macd = df['MACD_12_26_9'].iloc[-1]
    signal = df['MACDs_12_26_9'].iloc[-1]
    beta = info.get('beta', 1.0)
    
    laporan = f"**Laporan AI untuk {ticker}:**\n\n"
    laporan += "Berdsarkan pemindaian algoritma kami, "
    
    if rsi > 70: laporan += "aset ini saat ini menunjukkan tanda-tanda **Jenuh Beli (Overbought)**. Banyak investor yang telah meraup keuntungan, sehingga risiko koreksi atau penurunan harga dalam jangka pendek sangat tinggi. "
    elif rsi < 30: laporan += "aset ini berada di area **Jenuh Jual (Oversold)**. Ini menandakan kepanikan pasar berlebihan, dan sering kali menjadi area *support* kuat untuk memantul naik. "
    else: laporan += "pergerakan harga saat ini berada di area netral. "
    
    if macd > signal: laporan += "Tren momentum MACD mengonfirmasi adanya **akumulasi positif**, mendukung pergerakan harga ke atas.\n\n"
    else: laporan += "Indikator MACD menunjukkan tekanan jual masih mendominasi.\n\n"
    
    laporan += f"**Profil Risiko:** Beta perusahaan tercatat di angka {beta:.2f}. "
    if beta > 1.2: laporan += "Ini berarti aset ini lebih bergejolak dibanding rata-rata pasar. Anda bisa mendapat untung besar dengan cepat, tapi risikonya pun sangat tinggi."
    elif beta < 0.8: laporan += "Ini adalah aset defensif yang pergerakannya lambat namun stabil. Sangat cocok untuk mengamankan nilai uang dari inflasi."
    else: laporan += "Risiko pergerakan harga berada pada level moderat dan wajar."
    
    return laporan

# ==========================================
# 4. MODUL AI TRADING
# ==========================================
def menu_trading():
    col_bck, col_title = st.columns([1, 5])
    with col_bck: st.button("⬅️ KEMBALI", on_click=navigate, args=('home',))
    with col_title: st.markdown("<h2 style='color: #fbbf24; margin-top:-10px;'>📊 AI Trading & Analisis Investasi</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: ticker_symbol = st.text_input("Masukkan Kode Emiten (Contoh: BBCA.JK, AAPL, BTC-USD)", "BBCA.JK").upper()
    with c2: timeframe = st.selectbox("Rentang Data", ["3mo", "6mo", "1y", "2y"], index=2)
    with c3:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("Pindai Perusahaan")

    if analyze_btn and ticker_symbol:
        with st.spinner("Mengaktifkan Neural Network & Mengunduh Data Bursa..."):
            try:
                data_raw = yf.Ticker(ticker_symbol)
                df = data_raw.history(period=timeframe)
                info = data_raw.info
                
                if df.empty:
                    st.error("Data tidak ditemukan.")
                    return
                
                # Kalkulasi Teknikal
                df.ta.macd(append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=20, append=True)
                df.ta.ema(length=50, append=True)

                tab1, tab2, tab3 = st.tabs(["📈 Terminal Grafik", "🧠 AI Advisor (Saran Pintar)", "🏢 Fundamental Bisnis"])
                
                with tab1:
                    st.markdown("### Grafik Pergerakan Harga")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Harga Saat Ini", f"{df['Close'].iloc[-1]:,.2f}")
                    m2.metric("RSI (Volatilitas)", f"{df['RSI_14'].iloc[-1]:.2f}")
                    m3.metric("Volume Trading", f"{df['Volume'].iloc[-1]:,.0f}")

                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_width=[0.2, 0.8])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Harga'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#fbbf24', width=1.5), name='EMA 20'), row=1, col=1)
                    v_colors = ['#10b981' if df.iloc[i]['Close'] >= df.iloc[i]['Open'] else '#ef4444' for i in range(len(df))]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)
                    fig.update_layout(template='plotly_dark', height=550, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.markdown("### 🤖 Bantuan AI Advisor")
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write("Halo! Saya asisten AI Anda. Membaca data pasar...")
                        time.sleep(1) # Efek AI sedang berpikir
                        laporan_ai = generate_ai_report(ticker_symbol, df, info)
                        st.write(laporan_ai)
                        
                    st.info("💡 **Tips AI:** Jangan pernah menggunakan 100% modal Anda pada satu waktu. Selalu gunakan strategi Cicil (DCA - Dollar Cost Averaging).")

                with tab3:
                    st.markdown("### Kesehatan Perusahaan")
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        st.write(f"**Nama Bisnis:** {info.get('longName', ticker_symbol)}")
                        st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
                        st.write(f"**Margin Laba (Profit):** {info.get('profitMargins', 0)*100:.2f}%")
                    with col_f2:
                        st.write(f"**Rekomendasi Analis Global:** {info.get('recommendationKey', 'N/A').upper()}")
                        st.write(f"**Target Harga Masa Depan:** {info.get('targetMeanPrice', 'N/A')}")
                        st.write(f"**Dominasi Institusi:** {info.get('heldPercentInstitutions', 0)*100:.2f}%")

            except Exception as e:
                st.error(f"Gagal memproses data: {e}")

# ==========================================
# 5. MODUL KALKULATOR HPP
# ==========================================
def menu_hpp():
    col_bck, col_title = st.columns([1, 5])
    with col_bck: st.button("⬅️ KEMBALI", on_click=navigate, args=('home',))
    with col_title: st.markdown("<h2 style='color: #fbbf24; margin-top:-10px;'>📦 AI Business & HPP Optimizer</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Input Biaya Modal")
        bahan = st.number_input("Biaya Bahan Baku (Rp)", value=1000000)
        tenaga = st.number_input("Biaya Tenaga Kerja (Rp)", value=300000)
        lain = st.number_input("Overhead / Operasional (Rp)", value=200000)
    with col_b:
        st.markdown("#### Strategi Penjualan")
        qty = st.number_input("Estimasi Unit Terjual", value=100)
        margin = st.slider("Target Profit Margin (%)", 5, 100, 35)
        
    if st.button("Kalkulasi & Minta Saran AI"):
        total = bahan + tenaga + lain
        hpp = total / qty if qty > 0 else 0
        jual = hpp * (1 + margin/100)
        laba_satuan = jual - hpp
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Modal per Unit (HPP)", f"Rp {hpp:,.0f}")
        c2.metric("Saran Harga Jual", f"Rp {jual:,.0f}")
        c3.metric("Potensi Laba/Unit", f"Rp {laba_satuan:,.0f}")
        
        st.markdown("---")
        st.markdown("### 🤖 Saran Bisnis AI")
        if margin > 50:
            st.warning("⚠️ **Peringatan AI:** Margin di atas 50% sangat tinggi. Pastikan produkmu memiliki kualitas Premium atau *branding* yang kuat agar konsumen tidak merasa kemahalan.")
        elif margin < 15:
            st.error("⚠️ **Peringatan AI:** Margin terlalu tipis! Kamu rentan rugi jika ada kenaikan harga bahan baku yang mendadak. Coba tekan biaya operasional.")
        else:
            st.success("✅ **Saran AI:** Margin sangat ideal dan kompetitif untuk pasar umum. Lanjutkan strategi penjualanmu!")

# ==========================================
# 6. HALAMAN UTAMA (LANDING PAGE)
# ==========================================
if check_password():
    if st.session_state['page'] == 'home':
        st.markdown("<div style='text-align: center; margin-top: 5vh;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #fbbf24; font-size: 3rem;'>BIZINVEST PRO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9ca3af; font-size: 1.2rem; margin-bottom: 50px;'>Suite Analisis Finansial Terpadu dengan Kecerdasan Buatan</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📈 Masuk ke Terminal Investasi"): navigate('trading')
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📦 Masuk ke Kalkulator Bisnis"): navigate('hpp')
            
    elif st.session_state['page'] == 'trading': menu_trading()
    elif st.session_state['page'] == 'hpp': menu_hpp()
