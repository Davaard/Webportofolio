import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ==========================================
# FASE 1: IMPORT & TRANSFORMASI DATA
# ==========================================

# 1. Baca data mentah 
# Ubah baris ini:
df_raw = pd.read_csv("Data_Set_IKL_HOK.csv")

# 2. Ambil dari sudut pandang Sisi Biru (Sebagai Tim Utama)
df_A = df_raw.copy()
df_A = df_A[['Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)', 'Result', 'Duration_min', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 'Heroes_Picked', 'Opponent_Picked']]
# Standarisasi nama kolom agar mudah dipanggil di rumus selanjutnya
kolom_standar = ['Week', 'Day', 'Match', 'Game', 'Team', 'Opponent', 'Win', 'Durasi', 'Gold', 'Opp_Gold', 'Kill', 'Opp_Kill', 'Ast', 'Opp_Ast', 'Obj', 'Opp_Obj', 'Heroes', 'Opp_Heroes']
df_A.columns = kolom_standar

# 3. Ambil dari sudut pandang Sisi Merah (Sebagai Tim Utama)
df_B = df_raw.copy()
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

# ==========================================
# FASE 8: NORMALISASI MIN-MAX SCALING (0 - 100)
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

# Lakukan scaling 0-100 untuk setiap kolom
for col in metrik_mentah:
    min_val = rapor_akhir[col].min()
    max_val = rapor_akhir[col].max()
    
    # Rumus Min-Max: ((Nilai - Min) / (Max - Min)) * 100
    nama_kolom_baru = col.replace('_Skor', '_100')
    rapor_akhir[nama_kolom_baru] = ((rapor_akhir[col] - min_val) / (max_val - min_val)) * 100

# Buat dataframe final yang hanya berisi kolom 0-100 agar rapi untuk Streamlit
kolom_final = ['Team'] + [col.replace('_Skor', '_100') for col in metrik_mentah]
rapor_radar = rapor_akhir[kolom_final].round(2)

st.title("🛡️ Profiling Tim IKL - Honor of Kings")
st.write("Dashboard ini menganalisis kekuatan tim menggunakan model Hexagon Radar.")

# Bikin Dropdown
tim_pilihan = st.selectbox("Pilih Tim:", options=rapor_radar['Team'].unique())

# Filter data sesuai tim yang dipilih
data_tim = rapor_radar[rapor_radar['Team'] == tim_pilihan]

# Siapkan data untuk grafik
kategori_metrik = ['Dominance_100', 'Toughness_100', 'Discipline_100', 
                   'Volatility_100', 'TeamFight_100', 'Flexibility_100']

skor_tim = data_tim[kategori_metrik].values.flatten().tolist()
# Tambahkan elemen pertama ke akhir agar garis radar menyambung
skor_tim.append(skor_tim[0])
kategori_radar = ['Dominance', 'Toughness', 'Discipline', 'Volatility', 'Team Fight', 'Flexibility']
kategori_radar.append(kategori_radar[0])

# Gambar Hexagon Radar
fig = px.line_polar(
    r=skor_tim, 
    theta=kategori_radar, 
    line_close=True,
    title=f"Hexagon Radar: {tim_pilihan}",
    range_r=[0, 100]
)
fig.update_traces(fill='toself', line_color='cyan')
fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)") # Transparan

# Tampilkan di website
st.plotly_chart(fig)

# Tampilkan tabel mentahnya juga di bawah grafik
st.subheader("Data Skor (Skala 0-100)")
st.dataframe(data_tim)