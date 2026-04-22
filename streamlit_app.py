import streamlit as st
import yt_dlp
import os
import time
from moviepy.video.io.VideoFileClip import VideoFileClip

# --- KONFIGURASI HALAMAN & CSS ---
st.set_page_config(page_title="AutoClip AI | Viral Shorts", page_icon="✂️", layout="wide")

st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ff3333;
    }
    .result-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNGSI BACKEND UTAMA ---
def download_youtube_video(url, output_filename="raw_video.mp4"):
    """Mengunduh video dari YouTube dalam format terbaik yang tersedia."""
    if os.path.exists(output_filename):
        os.remove(output_filename) # Hapus file lama jika ada
        
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_filename
    except Exception as e:
        raise Exception(f"Gagal mengunduh video: {e}")

def process_video_vertical(input_path, output_path="viral_clip.mp4", start_t=30, end_t=60):
    """Memotong video dan mengubah dimensinya menjadi vertikal (9:16)."""
    if os.path.exists(output_path):
        os.remove(output_path)
        
    try:
        with VideoFileClip(input_path) as video:
            # 1. Potong video (trim) berdasarkan detik
            clip = video.subclip(start_t, end_t)
            
            # 2. Kalkulasi rasio untuk vertikal (9:16)
            w, h = clip.size
            target_ratio = 9 / 16
            target_w = h * target_ratio
            
            # 3. Potong area tengah video (crop to center)
            x_center = w / 2
            x1 = x_center - (target_w / 2)
            x2 = x_center + (target_w / 2)
            
            # Eksekusi pemotongan ruang & resize agar standar HD
            clip_resized = clip.crop(x1=x1, y1=0, x2=x2, y2=h).resize(height=1920, width=1080)
            
            # 4. Render hasil akhir (Bisa memakan waktu tergantung CPU)
            clip_resized.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                preset="ultrafast", # Gunakan ultrafast agar proses di Streamlit tidak timeout
                logger=None
            )
        return output_path
    except Exception as e:
        raise Exception(f"Gagal memproses video: {e}")


# --- ANTARMUKA PENGGUNA (UI) ---
with st.sidebar:
    st.header("⚙️ Pengaturan Mesin")
    openai_key = st.text_input("OpenAI API Key (Tahap Selanjutnya)", type="password")
    target_start = st.number_input("Mulai Potong di Detik ke-", min_value=0, value=30)
    target_end = st.number_input("Selesai di Detik ke-", min_value=10, value=45)
    st.caption("Catatan: Di versi full, detik ini akan ditentukan otomatis oleh AI.")

st.title("✂️ AutoClip AI Engine")
st.markdown("Mesin pemotong video otomatis menjadi format vertikal.")
st.markdown("---")

col_input, col_button = st.columns([4, 1])

with col_input:
    youtube_url = st.text_input("Tautan YouTube", placeholder="Masukkan link YouTube...", label_visibility="collapsed")

with col_button:
    generate_btn = st.button("🚀 Eksekusi Video")

# --- LOGIKA EKSEKUSI (SAAT TOMBOL DITEKAN) ---
if generate_btn:
    if not youtube_url:
        st.error("Masukkan tautan terlebih dahulu.")
    else:
        with st.status("Memproses Video... (Ini akan memakan waktu)", expanded=True) as status:
            try:
                # Langkah 1: Unduh
                st.write("📥 Menghubungkan ke YouTube dan mengunduh video...")
                raw_vid_path = download_youtube_video(youtube_url)
                st.write("✅ Unduhan selesai!")
                
                # Langkah 2: Proses & Potong
                st.write(f"✂️ Memotong video dari detik {target_start} ke {target_end} & mengubah ke rasio vertikal...")
                final_vid_path = process_video_vertical(raw_vid_path, start_t=target_start, end_t=target_end)
                st.write("✅ Rendering selesai!")
                
                status.update(label="Selesai! Video berhasil diproses.", state="complete", expanded=False)
                
                # Menampilkan Hasil
                st.markdown("---")
                st.subheader("🎥 Hasil Potongan Vertikal")
                
                res_col1, res_col2 = st.columns([1, 1.5])
                
                with res_col1:
                    st.video(final_vid_path)
                    
                    # Tombol Download Asli
                    with open(final_vid_path, "rb") as file:
                        btn = st.download_button(
                            label="⬇️ Unduh Video Vertikal (.mp4)",
                            data=file,
                            file_name="auto_viral_clip.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                with res_col2:
                    st.success("Logika inti berhasil dieksekusi!")
                    st.markdown("""
                    **Apa yang terjadi di balik layar?**
                    1. `yt-dlp` berhasil menembus proteksi YouTube dan mengambil file mentah.
                    2. `moviepy` secara akurat menghitung titik tengah video.
                    3. Video di-*crop* membuang sisi kiri-kanan, dan di-*resize* ke resolusi standar sosial media (1080x1920).
                    """)
                    
                    # Pembersihan memori file mentah agar server tidak penuh
                    if os.path.exists(raw_vid_path):
                        os.remove(raw_vid_path)
                        
            except Exception as error_msg:
                status.update(label="Terjadi Kesalahan", state="error")
                st.error(error_msg)
