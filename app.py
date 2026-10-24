import streamlit as st

# Konfigurasi dasar halaman (Wajib di baris paling atas)
st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="🚀", layout="wide")

# 1. Menangkap 'kode rahasia' dari URL
query_params = st.query_params
mode_pengunjung = query_params.get("mode", "umum")

# 2. Mendefinisikan Semua Halaman (Membaca file di folder pages/)
# -- Bagian Utama --
home = st.Page("pages/0_Home.py", title="Beranda & CV", icon="🏠", default=True)
track_record = st.Page("pages/1_Track_Record.py", title="Rekam Jejak", icon="🏆")

# -- Bagian Proyek IKL (Honor of Kings) --
ikl_hub = st.Page("pages/2_IKL_Hub.py", title="IKL Standings", icon="📊")
ikl_profil = st.Page("pages/2a_IKL_Team_Profiling.py", title="Team Profiling", icon="🛡️")
ikl_h2h = st.Page("pages/2b_IKL_H2H.py", title="Versus Mode (H2H)", icon="⚔️")

# -- Bagian Proyek Lain --
geothermal = st.Page("pages/3_Belajar_Bareng.py", title="Belajar Bareng", icon="📚")

# 3. Logika Navigasi "Bunglon"
if mode_pengunjung == "hok":
    # Tampilan eksklusif jika URL mengandung ?mode=hok
    nav = st.navigation([ikl_hub, ikl_profil, ikl_h2h])
    
    with st.sidebar:
        st.markdown("---")
        # Tombol rahasia untuk kembali ke tampilan portofolio penuh
        if st.button("💼 Lihat Portofolio Penuh Dava"):
            st.query_params.clear() 
            st.switch_page(home)
else:
    # Tampilan lengkap standar (Untuk HRD)
    nav = st.navigation({
        "Profil Utama": [home, track_record],
        "Esports Analytics": [ikl_hub, ikl_profil, ikl_h2h],
        "Spatial & Engineering": [geothermal]
    })
    
    # Kontak permanen di bawah sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Let's Connect!**")
        st.markdown("🔗 [LinkedIn](#) | 💻 [GitHub](#Davaard) | ✉️ [Email](mailto:daryadarendra@gmail.com)")

# Jalankan sistem navigasi
nav.run()