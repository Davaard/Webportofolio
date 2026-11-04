import streamlit as st

st.set_page_config(page_title="Rekam Jejak | Dava Arya Danendra", page_icon="📜", layout="wide", initial_sidebar_state="expanded")

# =====================================================================================
# 1. DATABASE
# =====================================================================================
DATABASE_PORTFOLIO = [
    {
        "id": "bmkg_2025",
        "kategori": "Kerja",  # Opsi: Kerja, Riset, Pendidikan
        "tahun": 2025,
        "judul": "Staf Magang Instrumentasi dan Kalibrasi Geofisika",
        "subjudul": "BMKG Pusat, Deputi Bidang Infrastruktur MKG | Feb 2025 – Jun 2025",
        "deskripsi": [
            "Memantau status operasional dan kontinuitas transmisi data instrumen geofisika dari seluruh stasiun pengamatan di Indonesia secara real-time",
            "Melakukan diagnosis awal via server BMKG untuk melacak gangguan atau downtime pada perangkat jarak jauh",
            "Melaksanakan pemeliharaan dan perbaikan fisik pada perangkat yang mengalami gangguan operasional (Sensor, Digitizer, Modul GPS, Panel Surya, dan Sistem Catu Daya)",
            "Melakukan kalibrasi presisi pada instrumen sensor gempa, meliputi Seismometer (termasuk Broadband sensor) dan Accelerometer (baik tipe FBA maupun teknologi MEMS yang terintegrasi) untuk menjaga akurasi pembacaan aktivitas seismik",
            "Menyusun laporan teknis terkait hasil diagnosis kerusakan dan log kalibrasi alat"
        ],
        "ada_dokumentasi": True,
        "dok_teks": "",
        "dok_gambar": [
            {"path": "assets/Profile/BMKG/bmkg-1.png", "caption": "Surat Keterangan"},
            {"path": "assets/Profile/BMKG/bmkg-2.png", "caption": "Dokumentasi"},
            {"path": "assets/Profile/BMKG/bmkg-3.png", "caption": "Dokumentasi"}
        ],
        "dok_tools": ""
    },
    {
        "id": "bem_2025",
        "kategori": "Kerja",
        "tahun": 2025,
        "judul": "Wakil Gubernur",
        "subjudul": "BEM FMIPA Universitas Negeri Semarang | Feb 2025 – Feb 2026",
        "deskripsi": [
            "Merumuskan blueprint program kerja strategis dan mengelola manajemen SDM 125 anggota pengurus.",
            "Memonitor evaluasi Key Performance Indicators (KPI) seluruh departemen.",
            "Bertindak sebagai fasilitator utama dalam memimpin resolusi konflik internal tim."
        ],
        "ada_dokumentasi": False,
        "dok_teks": "",
        "dok_gambar": [
            {"path": "assets/", "caption": ""},
            {"path": "assets/", "caption": ""}
        ],
        "dok_tools": ""
    },
    {
        "id": "indobert_2025",
        "kategori": "Riset",
        "tahun": 2025,
        "judul": "Pengembang Aplikasi AI: IndoBERT Emotion Classifier",
        "subjudul": "Kecerdasan Buatan & NLP",
        "deskripsi": [
            "Membangun arsitektur aplikasi web interaktif untuk klasifikasi emosi teks berbasis Deep Learning menggunakan model bahasa IndoBERT dan framework Gradio.",
            "Meraih tingkat akurasi evaluasi performa pada metrik F1-Score 0.89."
        ],
        "ada_dokumentasi": True,
        "dok_teks": "Tangkapan layar antarmuka pengguna (Gradio) yang menampilkan hasil kalkulasi matriks probabilitas sentimen dan emosi dari teks berbahasa Indonesia.",
        "dok_gambar": [
            {"path": "assets/Penelitian/IndoBERT/bert-1.png", "caption": "Abstrak"},
            {"path": "assets/Penelitian/IndoBERT/bert-2.png", "caption": "Tampilan Sistem"},
            {"path": "assets/Penelitian/IndoBERT/bert-3.png", "caption": "Tampilan Sistem"},
            {"path": "assets/Penelitian/IndoBERT/bert-4.png", "caption": "Tampilan Sistem"},
            {"path": "assets/Penelitian/IndoBERT/bert-5.png", "caption": "Tampilan Sistem"}
        ],
        "dok_tools": ""
    },
    {
        "id": "kimi_2026",
        "kategori": "Riset",
        "tahun": 2026,
        "judul": "Kongres Ilmuwan Muda Indonesia (KIMI) V",
        "subjudul": "Presenter Ilmiah Nasional | 2026",
        "deskripsi": [
            "Tampil sebagai presenter riset inovatif mengenai rancang bangun model numerik prediksi cuaca pesisir.",
            "Model dibangun menggunakan algoritma Logika Fuzzy Mamdani dan dipaparkan di forum sains tingkat nasional."
        ],
        "ada_dokumentasi": True,
        "dok_teks": "",
        "dok_gambar": [
            {"path": "assets/Profile/Penelitian/KIMI-V/kimi-1.jpg", "caption": "Sertifikat"},
            {"path": "assets/Profile/Penelitian/KIMI-V/kimi-2.jpg", "caption": "Dokumentasi"},
            {"path": "assets/Profile/Penelitian/KIMI-V/kimi-3.jpg", "caption": "Dokumentasi"},
            {"path": "assets/Profile/Penelitian/KIMI-V/kimi-4.jpg", "caption": "Dokumentasi"},
        ],
        "dok_tools": ""
    },
    {
        "id": "ppko_2024",
        "kategori": "Riset",
        "tahun": 2024,
        "judul": "Penerima Pendanaan Nasional PPK Ormawa 2024",
        "subjudul": "Kurikulum Sanggar Tani Muda Desa Singasari, Boyolali | 2024",
        "deskripsi": [
            "Terlibat langsung dalam program pemberdayaan masyarakat di Desa Singosari, Kabupaten Boyolali",
            "Bertanggung jawab dalam memimpin penyelenggaraan berbagai sesi pelatihan petani muda",
            "Menyusun Kurikulum Program Peningkatan Kapasitas Sanggar Tani Muda secara komprehensif"
        ],
        "ada_dokumentasi": True,
        "dok_teks": "",
        "dok_gambar": [
            {"path": "assets/Profile/Pengabdian/PPKO/ppko-1.png", "caption": "Sertifikat Belmawa"},
            {"path": "assets/Profile/Pengabdian/PPKO/ppko-2.png", "caption": "Sertifikat Apresiasi"},
            {"path": "assets/Profile/Pengabdian/PPKO/ppko-3.png", "caption": "Surat Keterangan"},
            {"path": "assets/Profile/Pengabdian/PPKO/ppko-4.png", "caption": "Sampul Kurikulum"}
        ],
        "dok_tools": ""
    },
    {
        "id": "grk_2025",
        "kategori": "Riset",
        "tahun": 2025,
        "judul": "Penerima Pendanaan DPA LPPM UNNES Tahun 2025",
        "subjudul": "Surat Pencatatan Ciptaan Video Profil Desa Jetak, Getasan | 2025",
        "deskripsi": [
            "Berhasil meraih pendanaan hibah riset perguruan tinggi dengan luaran tersertifikasi Hak Cipta resmi dari Kementerian Hukum dan HAM RI."
        ],
        "ada_dokumentasi": True,
        "dok_teks": "Surat Pencatatan Ciptaan Video Profil Desa Jetak",
        "dok_gambar": [
            {"path": "assets/Profile/Pengabdian/UNNES/hal-1.png", "caption": ""},
            {"path": "assets/Profile/Pengabdian/UNNES/hal-2.png", "caption": ""}
        ],
        "dok_tools": ""
    },
    {
        "id": "unnes_2026",
        "kategori": "Pendidikan",
        "tahun": 2026,
        "judul": "Universitas Negeri Semarang (UNNES)",
        "subjudul": "Sarjana Sains (S.Si.) - Fisika | 2022 – 2026",
        "deskripsi": [
            "<b>IPK: 3.44</b>",
            "<b>Tugas Akhir / Skripsi:</b><br><i>Simulasi Lagrangian Particle Tracking (LPT) 2D & 3D untuk Pemodelan Dispersi Gas Non-Kondensabel (H2S dan CO2) di Kawasan Panas Bumi Dieng.</i>",
            "<b>Fokus Keilmuan:</b><br>• Pemodelan Numerik & Komputasi Sains<br>• Pemrosesan Data & Machine Learning Terapan<br>• Sistem Instrumentasi & Kalibrasi Geofisika<br>• Integrasi Perangkat Keras (IoT) & Telemetri"
        ],
        "ada_dokumentasi": False
    },
    {
        "id": "topel_2026",
        "kategori": "Pendidikan",
        "tahun": 2026,
        "judul": "Sertifikasi & Kemampuan Bahasa",
        "subjudul": "Kualifikasi Profesional",
        "deskripsi": [
            "<b>Bahasa Inggris:</b> UNNES-TOPEL / Test of Proficiency in English Language (Score: <b>580</b>).",
            "Mampu membaca dan menganalisis dokumentasi teknis atau jurnal ilmiah internasional secara mendalam."
        ],
        "ada_dokumentasi": True,
        "dok_teks": "",
        "dok_gambar": [
            {"path": "assets/Profile/Bahasa/Sertifikat-Topel.jpg", "caption": "Sertifikat dari LP3 UNNES"}
        ],
        "dok_tools": ""
    }
]

