import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Konfigurasi Halaman & CSS Kustom
st.set_page_config(page_title="BizInvest Suite", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Sistem Login Sederhana (Untuk SaaS Gated Access)
def check_password():
    """Mengembalikan `True` jika pengguna memasukkan password yang benar."""
    def password_entered():
        if st.session_state["password"] == "AksesPremium123": # Password ini yang akan dijual di LYNK
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Hapus password dari memory
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        st.error("Password salah. Silakan beli akses di Lynk.id/usernamekamu")
        return False
    return True

# 3. Modul Kalkulator HPP (Fokus Manufaktur)
def menu_hpp():
    st.header("📦 Kalkulator HPP Produksi")
    st.write("Hitung Harga Pokok Penjualan untuk produksi manufaktur dengan presisi.")
    
    col1, col2 = st.columns(2)
    with col1:
        bahan_baku = st.number_input("Total Biaya Bahan Baku (Rp)", min_value=0, value=1500000)
        tenaga_kerja = st.number_input("Total Biaya Tenaga Kerja (Rp)", min_value=0, value=500000)
        overhead = st.number_input("Biaya Overhead / Operasional (Rp)", min_value=0, value=200000)
        
    with col2:
        jumlah_produksi = st.number_input("Target Jumlah Produksi (Unit/Pcs)", min_value=1, value=100)
        margin = st.slider("Target Margin Keuntungan (%)", min_value=0, max_value=100, value=30)
        
    if st.button("Hitung HPP & Harga Jual"):
        total_biaya = bahan_baku + tenaga_kerja + overhead
        hpp_per_unit = total_biaya / jumlah_produksi
        harga_jual = hpp_per_unit + (hpp_per_unit * (margin / 100))
        
        st.success("✅ Kalkulasi Selesai")
        st.metric(label="HPP per Unit", value=f"Rp {hpp_per_unit:,.0f}")
        st.metric(label="Rekomendasi Harga Jual", value=f"Rp {harga_jual:,.0f}")

# 4. Modul Analisis Trading AI
def menu_trading():
    st.header("📈 AI Trading Analyzer")
    st.write("Analisis teknikal cepat untuk pasar saham.")
    
    ticker_symbol = st.text_input("Masukkan Kode Saham (Contoh: LPKR.JK)", value="LPKR.JK")
    
    if st.button("Analisis Sekarang"):
        try:
            # Mengambil data 1 bulan terakhir
            ticker_data = yf.Ticker(ticker_symbol)
            df = ticker_data.history(period="1mo")
            
            st.subheader(f"Pergerakan Harga {ticker_symbol} (1 Bulan Terakhir)")
            st.line_chart(df['Close'])
            
            # Simulasi Kesimpulan AI (Nantinya bisa disambung ke API OpenAI/Gemini)
            harga_terakhir = df['Close'].iloc[-1]
            st.info(f"💡 **Ringkasan AI:** Harga penutupan terakhir adalah Rp {harga_terakhir:,.0f}. Berdasarkan tren volume dan harga historis satu bulan ini, momentum pergerakan sedang diuji di titik *support* terdekat.")
        except Exception as e:
            st.error("Gagal mengambil data saham. Pastikan format kode benar.")

# 5. Navigasi Utama Aplikasi
if check_password():
    st.sidebar.title("Navigasi Suite")
    pilihan = st.sidebar.radio("Pilih Alat:", ["Kalkulator HPP", "AI Trading Analyzer"])
    
    if pilihan == "Kalkulator HPP":
        menu_hpp()
    elif pilihan == "AI Trading Analyzer":
        menu_trading()
        
