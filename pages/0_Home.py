import streamlit as st
import os
import base64

# Konfigurasi Halaman 
st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="👨‍💻", layout="wide", initial_sidebar_state="expanded")

def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# === STYLING CSS ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    
    .hero-title { font-weight: 800; font-size: 42px; color: white; margin-bottom: 5px; line-height: 1.2; }
    .hero-subtitle { font-weight: 600; font-size: 18px; color: #00d2ff; margin-bottom: 20px; }
    .hero-text { font-weight: 400; font-size: 15px; color: #d1d1d1; line-height: 1.7; text-align: justify; margin-bottom: 15px; }
    
    .section-title { font-weight: 700; font-size: 22px; color: white; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #333; padding-bottom: 10px; }
    
    .skill-tag {
        display: inline-block; background-color: #2a2a35; border: 1px solid #444; border-radius: 20px;
        padding: 6px 15px; margin: 5px 8px 5px 0; font-size: 13px; font-weight: 600; color: #e0e0e0;
    }
    
    div[data-testid="stDownloadButton"] button {
        border-radius: 6px !important; border: 1px solid #00d2ff !important; color: #00d2ff !important;
        background-color: transparent !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100%;
    }
    div[data-testid="stDownloadButton"] button:hover { background-color: #00d2ff !important; color: black !important; }
    
    div[data-testid="stLinkButton"] button { border-radius: 6px !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# === BARIS 1: FOTO (KIRI) & RESUME (KANAN) ===
col_foto, col_intro = st.columns([0.9, 2.5], gap="large")

with col_foto:
    path_foto = "assets/Profile/foto_dava.jpg" 
    b64_foto = image_to_base64(path_foto)
    
    if b64_foto:
        st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <img src="data:image/png;base64,{b64_foto}" style="width: 100%; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.6); border: 2px solid #333; display: block;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='aspect-ratio: 3/4; width:100%; background:#222; border-radius:15px; border: 2px dashed #444; display:flex; align-items:center; justify-content:center; color:gray; margin-bottom:10px;'>[Foto Profil]</div>", unsafe_allow_html=True)

with col_intro:
    st.markdown("""
    <div class="hero-title">Dava Arya Danendra</div>
    <div class="hero-subtitle">S.Si. Fisika | Data Science, Computational Physics & Instrumentation</div>
    <div class="hero-text">
        Lulusan Fisika Universitas Negeri Semarang (UNNES) yang memiliki minat besar pada pengembangan Internet of Things (IoT) dan otomasi data. Terampil merancang sistem berbasis mikrokontroler (terkhusus ESP32) menggunakan bahasa pemrograman C++ melalui Arduino IDE untuk pembacaan sensor lingkungan, serta mengintegrasikan perangkat keras tersebut ke sistem pemantauan industri seperti SCADA menggunakan protokol Modbus RTU atau TCP-IP. Memiliki pengalaman berharga selama 5 bulan magang di BMKG untuk terjun langsung membantu pemeliharaan jaringan telemetri dan perangkat instrumentasi lapangan. Mampu menulis script pemrograman menggunakan Python, MATLAB, dan Google Apps Script untuk kebutuhan pemodelan numerik yang juga diterapkan dalam penyelesaian tugas akhir, maupun otomasi pengarsipan data, serta memiliki pemahaman dasar mengenai visualisasi data dan UI/UX. Pembelajar yang adaptif dan selalu antusias untuk memecahkan masalah teknis, baik pada sistem keras maupun logika perangkat lunak..
    </div>
    """, unsafe_allow_html=True)

# === BARIS 2: SOSIAL MEDIA (UJUNG KANAN) ===
# Memperbesar pendorong spasi (rasio 6.5) dan merapatkan celah antar tombol dengan gap="small"
col_space, col_li, col_gh, col_em = st.columns([6.5, 1, 1, 1.2], gap="small")

with col_li: 
    st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username_kamu", use_container_width=True)
with col_gh: 
    st.link_button("🐙 GitHub", "https://github.com/username_kamu", use_container_width=True)
with col_em: 
    st.link_button("📧 Email", "mailto:daryadarendra@gmail.com", use_container_width=True)

# === BARIS 3: KEMAMPUAN INTI (FULL 1 KOLOM) ===
st.markdown("<div class='section-title' style='margin-top: 0px;'>Kemampuan Inti</div>", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 15px;">
    <b>Komputasi & Data Analytics</b><br>
    <span class="skill-tag">Python & MATLAB</span><span class="skill-tag">Data Visualization (Plotly)</span><span class="skill-tag">Machine Learning Terapan</span><span class="skill-tag">Pemodelan Numerik</span>
</div>
<div style="margin-bottom: 15px;">
    <b>Instrumentasi & Hardware</b><br>
    <span class="skill-tag">Kalibrasi Alat Ukur</span><span class="skill-tag">Akuisisi Data Lapangan</span><span class="skill-tag">Elektronika (C++, Arduino, Modbus)</span><span class="skill-tag">K3 Lab. Lingkungan</span>
</div>
<div style="margin-bottom: 10px;">
    <b>Manajemen & Strategi</b><br>
    <span class="skill-tag">Manajemen Proyek & SDM</span><span class="skill-tag">Pemecahan Masalah Operasional</span><span class="skill-tag">Resolusi Konflik</span><span class="skill-tag">Analisis Kritis</span>
</div>
""", unsafe_allow_html=True)

# === BARIS 4: UNDUH CV ===
st.markdown("<div class='section-title'>📥 Unduh Curriculum Vitae (CV)</div>", unsafe_allow_html=True)
st.markdown("<p style='color: gray; font-size: 14px;'>Pilih spesialisasi CV yang relevan sebelum mengunduh dokumen:</p>", unsafe_allow_html=True)

# Membuat tata letak sejajar untuk dropdown dan tombol
col_cv_drop, col_cv_btn, col_cv_space = st.columns([2.5, 1.5, 3])

pilihan_cv = {
    "CV Umum / General": "CV_Umum_Dava_Arya.pdf",
    "CV Data Science & Analyst": "CV_Data Science_Dava Arya Danendra.pdf",
    "CV Instrumentasi Geofisika": "CV_Instrumentasi_Dava Arya Danendra.pdf",
    "CV IoT & Hardware": "CV_IoT_Dava Arya Danendra.pdf",
    "CV Operasional & Manajemen": "CV_Operasional_Dava Arya Danendra.pdf",
    "CV Sampling & Akuisisi Lapangan": "CV_Sampling_Dava Arya Danendra.pdf"
}

with col_cv_drop:
    cv_terpilih = st.selectbox("Pilih spesialisasi CV:", list(pilihan_cv.keys()), label_visibility="collapsed")
    nama_file_cv = pilihan_cv[cv_terpilih]
    path_file_cv = os.path.join("assets", "CV", nama_file_cv)

with col_cv_btn:
    try:
        with open(path_file_cv, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        st.download_button(label=f"Unduh File PDF", data=PDFbyte, file_name=nama_file_cv, mime='application/octet-stream')
    except FileNotFoundError:
        st.error("File belum tersedia")

st.markdown("<br><br><hr style='border-color: #333;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2026 Dava Arya Danendra. Engineered with Streamlit.</p>", unsafe_allow_html=True)