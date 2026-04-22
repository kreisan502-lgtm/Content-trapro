import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta

def menu_trading():
    st.header("📊 Advanced AI Trading Analyzer")
    st.write("Analisis teknikal komprehensif dengan indikator profesional.")
    
    # Pengaturan Parameter Input
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker_symbol = st.text_input("Kode Saham", value="LPKR.JK")
    with col2:
        timeframe = st.selectbox("Rentang Waktu", ["1mo", "3mo", "6mo", "1y"], index=1)
    with col3:
        interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    
    if st.button("Jalankan Analisis Canggih"):
        try:
            with st.spinner("Memproses data pasar dan menghitung indikator..."):
                # 1. Mengambil Data
                ticker_data = yf.Ticker(ticker_symbol)
                df = ticker_data.history(period=timeframe, interval=interval)
                
                if df.empty:
                    st.error("Data tidak ditemukan. Pastikan kode saham benar.")
                    return
                
                # 2. Menghitung Indikator Teknikal Otomatis (menggunakan pandas_ta)
                df.ta.macd(append=True)
                df.ta.rsi(length=14, append=True)
                df.ta.bbands(append=True)
                
                # 3. Menampilkan Harga Saat Ini
                st.subheader(f"Dashboard {ticker_symbol.upper()}")
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                price_change = current_price - prev_price
                pct_change = (price_change / prev_price) * 100
                
                st.metric("Harga Penutupan Terakhir", f"Rp {current_price:,.0f}", f"Rp {price_change:,.0f} ({pct_change:.2f}%)")
                
                # 4. Membuat Grafik Candlestick Interaktif dengan Plotly
                fig = go.Figure(data=[go.Candlestick(x=df.index,
                                open=df['Open'],
                                high=df['High'],
                                low=df['Low'],
                                close=df['Close'],
                                name='Candlestick')])
                fig.update_layout(title='Grafik Candlestick', xaxis_rangeslider_visible=False, height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # 5. Panel Indikator Teknikal
                st.subheader("Indikator Sinyal Trading")
                col_ind1, col_ind2, col_ind3 = st.columns(3)
                
                with col_ind1:
                    rsi_val = df['RSI_14'].iloc[-1]
                    st.metric("RSI (14 Hari)", f"{rsi_val:.2f}")
                    if rsi_val > 70: st.error("Status: Overbought (Jenuh Beli - Rawan Koreksi)")
                    elif rsi_val < 30: st.success("Status: Oversold (Jenuh Jual - Potensi Rebound)")
                    else: st.info("Status: Netral")
                    
                with col_ind2:
                    # MACD_12_26_9 adalah default kolom dari pandas_ta
                    macd_val = df['MACD_12_26_9'].iloc[-1]
                    signal_val = df['MACDs_12_26_9'].iloc[-1]
                    st.metric("MACD", f"{macd_val:.2f}")
                    if macd_val > signal_val: st.success("Tren: Bullish Crossover (Momentum Naik)")
                    else: st.error("Tren: Bearish (Momentum Turun)")
                    
                with col_ind3:
                    bb_upper = df['BBU_5_2.0'].iloc[-1]
                    bb_lower = df['BBL_5_2.0'].iloc[-1]
                    st.metric("Rentang Bollinger", f"Rp {bb_lower:,.0f} - {bb_upper:,.0f}")
                    st.caption("Area Support & Resisten Volatilitas")

                # 6. Simulasi Keputusan AI
                st.markdown("---")
                st.subheader("🤖 Analisis Sinyal AI")
                rekomendasi = "HOLD / PANTAU"
                if rsi_val < 30 and macd_val > signal_val:
                    rekomendasi = "STRONG BUY (Sinyal Beli Kuat)"
                elif rsi_val > 70 or macd_val < signal_val:
                    rekomendasi = "TAKE PROFIT / SELL (Waspada Penurunan)"
                
                st.info(f"Berdasarkan algoritma teknikal jangka pendek, harga saat ini berada pada tren **{'Bullish' if macd_val > signal_val else 'Bearish'}** dengan tingkat RSI {rsi_val:.1f}. \n\n**Rekomendasi Sistem:** {rekomendasi}")

        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")
            
