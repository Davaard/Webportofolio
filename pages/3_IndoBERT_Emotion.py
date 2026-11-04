import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi Halaman (Nama disesuaikan menjadi spesifik IndoBERT)
st.set_page_config(page_title="IndoBERT Emotion", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# === STYLING CSS ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Montserrat:wght@300;400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    
    .page-title { font-weight: 900; font-size: 34px; color: white; margin-bottom: 5px; line-height: 1.2; }
    .page-subtitle { font-family: 'Fira Code', monospace; font-weight: 600; font-size: 16px; color: #00d2ff; margin-bottom: 25px; }
    
    .text-justify { text-align: justify; color: #d1d1d1; font-size: 15px; line-height: 1.7; }
    
    .stat-box {
        background-color: #24242e; border-left: 4px solid #00d2ff; padding: 15px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    .stat-title { font-size: 12px; color: gray; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
    .stat-value { font-size: 24px; color: white; font-weight: 900; font-family: 'Fira Code', monospace; }
    
    div[data-testid="stTabs"] button { font-family: 'Montserrat', sans-serif !important; font-weight: 600 !important; font-size: 15px !important; }
    
    /* Tombol Wake-up Server */
    div[data-testid="stLinkButton"] button {
        border-radius: 6px !important; border: 1px solid #ffc107 !important; color: #ffc107 !important;
        background-color: transparent !important; font-weight: 600 !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stLinkButton"] button:hover { background-color: #ffc107 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# === HEADER ===
st.markdown("<div class='page-title'>🧠 IndoBERT Emotion Classifier</div>", unsafe_allow_html=True)
st.markdown("<div class='page-subtitle'>> Natural Language Processing (NLP) & Affective Computing</div>", unsafe_allow_html=True)

st.markdown("""
<div class='text-justify' style='margin-bottom: 25px;'>
    Aplikasi <i>Artificial Intelligence</i> ini dibangun menggunakan arsitektur <b>Bidirectional Encoder Representations from Transformers (BERT)</b> 
    untuk melakukan klasifikasi emosi multi-label pada teks berbahasa Indonesia. Model telah <b>dioptimalkan sepenuhnya</b> untuk memetakan teks ke dalam 8 spektrum emosi dasar manusia 
    berdasarkan <i>Plutchik's Wheel of Emotions</i> secara presisi dan seimbang.
</div>
""", unsafe_allow_html=True)

# === EMBEDDING HUGGING FACE GRADIO DENGAN FALLBACK UI ===
st.markdown("### 🚀 Live Demo Interaktif")

# GANTI URL DI BAWAH INI DENGAN URL HUGGING FACE SPACES MILIKMU
HUGGING_FACE_URL = "https://darendra-bert-emotion-classification.hf.space"

# Panel Peringatan Server Sleep
st.markdown("""
<div style="background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
    <span style="color: #ffc107; font-weight: 800; font-size: 15px;">⚠️ Informasi Server Cloud (On-Demand)</span><br>
    <span style="color: #d1d1d1; font-size: 14px;">Karena keterbatasan memori arsitektur PyTorch, mesin inferensi model ini dideploy secara terpisah di ekosistem Hugging Face. Jika <i>frame</i> di bawah ini memuat terlalu lama atau berstatus <b>"Space is Sleeping"</b>, silakan klik tombol di bawah untuk membangunkan server secara manual (membutuhkan waktu <i>booting</i> sekitar 1-2 menit).</span>
</div>
""", unsafe_allow_html=True)

col_btn, col_space = st.columns([1, 3])
with col_btn:
    st.link_button("⚡ Bangunkan Server Hugging Face", HUGGING_FACE_URL, use_container_width=True)

try:
    # Menanamkan aplikasi Gradio langsung di dalam Streamlit
    components.iframe(HUGGING_FACE_URL, height=850, scrolling=True)
except Exception as e:
    st.error("Gagal memuat antarmuka dari Hugging Face.")

st.markdown("<hr style='border-color: #333; margin: 30px 0;'>", unsafe_allow_html=True)

# === TECHNICAL ANALYSIS ===
st.markdown("### 🔬 Arsitektur Model, Evaluasi & Resolusi")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown("<div class='stat-box'><div class='stat-title'>Base Model</div><div class='stat-value' style='font-size: 16px;'>IndoBERT-Base-p1</div></div>", unsafe_allow_html=True)
with col_s2:
    st.markdown("<div class='stat-box'><div class='stat-title'>Total Dataset (Tervalidasi)</div><div class='stat-value'>2.575 Baris</div></div>", unsafe_allow_html=True)
with col_s3:
    st.markdown("<div class='stat-box'><div class='stat-title'>F1-Macro Score</div><div class='stat-value' style='font-size: 24px;'>81.3%</div></div>", unsafe_allow_html=True)
with col_s4:
    st.markdown("<div class='stat-box'><div class='stat-title'>Output Activation</div><div class='stat-value' style='font-size: 20px;'>Sigmoid (Multi-Label)</div></div>", unsafe_allow_html=True)

tab_arsitektur, tab_evaluasi, tab_visual = st.tabs([
    "⚙️ Arsitektur Multi-Label", 
    "📊 Resolusi Imbalanced Data", 
    "🕸️ UX & Visualisasi Radar"
])

with tab_arsitektur:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='text-justify'>
        <b>Pendekatan Multi-Label Classification</b><br>
        Berbeda dengan analisis sentimen tradisional (Positif/Netral/Negatif), sistem ini dirancang untuk membaca kompleksitas emosi ganda manusia di mana satu kalimat bisa mengandung rasa marah (Anger) dan sedih (Sadness) secara bersamaan. <br><br>
        Oleh karena itu, pada tahap <i>Fine-Tuning</i>, model menggunakan:
        <ul>
            <li><b>Binary Cross-Entropy (BCE) Loss:</b> Menghitung <i>error</i> untuk setiap label secara terpisah, tidak memaksa satu kelas menjadi pemenang mutlak.</li>
            <li><b>Aktivasi Sigmoid:</b> Probabilitas akhir setiap emosi dihitung secara independen dalam rentang 0 hingga 1. Hal ini sangat berbeda dengan fungsi <i>Softmax (Multi-Class)</i> yang membagi total probabilitas hingga habis menjadi 100%.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab_evaluasi:
    st.markdown("<br>", unsafe_allow_html=True)
    col_e1, col_e2 = st.columns([1.5, 1])
    with col_e1:
        st.markdown("""
        <div class='text-justify'>
            <b>Studi Kasus: Mengatasi Bias Akibat Imbalanced Dataset</b><br>
            Pada iterasi pengembangan awal, model sempat mengalami <i>Minority Class Failure</i> (kegagalan deteksi kelas minoritas). Emosi seperti <i>Trust</i> dan <i>Anticipation</i> sangat jarang terdeteksi akibat minimnya sampel data latih awal (hanya sekitar 20 sampel) jika dibandingkan dengan dominasi kelas <i>Anger</i> yang mencapai 500 sampel.<br><br>
            <b>Resolusi:</b><br>
            Untuk menetralisir bias tersebut, dilakukan tindakan <b>Data Augmentation</b> menggunakan injeksi data sintetis bertaraf Platinum (kalimat kontradiktif ekstrem) secara spesifik pada kelas minoritas. Hasilnya, dataset gabungan berhasil menembus <b>2.575 baris data latih</b> dengan distribusi yang ideal, mengantarkan model pada pencapaian metrik <i>F1-Macro</i> di atas 81% secara merata pada keseluruhan 8 spektrum emosi.
        </div>
        """, unsafe_allow_html=True)
    with col_e2:
        st.success("✅ Model saat ini telah terbebas dari bias prediksi (overfitting) pada kelas mayoritas dan mampu mendeteksi emosi Trust/Anticipation secara akurat.")

with tab_visual:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='text-justify'>
        <b>Pemilihan Visualisasi Radar Chart</b><br>
        Tantangan terbesar dalam klasifikasi <i>Multi-Label</i> adalah penyampaian informasi kepada pengguna (UX). Penggunaan <i>Progress Bar</i> atau <i>Pie Chart</i> konvensional seringkali membingungkan karena total persentase emosi bisa melampaui 100% (karena setiap emosi dihitung independen).<br><br>
        Oleh karena itu, antarmuka dirancang menggunakan <b>Radar Chart (Jaring Laba-Laba)</b>. Pendekatan ini merupakan standar visualisasi akademis terbaik untuk <i>Plutchik's Wheel of Emotions</i>. Radar Chart memungkinkan representasi multivariat yang sangat intuitif—di mana sumbu poligon akan memanjang secara dinamis sesuai dengan intensitas emosi dominan tanpa terikat pada hukum total 100%.
    </div>
    """, unsafe_allow_html=True)