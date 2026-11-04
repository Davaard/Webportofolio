import streamlit as st

st.set_page_config(page_title="Rekam Jejak | Dava Arya Danendra", page_icon="📜", layout="wide", initial_sidebar_state="expanded")

# === DEFINISI FUNGSI POP-UP (ST.DIALOG) ===
@st.dialog("📸 Dokumentasi: Magang BMKG Pusat", width="large")
def modal_bmkg():
    st.markdown("<div style='text-align: justify; color: #d1d1d1; margin-bottom: 15px;'>Mendiagnosis kendala teknis dan memastikan reliabilitas akuisisi data sensor seismik secara langsung di stasiun pemantau lapangan.</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/Dokumentasi/bmkg_1.jpg", caption="Kalibrasi Sensor Seismik")
        st.image("assets/Dokumentasi/bmkg_3.jpg", caption="Monitoring Transmisi Data")
    with col2:
        st.image("assets/Dokumentasi/bmkg_2.jpg", caption="Perbaikan Modul Catu Daya")
    st.info("💡 Tools: Multitester, Software Kalibrator, Modbus Analyzer.")

@st.dialog("📸 Dokumentasi: BEM FMIPA", width="large")
def modal_bem():
    col1, col2 = st.columns(2)
    with col1: st.image("assets/Dokumentasi/bem_1.jpg", caption="Rapat Evaluasi KPI Departemen")
    with col2: st.image("assets/Dokumentasi/bem_2.jpg", caption="Eksekusi Program Kerja Utama")

@st.dialog("💻 UI/UX: IndoBERT Emotion Classifier", width="large")
def modal_indobert():
    st.markdown("<div style='text-align: justify; color: #d1d1d1; margin-bottom: 15px;'>Tangkapan layar antarmuka pengguna (Gradio) yang menampilkan hasil kalkulasi matriks probabilitas sentimen dan emosi dari teks berbahasa Indonesia (F1-Score 0.89).</div>", unsafe_allow_html=True)
    st.image("assets/Dokumentasi/indobert_ui.jpg", caption="Analisis Probabilitas Multi-label")

@st.dialog("🎤 Presentasi: KIMI V", width="large")
def modal_kimi():
    st.markdown("<div style='text-align: justify; color: #d1d1d1; margin-bottom: 15px;'>Sesi pemaparan dan tanya jawab riset mengenai rancang bangun model numerik cuaca berbasis Logika Fuzzy Mamdani.</div>", unsafe_allow_html=True)
    st.image("assets/Dokumentasi/kimi_1.jpg", caption="Sesi Presentasi Riset KIMI V 2026")


