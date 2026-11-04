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
        padding: 6px 15px; margin: 5px 5px 5px 0; font-size: 12px; font-weight: 600; color: #e0e0e0;
    }
    
    div[data-testid="stDownloadButton"] button {
        border-radius: 6px !important; border: 1px solid #00d2ff !important; color: #00d2ff !important;
        background-color: transparent !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100%;
    }
    div[data-testid="stDownloadButton"] button:hover { background-color: #00d2ff !important; color: black !important; }
    
    div[data-testid="stLinkButton"] button { border-radius: 6px !important; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# === BAGIAN HERO (PROFIL UTAMA) ===
st.markdown("<br>", unsafe_allow_html=True)
col_kiri, col_kanan = st.columns([1.2, 2.5], gap="large")

with col_kiri:
    path_foto = "assets/foto_dava.jpg" 
    b64_foto = image_to_base64(path_foto)
    
    if b64_foto:
        st.markdown(f"""<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;"><img src="data:image/png;base64,{b64_foto}" style="width: 100%; max-width: 250px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); border: 2px solid #333;"></div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:250px; background:#222; border-radius:15px; border: 2px dashed #444; display:flex; align-items:center; justify-content:center; color:gray; margin-bottom:20px;'>[Foto Profil]</div>", unsafe_allow_html=True)
    
    # Sosmed Link
    col_s1, col_s2 = st.columns(2)
    with col_s1: st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username_kamu")
    with col_s2: st.link_button("🐙 GitHub", "https://github.com/username_kamu")
    st.link_button("📧 Email: daryadarendra@gmail.com", "mailto:daryadarendra@gmail.com")
    
    st.markdown("<hr style='border-color: #333;'>", unsafe_allow_html=True)
    
    # DROPDOWN DOWNLOAD CV
    st.markdown("<div style='font-weight: 600; color: white; margin-bottom: 10px; font-size: 14px;'>📥 Unduh Curriculum Vitae (CV)</div>", unsafe_allow_html=True)
    
    pilihan_cv = {
        "CV Umum / General": "CV_Umum_Dava_Arya.pdf",
        "CV Data Science & AI": "CV_Data Science_Dava Arya Danendra.pdf",
        "CV Instrumentasi Geofisika": "CV_Instrumentasi_Dava Arya Danendra.pdf",
        "CV IoT & Hardware": "CV_IoT_Dava Arya Danendra.pdf",
        "CV Operasional & Manajemen": "CV_Operasional_Dava Arya Danendra.pdf",
        "CV Sampling & Akuisisi Lapangan": "CV_Sampling_Dava Arya Danendra.pdf"
    }
    
    cv_terpilih = st.selectbox("Pilih spesialisasi CV:", list(pilihan_cv.keys()), label_visibility="collapsed")
    nama_file_cv = pilihan_cv[cv_terpilih]
    path_file_cv = os.path.join("assets", "CV", nama_file_cv)
    
    try:
        with open(path_file_cv, "rb") as pdf_file:
            PDFbyte = pdf_file.read()
        st.download_button(label=f"Unduh {cv_terpilih}", data=PDFbyte, file_name=nama_file_cv, mime='application/octet-stream')
    except FileNotFoundError:
        st.error(f"File {nama_file_cv} belum tersedia di folder assets/CV/")

with col_kanan:
    st.markdown("""
    <div class="hero-title">Dava Arya Danendra</div>
    <div class="hero-subtitle">S.Si. Fisika | Data Science, AI & Instrumentation</div>
    <div class="hero-text">
        Lulusan Fisika Universitas Negeri Semarang (IPK 3.44) dengan spesialisasi pada pemodelan numerik, pengembangan kecerdasan buatan (AI), serta kalibrasi instrumentasi geofisika. Memiliki rekam jejak dalam <i>fine-tuning</i> model <i>Deep Learning</i> (IndoBERT), pemodelan data spasial dengan Logika Fuzzy, hingga akuisisi data perangkat keras lapangan (IoT). Berkomitmen mengubah data mentah menjadi metrik dan visualisasi interaktif yang akurat guna mendukung inovasi perusahaan.
    </div>
    """, unsafe_allow_html=True)
    
    # Core Skills
    st.markdown("<div class='section-title' style='margin-top: 20px;'>Kemampuan Inti</div>", unsafe_allow_html=True)
    
    st.markdown("<b>Komputasi & Data Analytics</b>", unsafe_allow_html=True)
    st.markdown("""<span class="skill-tag">Python & MATLAB</span><span class="skill-tag">Deep Learning (NLP)</span><span class="skill-tag">Logika Fuzzy</span><span class="skill-tag">Pemodelan Numerik</span>""", unsafe_allow_html=True)
    
    st.markdown("<br><b>Instrumentasi & Hardware</b>", unsafe_allow_html=True)
    st.markdown("""<span class="skill-tag">Kalibrasi Alat Ukur</span><span class="skill-tag">Akuisisi Data Lapangan</span><span class="skill-tag">Elektronika (C++, Arduino, Modbus)</span><span class="skill-tag">K3 Lab. Lingkungan</span>""", unsafe_allow_html=True)
    
    st.markdown("<br><b>Manajemen & Strategi</b>", unsafe_allow_html=True)
    st.markdown("""<span class="skill-tag">Manajemen Proyek & SDM</span><span class="skill-tag">Pemecahan Masalah Operasional</span><span class="skill-tag">Resolusi Konflik</span><span class="skill-tag">Analisis Kritis</span>""", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("Ingin melihat riwayat dan dokumentasi portofolio yang lebih detail?")
    if st.button("Lihat Rekam Jejak Selengkapnya ➔", use_container_width=True):
        st.switch_page("pages/1_Track_Record.py")

st.markdown("<br><br><hr style='border-color: #333;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2026 Dava Arya Danendra. Engineered with Streamlit.</p>", unsafe_allow_html=True)