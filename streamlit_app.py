import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas_ta as ta

# ==========================================
# 1. KONFIGURASI & UI PREMIUM CSS
# ==========================================
st.set_page_config(page_title="BizInvest Pro v4.0", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Tombol Utama (Menu & Navigasi) */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #141E30 0%, #243B55 100%);
        color: #00d2ff;
        font-weight: 800;
        font-size: 18px;
        border: 1px solid #00d2ff;
        padding: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 210, 255, 0.4);
        background: linear-gradient(135deg, #243B55 0%, #141E30 100%);
        color: white;
    }
    
    /* Tombol Kembali (Back Button) */
    .back-btn>div>button {
        background: transparent !important;
        border: 1px solid #ff4b4b !important;
        color: #ff4b4b !important;
        box-shadow: none !important;
        padding: 0.5rem !important;
    }
    .back-btn>div>button:hover {
        background: #ff4b4b !important;
        color: white !important;
    }

    /* Metrik Card */
    div[data-testid="metric-container"] {
        background: rgba(20, 30, 48, 0.7);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #00d2ff;
        backdrop-filter: blur(10px);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT (UNTUK NAVIGASI TOMBOL)
# ==========================================
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

def navigate(page_name):
    st.session_state['page'] = page_name

# ==========================================
# 3. DATABASE ASET & LOGIN
# ==========================================
DB_ASET = {
    "Saham Indonesia (BEI)": ["LPKR.JK - Lippo Karawaci", "BBCA.JK - Bank Central Asia", "BBRI.JK - Bank Rakyat", "TLKM.JK - Telkom Indonesia", "ASII.JK - Astra International", "GOTO.JK - GoTo", "BUMI.JK - Bumi Resources", "BRPT.JK - Barito Pacific"],
    "Saham Global (US)": ["AAPL - Apple Inc", "TSLA - Tesla Inc", "NVDA - NVIDIA", "MSFT - Microsoft"],
    "Crypto": ["BTC-USD - Bitcoin", "ETH-USD - Ethereum", "SOL-USD - Solana", "DOGE-USD - Dogecoin"]
}

def check_password():
    def password_entered():
        if st.session_state["password"] == "AksesPremium123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; margin-top: 100px;'>🔐 Akses Eksklusif BizInvest Pro</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Masukkan Lisensi / Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center; margin-top: 100px;'>🔐 Akses Eksklusif BizInvest Pro</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Masukkan Lisensi / Password:", type="password", on_change=password_entered, key="password")
            st.error("❌ Lisensi tidak valid.")
        return False
    return True

