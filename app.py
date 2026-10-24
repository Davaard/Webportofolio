import streamlit as st

st.set_page_config(page_title="Portofolio | Dava Arya Danendra", page_icon="🚀", layout="wide")

# ==========================================
# 1. SISTEM MEMORI (SESSION STATE)
# ==========================================
# Tangkap parameter dari URL
url_mode = st.query_params.get("mode")

# Jika ada parameter di URL, simpan permanen ke memori
if url_mode:
    st.session_state["mode_pengunjung"] = url_mode

# Baca mode dari memori (jika kosong, anggap sebagai pengunjung "umum")
mode_aktif = st.session_state.get("mode_pengunjung", "umum")


# ==========================================
# 2. LOGIKA NAVIGASI BINGLON
# ==========================================
if mode_aktif == "hok":
    # --- TAMPILAN EKSKLUSIF KOMUNITAS HOK ---
    ikl_hub = st.Page("pages/2_IKL_Hub.py", title="IKL Standings", icon="📊", default=True)
    ikl_profil = st.Page("pages/2a_IKL_Team_Profiling.py", title="Team Profiling", icon="🛡️")
    ikl_h2h = st.Page("pages/2b_IKL_H2H.py", title="Versus Mode (H2H)", icon="⚔️")
    
    nav = st.navigation([ikl_hub, ikl_profil, ikl_h2h])
    
    with st.sidebar:
        st.markdown("---")
        # Tombol rahasia membuang ingatan memori dan URL
        if st.button("💼 Lihat Portofolio Penuh Dava"):
            st.query_params.clear() 
            st.session_state["mode_pengunjung"] = "umum" # Kunci kembali ke mode umum
            st.rerun()

else:
    # --- TAMPILAN LENGKAP STANDAR (HRD/UMUM) ---
    home = st.Page("pages/0_Home.py", title="Beranda & CV", icon="🏠", default=True)
    track_record = st.Page("pages/1_Track_Record.py", title="Rekam Jejak", icon="🏆")
    
    ikl_hub = st.Page("pages/2_IKL_Hub.py", title="IKL Standings", icon="📊")
    ikl_profil = st.Page("pages/2a_IKL_Team_Profiling.py", title="Team Profiling", icon="🛡️")
    ikl_h2h = st.Page("pages/2b_IKL_H2H.py", title="Versus Mode (H2H)", icon="⚔️")
    
    data_analyst = st.Page("pages/3_Data_Analyst.py", title="Data Analyst", icon="📈")

    nav = st.navigation({
        "Profil Utama": [home, track_record],
        "Esports Analytics": [ikl_hub, ikl_profil, ikl_h2h],
        "Learning Hub": [data_analyst]
    })
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("**Let's Connect!**")
        st.markdown("🔗 [LinkedIn](#) | 💻 [GitHub](https://github.com/Davaard) | ✉️ [Email](mailto:daryadarendra@gmail.com)")

nav.run()