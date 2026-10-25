# region INISIALISASI
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations
from collections import Counter

st.set_page_config(page_title="IKL Dashboard", layout="wide")

@st.cache_data
def load_and_preprocess_data(filepath):
    # 1. Membaca CSV
    df = pd.read_csv(filepath)
    
    # 2. Membersihkan kolom sebelum digabung menjadi Smart Key 
    # (Menghindari angka seperti 1.0 menjadi 'IKL1111.0', kita buang '.0'-nya)
    df['Week_str'] = df['Week'].fillna('').astype(str)
    df['Day_str'] = df['Day'].fillna('').astype(str)
    df['Match_str'] = df['Match'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
    df['Game_str'] = df['Game'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
    
    # 3. Membuat Match_ID (Contoh hasil: IKL1111, IKLUpSf1)
    df['Match_ID'] = 'IKL' + df['Week_str'] + df['Day_str'] + df['Match_str'] + df['Game_str']
    
    # 4. Deteksi Otomatis (History vs Upcoming)
    # Jika Result-nya kosong (NaN), maka itu adalah laga jadwal (Upcoming)
    df['Status'] = df['Result'].apply(lambda x: 'Upcoming' if pd.isna(x) else 'History')
    
    # Bersihkan kolom string sementara agar tabel tetap rapi
    df = df.drop(columns=['Week_str', 'Day_str', 'Match_str', 'Game_str'])
    
    return df
# endregion

# region PRA-PEMPROSESAN
# ==========================================
# FASE 1: IMPORT & TRANSFORMASI DATA
# ==========================================

# 1. Baca masterdata
df_master = load_and_preprocess_data("Data_Set_IKL_HOK.csv")

# Memisahkan data untuk profil tim (hanya ambil laga yang sudah selesai)
df_history = df_master[df_master['Status'] == 'History'].copy()

# 2. Ambil dari sudut pandang Sisi Biru (Sebagai Tim Utama)
df_A = df_history.copy()
df_A = df_A[['Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)', 'Result', 'Duration_min', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 'Heroes_Picked', 'Opponent_Picked']]
# Standarisasi nama kolom agar mudah dipanggil di rumus selanjutnya
kolom_standar = ['Week', 'Day', 'Match', 'Game', 'Team', 'Opponent', 'Win', 'Durasi', 'Gold', 'Opp_Gold', 'Kill', 'Opp_Kill', 'Ast', 'Opp_Ast', 'Obj', 'Opp_Obj', 'Heroes', 'Opp_Heroes']
df_A.columns = kolom_standar

# 3. Ambil dari sudut pandang Sisi Merah (Sebagai Tim Utama)
df_B = df_history.copy()
# Hitung kebalikan hasil untuk Sisi Merah (Jika Biru menang/1, Merah kalah/0)
df_B['Result_Red'] = 1 - df_B['Result'] 
# Tarik kolom dengan posisi silang (Milik Merah di depan, Biru di belakang)
df_B = df_B[['Week', 'Day', 'Match', 'Game', 'Opponent_(Red)', 'Team_(Blue)', 'Result_Red', 'Duration_min', 'O_Gold', 'T_Gold', 'O_Kill', 'T_Kill', 'O_Assist', 'T_Assist', 'O_Objective', 'T_Objective', 'Opponent_Picked', 'Heroes_Picked']]
# Gunakan nama kolom standar yang persis sama dengan Sisi Biru
df_B.columns = kolom_standar

# 4. Tumpuk (Concat) menjadi format Long Data & urutkan
df_long = pd.concat([df_A, df_B], ignore_index=True)
df_long = df_long.sort_values(by=['Week', 'Day', 'Match', 'Game']).reset_index(drop=True)

# 5. Pra-Pemrosesan Kolom Hero (Mengubah teks koma menjadi List)
# Menghapus spasi ekstra di awal/akhir nama hero agar tidak ada duplikat palsu (misal ' Heino' vs 'Heino')
df_long['Heroes'] = df_long['Heroes'].astype(str).apply(lambda x: [hero.strip() for hero in x.split(',')])
df_long['Opp_Heroes'] = df_long['Opp_Heroes'].astype(str).apply(lambda x: [hero.strip() for hero in x.split(',')])
# endregion

# region RADAR PENILAIAN

# region DOMINASI
# ==========================================
# FASE 2: KLASEMEN RETROAKTIF & DOMINASI H2H
# ==========================================

# A. MENGHITUNG KLASEMEN AKHIR IKL
klasemen = df_long.groupby('Team')['Win'].agg(
    Total_Menang='sum',
    Total_Kalah=lambda x: (x == 0).sum()
).reset_index()

# Skor IKL = Total Menang - Total Kalah
klasemen['Skor_IKL'] = klasemen['Total_Menang'] - klasemen['Total_Kalah']

# Rank 1 untuk Skor tertinggi (jika skor sama, gunakan rank yang sama/min)
klasemen['Rank_Akhir'] = klasemen['Skor_IKL'].rank(method='min', ascending=False)

#print("\n--- Klasemen Akhir IKL (Retroaktif) ---")
#print(klasemen[['Team', 'Skor_IKL', 'Rank_Akhir']].sort_values(by='Rank_Akhir').to_string(index=False))


# B. MEMASUKKAN PERINGKAT KE DATA PERTANDINGAN (Pengganti VLOOKUP)
# Map Rank_Akhir ini kembali ke df_long sebagai T_Rank dan O_Rank
df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], on='Team', how='left').rename(columns={'Rank_Akhir': 'T_Rank'})
df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], left_on='Opponent', right_on='Team', how='left', suffixes=('', '_drop')).rename(columns={'Rank_Akhir': 'O_Rank'})
df_long = df_long.drop(columns=['Team_drop'], errors='ignore') 