# =====================================================================================
# 2. MESIN RENDER (UI & FUNGSI)
# =====================================================================================

# --- Styling CSS Universal ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    
    .page-title { font-weight: 900; font-size: 34px; color: white; margin-bottom: 10px; line-height: 1.2;}
    .page-subtitle { font-weight: 500; font-size: 16px; color: gray; margin-bottom: 15px;}
    
    .timeline-container { border-left: 2px solid #333; padding-left: 25px; position: relative; margin-bottom: 15px; margin-top: 15px;}
    .timeline-container::before {
        content: ''; position: absolute; left: -7px; top: 5px; width: 12px; height: 12px; 
        background-color: #00d2ff; border-radius: 50%; box-shadow: 0 0 8px #00d2ff;
    }
    
    .tl-title { font-weight: 800; font-size: 20px; color: white; margin-bottom: 5px; }
    .tl-subtitle { font-weight: 600; font-size: 14.5px; color: #d4af37; margin-bottom: 12px; }
    .tl-content { font-weight: 400; font-size: 15px; color: #d1d1d1; line-height: 1.7; text-align: justify; margin-bottom: 15px;}
    .tl-content ul { margin-top: 5px; padding-left: 20px; margin-bottom: 0px;}
    .tl-content li { margin-bottom: 8px; }
    
    div[data-testid="stTabs"] button { font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 16px !important; }
    
    div[data-testid="stButton"] button {
        border-radius: 6px !important; border: 1px solid #444 !important; background-color: #222 !important; color: #00d2ff !important; font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button:hover { border-color: #00d2ff !important; background-color: #00d2ff !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- Fungsi Pop-Up Universal ---
@st.dialog("📸 Dokumentasi Detail", width="large")
def buka_modal_dokumentasi(item_data):
    st.markdown(f"<h4 style='margin-top: 0; color: white;'>{item_data['judul']}</h4>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: justify; color: #d1d1d1; margin-bottom: 20px;'>{item_data.get('dok_teks', '')}</div>", unsafe_allow_html=True)
    
    gambar_list = item_data.get('dok_gambar', [])
    if gambar_list:
        # Membagi gambar ke dalam 2 kolom agar rapi
        cols = st.columns(2)
        for idx, img in enumerate(gambar_list):
            with cols[idx % 2]:
                st.image(img['path'], caption=img['caption'])
                
    if item_data.get('dok_tools'):
        st.info(item_data['dok_tools'])

# --- Fungsi Pembangun HTML Timeline ---
def render_timeline_item(item):
    # Menyusun HTML List Bullet Points
    deskripsi_html = "<ul>"
    for poin in item["deskripsi"]:
        deskripsi_html += f"<li>{poin}</li>"
    deskripsi_html += "</ul>"
    
    # Render Kotak HTML
    html_str = f"""
    <div class="timeline-container">
        <div class="tl-title">{item['judul']}</div>
        <div class="tl-subtitle">{item['subjudul']}</div>
        <div class="tl-content">{deskripsi_html}</div>
    </div>
    """
    st.markdown(html_str, unsafe_allow_html=True)
    
    # Render Tombol Dokumentasi (Jika Ada)
    if item.get("ada_dokumentasi"):
        if st.button(f"🖼️ Lihat Dokumentasi", key=f"btn_dok_{item['id']}"):
            buka_modal_dokumentasi(item)
    
    st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================================
# 3. TATA LETAK HALAMAN (LAYOUTING)
# =====================================================================================

col_header, col_filter = st.columns([3, 1])
with col_header:
    st.markdown("<div class='page-title'>Rekam Jejak & Dokumentasi</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Rincian kronologis perjalanan profesional, akademik, dan inovasi.</div>", unsafe_allow_html=True)
with col_filter:
    sort_option = st.selectbox("Urutkan Berdasarkan:", ["Terbaru (Tahun)", "Terlama (Tahun)", "Abjad (A - Z)"])

st.markdown("<hr style='border-color: #333; margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# --- Logika Pengurutan (Sorting) ---
if sort_option == "Terbaru (Tahun)":
    data_terurut = sorted(DATABASE_PORTFOLIO, key=lambda x: x['tahun'], reverse=True)
elif sort_option == "Terlama (Tahun)":
    data_terurut = sorted(DATABASE_PORTFOLIO, key=lambda x: x['tahun'], reverse=False)
else:
    data_terurut = sorted(DATABASE_PORTFOLIO, key=lambda x: x['judul'])

# --- Pembagian Tab & Eksekusi Render ---
tab_kerja, tab_projek, tab_pendidikan = st.tabs([
    "💼 Pengalaman & Kepemimpinan", 
    "🚀 Riset & Inovasi", 
    "🎓 Akademik & Kualifikasi"
])

with tab_kerja:
    st.markdown("<br>", unsafe_allow_html=True)
    for data in data_terurut:
        if data["kategori"] == "Kerja":
            render_timeline_item(data)

with tab_projek:
    st.markdown("<br>", unsafe_allow_html=True)
    for data in data_terurut:
        if data["kategori"] == "Riset":
            render_timeline_item(data)

with tab_pendidikan:
    st.markdown("<br>", unsafe_allow_html=True)
    for data in data_terurut:
        if data["kategori"] == "Pendidikan":
            render_timeline_item(data)