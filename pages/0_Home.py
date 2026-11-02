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

# === STYLING CSS (TEMA DEEP TECH / CYBER-SCIENCE) ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&family=Fira+Code:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    
    .hero-title {
        font-weight: 800;
        font-size: 46px;
        background: linear-gradient(90deg, #ffffff 0%, #00e6e6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-family: 'Fira Code', monospace;
        font-weight: 500;
        font-size: 18px;
        color: #a78bfa;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
    }
    
    .hero-text {
        font-weight: 400;
        font-size: 15px;
        color: #94a3b8;
        line-height: 1.8;
        text-align: justify;
    }
    
    .section-title {
        font-weight: 800;
        font-size: 22px;
        color: white;
        margin-top: 40px;
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0, 230, 230, 0.3);
        position: relative;
    }
    
    /* Garis bawah menyala untuk Section Title */
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -1px;
        left: 0;
        width: 60px;
        height: 2px;
        background-color: #00e6e6;
        box-shadow: 0 0 10px #00e6e6;
    }
    
    /* Desain Timeline Kustom */
    .timeline-container {
        border-left: 2px solid #334155;
        padding-left: 25px;
        margin-left: 10px;
        margin-bottom: 35px;
    }
    
    .timeline-title {
        font-weight: 700;
        font-size: 18px;
        color: #f8fafc;
        position: relative;
        margin-bottom: 4px;
    }
    
    /* Titik Timeline Menyala */
    .timeline-title::before {
        content: '';
        position: absolute;
        left: -32px;
        top: 6px;
        width: 12px;
        height: 12px;
        background-color: #0e1117;
        border: 2.5px solid #00e6e6;
        border-radius: 50%;
        box-shadow: 0 0 8px rgba(0, 230, 230, 0.6);
    }
    
    .timeline-subtitle {
        font-family: 'Fira Code', monospace;
        font-weight: 400;
        font-size: 13px;
        color: #a78bfa;
        margin-bottom: 12px;
    }
    
    .timeline-content {
        font-size: 14.5px;
        color: #94a3b8;
        line-height: 1.7;
        margin-bottom: 20px;
        text-align: justify;
    }
    
    .timeline-content li {
        margin-bottom: 8px;
    }
    
    /* Desain Skill Tag ala Glassmorphism */
    .skill-tag {
        display: inline-block;
        background: rgba(0, 230, 230, 0.05);
        border: 1px solid rgba(0, 230, 230, 0.3);
        border-radius: 6px;
        padding: 6px 14px;
        margin: 5px;
        font-size: 13px;
        font-family: 'Fira Code', monospace;
        font-weight: 500;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .skill-tag:hover {
        background: rgba(0, 230, 230, 0.15);
        border-color: #00e6e6;
        box-shadow: 0 0 10px rgba(0, 230, 230, 0.2);
        transform: translateY(-2px);
    }
    
    /* Styling khusus Tab Streamlit agar warnanya matching dengan tema Teal */
    div[data-baseweb="tab-list"] {
        gap: 20px;
    }
    div[data-baseweb="tab"] {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        color: #00e6e6 !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #00e6e6 !important;
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
            <div style="position: relative; padding: 5px; border-radius: 20px; background: linear-gradient(135deg, #00e6e6, #a78bfa);">
                <img src="data:image/png;base64,{b64_foto}" style="width: 100%; max-width: 280px; border-radius: 16px; display: block; background-color: #0e1117;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 280px; background: #0e1117; border-radius: 20px; border: 2px dashed #00e6e6; box-shadow: inset 0 0 20px rgba(0,230,230,0.1);">
            <span style="color: #94a3b8; font-family: 'Fira Code'; font-size: 14px;">[ image_not_found ]</span>
        </div>
        """, unsafe_allow_html=True)

with col_intro:
    st.markdown("""
    <div class="hero-title">Dava Arya Danendra</div>
    <div class="hero-subtitle">> S.Si. Fisika | Data Analyst | Computational Physics</div>
    <div class="hero-text">
        Lulusan Fisika Universitas Negeri Semarang (UNNES) yang memiliki minat mendalam pada komputasi ilmiah, analisis data, dan pengembangan aplikasi berbasis data. Berpengalaman dalam menerjemahkan pemodelan matematis kompleks—mulai dari dispersi gas lingkungan (LPT) hingga metrik performa <i>esports</i>—menjadi solusi <i>dashboard</i> interaktif yang mudah dipahami dan siap memecahkan masalah di dunia nyata.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tautan Eksternal dengan tombol bawaan Streamlit
    col_btn1, col_btn2, col_btn3, _ = st.columns([1.2, 1.2, 1.2, 2.5])
    with col_btn1:
        st.link_button("🔗 LinkedIn", "https://linkedin.com/in/username_kamu", use_container_width=True)
    with col_btn2:
        st.link_button("🐙 GitHub", "https://github.com/username_kamu", use_container_width=True)
    with col_btn3:
        st.link_button("📧 Email", "mailto:email_kamu@gmail.com", use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# === TABS CV / REKAM JEJAK ===
tab_pengalaman, tab_pendidikan, tab_projek, tab_keahlian = st.tabs([
    "💼 Experience", 
    "🎓 Education", 
    "🚀 Featured Projects", 
    "🛠️ Tech Stack"
])

# --- TAB 1: PENGALAMAN ---
with tab_pengalaman:
    st.markdown("<div class='section-title'>Professional & Research Experience</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="timeline-title">Research Intern - Pemodelan Dispersi Numerik</div>
        <div class="timeline-subtitle">Badan Meteorologi, Klimatologi, dan Geofisika (BMKG) Pusat | [Bulan] 202X - [Bulan] 202X</div>
        <ul class="timeline-content">
            <li>Mengembangkan <i>pipeline</i> pemodelan dispersi numerik menggunakan Python untuk memodelkan sebaran emisi gas non-kondensabel (H2S dan CO2) dari <i>wellpad</i> panas bumi di Dieng.</li>
            <li>Menerapkan metode <i>Lagrangian Particle Tracking</i> (LPT) dan mengintegrasikannya dengan pustaka spasial seperti Rasterio, NumPy, dan Matplotlib untuk menghasilkan simulasi akurat.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Leadership & Organization</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="timeline-title">Wakil Gubernur Mahasiswa</div>
        <div class="timeline-subtitle">BEM FMIPA UNNES | Jan 2026 - Des 2026</div>
        <ul class="timeline-content">
            <li>Mengelola dan memimpin 125 anggota pengurus dalam mengeksekusi 9 program kerja strategis tingkat fakultas.</li>
            <li>Menyusun draf peraturan organisasi, mengevaluasi jalannya program, serta bertindak sebagai negosiator utama dalam resolusi konflik internal.</li>
        </ul>
    </div>
    
    <div class="timeline-container">
        <div class="timeline-title">Kepala Sekolah Kaderisasi</div>
        <div class="timeline-subtitle">FMIPA UNNES | Jan 2026 - Des 2026</div>
        <ul class="timeline-content">
            <li>Merancang dan mengawal implementasi kurikulum pengembangan kepemimpinan dan manajerial bagi mahasiswa baru FMIPA.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 2: PENDIDIKAN ---
with tab_pendidikan:
    st.markdown("<div class='section-title'>Academic Background</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="timeline-title">Universitas Negeri Semarang (UNNES)</div>
        <div class="timeline-subtitle">Sarjana Sains (S.Si.) - Fisika | Ags 2022 - Ags 2026</div>
        <ul class="timeline-content">
            <li><b>Fokus Riset:</b> Fisika Komputasi, Analisis Data Spasial (GIS), dan Dinamika Pemodelan Lingkungan.</li>
            <li><b>Sertifikasi Bahasa:</b> UNNES-TEP / TOEFL Prediction (Score: 580).</li>
            <li><b>Pendanaan Riset:</b> Menerima pendanaan riset kompetitif dari DPA LPPM UNNES tahun 2025 untuk proyek simulasi lingkungan.</li>
            <li><b>Konferensi Ilmiah:</b> Tampil sebagai pembicara dalam presentasi riset akademik di Kongres Ilmuwan Muda Indonesia (KIMI) V, 2026.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 3: PROJEK & PENGABDIAN ---
with tab_projek:
    st.markdown("<div class='section-title'>Data Analytics & Web Engineering</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="timeline-title">Indonesia Kings Laga (IKL) - Esports Performance Analyst</div>
        <div class="timeline-subtitle">Python, Streamlit, Plotly, Pandas | 2026</div>
        <ul class="timeline-content">
            <li>Membangun <i>dashboard</i> interaktif berskala produksi untuk menganalisis statistik <i>head-to-head</i> dan profil tim <i>esports</i> Honor of Kings (HOK).</li>
            <li>Mengembangkan arsitektur metrik <i>custom</i> yang menghitung stabilitas, kedisiplinan objektif, dan dominasi (*win/loss ratio*) yang direpresentasikan ke dalam <i>Interactive Radar Chart</i>.</li>
            <li>Membuat algoritma pencarian <i>Signature Hero Combos</i> berdasarkan frekuensi *pick* dan *win rate* historis yang melampaui statistik <i>Global Meta</i>.</li>
        </ul>
    </div>
    
    <div class="timeline-container">
        <div class="timeline-title">IndoBERT Emotion Classifier Web App</div>
        <div class="timeline-subtitle">Python, Streamlit, HuggingFace, NLP | 202X</div>
        <ul class="timeline-content">
            <li>Merancang antarmuka klasifikasi teks multi-label berbasis kecerdasan buatan (<i>Transformer</i>) untuk membedah sentimen dan emosi pada teks berbahasa Indonesia secara <i>real-time</i>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Community Engagement</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="timeline-title">Penyusun Kurikulum Sanggar Tani Muda</div>
        <div class="timeline-subtitle">PPK Ormawa 2024 (Didanai oleh Belmawa Kemdikbudristek RI) | Desa Singosari, Kab. Boyolali</div>
        <ul class="timeline-content">
            <li>Merancang dan mengimplementasikan kurikulum peningkatan kapasitas teknologi dan efisiensi bertani untuk komunitas pemuda desa.</li>
        </ul>
    </div>
    
    <div class="timeline-container">
        <div class="timeline-title">Tsunami Ready Community 2025</div>
        <div class="timeline-subtitle">Pemetaan Spasial & Mitigasi Bencana | Kalurahan Parangtritis</div>
        <ul class="timeline-content">
            <li>Melakukan pemetaan spasial dan penempatan penanda indikator prioritas evakuasi di 78 rumah warga penyandang disabilitas yang tersebar di 11 padukuhan guna meningkatkan respon bencana tingkat daerah.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 4: KEAHLIAN ---
with tab_keahlian:
    st.markdown("<div class='section-title'>Core Competencies & Tools</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='timeline-subtitle' style='margin-top: 15px;'>// Programming & Data Science</div>", unsafe_allow_html=True)
    st.markdown("""
    <span class="skill-tag">Python (Advanced)</span>
    <span class="skill-tag">MATLAB</span>
    <span class="skill-tag">Pandas</span>
    <span class="skill-tag">NumPy</span>
    <span class="skill-tag">Streamlit</span>
    <span class="skill-tag">Plotly & Matplotlib</span>
    <span class="skill-tag">Jupyter Notebook</span>
    <span class="skill-tag">JSON / CSV Archiving</span>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='timeline-subtitle' style='margin-top: 25px;'>// Computational Physics & Geospatial</div>", unsafe_allow_html=True)
    st.markdown("""
    <span class="skill-tag">Numerical Dispersion Modeling</span>
    <span class="skill-tag">Lagrangian Particle Tracking (LPT)</span>
    <span class="skill-tag">Geospatial Analysis (GIS)</span>
    <span class="skill-tag">Rasterio</span>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='timeline-subtitle' style='margin-top: 25px;'>// Hardware & Control Systems</div>", unsafe_allow_html=True)
    st.markdown("""
    <span class="skill-tag">Haiwell SCADA</span>
    <span class="skill-tag">Modbus RTU / TCP</span>
    <span class="skill-tag">IoT Integration</span>
    <span class="skill-tag">ESP32 & Arduino</span>
    """, unsafe_allow_html=True)

st.markdown("<br><br><hr style='border-color: rgba(0, 230, 230, 0.2);'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; font-family: \"Fira Code\", monospace;'>© 2026 Dava Arya Danendra. Engineered with Streamlit.</p>", unsafe_allow_html=True)