# ==========================================
# 4. MODUL 1: AI TRADING & FUNDAMENTAL
# ==========================================
def menu_trading():
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    st.button("⬅️ Kembali ke Menu Utama", on_click=navigate, args=('home',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## 📈 AI Terminal & Corporate Intelligence")
    
    with st.container():
        c1, c2, c3 = st.columns([1.5, 1.5, 1])
        with c1:
            kategori = st.selectbox("Market / Pasar", list(DB_ASET.keys()))
        with c2:
            pilihan = st.selectbox("Emiten / Aset", DB_ASET[kategori] + ["➕ Input Manual Ticker..."])
            ticker_symbol = st.text_input("Ketik Kode (Jika Pilih Manual)", "").upper() if pilihan == "➕ Input Manual Ticker..." else pilihan.split(" - ")[0]
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_btn = st.button("🚀 Pindai Perusahaan")

    st.markdown("---")

    if analyze_btn and ticker_symbol:
        try:
            with st.spinner(f"Menyinkronkan data dengan bursa untuk {ticker_symbol}..."):
                data_raw = yf.Ticker(ticker_symbol)
                df = data_raw.history(period="1y", interval="1d")
                info = data_raw.info
                
                if df.empty:
                    st.error("⚠️ Data tidak ditemukan.")
                    return

                # Indikator
                df.ta.macd(append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.ema(length=20, append=True)
                df.ta.ema(length=50, append=True)

                tab1, tab2, tab3 = st.tabs(["📊 Analisis Teknikal (Grafik)", "🤖 Sinyal AI Jangka Pendek", "🏢 Laporan Fundamental & Risiko (Long-term)"])
                
                with tab1: # GRAFIK SAMA SEPERTI SEBELUMNYA
                    last_price = df['Close'].iloc[-1]
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Harga Terakhir", f"{last_price:,.2f}")
                    m2.metric("RSI (14)", f"{df['RSI_14'].iloc[-1]:.2f}")
                    m3.metric("Volume", f"{df['Volume'].iloc[-1]:,.0f}")
                    m4.metric("Tren EMA", "Bullish" if df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1] else "Bearish")

                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_width=[0.2, 0.8])
                    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Harga'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='yellow', width=1), name='EMA 20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='cyan', width=1), name='EMA 50'), row=1, col=1)
                    
                    v_colors = ['green' if df.iloc[i]['Close'] >= df.iloc[i]['Open'] else 'red' for i in range(len(df))]
                    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=v_colors, name='Volume'), row=2, col=1)

                    fig.update_layout(template='plotly_dark', height=600, xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)

                with tab2: # AI TEKNIKAL
                    st.subheader("Sinyal Perdagangan Harian/Mingguan")
                    rsi = df['RSI_14'].iloc[-1]
                    macd = df['MACD_12_26_9'].iloc[-1]
                    signal = df['MACDs_12_26_9'].iloc[-1]
                    
                    if rsi < 35 and macd > signal:
                        st.success("### 🟢 REKOMENDASI AI: BUY (PELUANG MASUK)")
                        st.write("Aset sedang berada di bawah harga wajarnya (Oversold).")
                    elif rsi > 65 or macd < signal:
                        st.error("### 🔴 REKOMENDASI AI: SELL (TAKE PROFIT)")
                        st.write("Aset rawan koreksi karena sudah terlalu banyak dibeli (Overbought).")
                    else:
                        st.warning("### 🟡 REKOMENDASI AI: HOLD (PANTAU)")
                        st.write("Pasar sedang sideways. Tunggu momentum yang lebih jelas.")

                with tab3: # FUNDAMENTAL & RISIKO (BARU & SANGAT DETAIL)
                    st.markdown("### 📋 Laporan Eksekutif Perusahaan")
                    
                    # Ekstraksi Data Fundamental
                    beta = info.get('beta', 1.0) # Beta mengukur volatilitas vs pasar
                    profit_margin = info.get('profitMargins', 0) * 100
                    revenue_growth = info.get('revenueGrowth', 0) * 100
                    target_price = info.get('targetMeanPrice', last_price)
                    recommendation = info.get('recommendationKey', 'N/A').upper()
                    
                    col_fund1, col_fund2 = st.columns(2)
                    
                    with col_fund1:
                        st.markdown("#### 1. Tingkat Risiko (Market Volatility)")
                        if beta > 1.2:
                            st.error(f"**Risiko TINGGI (Beta: {beta:.2f})**\nHarga aset ini sangat bergejolak dan lebih sensitif terhadap kepanikan pasar global. Cocok untuk trader agresif.")
                        elif beta < 0.8:
                            st.success(f"**Risiko RENDAH (Beta: {beta:.2f})**\nAset ini cenderung stabil dan defensif meskipun pasar sedang turun. Cocok untuk investasi jangka panjang.")
                        else:
                            st.info(f"**Risiko MENENGAH (Beta: {beta:.2f})**\nVolatilitas wajar, bergerak seirama dengan rata-rata pasar.")
                            
                        st.markdown("#### 2. Keadaan Perusahaan (Kesehatan Finansial)")
                        st.write(f"• **Margin Keuntungan:** {profit_margin:.2f}%")
                        st.write(f"• **Pertumbuhan Pendapatan:** {revenue_growth:.2f}%")
                        if profit_margin > 10 and revenue_growth > 5:
                            st.success("Kinerja perusahaan SANGAT SEHAT. Mampu mencetak laba operasional dengan stabil di tengah kondisi ekonomi saat ini.")
                        elif profit_margin < 0:
                            st.error("Perusahaan sedang MERUGI (Defisit). Waspada terhadap beban hutang dan biaya operasional.")
                        else:
                            st.warning("Perusahaan sehat namun pertumbuhannya stagnan. Perlu inovasi baru.")

                    with col_fund2:
                        st.markdown("#### 3. Kemungkinan Ke Depannya (Outlook & Target)")
                        st.write(f"• **Target Harga Analis WallStreet:** Rp/USD {target_price:,.2f}")
                        st.write(f"• **Konsensus Analis Global:** **{recommendation}**")
                        
                        upside = ((target_price - last_price) / last_price) * 100 if last_price > 0 else 0
                        if upside > 10:
                            st.success(f"Terdapat potensi KENAIKAN (Upside) sebesar **{upside:.2f}%** dari harga saat ini menuju target harga wajarnya.")
                        elif upside < -5:
                            st.error(f"Aset ini dinilai sudah terlalu mahal (Overvalued). Potensi PENURUNAN sebesar **{abs(upside):.2f}%**.")
                        else:
                            st.info("Harga saat ini sudah sesuai dengan nilai wajarnya (Fair Value).")

                    st.markdown("---")
                    st.markdown("#### 4. Informasi Internal & Eksternal")
                    info_col1, info_col2 = st.columns(2)
                    with info_col1:
                        st.write(f"**Sektor (Faktor Eksternal):** {info.get('sector', 'N/A')}")
                        st.write(f"**Industri Spesifik:** {info.get('industry', 'N/A')}")
                        st.write(f"**Karyawan:** {info.get('fullTimeEmployees', 'N/A')} Orang")
                    with info_col2:
                        st.write(f"**Pegangan Institusi:** {info.get('heldPercentInstitutions', 0)*100:.2f}% (Kepemilikan modal besar)")
                        st.write(f"**Hutang terhadap Ekuitas:** {info.get('debtToEquity', 'N/A')}")
                        
                    with st.expander("Baca Rangkuman Eksekutif Bisnis (Internal Info)"):
                        st.write(info.get('longBusinessSummary', 'Data deskripsi internal tidak disediakan oleh bursa untuk emiten ini.'))

        except Exception as e:
            st.error(f"Gagal mengambil data mendalam: {e}")

