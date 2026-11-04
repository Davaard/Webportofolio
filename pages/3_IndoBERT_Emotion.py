import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi Halaman 
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
        height: 100px; /* Tinggi disamaratakan */
        display: flex; flex-direction: column; justify-content: center;
    }
    .stat-title { font-size: 11px; color: gray; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; margin-bottom: 5px; }
    .stat-value { font-size: 20px; color: white; font-weight: 900; font-family: 'Fira Code', monospace; line-height: 1.2;}
    
    /* Mengurangi jarak kosong (whitespace) iframe dan garis bawah */
    .stIframe { margin-bottom: -20px !important; }
    hr { margin: 10px 0 20px 0 !important; border-color: #333; }
    
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

# === EMBEDDING HUGGING FACE GRADIO ===
# GANTI URL DI BAWAH INI DENGAN URL HUGGING FACE SPACES MILIKMU
HUGGING_FACE_URL = "https://darendra-bert-emotion-classification.hf.space"

# Panel Peringatan Server Sleep
st.markdown("""
<div style="background-color: rgba(255, 193, 7, 0.1); border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
    <span style="color: #ffc107; font-weight: 800; font-size: 15px;">⚠️ Informasi Server Cloud (On-Demand)</span><br>
    <span style="color: #d1d1d1; font-size: 14px;">Karena keterbatasan memori arsitektur PyTorch, mesin inferensi model ini dideploy secara terpisah di ekosistem Hugging Face. Jika <i>frame</i> di bawah ini memuat terlalu lama atau berstatus <b>"Space is Sleeping"</b>, silakan klik tombol di bawah untuk membangunkan server secara manual.</span>
</div>
""", unsafe_allow_html=True)

col_btn, col_space = st.columns([1, 3])
with col_btn:
    st.link_button("⚡ Bangunkan Server Hugging Face", HUGGING_FACE_URL, use_container_width=True)

try:
    # Menanamkan aplikasi Gradio dengan tinggi yang disesuaikan (dikurangi agar tidak terlalu jauh ke bawah)
    components.iframe(HUGGING_FACE_URL, height=650, scrolling=True)
except Exception as e:
    st.error("Gagal memuat antarmuka dari Hugging Face.")

st.markdown("<hr>", unsafe_allow_html=True)

# === TECHNICAL SPECIFICATIONS (STAT-BOX SAJA) ===
st.markdown("### 🔬 Spesifikasi Model Final")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown("<div class='stat-box'><div class='stat-title'>Base Model</div><div class='stat-value'>IndoBERT-Base-p1</div></div>", unsafe_allow_html=True)
with col_s2:
    st.markdown("<div class='stat-box'><div class='stat-title'>Total Dataset (Tervalidasi)</div><div class='stat-value'>2.575 Baris</div></div>", unsafe_allow_html=True)
with col_s3:
    st.markdown("<div class='stat-box'><div class='stat-title'>F1-Macro Score</div><div class='stat-value'>81.3%</div></div>", unsafe_allow_html=True)
with col_s4:
    st.markdown("<div class='stat-box'><div class='stat-title'>Output Activation</div><div class='stat-value'>Sigmoid (Multi-Label)</div></div>", unsafe_allow_html=True)