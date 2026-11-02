import streamlit as st
import os
import base64

st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="👨‍💻", layout="wide", initial_sidebar_state="collapsed")

def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# === STYLING CSS (CYBER-SCIENCE THEME) ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Montserrat:wght@300;400;600;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    
    .hero-name {
        font-weight: 900; font-size: 55px; line-height: 1.1; margin-bottom: 10px;
        background: linear-gradient(90deg, #ffffff, #00e6e6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    .hero-title {
        font-family: 'Fira Code', monospace; font-weight: 600; font-size: 20px; color: #a78bfa; margin-bottom: 25px;
    }
    
    .hero-desc { font-weight: 400; font-size: 16px; color: #d1d1d1; line-height: 1.8; text-align: justify; margin-bottom: 30px; }
    
    .section-header {
        font-family: 'Fira Code', monospace; font-weight: 700; font-size: 22px; color: #00e6e6; 
        margin-top: 40px; margin-bottom: 20px; border-bottom: 1px solid rgba(0, 230, 230, 0.3); padding-bottom: 10px;
    }
    
    .timeline-container { border-left: 2px solid #333; padding-left: 25px; position: relative; margin-bottom: 30px; }
    .timeline-container::before {
        content: ''; position: absolute; left: -7px; top: 5px; width: 12px; height: 12px; 
        background-color: #00e6e6; border-radius: 50%; box-shadow: 0 0 10px #00e6e6;
    }
    
    .tl-title { font-weight: 800; font-size: 18px; color: white; margin-bottom: 5px; }
    .tl-subtitle { font-family: 'Fira Code', monospace; font-weight: 600; font-size: 13px; color: #a78bfa; margin-bottom: 15px; }
    .tl-content { font-weight: 400; font-size: 14.5px; color: #c4c4c4; line-height: 1.7; text-align: justify; }
    
    .glass-tag {
        display: inline-block; background: rgba(0, 230, 230, 0.05); border: 1px solid rgba(0, 230, 230, 0.2); 
        border-radius: 4px; padding: 6px 14px; margin: 4px 6px 4px 0; font-family: 'Fira Code', monospace; 
        font-size: 12px; font-weight: 600; color: #00e6e6;
    }
    </style>
""", unsafe_allow_html=True)

# Navigasi Utama menggunakan Tabs besar
tab_home, tab_cv = st.tabs(["🏠 BERANDA UTAMA", "📜 REKAM JEJAK (CV)"])

# =====================================================================
# TAB 1: BERANDA (ELEVATOR PITCH)
# =====================================================================
with tab_home:
    st.markdown("<br>", unsafe_allow_html=True)
    col_img, col_text = st.columns([1, 2.2])
    
    with col_img:
        # Ganti dengan path fotomu
        b64_foto = image_to_base64("assets/foto_dava.png")
        if b64_foto:
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: flex-start; padding-top: 10px;">
                <div style="position: relative; padding: 4px; background: linear-gradient(135deg, #00e6e6, #a78bfa); border-radius: 20px; box-shadow: 0 10px 30px rgba(0,230,230,0.2);">
                    <img src="data:image/png;base64,{b64_foto}" style="width: 100%; max-width: 320px; border-radius: 16px; display: block;">
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:300px; background:#222; border-radius:15px; display:flex; align-items:center; justify-content:center; color:gray;'>[Foto Profil]</div>", unsafe_allow_html=True)
            
    with col_text:
        st.markdown("""
        <div class="hero-name">Dava Arya Danendra</div>
        <div class="hero-title">> Fisikawan Komputasi & Pengembang AI</div>
        <div class="hero-desc">
            Lulusan Fisika Universitas Negeri Semarang (IPK 3.44) yang berfokus pada integrasi sains numerik, analisis data, dan kecerdasan buatan. 
            Mampu menjembatani kompleksitas perangkat keras (instrumentasi IoT/sensor) hingga pengembangan model komputasi tingkat tinggi 
            seperti <i>fine-tuning Deep Learning</i> (NLP) dan pemodelan prediktif berbasis <i>Fuzzy Logic</i>. Terbiasa mengorkestrasi alur data mentah 
            menjadi wawasan strategis interaktif yang berdampak langsung pada efisiensi sistem dan pengambilan keputusan.
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Highlight / Top Skills
        st.markdown("<div>", unsafe_allow_html=True)
        st.markdown("""
        <span class="glass-tag">Python & MATLAB</span>
        <span class="glass-tag">Deep Learning (NLP)</span>
        <span class="glass-tag">Data Visualization</span>
        <span class="glass-tag">C++ & Arduino (IoT)</span>
        <span class="glass-tag">Numerical Modeling</span>
        """, unsafe_allow_html=True)
        st.markdown("</div><br><br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1.2, 2])
        with col_btn1: st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username", use_container_width=True)
        with col_btn2: st.link_button("🐙 GitHub", "https://github.com/username", use_container_width=True)
        with col_btn3: st.link_button("📧 daryadarendra@gmail.com", "mailto:daryadarendra@gmail.com", use_container_width=True)

# =====================================================================
# TAB 2: REKAM JEJAK (CURRICULUM VITAE)
# =====================================================================
with tab_cv:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Membagi layout menjadi 2 kolom utama agar terlihat seperti CV profesional
    col_kiri, col_kanan = st.columns([1.8, 1.2], gap="large")
    
    with col_kiri:
        # --- PENGALAMAN PROFESIONAL ---
        st.markdown("<div class='section-header'>// PENGALAMAN PROFESIONAL</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-container">
            <div class="tl-title">Staf Magang Instrumentasi dan Kalibrasi Geofisika</div>
            <div class="tl-subtitle">BMKG Pusat, Deputi Bidang Infrastruktur MKG | Feb 2025 – Jun 2025</div>
            <div class="tl-content">
                <ul>
                    <li>Memantau transmisi data instrumen geofisika secara <i>real-time</i> dan mendiagnosis <i>downtime server</i> jarak jauh.</li>
                    <li>Melaksanakan pemeliharaan dan perbaikan fisik perangkat keras lapangan (Sensor, Digitizer, Modul GPS, Panel Surya, dan Sistem Catu Daya).</li>
                    <li>Mengeksekusi proses kalibrasi tingkat tinggi pada instrumen sensor gempa, meliputi Seismometer dan Accelerometer.</li>
                    <li>Menyusun laporan analitis dan log historis kalibrasi guna memastikan tingkat akurasi operasional instrumen teknis.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- KEPEMIMPINAN ---
        st.markdown("<div class='section-header'>// KEPEMIMPINAN & ORGANISASI</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-container">
            <div class="tl-title">Wakil Gubernur</div>
            <div class="tl-subtitle">BEM FMIPA UNNES | Feb 2025 – Feb 2026</div>
            <div class="tl-content">
                <ul>
                    <li>Merumuskan Anggaran Rumah Tangga (ART), arsitektur kabinet, dan <i>blueprint</i> program kerja strategis untuk 1 periode kepengurusan.</li>
                    <li>Mengeksekusi manajemen SDM berskala besar dengan mengorkestrasi 125 anggota pengurus ke dalam 9 program kerja melalui analisis kompetensi.</li>
                    <li>Memonitor metrik dan <i>Key Performance Indicators</i> (KPI) seluruh departemen untuk akurasi target capaian.</li>
                    <li>Menjadi fasilitator utama dalam resolusi konflik dan penyelesaian masalah guna menjamin stabilitas operasional internal.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- PENDIDIKAN ---
        st.markdown("<div class='section-header'>// PENDIDIKAN</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-container">
            <div class="tl-title">Universitas Negeri Semarang (UNNES)</div>
            <div class="tl-subtitle">Sarjana Sains (S.Si.) Fisika | 2022 – 2026</div>
            <div class="tl-content">
                <b>IPK: 3.44</b><br>
                Fokus Akademik: Pemodelan Numerik, Kecerdasan Buatan (AI), Integrasi Perangkat Keras IoT, dan Telemetri Jarak Jauh.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kanan:
        # --- PENCAPAIAN RISET & PROYEK ---
        st.markdown("<div class='section-header'>// PENCAPAIAN & INOVASI</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="timeline-container">
            <div class="tl-title">Kongres Ilmuwan Muda Indonesia (KIMI) V</div>
            <div class="tl-subtitle">Presenter Ilmiah Nasional | 2026</div>
            <div class="tl-content">Mempresentasikan riset rancang bangun model numerik prediksi cuaca pesisir yang dioptimasi menggunakan algoritma <b>Logika Fuzzy Mamdani</b>.</div>
        </div>
        
        <div class="timeline-container">
            <div class="tl-title">IndoBERT Emotion Classifier Web App</div>
            <div class="tl-subtitle">Pengembang Aplikasi AI</div>
            <div class="tl-content">Membangun arsitektur NLP untuk pemrosesan bahasa alami menggunakan model <i>Deep Learning</i> IndoBERT dan <i>framework</i> Gradio. Meraih tingkat akurasi evaluasi performa pada <b>F1-Score 0.89</b>.</div>
        </div>
        
        <div class="timeline-container">
            <div class="tl-title">Inventarisasi Emisi Gas Rumah Kaca</div>
            <div class="tl-subtitle">DPA LPPM UNNES | 2025</div>
            <div class="tl-content">Meraih pendanaan hibah riset universitas yang berhasil bermuara pada luaran tersertifikasi Hak Cipta resmi dari Kemenkumham RI.</div>
        </div>
        
        <div class="timeline-container">
            <div class="tl-title">Tsunami Ready Community</div>
            <div class="tl-subtitle">Pelaksana Program BMKG | 2025</div>
            <div class="tl-content">Mengeksekusi mitigasi bencana di Kalurahan Parangtritis dengan memetakan dan mendistribusikan penanda evakuasi di 78 titik rumah kelompok rentan.</div>
        </div>
        
        <div class="timeline-container">
            <div class="tl-title">Program Peningkatan Kapasitas Ormawa</div>
            <div class="tl-subtitle">PPK Nasional Kemdikbudristek | 2024</div>
            <div class="tl-content">Merancang 6 modul kurikulum pelatihan inovasi agrikultur untuk memacu pemberdayaan ekonomi masyarakat Desa Singosari, Boyolali.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- KEAHLIAN TEKNIS ---
        st.markdown("<div class='section-header'>// KEAHLIAN INTI</div>", unsafe_allow_html=True)
        
        st.markdown("<b>Teknis & Komputasi:</b>", unsafe_allow_html=True)
        st.markdown("""
        <span class="glass-tag">Pemodelan Numerik (Python, MATLAB)</span>
        <span class="glass-tag">Elektronika (C++, Arduino, Modbus)</span>
        <span class="glass-tag">Akuisisi Data Lapangan</span>
        <span class="glass-tag">Kalibrasi Alat Ukur</span>
        <span class="glass-tag">K3 Laboratorium Lingkungan</span>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><b>Manajemen & Strategi:</b>", unsafe_allow_html=True)
        st.markdown("""
        <span class="glass-tag">Manajemen Proyek & SDM</span>
        <span class="glass-tag">Resolusi Konflik</span>
        <span class="glass-tag">Pemecahan Masalah Operasional</span>
        <span class="glass-tag">Analisis Kritis</span>
        """, unsafe_allow_html=True)

st.markdown("<br><br><hr style='border-color: rgba(0,230,230,0.2);'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>© 2026 Dava Arya Danendra. Engineered with Streamlit.</p>", unsafe_allow_html=True)