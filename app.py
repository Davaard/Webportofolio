import streamlit as st

# Konfigurasi dasar halaman (Wajib di baris paling atas)
st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="🚀", layout="wide")

# Menangkap 'kode rahasia' dari URL
mode_pengunjung = st.query_params.get("mode", "umum")

# ==========================================
# LOGIKA NAVIGASI BINGLON
# ==========================================
if mode_pengunjung == "hok":
    # --- TAMPILAN EKSKLUSIF KOMUNITAS HOK ---
    # IKL Hub diset default=True agar langsung terbuka tanpa error
    ikl_hub = st.Page("pages/2_IKL_Hub.py", title="IKL Standings", icon="📊", default=True)
    ikl_profil = st.Page("pages/2a_IKL_Team_Profiling.py", title="Team Profiling", icon="🛡️")
    ikl_h2h = st.Page("pages/2b_IKL_H2H.py", title="Versus Mode (H2H)", icon="⚔️")
    
    nav = st.navigation([ikl_hub, ikl_profil, ikl_h2h])
    
    with st.sidebar:
        st.markdown("---")
        # Tombol rahasia untuk mereset URL dan kembali ke portofolio penuh
        if st.button("💼 Lihat Portofolio Penuh Dava"):
            st.query_params.clear() 
            st.rerun()

else:
    # --- TAMPILAN LENGKAP STANDAR (HRD/UMUM) ---
    # Home diset default=True
    home = st.Page("pages/0_Home.py", title="Beranda & CV", icon="🏠", default=True)
    track_record = st.Page("pages/1_Track_Record.py", title="Rekam Jejak", icon="🏆")
    
    ikl_hub = st.Page("pages/2_IKL_Hub.py", title="IKL Standings", icon="📊")
    ikl_profil = st.Page("pages/2a_IKL_Team_Profiling.py", title="Team Profiling", icon="🛡️")
    ikl_h2h = st.Page("pages/2b_IKL_H2H.py", title="Versus Mode (H2H)", icon="⚔️")
    
    data_analyst = st.Page("pages/3_Data_Analyst.py", title="Data Analyst", icon="📈")

    # Struktur pengelompokan sidebar
    nav = st.navigation({
        "Profil Utama": [home, track_record],
        "Esports Analytics": [ikl_hub, ikl_profil, ikl_h2h],
        "Learning Hub": [data_analyst]
    })
    
    # Kontak permanen di bawah sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Let's Connect!**")
        st.markdown("🔗 [LinkedIn](#) | 💻 [GitHub](https://github.com/Davaard) | ✉️ [Email](mailto:daryadarendra@gmail.com)")

# Menjalankan mesin navigasi
nav.run()