# C. MENGHITUNG RUMUS DOMINASI (METODE RASIO)
# Kita tambahkan +1 di pembagi Kill agar terhindar dari error jika musuh 0 Kill
df_long['Points_Ratio'] = (df_long['Gold'] / df_long['Opp_Gold']) + (df_long['Kill'] / (df_long['Opp_Kill'] + 1))

# Pisahkan poin saat menang dan kalah
df_long['Points_Won'] = np.where(df_long['Win'] == 1, df_long['Points_Ratio'], np.nan)
df_long['Points_Lost'] = np.where(df_long['Win'] == 0, df_long['Points_Ratio'], np.nan)

# Agregasi untuk perhitungan Dominasi per Tim
dominasi_df = df_long.groupby('Team').agg(
    Total_Wins=('Win', 'sum'),
    Total_Losses=('Win', lambda x: (x == 0).sum()),
    Sum_Points_Won=('Points_Won', 'sum'),
    Sum_Points_Lost=('Points_Lost', 'sum')
).reset_index()

# Isi nilai kosong (NaN) dengan 0 (untuk tim yang tidak pernah menang atau kalah)
dominasi_df.fillna(0, inplace=True)

# Eksekusi Rumus Cross-Penalty Dominance Murni
dominasi_df['Dominance_Skor'] = (
    (dominasi_df['Sum_Points_Won'] / (dominasi_df['Total_Losses'] + 1)) - 
    (dominasi_df['Sum_Points_Lost'] / (dominasi_df['Total_Wins'] + 1))
)

# D. NORMALISASI DOMINASI KE SKALA 0-100 (MIN-MAX SCALING)
min_dom = dominasi_df['Dominance_Skor'].min()
max_dom = dominasi_df['Dominance_Skor'].max()
# endregion

# region KETANGGUHAN
# ==========================================
# FASE 3: MENGHITUNG KETANGGUHAN (REVISI H2H SIMETRIS)
# ==========================================

# A. Pembersihan Data Durasi
def konversi_waktu(waktu):
    waktu = str(waktu).strip()
    if ':' in waktu:
        menit, detik = waktu.split(':')
        return float(menit) + (float(detik) / 60.0)
    return float(waktu)

df_long['Durasi'] = df_long['Durasi'].apply(konversi_waktu)
df_long['Kill'] = pd.to_numeric(df_long['Kill'], errors='coerce').fillna(0)
df_long['Opp_Kill'] = pd.to_numeric(df_long['Opp_Kill'], errors='coerce').fillna(0)

