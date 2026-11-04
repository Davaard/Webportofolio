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
    untuk melakukan klasifikasi emosi multi-label pada teks berbahasa Indonesia. Model dilatih untuk memetakan teks ke dalam 8 spektrum emosi dasar manusia 
    berdasarkan <i>Plutchik's Wheel of Emotions</i> (Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation).
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
    <span style="color: #d1d1d1; font-size: 14px;">Karena keterbatasan memori arsitektur PyTorch, model inferensi ini dideploy di ekosistem Hugging Face. Jika <i>frame</i> di bawah ini menampilkan tulisan <b>"Space is Sleeping"</b> atau memuat terlalu lama, silakan klik tombol di bawah untuk membangunkan server secara manual (membutuhkan waktu <i>booting</i> sekitar 1-2 menit).</span>
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

# === TECHNICAL ANALYSIS (DARI LAPORAN PDF) ===
st.markdown("### 🔬 Analisis Model & Evaluasi Performa")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown("<div class='stat-box'><div class='stat-title'>Base Model</div><div class='stat-value' style='font-size: 16px;'>IndoBERT-Base-p1</div></div>", unsafe_allow_html=True)
with col_s2:
    st.markdown("<div class='stat-box'><div class='stat-title'>Top F1-Score</div><div class='stat-value'>0.89 - 0.95</div></div>", unsafe_allow_html=True)
with col_s3:
    st.markdown("<div class='stat-box'><div class='stat-title'>Loss Function</div><div class='stat-value' style='font-size: 18px;'>BCEWithLogits</div></div>", unsafe_allow_html=True)
with col_s4:
    st.markdown("<div class='stat-box'><div class='stat-title'>Output Activation</div><div class='stat-value' style='font-size: 20px;'>Sigmoid</div></div>", unsafe_allow_html=True)

tab_arsitektur, tab_evaluasi, tab_future = st.tabs([
    "⚙️ Arsitektur & Pelatihan", 
    "📊 Bias Data (Evaluasi Empiris)", 
    "💡 Resolusi & Future Work"
])

with tab_arsitektur:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='text-justify'>
        <b>Pendekatan Multi-Label Classification</b><br>
        Berbeda dengan analisis sentimen tradisional (Positif/Netral/Negatif), sistem ini dirancang untuk membaca kompleksitas emosi manusia di mana satu kalimat bisa mengandung rasa marah (Anger) dan sedih (Sadness) secara bersamaan. <br><br>
        Oleh karena itu, pada tahap <i>Fine-Tuning</i>, model menggunakan:
        <ul>
            <li><b>Binary Cross-Entropy (BCE) Loss:</b> Menghitung <i>error</i> untuk setiap label secara terpisah, tidak memaksa satu kelas menjadi pemenang mutlak.</li>
            <li><b>Aktivasi Sigmoid:</b> Probabilitas akhir setiap emosi dihitung secara independen dalam rentang 0 hingga 1, berbeda dengan Softmax yang membagi total probabilitas menjadi 100%.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab_evaluasi:
    st.markdown("<br>", unsafe_allow_html=True)
    col_e1, col_e2 = st.columns([1.5, 1])
    with col_e1:
        st.markdown("""
        <div class='text-justify'>
            <b>Tantangan Imbalanced Dataset</b><br>
            Hasil pengujian menunjukkan bahwa model mencapai <b>F1-Score yang sangat tinggi (0.89 - 0.95)</b> pada kelas mayoritas seperti <i>Joy</i>, <i>Fear</i>, dan <i>Anger</i> yang memiliki >300 sampel data latih. Model terbukti handal menangkap pola semantik kata slang dan informal.<br><br>
            Namun, terjadi anomali <b>Bias Prediksi</b> pada kelas minoritas (<i>Trust</i> dan <i>Anticipation</i>). Karena sampel latih yang sangat sedikit (misalnya hanya 24 sampel untuk Anticipation), model mengalami kegagalan deteksi <i>(Minority Class Failure)</i>. Kalimat yang seharusnya bernada antisipasi kerap salah diprediksi menjadi <i>Fear</i> karena kedekatan fitur linguistik dan dominasi bobot data kelas mayoritas.
        </div>
        """, unsafe_allow_html=True)
    with col_e2:
        st.info("📝 Keterbukaan terhadap limitasi dataset ini ditujukan untuk memahami pentingnya perlakuan data yang seimbang sebelum memasuki tahap pemodelan NLP, yang akan disempurnakan dikemudian hari")

with tab_future:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='text-justify'>
        <b>Rekomendasi Optimasi Lanjutan</b><br>
        Berdasarkan analisis bias empiris tersebut, pengembangan model ke depan difokuskan pada manipulasi data dan fungsi kerugian:
        <ol>
            <li><b>Penerapan Focal Loss:</b> Mengganti BCE standar dengan <i>Focal Loss</i> untuk memberikan "penalti" yang jauh lebih besar ketika model salah memprediksi kelas minoritas.</li>
            <li><b>Optimasi Threshold Dinamis:</b> Menurunkan nilai ambang batas (<i>threshold</i>) dari standar 0.5 menjadi 0.3 khusus untuk label minoritas guna mendongkrak nilai <i>Recall</i>.</li>
            <li><b>Data Balancing (SMOTE / Augmentasi):</b> Melakukan augmentasi data teks (seperti <i>back-translation</i>) pada kelas yang kekurangan sampel agar eksposur model selama <i>training</i> lebih merata.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)