# === STYLING CSS TIMELINE ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    
    .page-title { font-weight: 900; font-size: 34px; color: white; margin-bottom: 10px; line-height: 1.2;}
    .page-subtitle { font-weight: 500; font-size: 16px; color: gray; margin-bottom: 30px; border-bottom: 1px solid #333; padding-bottom: 20px;}
    
    .timeline-container { border-left: 2px solid #333; padding-left: 25px; position: relative; margin-bottom: 15px; }
    .timeline-container::before {
        content: ''; position: absolute; left: -7px; top: 5px; width: 12px; height: 12px; 
        background-color: #00d2ff; border-radius: 50%; box-shadow: 0 0 8px #00d2ff;
    }
    
    .tl-title { font-weight: 800; font-size: 20px; color: white; margin-bottom: 5px; }
    .tl-subtitle { font-weight: 600; font-size: 14.5px; color: #d4af37; margin-bottom: 12px; }
    .tl-content { font-weight: 400; font-size: 15px; color: #d1d1d1; line-height: 1.7; text-align: justify; margin-bottom: 15px;}
    .tl-content ul { margin-top: 5px; padding-left: 20px; }
    .tl-content li { margin-bottom: 8px; }
    
    div[data-testid="stTabs"] button { font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 16px !important; }
    
    /* Styling tombol trigger Pop-up */
    div[data-testid="stButton"] button {
        border-radius: 6px !important; border: 1px solid #444 !important; background-color: #222 !important; color: #00d2ff !important; font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button:hover { border-color: #00d2ff !important; background-color: #00d2ff !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='page-title'>Rekam Jejak & Dokumentasi</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>Rincian kronologis perjalanan profesional, akademik, dan inovasi teknologi yang pernah dikembangkan.</div>", unsafe_allow_html=True)

tab_kerja, tab_projek, tab_pendidikan = st.tabs([
    "💼 Pengalaman & Kepemimpinan", 
    "🚀 Riset & Inovasi", 
    "🎓 Akademik & Kualifikasi"
])

# --- TAB 1: PENGALAMAN & KEPEMIMPINAN ---
with tab_kerja:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BMKG ---
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Staf Magang Instrumentasi dan Kalibrasi Geofisika</div>
        <div class="tl-subtitle">BMKG Pusat, Deputi Bidang Infrastruktur MKG | Feb 2025 – Jun 2025</div>
        <div class="tl-content">
            <ul>
                <li>Memantau transmisi data instrumen geofisika secara <i>real-time</i> dan mendiagnosis penyebab <i>downtime server</i> dari jarak jauh.</li>
                <li>Melaksanakan tindakan pemeliharaan kuratif dan perbaikan fisik pada perangkat keras lapangan.</li>
                <li>Mengeksekusi proses kalibrasi tingkat tinggi pada instrumen sensor gempa (Seismometer dan Accelerometer).</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🖼️ Lihat Dokumentasi BMKG", key="btn_bmkg"): modal_bmkg()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- BEM ---
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Wakil Gubernur</div>
        <div class="tl-subtitle">BEM FMIPA Universitas Negeri Semarang | Feb 2025 – Feb 2026</div>
        <div class="tl-content">
            <ul>
                <li>Merumuskan <i>blueprint</i> program kerja strategis dan mengelola manajemen SDM 125 anggota pengurus.</li>
                <li>Memonitor evaluasi <i>Key Performance Indicators</i> (KPI) seluruh departemen.</li>
                <li>Bertindak sebagai fasilitator utama dalam memimpin resolusi konflik internal tim.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🖼️ Lihat Dokumentasi BEM", key="btn_bem"): modal_bem()

# --- TAB 2: RISET & INOVASI ---
with tab_projek:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- INDOBERT ---
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Pengembang Aplikasi AI: IndoBERT Emotion Classifier Web App</div>
        <div class="tl-subtitle">Kecerdasan Buatan & NLP</div>
        <div class="tl-content">Membangun arsitektur aplikasi web interaktif untuk klasifikasi emosi teks berbasis <i>Deep Learning</i> menggunakan model bahasa IndoBERT dan <i>framework</i> Gradio. Meraih tingkat akurasi evaluasi performa pada metrik <b>F1-Score 0.89</b>.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💻 Lihat Antarmuka Aplikasi", key="btn_nlp"): modal_indobert()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # --- KIMI V ---
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Kongres Ilmuwan Muda Indonesia (KIMI) V</div>
        <div class="tl-subtitle">Presenter Ilmiah Nasional | 2026</div>
        <div class="tl-content">Tampil sebagai pemateri untuk mempresentasikan riset inovatif mengenai rancang bangun model numerik prediksi cuaca pesisir yang dioptimasi menggunakan algoritma <b>Logika Fuzzy Mamdani</b> di forum sains tingkat nasional.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎤 Dokumentasi Presentasi", key="btn_kimi"): modal_kimi()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Sisa pencapaian
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Inventarisasi Emisi Gas Rumah Kaca</div>
        <div class="tl-subtitle">DPA LPPM UNNES | 2025</div>
        <div class="tl-content">Berhasil meraih pendanaan hibah riset perguruan tinggi dengan luaran tersertifikasi Hak Cipta resmi dari Kementerian Hukum dan HAM RI.</div>
    </div>
    <div class="timeline-container">
        <div class="tl-title">Tsunami Ready Community 2025</div>
        <div class="tl-subtitle">Pelaksana Program BMKG di Kelurahan Parangtritis</div>
        <div class="tl-content">Memetakan spasial dan mendistribusikan "Stiker Prioritas Evakuasi Bencana" pada 78 titik rumah kelompok rentan.</div>
    </div>
    <div class="timeline-container">
        <div class="tl-title">Penyusun Kurikulum Inovasi Agrikultur (PPK Ormawa)</div>
        <div class="tl-subtitle">Pendanaan Nasional Kemdikbudristek RI | 2024</div>
        <div class="tl-content">Menyusun kurikulum operasional 6 modul pelatihan agrikultur guna pemberdayaan ekonomi masyarakat di Desa Singosari, Boyolali.</div>
    </div>
    """, unsafe_allow_html=True)

# --- TAB 3: AKADEMIK & KUALIFIKASI ---
with tab_pendidikan:
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="timeline-container">
        <div class="tl-title">Universitas Negeri Semarang (UNNES)</div>
        <div class="tl-subtitle">Sarjana Sains (S.Si.) - Fisika | 2022 – 2026</div>
        <div class="tl-content">
            <b>IPK: 3.44</b><br><br>
            <b>Tugas Akhir / Skripsi:</b><br>
            <i>Simulasi Lagrangian Particle Tracking (LPT) 2D & 3D untuk Pemodelan Dispersi Gas Non-Kondensabel (H2S dan CO2) di Kawasan Panas Bumi Dieng.</i><br><br>
            <b>Fokus Keilmuan:</b>
            <ul>
                <li>Pemodelan Numerik & Komputasi Sains</li>
                <li>Pemrosesan Data & <i>Machine Learning</i> Terapan</li>
                <li>Sistem Instrumentasi & Kalibrasi Geofisika</li>
                <li>Integrasi Perangkat Keras (IoT) & Telemetri</li>
            </ul>
        </div>
    </div>
    
    <div class="timeline-container">
        <div class="tl-title">Sertifikasi & Kemampuan Bahasa</div>
        <div class="tl-subtitle">Kualifikasi Profesional</div>
        <div class="tl-content">
            <ul>
                <li><b>Bahasa Inggris:</b> UNNES-TEP / TOEFL Prediction (Score: <b>580</b>). Mampu membaca dan menganalisis dokumentasi teknis atau jurnal ilmiah internasional secara mendalam.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)