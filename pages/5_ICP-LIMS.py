import streamlit as st
import pandas as pd
import numpy as np
import io
import json
import os

# ==========================================
# 1. KONFIGURASI DATA & LIMIT
# ==========================================
DICT_LOGAM = {
    "MIX A": ["Fe", "Mn", "Mo", "Sn", "Ti", "Zn", "Ba", "Cd", "Co", "Cr", "Cu", "Ni", "Pb", "Al"],
    "MIX B": ["Hg", "As", "Se", "Sb"],
    "BORON": ["B"]
}

KOLOM_STANDAR = DICT_LOGAM["MIX A"] + DICT_LOGAM["BORON"] + DICT_LOGAM["MIX B"]

LIMIT_DETEKSI = {
    "Fe": 0.08, "Mn": 0.012, "Mo": 0.01, "Sn": 0.01, "Ti": 0.01, "Zn": 0.02, 
    "Ba": 0.1, "Cd": 0.008, "Co": 0.02, "Cr": 0.059, "Cu": 0.018, "Ni": 0.031, 
    "Pb": 0.03, "Al": 0.01, "B": 0.01, "Hg": 0.0002, "As": 0.002, "Se": 0.01, "Sb": 0.01
}

def get_kategori(logam):
    for kategori, list_logam in DICT_LOGAM.items():
        if logam in list_logam: return kategori
    return "UNKNOWN"

# ==========================================
# 2. INISIALISASI HALAMAN & STATE (SHOWCASE)
# ==========================================
st.set_page_config(page_title="LIMS ICP-OES", page_icon="🧪", layout="wide")

st.title("🧪 LIMS ICP-OES Terintegrasi")
st.markdown("""
**Sistem Manajemen Informasi Laboratorium (Preparasi & Ekstraksi Data Otomatis)**  
""")

# Membaca Seed Data secara Read-Only
if "init_showcase" not in st.session_state:
    if os.path.exists("assets/ICP_LIMS/dummy_preparasi.json"):
        try:
            with open("assets/ICP_LIMS/dummy_preparasi.json", "r") as f:
                st.session_state.data_preparasi = json.load(f)
        except json.JSONDecodeError:
            st.session_state.data_preparasi = []
    else:
        st.session_state.data_preparasi = [] 
        
    st.session_state.work_order_final = None
    st.session_state.status_selesai = {}
    st.session_state.init_showcase = True

tab1, tab2 = st.tabs(["📋 Preparasi & Work Order", "📈 Simulasi Data Ingestion"])

