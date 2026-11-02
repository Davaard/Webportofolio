import streamlit as st
import os
import base64

# Konfigurasi Halaman 
st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="👨‍💻", layout="wide", initial_sidebar_state="expanded")

def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# === STYLING CSS (GAYA KLASIK & ELEGAN) ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    
    .hero-title {
        font-weight: 800;
        font-size: 42px;
        color: white;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-weight: 600;
        font-size: 20px;
        color: #00d2ff;
        margin-bottom: 20px;
    }
    
    .hero-text {
        font-weight: 400;
        font-size: 15px;
        color: #d1d1d1;
        line-height: 1.7;
        text-align: justify;
        margin-bottom: 15px;
    }
    
    .section-title {
        font-weight: 700;
        font-size: 24px;
        color: white;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }
    
    .timeline-title {
        font-weight: 700;
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 2px;
    }
    
    .timeline-subtitle {
        font-weight: 600;
        font-size: 14px;
        color: #d4af37;
        margin-bottom: 10px;
    }
    
    .skill-tag {
        display: inline-block;
        background-color: #2a2a35;
        border: 1px solid #444;
        border-radius: 20px;
        padding: 6px 15px;
        margin: 5px 5px 5px 0;
        font-size: 12px;
        font-weight: 600;
        color: #e0e0e0;
    }
    
    /* Modifikasi tombol detail agar terlihat elegan */
    div[data-testid="stButton"] button {
        border-radius: 6px !important;
        border: 1px solid #00d2ff !important;
        color: #00d2ff !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #00d2ff !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# === BAGIAN HERO (PROFIL UTAMA) ===
st.markdown("<br>", unsafe_allow_html=True)
col_foto, col_intro = st.columns([1, 2.5])

with col_foto:
    path_foto = "assets/foto_dava.png" 
    b64_foto = image_to_base64(path_foto)
    
    if b64_foto:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <img src="data:image/png;base64,{b64_foto}" style="width: 100%; max-width: 280px; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); border: 2px solid #333;">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 280px; background: #222; border-radius: 15px; border: 2px dashed #444;">
            <span style="color: gray;">[Masukkan Foto Profil di sini]</span>
        </div>
        """, unsafe_allow_html=True)

with col_intro:
    st.markdown("""
    <div class="hero-title">Dava Arya Danendra</div>
    <div class="hero-subtitle">S.Si. Fisika | Data Science, AI & Instrumentation</div>
    <div class="hero-text">
        Lulusan Fisika Universitas Negeri Semarang (IPK 3.44) dengan spesialisasi pada pemodelan numerik, pengembangan kecerdasan buatan (AI), serta kalibrasi instrumentasi geofisika. Memiliki rekam jejak dalam <i>fine-tuning</i> model <i>Deep Learning</i> (IndoBERT), pemodelan data spasial dengan Logika Fuzzy, hingga akuisisi data perangkat keras lapangan (IoT). Berkomitmen mengubah data mentah menjadi metrik dan visualisasi interaktif yang akurat guna mendukung inovasi perusahaan.
    </div>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 3])
    with col_btn1: st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username_kamu", use_container_width=True)
    with col_btn2: st.link_button("🐙 GitHub", "https://github.com/username_kamu", use_container_width=True)
    with col_btn3: st.link_button("📧 Email", "mailto:daryadarendra@gmail.com", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# === TABS RINGKASAN REKAM JEJAK ===
tab_pengalaman, tab_pendidikan, tab_projek, tab_keahlian = st.tabs([
    "💼 Pengalaman Profesional", 
    "🎓 Pendidikan", 
    "🚀 Pencapaian & Inovasi", 
    "🛠️ Kemampuan Inti"
])

# --- TAB 1: PENGALAMAN ---
with tab_pengalaman:
    st.markdown("<div class='section-title'>Pengalaman Kerja & Organisasi</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Staf Magang Instrumentasi dan Kalibrasi Geofisika</div>
    <div class="timeline-subtitle">BMKG Pusat, Deputi Bidang Infrastruktur MKG | Feb 2025 – Jun 2025</div>
    <div class="hero-text">
        Mendiagnosis <i>downtime server</i> jarak jauh, memelihara perangkat keras lapangan (Digitizer, Panel Surya), serta mengeksekusi kalibrasi sensor gempa (Seismometer & Accelerometer).
    </div>
    """, unsafe_allow_html=True)
    if st.button("Lihat Log Kalibrasi & Dokumentasi BMKG ➔", key="btn_bmkg"):
        st.switch_page("pages/1_Track_Record.py")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Wakil Gubernur</div>
    <div class="timeline-subtitle">BEM FMIPA UNNES | Feb 2025 – Feb 2026</div>
    <div class="hero-text">
        Mengelola manajemen SDM 125 anggota dalam mengeksekusi 9 program kerja strategis, mengevaluasi KPI departemen, serta bertindak sebagai <i>problem solver</i> utama organisasi.
    </div>
    """, unsafe_allow_html=True)
    if st.button("Lihat Metrik & Kinerja Organisasi ➔", key="btn_bem"):
        st.switch_page("pages/1_Track_Record.py")

# --- TAB 2: PENDIDIKAN ---
with tab_pendidikan:
    st.markdown("<div class='section-title'>Riwayat Pendidikan</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Universitas Negeri Semarang (UNNES)</div>
    <div class="timeline-subtitle">S1 - Fisika | 2022 – 2026</div>
    <div class="hero-text">
        <b>IPK: 3.44</b><br>
        Berfokus pada pemodelan numerik (Python, MATLAB), pengembangan kecerdasan buatan, sistem instrumentasi, dan kalibrasi sensor geofisika. Aktif dalam riset akademik dan pendanaan nasional.
    </div>
    """, unsafe_allow_html=True)

# --- TAB 3: PENCAPAIAN & INOVASI ---
with tab_projek:
    st.markdown("<div class='section-title'>Sorotan Pencapaian</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Pengembang Aplikasi AI: IndoBERT Emotion Classifier Web App</div>
    <div class="hero-text">Membangun aplikasi web klasifikasi emosi teks berbasis arsitektur IndoBERT dan Gradio dengan evaluasi performa F1-Score mencapai <b>0.89</b>.</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Presenter Kongres Ilmuwan Muda Indonesia / KIMI V (2026)</div>
    <div class="hero-text">Mempresentasikan riset rancang bangun model numerik prediksi cuaca pesisir berbasis Logika Fuzzy Mamdani.</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Penerima Pendanaan DPA LPPM UNNES Tahun (2025)</div>
    <div class="hero-text">Hibah riset inventarisasi emisi gas rumah kaca yang menghasilkan luaran tersertifikasi Hak Cipta resmi Kemenkumham RI.</div>
    """, unsafe_allow_html=True)
    
    if st.button("Lihat Detail & Repositori Proyek ➔", key="btn_projek"):
        st.switch_page("pages/1_Track_Record.py")

# --- TAB 4: KEMAMPUAN ---
with tab_keahlian:
    st.markdown("<div class='section-title'>Kemampuan Teknis & Non-Teknis</div>", unsafe_allow_html=True)
    
    col_tech, col_non = st.columns(2)
    with col_tech:
        st.markdown("<b>Komputasi & Data</b>", unsafe_allow_html=True)
        st.markdown("""
        <span class="skill-tag">Python & MATLAB</span>
        <span class="skill-tag">Deep Learning (IndoBERT)</span>
        <span class="skill-tag">Logika Fuzzy</span>
        <span class="skill-tag">Pemodelan Numerik</span>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><b>Instrumentasi & Hardware</b>", unsafe_allow_html=True)
        st.markdown("""
        <span class="skill-tag">Kalibrasi Alat Ukur</span>
        <span class="skill-tag">Akuisisi Data Lapangan</span>
        <span class="skill-tag">Elektronika (C++, Arduino, Modbus)</span>
        <span class="skill-tag">K3 Lab. Lingkungan</span>
        """, unsafe_allow_html=True)
        
    with col_non:
        st.markdown("<b>Manajemen & Profesional</b>", unsafe_allow_html=True)
        st.markdown("""
        <span class="skill-tag">Manajemen Proyek & SDM</span>
        <span class="skill-tag">Pemecahan Masalah Operasional</span>
        <span class="skill-tag">Resolusi Konflik</span>
        <span class="skill-tag">Analisis Kritis</span>
        <span class="skill-tag">Komunikasi Efektif</span>
        """, unsafe_allow_html=True)

st.markdown("<br><br><hr style='border-color: #333;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2026 Dava Arya Danendra. Engineered with Streamlit.</p>", unsafe_allow_html=True)