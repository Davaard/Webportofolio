import streamlit as st
import os
import base64

# Konfigurasi Halaman (Hanya boleh dipanggil 1 kali di paling atas)
st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="👨‍💻", layout="wide", initial_sidebar_state="expanded")

# Fungsi konversi gambar ke Base64 (untuk merender UI)
def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# === STYLING CSS ===
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
        font-size: 16px;
        color: #d1d1d1;
        line-height: 1.7;
        text-align: justify;
    }
    
    .section-title {
        font-weight: 700;
        font-size: 24px;
        color: white;
        margin-top: 30px;
        margin-bottom: 15px;
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
        padding: 5px 15px;
        margin: 5px;
        font-size: 13px;
        font-weight: 600;
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# === BAGIAN HERO (PROFIL UTAMA) ===
st.markdown("<br>", unsafe_allow_html=True)
col_foto, col_intro = st.columns([1, 2.5])

with col_foto:
    # Siapkan fotomu dengan nama "foto_dava.png" di dalam folder assets
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
    <div class="hero-subtitle">S.Si. Fisika | Data Analyst & Computational Physics Enthusiast</div>
    <div class="hero-text">
        Lulusan Fisika Universitas Negeri Semarang (UNNES) yang memiliki minat mendalam pada komputasi ilmiah, analisis data, dan pengembangan aplikasi berbasis data. 
        Berpengalaman dalam menerjemahkan pemodelan matematis kompleks—mulai dari dispersi gas lingkungan hingga metrik performa <i>esports</i>—menjadi solusi <i>dashboard</i> interaktif yang mudah dipahami dan memberikan dampak nyata.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tautan Eksternal (LinkedIn, GitHub, dll)
    col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 3])
    with col_btn1:
        st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username_kamu", use_container_width=True)
    with col_btn2:
        st.link_button("🐙 GitHub", "https://github.com/username_kamu", use_container_width=True)
    with col_btn3:
        st.link_button("📧 Email", "mailto:email_kamu@gmail.com", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# === TABS CV / REKAM JEJAK ===
tab_pengalaman, tab_pendidikan, tab_projek, tab_keahlian = st.tabs([
    "💼 Pengalaman & Organisasi", 
    "🎓 Pendidikan", 
    "🚀 Sorotan Projek", 
    "🛠️ Keahlian Teknis"
])

# --- TAB 1: PENGALAMAN ---
with tab_pengalaman:
    st.markdown("<div class='section-title'>Pengalaman Riset & Profesional</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Research Intern - Pemodelan Dispersi Numerik</div>
    <div class="timeline-subtitle">Badan Meteorologi, Klimatologi, dan Geofisika (BMKG) Pusat</div>
    <ul class="hero-text">
        <li>Mengembangkan <i>pipeline</i> pemodelan dispersi numerik menggunakan Python untuk memodelkan sebaran emisi gas non-kondensabel (H2S dan CO2) dari <i>wellpad</i> panas bumi di Dieng.</li>
        <li>Menerapkan metode <i>Lagrangian Particle Tracking</i> (LPT) dan mengintegrasikannya dengan pustaka spasial seperti Rasterio, NumPy, dan Matplotlib.</li>
    </ul>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Pengalaman Kepemimpinan & Organisasi</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Wakil Gubernur BEM FMIPA UNNES</div>
    <div class="timeline-subtitle">BEM FMIPA UNNES | 2026</div>
    <ul class="hero-text">
        <li>Mengelola dan memimpin 125 anggota pengurus dalam mengeksekusi 9 program kerja strategis.</li>
        <li>Menyusun draf peraturan organisasi, mengevaluasi jalannya program, serta bertindak sebagai negosiator dalam resolusi konflik internal.</li>
    </ul>
    
    <div class="timeline-title">Kepala Sekolah Kaderisasi</div>
    <div class="timeline-subtitle">FMIPA UNNES | 2026</div>
    <ul class="hero-text">
        <li>Merancang dan mengawal kurikulum pengembangan kepemimpinan bagi mahasiswa baru FMIPA.</li>
    </ul>
    """, unsafe_allow_html=True)

# --- TAB 2: PENDIDIKAN ---
with tab_pendidikan:
    st.markdown("<div class='section-title'>Riwayat Pendidikan Akademik</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Universitas Negeri Semarang (UNNES)</div>
    <div class="timeline-subtitle">Sarjana Sains (S.Si.) - Fisika | Lulus: Agustus 2026</div>
    <ul class="hero-text">
        <li><b>Fokus Studi:</b> Fisika Komputasi, Analisis Data Spasial (GIS), dan Pemodelan Lingkungan.</li>
        <li><b>Sertifikasi Bahasa:</b> UNNES-TEP / TOEFL Prediction (Score: 580).</li>
        <li><b>Pendanaan Riset:</b> Menerima pendanaan riset kompetitif dari DPA LPPM UNNES tahun 2025.</li>
        <li><b>Publikasi/Simposium:</b> Tampil sebagai pembicara dalam presentasi riset akademik di Kongres Ilmuwan Muda Indonesia (KIMI) V, 2026.</li>
    </ul>
    """, unsafe_allow_html=True)

# --- TAB 3: PROJEK & PENGABDIAN ---
with tab_projek:
    st.markdown("<div class='section-title'>Inovasi Web & Analitik Data</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Indonesia Kings Laga (IKL) - Esports Dashboard</div>
    <div class="timeline-subtitle">Streamlit Web Application</div>
    <ul class="hero-text">
        <li>Membangun <i>dashboard</i> interaktif komprehensif untuk menganalisis statistik pertandingan <i>esports</i> Honor of Kings (HOK).</li>
        <li>Mengembangkan formula matematis khusus untuk mengukur stabilitas, dominasi, dan metrik performa tim dengan render visualisasi <i>Radar Chart</i> dan tata letak UI/UX yang responsif.</li>
    </ul>
    
    <div class="timeline-title">IndoBERT Emotion Classifier Web App</div>
    <div class="timeline-subtitle">Natural Language Processing (NLP)</div>
    <ul class="hero-text">
        <li>Merancang antarmuka klasifikasi teks multi-label berbasis kecerdasan buatan untuk membedah sentimen dan emosi pada teks berbahasa Indonesia.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Pengabdian Masyarakat</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-title">Penyusun Kurikulum Sanggar Tani Muda (PPK Ormawa 2024)</div>
    <div class="timeline-subtitle">Desa Singosari, Kab. Boyolali | Didanai oleh Belmawa Kemdikbudristek RI</div>
    <ul class="hero-text">
        <li>Merancang dan mengimplementasikan kurikulum peningkatan kapasitas bertani untuk pemuda desa.</li>
    </ul>
    
    <div class="timeline-title">Tsunami Ready Community 2025</div>
    <div class="timeline-subtitle">Kalurahan Parangtritis</div>
    <ul class="hero-text">
        <li>Melakukan pemetaan spasial dan penempatan penanda indikator prioritas evakuasi di 78 rumah warga penyandang disabilitas yang tersebar di 11 padukuhan.</li>
    </ul>
    """, unsafe_allow_html=True)

# --- TAB 4: KEAHLIAN ---
with tab_keahlian:
    st.markdown("<div class='section-title'>Core Competencies & Tools</div>", unsafe_allow_html=True)
    
    st.markdown("#### Bahasa Pemrograman & Data Science")
    st.markdown("""
    <span class="skill-tag">Python</span>
    <span class="skill-tag">MATLAB</span>
    <span class="skill-tag">Pandas</span>
    <span class="skill-tag">NumPy</span>
    <span class="skill-tag">Streamlit</span>
    <span class="skill-tag">Matplotlib</span>
    <span class="skill-tag">Jupyter Notebook</span>
    <span class="skill-tag">JSON / Data Archiving</span>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Fisika Komputasi & Pemodelan")
    st.markdown("""
    <span class="skill-tag">Numerical Dispersion Modeling</span>
    <span class="skill-tag">Lagrangian Particle Tracking (LPT)</span>
    <span class="skill-tag">GIS Analysis</span>
    <span class="skill-tag">Rasterio</span>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Hardware & Sistem Kontrol")
    st.markdown("""
    <span class="skill-tag">Haiwell SCADA</span>
    <span class="skill-tag">Modbus RTU/TCP</span>
    <span class="skill-tag">IoT Integration</span>
    <span class="skill-tag">ESP32 / Arduino</span>
    """, unsafe_allow_html=True)

st.markdown("<br><br><hr style='border-color: #333;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>© 2026 Dava Arya Danendra. Built with Streamlit.</p>", unsafe_allow_html=True)