# =========================================================================
# ==================== TAB 1: SESI PRA-ICP (WORK ORDER) ===================
# =========================================================================
with tab1:
    st.markdown("### 📥 Input Permintaan Uji")
    with st.form("form_input", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1: 
            no_sampel = st.text_input("Kode Sampel (Contoh: 654.10)")
            
        with col2:
            opsi_tanpa_b = [x for x in KOLOM_STANDAR if x != "B"]
            pilihan_logam = st.multiselect("Pilih Logam", options=opsi_tanpa_b)
            
        with col3:
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            uji_boron = st.checkbox("🧪 + Boron (B)")
        
        if st.form_submit_button("➕ Tambahkan ke Antrian"):
            final_logam = pilihan_logam.copy()
            if uji_boron:
                final_logam.append("B")
                
            if not no_sampel or not final_logam:
                st.error("Kode sampel dan logam tidak boleh kosong!")
            else:
                st.session_state.data_preparasi.append({"no_sampel": no_sampel, "logam": final_logam})
                st.success(f"Sampel **{no_sampel}** ditambahkan!")

    if st.session_state.data_preparasi:
        st.markdown("---")
        st.markdown("### 📋 Daftar Sample Terdaftar")
        df_antrian = pd.DataFrame(st.session_state.data_preparasi)
        st.dataframe(df_antrian, use_container_width=True)
        
        with st.expander("🛠️ Koreksi: Hapus Sampel Tertentu dari Antrian"):
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                list_antrian = [item["no_sampel"] for item in st.session_state.data_preparasi]
                sampel_hapus = st.selectbox("Pilih kode sampel yang ingin dihapus:", options=list_antrian)
            with col_del2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Hapus Sampel", use_container_width=True):
                    st.session_state.data_preparasi = [x for x in st.session_state.data_preparasi if x["no_sampel"] != sampel_hapus]
                    st.session_state.work_order_final = None
                    st.session_state.status_selesai = {}
                    st.rerun()
        
        st.markdown("### ⚙️ Pengaturan Kapasitas Pengujian")
        if st.checkbox("Gunakan kapasitas slot yang sama untuk semua", value=True):
            slot_mix_a = slot_mix_b = slot_boron = st.number_input("Maks. Sampel per Run", min_value=1, value=5)
        else:
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1: slot_mix_a = st.number_input("Maks. MIX A", value=40)
            with col_s2: slot_mix_b = st.number_input("Maks. MIX B", value=40)
            with col_s3: slot_boron = st.number_input("Maks. BORON", value=40)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("🗑️ Kosongkan Seluruh Antrian"):
                st.session_state.data_preparasi = []
                st.session_state.work_order_final = None
                st.session_state.status_selesai = {}
                st.rerun()
                
        with col_btn2:
            tombol_cetak = st.button("💾 Simpan & Cetak Work Order", type="primary")

        if tombol_cetak:
            wm = {"MIX A": [], "MIX B": [], "BORON": []}
            for item in st.session_state.data_preparasi:
                kat_pilih = {"MIX A": [], "MIX B": [], "BORON": []}
                for l in item["logam"]:
                    if get_kategori(l) != "UNKNOWN": kat_pilih[get_kategori(l)].append(l)
                for kat in ["MIX A", "MIX B", "BORON"]:
                    if kat_pilih[kat]: wm[kat].append({"no_sampel": item["no_sampel"], "logam": kat_pilih[kat]})
            
            def pecah(data, uk): return [data[i:i+uk] for i in range(0, len(data), uk)]
            
            st.session_state.work_order_final = {
                "MIX A": pecah(wm["MIX A"], slot_mix_a), "MIX B": pecah(wm["MIX B"], slot_mix_b), "BORON": pecah(wm["BORON"], slot_boron)
            }
            st.session_state.status_selesai = {}
            st.session_state.df_combined_cache = None
            st.success("✓ Work Order berhasil dicetak!")

    if st.session_state.work_order_final:
        st.markdown("---")
        st.markdown("### 📝 Work Order ICP")
        c_a, c_b, c_c = st.columns(3)
        cfg = {"MIX A": ("🔴", c_a), "MIX B": ("🟡", c_b), "BORON": ("🟢", c_c)}

        for k, (ikon, col_render) in cfg.items():
            with col_render:
                st.markdown(f"#### {ikon} ANTRIAN {k}")
                batches = st.session_state.work_order_final[k]
                if not batches: st.info(f"Kosong")
                for i, batch in enumerate(batches):
                    key_run = f"{k}_{i}"
                    if st.session_state.status_selesai.get(key_run, False):
                        with st.expander(f"~~✓ BATCH {i+1} (SELESAI)~~"):
                            for w in batch: st.markdown(f"**{w['no_sampel']}** → *{', '.join(w['logam'])}*")
                            if st.button("↩ Batal", key=f"u_{key_run}", use_container_width=True):
                                st.session_state.status_selesai[key_run] = False
                                st.rerun()
                    else:
                        with st.container(border=True):
                            st.markdown(f"##### ▷ BATCH {i+1}, Total: {len(batch)} Sampel")
                            st.divider() 
                            for w in batch: st.markdown(f"**{w['no_sampel']}** → *{', '.join(w['logam'])}*")
                            if st.button("✓ Selesai", key=f"d_{key_run}", type="primary", use_container_width=True):
                                st.session_state.status_selesai[key_run] = True
                                st.rerun()

# =========================================================================
# =================== TAB 2: SESI PASCA-ICP ===============================
# =========================================================================
with tab2:
    st.markdown("### 🚀 Ekstraksi Data ICPEsolution")
    
    wo_data = st.session_state.work_order_final
    
    if not wo_data:
        st.warning("⚠️ Work Order kosong! Harap klik 'Simpan & Cetak Work Order' di Sesi 1 terlebih dahulu.")
    else:
        opsi_sumber = st.radio(
            "Pilih Sumber Data Mentah:", 
            ["🧪 Gunakan Data Sintetis", "📂 Upload File CSV Mesin Asli"], 
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        wo_flat = {}
        for kat, batches in wo_data.items():
            for batch in batches:
                for item in batch:
                    s = str(item["no_sampel"])
                    if s not in wo_flat: wo_flat[s] = set()
                    wo_flat[s].update(item["logam"])

        # ==========================================
        # INISIALISASI CACHE UNTUK TAB 2
        # ==========================================
        if "df_combined_cache" not in st.session_state:
            st.session_state.df_combined_cache = None
        if "sumber_cache" not in st.session_state:
            st.session_state.sumber_cache = None
            
        wo_flat = {}
        for kat, batches in wo_data.items():
            for batch in batches:
                for item in batch:
                    s = str(item["no_sampel"])
                    if s not in wo_flat: wo_flat[s] = set()
                    wo_flat[s].update(item["logam"])

        # ----------------------------------------------------
        # CABANG 1: UPLOAD CSV
        # ----------------------------------------------------
        if opsi_sumber == "📂 Upload File CSV Mesin Asli":
            file_csvs = st.file_uploader("Upload SATU atau LEBIH file CSV hasil running", type=["csv"], accept_multiple_files=True)
            
            if file_csvs:
                if st.button("🚀 Ekstrak Data CSV", type="primary", use_container_width=True):
                    with st.spinner("Membaca dan menyatukan file CSV..."):
                        try:
                            all_dfs = []
                            for f_csv in file_csvs:
                                df_raw = pd.read_csv(f_csv, header=None, on_bad_lines='skip', low_memory=False)
                                df_unk = df_raw[df_raw[1] == "UNK"].copy()
                                
                                df_unk[9] = pd.to_numeric(df_unk[9], errors='coerce') 
                                df_opt = df_unk[df_unk[9] == 1].copy()
                                
                                df_clean = df_opt[[2, 6, 11]].copy()
                                df_clean.columns = ["No_Sampel", "Logam", "Konsentrasi"]
                                df_clean["Konsentrasi"] = pd.to_numeric(df_clean["Konsentrasi"], errors='coerce')
                                df_pivot = df_clean.pivot_table(index="No_Sampel", columns="Logam", values="Konsentrasi", aggfunc='first')
                                all_dfs.append(df_pivot)
                            
                            df_temp = pd.concat(all_dfs)
                            df_temp = df_temp.groupby(df_temp.index).first()
                            
                            # 💡 SIMPAN KE MEMORI STREAMLIT
                            st.session_state.df_combined_cache = df_temp
                            st.session_state.sumber_cache = opsi_sumber
                            
                        except Exception as e:
                            st.error(f"Gagal membaca CSV. Error: {e}")

        # ----------------------------------------------------
        # CABANG 2: DATA SINTETIS
        # ----------------------------------------------------
        else:
            st.info("💡 **Mode Simulasi:** Sistem akan menghasilkan data sintetis acak yang meniru output ICP-OES")
            
            if st.button("⚙️ Jalankan Simulasi Mesin ICP", type="primary", use_container_width=True):
                with st.spinner("Membuat data sintetis..."):
                    semua_sampel_mesin = list(wo_flat.keys()) + ["blk", "CAL1", "CAL2", "999.9_GHOST"]
                    df_temp = pd.DataFrame(index=semua_sampel_mesin, columns=KOLOM_STANDAR)
                    
                    for sampel in df_temp.index:
                        for logam in df_temp.columns:
                            if np.random.rand() > 0.7:
                                df_temp.at[sampel, logam] = np.nan
                            else:
                                limit = LIMIT_DETEKSI.get(logam, 0.01)
                                rand_val = np.random.uniform(limit / 2, limit * 10)
                                df_temp.at[sampel, logam] = round(rand_val, 4)
                                
                    # 💡 SIMPAN KE MEMORI STREAMLIT
                    st.session_state.df_combined_cache = df_temp
                    st.session_state.sumber_cache = opsi_sumber

        # ----------------------------------------------------
        # PROSES HILIR: FINAL REPORT & COA DINAMIS
        # ----------------------------------------------------
        # 💡 PANGGIL DARI MEMORI (Bukan dari variabel lokal sementara)
        if st.session_state.df_combined_cache is not None:
            df_combined = st.session_state.df_combined_cache
            sumber_aktif = st.session_state.sumber_cache
            
            try:
                # 1. PERBEDAAN LOGIKA BERDASARKAN SUMBER DATA
                if sumber_aktif == "📂 Upload File CSV Mesin Asli":
                    kata_kunci_blanko = ['blk', 'cal', 'std', 'blank', 'ghost']
                    sampel_valid = [s for s in df_combined.index if not any(k in str(s).lower() for k in kata_kunci_blanko)]
                    
                    df_final = pd.DataFrame(index=sampel_valid, columns=df_combined.columns, dtype=object)
                    for sampel in sampel_valid:
                        for logam in df_combined.columns:
                            nilai = df_combined.at[sampel, logam]
                            limit = LIMIT_DETEKSI.get(logam, 0)
                            if pd.isna(nilai):
                                df_final.at[sampel, logam] = np.nan # Gunakan NaN agar bisa di-drop
                            elif nilai < limit:
                                df_final.at[sampel, logam] = f"<{str(limit).replace('.', ',')}"
                            else:
                                df_final.at[sampel, logam] = round(nilai, 4)
                else:
                    # Mode Simulasi: Filter ketat berdasarkan Work Order (Demo Anti-Bocor)
                    sampel_yg_diproses = [s for s in df_combined.index if str(s) in wo_flat]
                    df_final = pd.DataFrame(index=sampel_yg_diproses, columns=df_combined.columns, dtype=object)
                    
                    for sampel in sampel_yg_diproses:
                        logam_diminta = wo_flat.get(str(sampel), set())
                        for logam in df_combined.columns:
                            if logam in logam_diminta:
                                nilai = df_combined.at[sampel, logam]
                                limit = LIMIT_DETEKSI.get(logam, 0)
                                if pd.isna(nilai):
                                    df_final.at[sampel, logam] = np.nan
                                elif nilai < limit:
                                    df_final.at[sampel, logam] = f"<{str(limit).replace('.', ',')}"
                                else:
                                    df_final.at[sampel, logam] = round(nilai, 4)
                            else:
                                df_final.at[sampel, logam] = np.nan 

                # Buang kolom logam yang 100% tidak ada isinya di tabel utama
                df_final = df_final.dropna(axis=1, how='all')
                
                st.success(f"✅ Ekstraksi Selesai! Berhasil memproses {len(df_final)} Sampel Valid.")
                
                # =====================================================================
                # 2. TAMPILAN TABEL KESELURUHAN (MASTER DATA)
                # =====================================================================
                st.markdown("### 📋 TABEL HASIL UJI KESELURUHAN")
                st.markdown("*Tabel di bawah menampilkan seluruh hasil ekstraksi valid yang telah dibersihkan dari blanko.*")
                
                # Tampilkan tabel, ubah NaN (kosong) jadi strip "-" agar rapi
                st.dataframe(df_final.fillna("-"), use_container_width=True)
                
                st.markdown("---")
                
                # =====================================================================
                # 3. GENERATOR CERTIFICATE OF ANALYSIS (COA) PER BATCH PERUSAHAAN
                # =====================================================================
                st.markdown("### 🖨️ GENERATOR CERTIFICATE OF ANALYSIS")
                st.markdown("*Pilih kode pesanan/perusahaan untuk mencetak CoA yang bersih, spesifik, dan siap rilis.*")
                
                # Ekstrak daftar Prefix (misal: "802" dari "802.1")
                prefixes = sorted(list(set([str(s).split('.')[0] for s in df_final.index])))
                
                col_sel1, col_sel2 = st.columns([1, 2])
                with col_sel1:
                    selected_group = st.selectbox("Pilih Kode Batch (Perusahaan):", prefixes)
                
                # Filter DataFrame KHUSUS untuk prefix yang dipilih
                df_coa = df_final[df_final.index.astype(str).str.match(f"^{selected_group}(\\.|$)")].copy()
                
                # MAGIC TRICK: Buang kolom logam yang sama sekali tidak dipesan oleh batch perusahaan ini!
                df_coa = df_coa.dropna(axis=1, how='all')
                
                # Ubah sisa NaN menjadi strip "-" agar tabel CoA terlihat super elegan
                df_coa_display = df_coa.fillna("-")
                
                import datetime
                tanggal_hari_ini = datetime.date.today().strftime("%d %B %Y")
                
                with st.container(border=True):
                    # Kop Sertifikat
                    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📄 CERTIFICATE OF ANALYSIS</h2>", unsafe_allow_html=True)
                    st.markdown("<p style='text-align: center; font-size: 16px; margin-top: -10px;'><b>Laboratorium Pengujian Kualitas Terpadu</b></p>", unsafe_allow_html=True)
                    st.divider()
                    
                    # Informasi Meta Analisis
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown("**Instrumen:** Shimadzu ICP-OES")
                        st.markdown(f"**Kode Pesanan / Klien:** {selected_group}")
                    with col_info2:
                        st.markdown(f"<p style='text-align: right;'><b>Tanggal Terbit:</b> {tanggal_hari_ini}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='text-align: right;'><b>Validasi Sistem:</b> LIMS Engine v1.0</p>", unsafe_allow_html=True)
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    Dengan hormat,  
                    Berdasarkan pengujian spektrometri emisi optik yang telah dilakukan terhadap sampel dengan identitas batch **{selected_group}**, berikut adalah laporan hasil analisis konsentrasi logam:
                    """)
                    
                    # Tabel Hasil Uji Spesifik
                    st.dataframe(df_coa_display, use_container_width=True)
                    
                    # Keterangan Tambahan
                    st.markdown("<p style='font-size: 12.5px; color: gray;'><i>* Keterangan: Tanda (<) menunjukkan konsentrasi analit berada di bawah Limit Deteksi (LoD) instrumen. Tanda strip (-) menunjukkan pengujian parameter tersebut tidak diminta oleh klien untuk sampel terkait.</i></p>", unsafe_allow_html=True)
                    
                    # Tanda Tangan Footer
                    st.markdown("<br>", unsafe_allow_html=True)
                    col_sig1, col_sig2 = st.columns([2, 1])
                    with col_sig2:
                        st.markdown("<div style='text-align: center;'><b>Disetujui oleh,</b><br><br><br><i>( Quality Control Manager )</i></div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses tabel akhir: {e}")