# ==========================================
# 5. MODUL 2: HPP & MANAJEMEN BISNIS
# ==========================================
def menu_hpp():
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    st.button("⬅️ Kembali ke Menu Utama", on_click=navigate, args=('home',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## 📦 Kalkulator HPP Bisnis")
    
    col_a, col_b = st.columns(2)
    with col_a:
        bahan = st.number_input("Biaya Bahan Baku", value=500000)
        tenaga = st.number_input("Biaya Tenaga Kerja", value=200000)
        lain = st.number_input("Overhead (Sewa, Listrik, dll)", value=50000)
    with col_b:
        qty = st.number_input("Jumlah Unit Produksi", value=100)
        margin = st.slider("Target Margin Bersih (%)", 0, 100, 30)
        
    if st.button("Hitung Struktur Harga"):
        total = bahan + tenaga + lain
        hpp = total / qty
        jual = hpp * (1 + margin/100)
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("HPP per Unit", f"Rp {hpp:,.0f}")
        c2.metric("Harga Jual Disarankan", f"Rp {jual:,.0f}")
        c3.metric("Estimasi Laba per Unit", f"Rp {jual-hpp:,.0f}")

# ==========================================
# 6. ROUTING (HALAMAN UTAMA)
# ==========================================
if check_password():
    if st.session_state['page'] == 'home':
        st.markdown("<br><br><h1 style='text-align: center; color: white;'>Selamat Datang di BizInvest Pro</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray; margin-bottom: 50px;'>Pilih modul instrumen yang ingin Anda gunakan</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.button("🏢\nANALISIS INVESTASI & RISIKO", on_click=navigate, args=('trading',))
            st.markdown("<p style='text-align: center; color: gray;'>Fitur lengkap analisis riwayat saham, crypto, perhitungan profitabilitas perusahaan, dan prediksi level risiko.</p>", unsafe_allow_html=True)
            
        with col2:
            st.button("📦\nKALKULATOR HPP & BISNIS", on_click=navigate, args=('hpp',))
            st.markdown("<p style='text-align: center; color: gray;'>Alat manajemen harga pokok penjualan untuk mengelola margin keuntungan produksi bisnis manufaktur/UMKM.</p>", unsafe_allow_html=True)
            
    elif st.session_state['page'] == 'trading':
        menu_trading()
    elif st.session_state['page'] == 'hpp':
        menu_hpp()