# B. Buat Multiplier Simetris (Defense & Offense)
df_long['Defense_Multiplier'] = df_long['Opp_Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)
df_long['Offense_Multiplier'] = df_long['Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)

# Terapkan bobot pada durasi menang dan kalah
df_long['Durasi_Menang_Berbobot'] = np.where(df_long['Win'] == 1, df_long['Durasi'] * df_long['Offense_Multiplier'], np.nan)
df_long['Durasi_Kalah_Berbobot'] = np.where(df_long['Win'] == 0, df_long['Durasi'] * df_long['Defense_Multiplier'], np.nan)

# C. Agregasi Rata-rata Menang Musiman (Untuk Skenario Kalah 0-2)
seasonal_win_dur = df_long.groupby('Team')['Durasi_Menang_Berbobot'].mean().reset_index()
seasonal_win_dur.rename(columns={'Durasi_Menang_Berbobot': 'Seasonal_Avg_Win_Bobot'}, inplace=True)
seasonal_win_dur['Seasonal_Avg_Win_Bobot'] = seasonal_win_dur['Seasonal_Avg_Win_Bobot'].fillna(7.5) # Asumsi baseline tengah

# D. Agregasi Level SERI / H2H Match
series_df = df_long.groupby(['Week', 'Day', 'Match', 'Team']).agg(
    Avg_Win_Series=('Durasi_Menang_Berbobot', 'mean'),
    Avg_Loss_Series=('Durasi_Kalah_Berbobot', 'mean')
).reset_index()

# E. Eksekusi Skenario Edge Cases
series_df = series_df.merge(seasonal_win_dur, on='Team', how='left')

# Skenario 0-2 (Timpa nilai NaN di Win pakai rata-rata musiman berbobot)
series_df['Avg_Win_Series'] = series_df['Avg_Win_Series'].fillna(series_df['Seasonal_Avg_Win_Bobot'])

# Hitung Toughness Level Seri (Menang 2-0 otomatis diabaikan karena Loss NaN)
series_df['Series_Toughness'] = series_df['Avg_Loss_Series'] - series_df['Avg_Win_Series']

# F. Agregasi Final Level Tim
toughness_df = series_df.groupby('Team').agg(
    Toughness_Skor=('Series_Toughness', 'mean')
).reset_index()

toughness_df['Toughness_Skor'] = toughness_df['Toughness_Skor'].fillna(0)

# G. Gabung ke Rapor Akhir
rapor_akhir = pd.merge(dominasi_df[['Team', 'Dominance_Skor']], toughness_df[['Team', 'Toughness_Skor']], on='Team')
# endregion

# region KEDISIPLINAN
# ==========================================
# FASE 4: MENGHITUNG KEDISIPLINAN (DISCIPLINE)
# ==========================================

# A. Pastikan kolom Objektif terbaca sebagai angka bulat
df_long['Obj'] = pd.to_numeric(df_long['Obj'], errors='coerce').fillna(0)
df_long['Opp_Obj'] = pd.to_numeric(df_long['Opp_Obj'], errors='coerce').fillna(0)

# B. Hitung Skor Efisiensi Objektif Kuadrat (Tim dan Musuh)
# Rumus: (Obj^2) / (Obj + Kill + 1)
df_long['Tim_Obj_Score'] = (df_long['Obj'] ** 2) / (df_long['Obj'] + df_long['Kill'] + 1)
df_long['Musuh_Obj_Score'] = (df_long['Opp_Obj'] ** 2) / (df_long['Opp_Obj'] + df_long['Opp_Kill'] + 1)

# C. Hitung Kedisiplinan H2H per Game (Selisih dibagi Durasi)
df_long['Discipline_Game'] = (df_long['Tim_Obj_Score'] - df_long['Musuh_Obj_Score']) / df_long['Durasi']

# D. Agregasi Rata-rata Kedisiplinan per Tim (Sigma semusim)
discipline_df = df_long.groupby('Team').agg(
    Discipline_Skor=('Discipline_Game', 'mean')
).reset_index()

# E. Gabungkan skor Kedisiplinan ke tabel Rapor Akhir
rapor_akhir = pd.merge(rapor_akhir, discipline_df[['Team', 'Discipline_Skor']], on='Team')
# endregion

# region FOLATILITAS
# ==========================================
# FASE 5: MENGHITUNG Volatility (Volatilitas)
# ==========================================

# A. Hitung Fluktuasi Ekonomi (Standard Deviation dari Gold Per Minute)
df_long['GPM'] = df_long['Gold'] / df_long['Durasi']
volatility_df = df_long.groupby('Team').agg(
    Volatility=('GPM', 'std') # Menghitung Standar Deviasi
).reset_index()

# Isi 0 jika tim hanya main 1 game (tidak ada fluktuasi), meski tidak mungkin terjadi di akhir musim
volatility_df['Volatility'] = volatility_df['Volatility'].fillna(0)

# B. Cari Rank Tertinggi yang Dikalahkan (Best Win)
won_games = df_long[df_long['Win'] == 1]
# Mencari angka Rank TERKECIL (Misal: 1 adalah rank tertinggi)
best_win = won_games.groupby('Team')['O_Rank'].min().reset_index()
best_win.rename(columns={'O_Rank': 'Best_Win_Rank'}, inplace=True)

# C. Cari Rank Terendah yang Menaklukkan Mereka (Worst Loss)
lost_games = df_long[df_long['Win'] == 0]
# Mencari angka Rank TERBESAR (Misal: 10 adalah rank terendah)
worst_loss = lost_games.groupby('Team')['O_Rank'].max().reset_index()
worst_loss.rename(columns={'O_Rank': 'Worst_Loss_Rank'}, inplace=True)

# D. Gabungkan ke tabel Potensi
volatility_df = volatility_df.merge(best_win, on='Team', how='left')
volatility_df = volatility_df.merge(worst_loss, on='Team', how='left')

# E. Tambal Edge Cases (Sapu Bersih & Lose Streak)
# Jika tidak pernah menang, rank tertinggi yang dikalahkan dianggap 10 (paling buruk)
volatility_df['Best_Win_Rank'] = volatility_df['Best_Win_Rank'].fillna(10)
# Jika tidak pernah kalah, rank terendah yang mengalahkan dianggap 1 (paling ideal)
volatility_df['Worst_Loss_Rank'] = volatility_df['Worst_Loss_Rank'].fillna(1)

# F. Hitung Skor Potensi = Volatility * (Worst Loss / Best Win)
volatility_df['Giant_Slayer_Ratio'] = volatility_df['Worst_Loss_Rank'] / volatility_df['Best_Win_Rank']
volatility_df['Volatility_Skor'] = volatility_df['Volatility'] * volatility_df['Giant_Slayer_Ratio']

# G. Gabungkan skor Potensi ke tabel Rapor Akhir
rapor_akhir = pd.merge(rapor_akhir, volatility_df[['Team', 'Volatility_Skor']], on='Team')
# endregion

# region TEAMFIGHT
# ==========================================
# FASE 6: MENGHITUNG TEAM FIGHT
# ==========================================

# A. Pastikan kolom Assist terbaca sebagai angka (Gunakan 'Ast')
df_long['Ast'] = pd.to_numeric(df_long['Ast'], errors='coerce').fillna(0)
df_long['Opp_Ast'] = pd.to_numeric(df_long['Opp_Ast'], errors='coerce').fillna(0)

# B. Hitung Rasio Keterlibatan Tim (Assist per Kill)
df_long['Team_Assist_Ratio'] = df_long['Ast'] / (df_long['Kill'] + 1)
df_long['Opp_Assist_Ratio'] = df_long['Opp_Ast'] / (df_long['Opp_Kill'] + 1)

# C. Hitung Keunggulan Team Fight (H2H Game)
df_long['TeamFight_Game'] = df_long['Team_Assist_Ratio'] - df_long['Opp_Assist_Ratio']

# D. Agregasi Rata-rata semusim (Sigma)
teamfight_df = df_long.groupby('Team').agg(
    TeamFight_Skor=('TeamFight_Game', 'mean')
).reset_index()

# E. Gabung ke Rapor Akhir
rapor_akhir = pd.merge(rapor_akhir, teamfight_df[['Team', 'TeamFight_Skor']], on='Team')
# endregion

# region FLEKSIBILITAS
# ==========================================
# FASE 7: MENGHITUNG FLEKSIBILITAS (HERO POOL)
# ==========================================
import ast

# A. Fungsi aman untuk membaca daftar hero (jika bentuknya string list atau dipisah koma)
def parse_heroes(val):
    if isinstance(val, list):
        return val
    try:
        # Jika formatnya string seperti "['Mai', 'Sun Ce']"
        return ast.literal_eval(val)
    except:
        # Jika formatnya teks biasa dipisah koma "Mai, Sun Ce"
        return [h.strip() for h in str(val).split(',') if h.strip()]

df_long['Heroes_List'] = df_long['Heroes'].apply(parse_heroes)

# B. Pecah list hero menjadi baris-baris individu (Explode) lalu hitung keunikannya per tim
flexibility_df = df_long.explode('Heroes_List').groupby('Team')['Heroes_List'].nunique().reset_index()
flexibility_df.rename(columns={'Heroes_List': 'Flexibility_Skor'}, inplace=True)

# C. Gabung ke Rapor Akhir
rapor_akhir = pd.merge(rapor_akhir, flexibility_df[['Team', 'Flexibility_Skor']], on='Team')
# endregion

# region NORMALISASI
# ==========================================
# FASE 8: NORMALISASI MIN-MAX SCALING (20 - 100)
# ==========================================

# Daftar metrik mentah yang akan diskala
metrik_mentah = [
    'Dominance_Skor', 
    'Toughness_Skor', 
    'Discipline_Skor', 
    'Volatility_Skor', 
    'TeamFight_Skor', 
    'Flexibility_Skor'
]

# Lakukan scaling 20-100 untuk setiap kolom (Batas bawah 20 agar grafik tidak hancur)
for col in metrik_mentah:
    min_val = rapor_akhir[col].min()
    max_val = rapor_akhir[col].max()
    
    nama_kolom_baru = col.replace('_Skor', '_100')
    
    # Mencegah error pembagian nol jika semua tim punya skor yang sama persis
    if max_val == min_val:
        rapor_akhir[nama_kolom_baru] = 100.0
    else:
        # Rumus Scaling [20, 100]: ((Nilai - Min) / (Max - Min)) * 80 + 20
        rapor_akhir[nama_kolom_baru] = ((rapor_akhir[col] - min_val) / (max_val - min_val)) * 80 + 20

# Buat dataframe final yang hanya berisi kolom skala agar rapi untuk Streamlit
kolom_final = ['Team'] + [col.replace('_Skor', '_100') for col in metrik_mentah]
rapor_radar = rapor_akhir[kolom_final].round(2)
# endregion

# endregion

# region KOMBINASI
# ==========================================
# FASE 9: MESIN EVOLUSI KOMBO (FUNGSI GLOBAL)
# ==========================================

# 1. Siapkan Data Global (Dihitung 1x saja saat aplikasi dimuat)
df_combo_history = df_long.dropna(subset=['Win']).copy()

def is_win(result_val):
    return 1 if float(result_val) == 1.0 else 0

global_freq = {}
global_wins = {}

for idx, row in df_combo_history.iterrows():
    heroes = row['Heroes_List']
    win_status = is_win(row['Win'])
    if isinstance(heroes, list) and len(heroes) > 0:
        n = len(heroes)
        for r in range(1, min(n + 1, 6)):
            for combo in combinations(sorted(heroes), r):
                global_freq[combo] = global_freq.get(combo, 0) + 1
                global_wins[combo] = global_wins.get(combo, 0) + win_status

# 2. Fungsi Pencetak Kombo Khusus Tim
def get_signature_combos(tim_target):
    team_freq = {}
    team_wins = {}
    df_tim = df_combo_history[df_combo_history['Team'] == tim_target]
    
    for idx, row in df_tim.iterrows():
        heroes = row['Heroes_List']
        win_status = is_win(row['Win'])
        if isinstance(heroes, list) and len(heroes) >= 2:
            n = len(heroes)
            for r in range(2, min(n + 1, 6)):
                for combo in combinations(sorted(heroes), r):
                    team_freq[combo] = team_freq.get(combo, 0) + 1
                    team_wins[combo] = team_wins.get(combo, 0) + win_status

    # Filter Threshold (Duo/Trio min 3x, Quad/Quintet min 2x)
    team_valid = {}
    for combo, freq in team_freq.items():
        sz = len(combo)
        if (sz == 2 and freq >= 3) or (sz == 3 and freq >= 3) or (sz >= 4 and freq >= 2):
            wr_tim = (team_wins[combo] / freq) * 100
            team_valid[combo] = {'freq': freq, 'wr': wr_tim}

    # Seleksi Alam (Resolusi Konflik Subset & Sisa Independen)
    combos_to_remove = set()
    sorted_combos = sorted(list(team_valid.keys()), key=lambda x: len(x), reverse=True)

    for i in range(len(sorted_combos)):
        c_large = sorted_combos[i]
        if c_large in combos_to_remove: continue
            
        for j in range(i + 1, len(sorted_combos)):
            c_small = sorted_combos[j]
            if c_small in combos_to_remove: continue
            
            if set(c_small).issubset(set(c_large)):
                wr_large, wr_small = team_valid[c_large]['wr'], team_valid[c_small]['wr']
                f_large, f_small = team_valid[c_large]['freq'], team_valid[c_small]['freq']
            
                if wr_large > wr_small:
                    combos_to_remove.add(c_small)
                elif wr_small > wr_large:
                    combos_to_remove.add(c_large)
                else:
                    indep_freq = f_small - f_large
                    syarat_mandiri = 3 if len(c_small) == 2 else 2
                    if indep_freq < syarat_mandiri:
                        combos_to_remove.add(c_small)

    kombo_final = {k: v for k, v in team_valid.items() if k not in combos_to_remove}
    top_3_combos = sorted(kombo_final.items(), key=lambda x: (x[1]['wr'], x[1]['freq']), reverse=True)[:3]
    
    # Merakit List Output Dictionary untuk Elemen UI
    hasil_ui = []
    for combo, stats in top_3_combos:
        freq_tim = stats['freq']
        wr_tim = stats['wr']
        g_freq_current = global_freq.get(combo, 0)
        g_wr_current = (global_wins.get(combo, 0) / g_freq_current * 100) if g_freq_current > 0 else 0
        
        is_red_worthy = False
        if len(combo) == 2:
            base_heroes = [global_freq.get((h,), 0) for h in combo]
            g_freq_base = min(base_heroes) if base_heroes else 1
            max_trio_wr = 0
            for g_combo, g_f in global_freq.items():
                if len(g_combo) == 3 and set(combo).issubset(set(g_combo)):
                    t_wr = (global_wins[g_combo] / g_f) * 100
                    if t_wr > max_trio_wr: max_trio_wr = t_wr
            if g_wr_current > max_trio_wr: is_red_worthy = True
        else:
            g_freq_base = 0
            g_wr_base = 0
            for sub_combo in combinations(combo, len(combo) - 1):
                f_sub = global_freq.get(sub_combo, 0)
                if f_sub > g_freq_base:
                    g_freq_base = f_sub
                    g_wr_base = (global_wins.get(sub_combo, 0) / f_sub) * 100
            if g_wr_current > g_wr_base: is_red_worthy = True
        
        rasio_global = (g_freq_current / g_freq_base) * 100 if g_freq_base > 0 else 0
        
        if rasio_global > 25.0:
            if is_red_worthy:
                warna, ikon, status = "error", "🌟", f"Supreme Meta ({rasio_global:.0f}%)"
            else:
                warna, ikon, status = "warning", "🔥", f"Global Meta ({rasio_global:.0f}%)"
        else:
            warna, ikon, status = "success", "🌿", "Team Signature Pick"

        nama_kombo = f"{', '.join(combo[:-1])} & {combo[-1]}"
        tipe = {2: "Duo", 3: "Trio", 4: "Quad", 5: "Quintet"}[len(combo)]
        teks = f"**{nama_kombo}**\n\n🎯 {tipe} Pick: **{freq_tim}x**\n🏆 Team WR: **{wr_tim:.0f}%**\n📊 Kategori: **{status}**"
        
        hasil_ui.append({"warna": warna, "ikon": ikon, "teks": teks})
        
    return hasil_ui

# endregion

# region DISPLAY

# region NAVIGASI
# ==========================================
# MENU NAVIGASI UTAMA (TAMPILAN TOMBOL HEADER)
# ==========================================
st.markdown("### 🎮 IKL Dashboard")

# 1. Inisialisasi memori halaman awal jika belum ada
if "menu_ikl" not in st.session_state:
    st.session_state['menu_ikl'] = "🏆 Klasemen & Meta"

# 2. Buat 3 kolom sejajar untuk tombol
col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("🏆 Klasemen & Meta", use_container_width=True):
        st.session_state['menu_ikl'] = "🏆 Klasemen & Meta"
        
with col_nav2:
    if st.button("🛡️ Team Profiling", use_container_width=True):
        st.session_state['menu_ikl'] = "🛡️ Team Profiling"
        
with col_nav3:
    if st.button("⚔️ Versus Mode (H2H)", use_container_width=True):
        st.session_state['menu_ikl'] = "⚔️ Versus Mode (H2H)"

st.markdown("---")

# 3. Masukkan ke variabel utama agar if-elif di bawahnya tetap berfungsi
menu_utama = st.session_state['menu_ikl']
# endregion

# region HOME
# ==========================================
# HALAMAN 1: KLASEMEN, JADWAL & INSIGHT
# ==========================================
if menu_utama == "🏆 Klasemen & Meta":
    
    # --- BAGIAN ATAS: LEADERBOARD & UPCOMING MATCHES ---
    col_kiri, col_kanan = st.columns([1.4, 1])
    
    with col_kiri:
        st.markdown("### 🏆 Leaderboard IKL")
        
        # 1. Agregasi Level Match (Bukan Game)
        df_match = df_long.groupby(['Week', 'Day', 'Match', 'Team'], sort=False).agg(
            Game_W=('Win', 'sum'),
            Game_L=('Win', lambda x: (x == 0).sum())
        ).reset_index()
        
        # Tim menang Match jika jumlah Game Win > Game Loss
        df_match['Match_W'] = np.where(df_match['Game_W'] > df_match['Game_L'], 1, 0)
        df_match['Match_L'] = np.where(df_match['Game_W'] < df_match['Game_L'], 1, 0)
        
        # 2. Agregasi Total Level Tim
        klasemen_baru = df_match.groupby('Team').agg(
            Total_Match=('Match', 'count'),
            M_W=('Match_W', 'sum'),
            M_L=('Match_L', 'sum'),
            G_W=('Game_W', 'sum'),
            G_L=('Game_L', 'sum')
        ).reset_index()
        
        # 3. Format Kolom Sesuai Permintaan (Mengatasi Desimal)
        klasemen_baru['Match (W-L)'] = klasemen_baru['M_W'].astype(int).astype(str) + "-" + klasemen_baru['M_L'].astype(int).astype(str)
        klasemen_baru['Game (W-L)'] = klasemen_baru['G_W'].astype(int).astype(str) + "-" + klasemen_baru['G_L'].astype(int).astype(str)
        klasemen_baru['Skor Windiff'] = (klasemen_baru['G_W'] - klasemen_baru['G_L']).astype(int)
        klasemen_baru['Peringkat'] = klasemen_baru['Skor Windiff'].rank(method='min', ascending=False).astype(int)
        
        # Rapikan dan urutkan
        df_klasemen_tampil = klasemen_baru.sort_values(by='Peringkat')[
            ['Peringkat', 'Team', 'Total_Match', 'Match (W-L)', 'Game (W-L)', 'Skor Windiff']
        ]
        df_klasemen_tampil = df_klasemen_tampil.set_index('Peringkat')
        
        st.dataframe(df_klasemen_tampil, use_container_width=True)

    with col_kanan:
        st.markdown("### 📅 Upcoming Matches")
        
        df_jadwal = df_master[df_master['Status'] == 'Upcoming'].copy()
        
        if df_jadwal.empty:
            st.info("Belum ada jadwal pertandingan baru.")
        else:
            # Kamus Penerjemah Kode Pertandingan (Gabungan Week + Day)
            dict_match = {
                'Pl St': 'Play-in Stages',
                'Pl S': 'Play-in Stages',
                'Up Sf': 'Upperbracket Semifinal',
                'Lw Sf': 'Lowerbracket Semifinal',
                'Up Fl': 'Upperbracket Final',
                'Lw Fl': 'Lowerbracket Final',
                'Gr Fl': 'Grand Final'
            }
            
            st.markdown("<hr style='margin: 0px; border-top: 2px solid #555;'>", unsafe_allow_html=True)
            
            # Buat baris tanpa header tabel standar
            for idx, row in df_jadwal.iterrows():
                # Gabungkan Week dan Day untuk deteksi fase (Misal: 'Pl' + 'St' = 'Pl St')
                w_val = str(row['Week']).strip()
                d_val = str(row['Day']).strip()
                phase_key = f"{w_val} {d_val}"
                
                f_match = dict_match.get(phase_key, phase_key)
                
                # Tanggal / Nomor Match
                match_num = str(row['Match']).replace('.0', '').strip()
                tgl = f"Match {match_num}" if match_num not in ['0', 'nan'] else "-"
                
                # Nama Tim (Ubah nan menjadi TBD)
                tim_a = str(row['Team_(Blue)'])
                tim_b = str(row['Opponent_(Red)'])
                tim_a = "TBD" if tim_a == "nan" else tim_a
                tim_b = "TBD" if tim_b == "nan" else tim_b
                
                # Format Baris ala Ticket/Jadwal
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; font-size: 14px; padding: 10px 0px;'>
                    <div style='width: 45%; font-weight: bold; color: #00d2ff;'>{f_match}</div>
                    <div style='width: 20%; text-align: center; color: gray;'>{tgl}</div>
                    <div style='width: 35%; text-align: right;'><b>{tim_a}</b> ⚔️ <b>{tim_b}</b></div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<hr style='margin: 0px; border-top: 1px dashed #444;'>", unsafe_allow_html=True)

    # --- BAGIAN BAWAH: HIGHLIGHT & GLOBAL META (Satu Baris Penuh) ---
    st.markdown("---")
    st.markdown("### 📰 Highlight Turnamen")
    
    # Kalkulasi Winstreak Terpanjang (Game Level)
    winstreak_record = {}
    for team in df_long['Team'].unique():
        wins = df_long[df_long['Team'] == team]['Win'].tolist()
        max_streak, current_streak = 0, 0
        for w in wins:
            if w == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        winstreak_record[team] = max_streak
        
    tim_ws = max(winstreak_record, key=winstreak_record.get)
    max_ws = winstreak_record[tim_ws]
    
    # Kalkulasi Top Meta Global Cepat (Untuk Teks Berita)
    top_meta_nama = "Belum ada"
    top_meta_wr = 0
    if global_freq:
        valid_g = {k: v for k, v in global_freq.items() if v >= 5}
        if valid_g:
            teratas = sorted(valid_g.items(), key=lambda x: (len(x[0]), (global_wins[x[0]]/x[1])*100), reverse=True)[0]
            top_meta_nama = " & ".join(teratas[0])
            top_meta_wr = (global_wins[teratas[0]] / teratas[1]) * 100
    
    st.info(
        f"Sepanjang turnamen berlangsung, peta kekuatan meta sangat dipengaruhi oleh formasi "
        f"**{top_meta_nama}** yang sukses mencatatkan rasio kemenangan global hingga **{top_meta_wr:.0f}%**. "
        f"Di sisi lain, **{tim_ws}** tampil mengerikan dengan memegang rekor *winstreak* terpanjang, "
        f"menyapu bersih **{max_ws} game** secara beruntun tanpa balas."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔥 Global Meta Snapshot")
    st.markdown("Prioritas formasi terbesar. Jika ada Duo dan Trio bertarung, pemenang *winrate* akan menyala Merah (Supreme Meta).")
    
    # Threshold Statis: Minimal 5x main agar valid
    threshold_global = 5 
    
    global_valid = {}
    for combo, freq in global_freq.items():
        if freq >= threshold_global:
            wr = (global_wins[combo] / freq) * 100
            global_valid[combo] = {'freq': freq, 'wr': wr}
            
    # SELEKSI ALAM GLOBAL (Resolusi Konflik Subset)
    g_combos_to_remove = set()
    g_red_combos = set()
    
    sorted_g_combos = sorted(list(global_valid.keys()), key=lambda x: len(x), reverse=True)
    
    for i in range(len(sorted_g_combos)):
        c_large = sorted_g_combos[i]
        if c_large in g_combos_to_remove: continue
            
        for j in range(i + 1, len(sorted_g_combos)):
            c_small = sorted_g_combos[j]
            if c_small in g_combos_to_remove: continue
            
            if set(c_small).issubset(set(c_large)):
                wr_large = global_valid[c_large]['wr']
                wr_small = global_valid[c_small]['wr']
                f_large = global_valid[c_large]['freq']
                f_small = global_valid[c_small]['freq']
                
                if wr_small > wr_large:
                    g_combos_to_remove.add(c_large)
                    g_red_combos.add(c_small)
                elif wr_large > wr_small:
                    g_combos_to_remove.add(c_small)
                    g_red_combos.add(c_large)
                else:
                    if (f_small - f_large) < threshold_global:
                        g_combos_to_remove.add(c_small)

    kombo_g_final = {k: v for k, v in global_valid.items() if k not in g_combos_to_remove}
    top_global = sorted(kombo_g_final.items(), key=lambda x: (len(x[0]), x[1]['wr'], x[1]['freq']), reverse=True)[:6]
    
    if not top_global:
        st.warning("Belum ada kombo yang memenuhi syarat minimal 5x main.")
    else:
        cols_meta = st.columns(3)
        for idx, (combo, stats) in enumerate(top_global):
            nama_kombo = f"{', '.join(combo[:-1])} & {combo[-1]}"
            tipe = {2: "Duo", 3: "Trio", 4: "Quad", 5: "Quintet"}[len(combo)]
            
            if combo in g_red_combos:
                warna, ikon, kategori = "error", "🌟", "Supreme Meta (Winrate Winner)"
            else:
                warna, ikon, kategori = "warning", "🔥", "Global Meta (Max Size)"
                
            teks = f"**{nama_kombo}**\n\n🎯 {tipe} Pick: **{stats['freq']}x**\n🏆 Global WR: **{stats['wr']:.0f}%**\n📊 Kategori: **{kategori}**"
            
            with cols_meta[idx % 3]:
                if warna == "error": st.error(f"{ikon} {teks}")
                else: st.warning(f"{ikon} {teks}")
# endregion

# region PROFILING
# ==========================================
# HALAMAN 2: TEAM PROFILING
# ==========================================
elif menu_utama == "🛡️ Team Profiling":
    st.title("🛡️ Profiling Tim IKL - Honor of Kings")
    
    # 1. Inisialisasi memori untuk halaman Profiling
    if 'profiling_team' not in st.session_state:
        st.session_state['profiling_team'] = None

    daftar_tim = sorted(rapor_radar['Team'].unique())

    # 2. KONDISI A: Tampilkan Grid jika belum ada tim yang dipilih
    if st.session_state['profiling_team'] is None:
        st.markdown("### 🔍 Pilih Tim untuk Dianalisis")
        st.markdown("---")
        
        # Membuat Grid 4 Kolom
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                # Jika tombol ditekan, simpan nama tim ke memori dan muat ulang halaman
                if st.button(tim, use_container_width=True, key=f"btn_{tim}"):
                    st.session_state['profiling_team'] = tim
                    st.rerun()

    # 3. KONDISI B: Tampilkan Data Profiling jika tim sudah dipilih
    else:
        tim_pilihan = st.session_state['profiling_team']
        
        # Tombol navigasi: Kembali dan Shortcut Versus
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1.5, 3.5])
        
        with col_nav1:
            if st.button("🔙 Kembali", use_container_width=True):
                st.session_state['profiling_team'] = None
                st.rerun()
                
        with col_nav2:
            # SHORTCUT AJAIB KE H2H
            if st.button("⚔️ Bandingkan (H2H)", use_container_width=True):
                st.session_state['h2h_team_A'] = tim_pilihan # Jadikan tim ini sebagai Tim 1
                st.session_state['h2h_team_B'] = None        # Kosongkan lawan (berjaga-jaga)
                st.session_state['menu_ikl'] = "⚔️ Versus Mode (H2H)" # Pindah Halaman
                st.rerun()
                
        with col_nav3:
            st.markdown(f"### Analisis Mendalam: {tim_pilihan}")
        
        st.markdown("---")
        data_tim = rapor_radar[rapor_radar['Team'] == tim_pilihan]

        # --- Bagian 1: Radar Chart ---
        kategori_metrik = ['Dominance_100', 'Toughness_100', 'Discipline_100', 
                           'Volatility_100', 'TeamFight_100', 'Flexibility_100']
        skor_tim = data_tim[kategori_metrik].values.flatten().tolist()
        skor_tim.append(skor_tim[0])
        
        kategori_radar = ['Dominance', 'Toughness', 'Discipline', 'Volatility', 'Team Fight', 'Flexibility']
        kategori_radar.append(kategori_radar[0])

        fig = px.line_polar(
            r=skor_tim, theta=kategori_radar, line_close=True,
            range_r=[0, 100]
        )
        fig.update_traces(fill='toself', line_color='cyan')
        fig.update_layout(
            polar=dict(radialaxis=dict(showticklabels=False, showline=False, ticks='')),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Bagian 2: Memanggil Mesin Kombo ---
        st.markdown("---")
        st.subheader("🔥 Signature Hero Combo (Evolusi Taktik)")
        
        kombo_A = get_signature_combos(tim_pilihan)
        
        if not kombo_A:
            st.info(f"Tim {tim_pilihan} belum memiliki kombinasi andalan yang lolos evaluasi taktik.")
        else:
            cols = st.columns(len(kombo_A))
            for idx, k in enumerate(kombo_A):
                with cols[idx]:
                    if k["warna"] == "error": st.error(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "warning": st.warning(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "success": st.success(f"{k['ikon']} {k['teks']}")
# endregion

# region H2H
# ==========================================
# HALAMAN 3: VERSUS MODE (H2H)
# ==========================================
elif menu_utama == "⚔️ Versus Mode (H2H)":
    st.title("⚔️ H2H: Duel Mekanik & Taktik")

    # 1. Inisialisasi 2 Memori Tim
    if 'h2h_team_A' not in st.session_state:
        st.session_state['h2h_team_A'] = None
    if 'h2h_team_B' not in st.session_state:
        st.session_state['h2h_team_B'] = None

    daftar_tim = sorted(rapor_radar['Team'].unique())

    # 2. TAHAP 1: Pilih Tim Kiri (Tim A)
    if st.session_state['h2h_team_A'] is None:
        st.markdown("### 🔴 Pilih Tim 1 (Sisi Kiri)")
        st.markdown("---")
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                if st.button(tim, use_container_width=True, key=f"btn_A_{tim}"):
                    st.session_state['h2h_team_A'] = tim
                    st.rerun()

    # 3. TAHAP 2: Pilih Tim Kanan (Tim B)
    elif st.session_state['h2h_team_B'] is None:
        tim_A = st.session_state['h2h_team_A']
        
        st.markdown("### ⚔️ Versus Mode: Pilih Lawan")
        
        # Desain 2 Slot (Kiri Terisi, Kanan Kosong)
        col_slot1, col_slot2 = st.columns(2)
        
        with col_slot1:
            st.info("🔴 Sisi Kiri (Tim 1)")
            # Tombol ini seolah-olah "Ikon" tim yang sudah terpilih. 
            # Kalau diklik, memori Tim 1 dihapus (kembali ke tahap 1)
            if st.button(f"✨ {tim_A} (Klik untuk ganti)", use_container_width=True, key="btn_reset_A"):
                st.session_state['h2h_team_A'] = None
                st.rerun()
                
        with col_slot2:
            st.warning("🔵 Sisi Kanan (Tim 2)")
            # Placeholder untuk slot kedua yang masih menunggu
            st.button("Menunggu pilihan...", use_container_width=True, disabled=True)
            
        st.markdown("---")
        st.markdown(f"**Pilih lawan dari daftar di bawah ini untuk menantang {tim_A}:**")
        
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                # Kunci tombol jika tim sama dengan Tim A
                if tim == tim_A:
                    st.button(f"🔒 {tim}", use_container_width=True, disabled=True, key=f"btn_B_{tim}")
                else:
                    if st.button(tim, use_container_width=True, key=f"btn_B_{tim}"):
                        st.session_state['h2h_team_B'] = tim
                        st.rerun()

    # 4. TAHAP 3: Tampilkan H2H Dashboard
    else:
        tim_A = st.session_state['h2h_team_A']
        tim_B = st.session_state['h2h_team_B']

        col_nav1, col_nav2 = st.columns([1, 4])
        with col_nav1:
            if st.button("🔄 Ganti Pertandingan", use_container_width=True):
                st.session_state['h2h_team_A'] = None
                st.session_state['h2h_team_B'] = None
                st.rerun()
        with col_nav2:
            st.markdown(f"### Duel: {tim_A} vs {tim_B}")
        
        st.markdown("---")

        # --- Bagian 1: Overlay Radar Tumpuk ---
        data_A = rapor_radar[rapor_radar['Team'] == tim_A].iloc[0]
        data_B = rapor_radar[rapor_radar['Team'] == tim_B].iloc[0]

        kategori = ['Dominance_100', 'Toughness_100', 'Discipline_100', 'Volatility_100', 'TeamFight_100', 'Flexibility_100']
        kategori_label = ['Dominance', 'Toughness', 'Discipline', 'Volatility', 'Team Fight', 'Flexibility']
        
        skor_A = data_A[kategori].values.flatten().tolist()
        skor_B = data_B[kategori].values.flatten().tolist()
        skor_A.append(skor_A[0])
        skor_B.append(skor_B[0])
        kategori_label.append(kategori_label[0])

        fig_h2h = go.Figure()
        fig_h2h.add_trace(go.Scatterpolar(
            r=skor_A, theta=kategori_label, fill='toself', 
            name=tim_A, line_color='cyan', fillcolor='rgba(0, 255, 255, 0.3)'
        ))
        fig_h2h.add_trace(go.Scatterpolar(
            r=skor_B, theta=kategori_label, fill='toself', 
            name=tim_B, line_color='magenta', fillcolor='rgba(255, 0, 255, 0.3)'
        ))
        fig_h2h.update_layout(
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.1, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_h2h, use_container_width=True)

        # --- Bagian 2: Adu Mekanik Kombo Side-by-Side ---
        st.markdown("---")
        st.subheader("🔥 Clash of Signatures (Top 3 Combos)")
        
        kombo_A = get_signature_combos(tim_A)
        kombo_B = get_signature_combos(tim_B)
        
        col_combo_A, divider, col_combo_B = st.columns([1, 0.05, 1])
        
        with col_combo_A:
            st.markdown(f"<h4 style='text-align: center; color: cyan;'>{tim_A}</h4>", unsafe_allow_html=True)
            if not kombo_A:
                st.info("Belum ada kombinasi andalan.")
            else:
                for k in kombo_A:
                    if k["warna"] == "error": st.error(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "warning": st.warning(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "success": st.success(f"{k['ikon']} {k['teks']}")
                
        with divider:
            st.markdown("<div style='border-left: 2px solid gray; height: 100%; min-height: 250px;'></div>", unsafe_allow_html=True)

        with col_combo_B:
            st.markdown(f"<h4 style='text-align: center; color: magenta;'>{tim_B}</h4>", unsafe_allow_html=True)
            if not kombo_B:
                st.info("Belum ada kombinasi andalan.")
            else:
                for k in kombo_B:
                    if k["warna"] == "error": st.error(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "warning": st.warning(f"{k['ikon']} {k['teks']}")
                    elif k["warna"] == "success": st.success(f"{k['ikon']} {k['teks']}")
# endregion
       
# endregion             