# region INISIALISASI
import os
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
    df = pd.read_csv(filepath)
    df['Week_str'] = df['Week'].fillna('').astype(str)
    df['Day_str'] = df['Day'].fillna('').astype(str)
    df['Match_str'] = df['Match'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
    df['Game_str'] = df['Game'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
    df['Match_ID'] = 'IKL' + df['Week_str'] + df['Day_str'] + df['Match_str'] + df['Game_str']
    df['Status'] = df['Result'].apply(lambda x: 'Upcoming' if pd.isna(x) else 'History')
    df = df.drop(columns=['Week_str', 'Day_str', 'Match_str', 'Game_str'])
    return df
# endregion

# region PRA-PEMPROSESAN
# ==========================================
# FASE 1: IMPORT & TRANSFORMASI DATA
# ==========================================
df_master = load_and_preprocess_data("Data_Set_IKL_HOK.csv")
df_history = df_master[df_master['Status'] == 'History'].copy()

df_A = df_history.copy()
df_A = df_A[['Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)', 'Result', 'Duration_min', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 'Heroes_Picked', 'Opponent_Picked']]
kolom_standar = ['Week', 'Day', 'Match', 'Game', 'Team', 'Opponent', 'Win', 'Durasi', 'Gold', 'Opp_Gold', 'Kill', 'Opp_Kill', 'Ast', 'Opp_Ast', 'Obj', 'Opp_Obj', 'Heroes', 'Opp_Heroes']
df_A.columns = kolom_standar

df_B = df_history.copy()
df_B['Result_Red'] = 1 - df_B['Result'] 
df_B = df_B[['Week', 'Day', 'Match', 'Game', 'Opponent_(Red)', 'Team_(Blue)', 'Result_Red', 'Duration_min', 'O_Gold', 'T_Gold', 'O_Kill', 'T_Kill', 'O_Assist', 'T_Assist', 'O_Objective', 'T_Objective', 'Opponent_Picked', 'Heroes_Picked']]
df_B.columns = kolom_standar

df_long = pd.concat([df_A, df_B], ignore_index=True)
df_long = df_long.sort_values(by=['Week', 'Day', 'Match', 'Game']).reset_index(drop=True)

df_long['Heroes'] = df_long['Heroes'].astype(str).apply(lambda x: [hero.strip() for hero in x.split(',')])
df_long['Opp_Heroes'] = df_long['Opp_Heroes'].astype(str).apply(lambda x: [hero.strip() for hero in x.split(',')])
# endregion

# region RADAR PENILAIAN

# region DOMINASI
klasemen = df_long.groupby('Team')['Win'].agg(
    Total_Menang='sum',
    Total_Kalah=lambda x: (x == 0).sum()
).reset_index()

klasemen['Skor_IKL'] = klasemen['Total_Menang'] - klasemen['Total_Kalah']
klasemen['Rank_Akhir'] = klasemen['Skor_IKL'].rank(method='min', ascending=False)

df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], on='Team', how='left').rename(columns={'Rank_Akhir': 'T_Rank'})
df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], left_on='Opponent', right_on='Team', how='left', suffixes=('', '_drop')).rename(columns={'Rank_Akhir': 'O_Rank'})
df_long = df_long.drop(columns=['Team_drop'], errors='ignore') 

df_long['Points_Ratio'] = (df_long['Gold'] / df_long['Opp_Gold']) + (df_long['Kill'] / (df_long['Opp_Kill'] + 1))
df_long['Points_Won'] = np.where(df_long['Win'] == 1, df_long['Points_Ratio'], np.nan)
df_long['Points_Lost'] = np.where(df_long['Win'] == 0, df_long['Points_Ratio'], np.nan)

dominasi_df = df_long.groupby('Team').agg(
    Total_Wins=('Win', 'sum'),
    Total_Losses=('Win', lambda x: (x == 0).sum()),
    Sum_Points_Won=('Points_Won', 'sum'),
    Sum_Points_Lost=('Points_Lost', 'sum')
).reset_index()

dominasi_df.fillna(0, inplace=True)
dominasi_df['Dominance_Skor'] = (
    (dominasi_df['Sum_Points_Won'] / (dominasi_df['Total_Losses'] + 1)) - 
    (dominasi_df['Sum_Points_Lost'] / (dominasi_df['Total_Wins'] + 1))
)
# endregion

# region KETANGGUHAN
def konversi_waktu(waktu):
    waktu = str(waktu).strip()
    if ':' in waktu:
        menit, detik = waktu.split(':')
        return float(menit) + (float(detik) / 60.0)
    return float(waktu)

df_long['Durasi'] = df_long['Durasi'].apply(konversi_waktu)
df_long['Kill'] = pd.to_numeric(df_long['Kill'], errors='coerce').fillna(0)
df_long['Opp_Kill'] = pd.to_numeric(df_long['Opp_Kill'], errors='coerce').fillna(0)

df_long['Defense_Multiplier'] = df_long['Opp_Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)
df_long['Offense_Multiplier'] = df_long['Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)

df_long['Durasi_Menang_Berbobot'] = np.where(df_long['Win'] == 1, df_long['Durasi'] * df_long['Offense_Multiplier'], np.nan)
df_long['Durasi_Kalah_Berbobot'] = np.where(df_long['Win'] == 0, df_long['Durasi'] * df_long['Defense_Multiplier'], np.nan)

seasonal_win_dur = df_long.groupby('Team')['Durasi_Menang_Berbobot'].mean().reset_index()
seasonal_win_dur.rename(columns={'Durasi_Menang_Berbobot': 'Seasonal_Avg_Win_Bobot'}, inplace=True)
seasonal_win_dur['Seasonal_Avg_Win_Bobot'] = seasonal_win_dur['Seasonal_Avg_Win_Bobot'].fillna(7.5) 

series_df = df_long.groupby(['Week', 'Day', 'Match', 'Team']).agg(
    Avg_Win_Series=('Durasi_Menang_Berbobot', 'mean'),
    Avg_Loss_Series=('Durasi_Kalah_Berbobot', 'mean')
).reset_index()

series_df = series_df.merge(seasonal_win_dur, on='Team', how='left')
series_df['Avg_Win_Series'] = series_df['Avg_Win_Series'].fillna(series_df['Seasonal_Avg_Win_Bobot'])
series_df['Series_Toughness'] = series_df['Avg_Loss_Series'] - series_df['Avg_Win_Series']

toughness_df = series_df.groupby('Team').agg(
    Toughness_Skor=('Series_Toughness', 'mean')
).reset_index()
toughness_df['Toughness_Skor'] = toughness_df['Toughness_Skor'].fillna(0)

rapor_akhir = pd.merge(dominasi_df[['Team', 'Dominance_Skor']], toughness_df[['Team', 'Toughness_Skor']], on='Team')
# endregion

# region KEDISIPLINAN
df_long['Obj'] = pd.to_numeric(df_long['Obj'], errors='coerce').fillna(0)
df_long['Opp_Obj'] = pd.to_numeric(df_long['Opp_Obj'], errors='coerce').fillna(0)
df_long['Tim_Obj_Score'] = (df_long['Obj'] ** 2) / (df_long['Obj'] + df_long['Kill'] + 1)
df_long['Musuh_Obj_Score'] = (df_long['Opp_Obj'] ** 2) / (df_long['Opp_Obj'] + df_long['Opp_Kill'] + 1)
df_long['Discipline_Game'] = (df_long['Tim_Obj_Score'] - df_long['Musuh_Obj_Score']) / df_long['Durasi']

discipline_df = df_long.groupby('Team').agg(
    Discipline_Skor=('Discipline_Game', 'mean')
).reset_index()

rapor_akhir = pd.merge(rapor_akhir, discipline_df[['Team', 'Discipline_Skor']], on='Team')
# endregion

# region FOLATILITAS
df_long['GPM'] = df_long['Gold'] / df_long['Durasi']
volatility_df = df_long.groupby('Team').agg(
    Volatility=('GPM', 'std') 
).reset_index()
volatility_df['Volatility'] = volatility_df['Volatility'].fillna(0)

won_games = df_long[df_long['Win'] == 1]
best_win = won_games.groupby('Team')['O_Rank'].min().reset_index()
best_win.rename(columns={'O_Rank': 'Best_Win_Rank'}, inplace=True)

lost_games = df_long[df_long['Win'] == 0]
worst_loss = lost_games.groupby('Team')['O_Rank'].max().reset_index()
worst_loss.rename(columns={'O_Rank': 'Worst_Loss_Rank'}, inplace=True)

volatility_df = volatility_df.merge(best_win, on='Team', how='left')
volatility_df = volatility_df.merge(worst_loss, on='Team', how='left')
volatility_df['Best_Win_Rank'] = volatility_df['Best_Win_Rank'].fillna(10)
volatility_df['Worst_Loss_Rank'] = volatility_df['Worst_Loss_Rank'].fillna(1)

volatility_df['Giant_Slayer_Ratio'] = volatility_df['Worst_Loss_Rank'] / volatility_df['Best_Win_Rank']
volatility_df['Volatility_Skor'] = volatility_df['Volatility'] * volatility_df['Giant_Slayer_Ratio']
rapor_akhir = pd.merge(rapor_akhir, volatility_df[['Team', 'Volatility_Skor']], on='Team')
# endregion

# region TEAMFIGHT
df_long['Ast'] = pd.to_numeric(df_long['Ast'], errors='coerce').fillna(0)
df_long['Opp_Ast'] = pd.to_numeric(df_long['Opp_Ast'], errors='coerce').fillna(0)
df_long['Team_Assist_Ratio'] = df_long['Ast'] / (df_long['Kill'] + 1)
df_long['Opp_Assist_Ratio'] = df_long['Opp_Ast'] / (df_long['Opp_Kill'] + 1)
df_long['TeamFight_Game'] = df_long['Team_Assist_Ratio'] - df_long['Opp_Assist_Ratio']

teamfight_df = df_long.groupby('Team').agg(
    TeamFight_Skor=('TeamFight_Game', 'mean')
).reset_index()
rapor_akhir = pd.merge(rapor_akhir, teamfight_df[['Team', 'TeamFight_Skor']], on='Team')
# endregion

# region FLEKSIBILITAS
import ast
def parse_heroes(val):
    if isinstance(val, list):
        return val
    try:
        return ast.literal_eval(val)
    except:
        return [h.strip() for h in str(val).split(',') if h.strip()]

df_long['Heroes_List'] = df_long['Heroes'].apply(parse_heroes)
flexibility_df = df_long.explode('Heroes_List').groupby('Team')['Heroes_List'].nunique().reset_index()
flexibility_df.rename(columns={'Heroes_List': 'Flexibility_Skor'}, inplace=True)
rapor_akhir = pd.merge(rapor_akhir, flexibility_df[['Team', 'Flexibility_Skor']], on='Team')
# endregion

# region NORMALISASI
metrik_mentah = ['Dominance_Skor', 'Toughness_Skor', 'Discipline_Skor', 'Volatility_Skor', 'TeamFight_Skor', 'Flexibility_Skor']

for col in metrik_mentah:
    min_val = rapor_akhir[col].min()
    max_val = rapor_akhir[col].max()
    nama_kolom_baru = col.replace('_Skor', '_100')
    if max_val == min_val:
        rapor_akhir[nama_kolom_baru] = 100.0
    else:
        rapor_akhir[nama_kolom_baru] = ((rapor_akhir[col] - min_val) / (max_val - min_val)) * 80 + 20

kolom_final = ['Team'] + [col.replace('_Skor', '_100') for col in metrik_mentah]
rapor_radar = rapor_akhir[kolom_final].round(2)
# endregion

# endregion

# region KOMBINASI
# ==========================================
# FASE 9: MESIN EVOLUSI KOMBO (FUNGSI GLOBAL)
# ==========================================
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

    team_valid = {}
    for combo, freq in team_freq.items():
        sz = len(combo)
        if (sz == 2 and freq >= 3) or (sz == 3 and freq >= 3) or (sz >= 4 and freq >= 2):
            wr_tim = (team_wins[combo] / freq) * 100
            team_valid[combo] = {'freq': freq, 'wr': wr_tim}

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
        
        # Tambahan pengiriman array combo ke UI
        hasil_ui.append({"warna": warna, "ikon": ikon, "teks": teks, "combo": combo})
        
    return hasil_ui
# endregion

# region DISPLAY

# region LOAD ASET
# ==========================================
# FUNGSI PEMBANTU VISUAL ASET (DENGAN CUSTOM UI CARD)
# ==========================================
import os
import base64

def get_logo_path(team_name):
    team_mapping = {
        "AE": "Alter_Ego_Esports", "OG": "OG_Esports", "DESJ": "Deuscard_x_Sriwijaya_Esports",
        "BTR": "Bigetron_by_Vitality", "ONIC": "ONIC", "CARS": "Carstensz_DuskMaven",
        "DMT": "DOMINATOR_by_NEMESIS", "RRQ": "Rex_Regum_Qeon", "KAGE": "Kagendra",
        "MAVE": "Mahadewa_Vesakha"
    }
    nama_lengkap = team_mapping.get(team_name, team_name)
    safe_name = nama_lengkap.replace(" ", "_")
    for ext in ['.png', '.jpg', '.jpeg']:
        path = f"assets/logos/{safe_name}{ext}"
        if os.path.exists(path): return path
    return None

def get_hero_path(hero_name):
    safe_name = hero_name.replace(" ", "_").replace(".png", "").replace(".jpg", "")
    for ext in ['.png', '.jpg', '.jpeg']:
        path = f"assets/heroes/{safe_name}{ext}"
        if os.path.exists(path): return path
    return None

# Fungsi pengubah gambar menjadi kode sandi (Base64) agar bisa masuk ke HTML
def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# FUNGSI BARU: Perender Kartu Satu Kesatuan
def render_combo_card(combo_tuple, warna, ikon, teks):
    # Definisi palet warna Streamlit
    tema_warna = {
        "error": {"bg": "rgba(255, 75, 75, 0.15)", "border": "rgba(255, 75, 75, 1)"},
        "warning": {"bg": "rgba(255, 190, 0, 0.15)", "border": "rgba(255, 190, 0, 1)"},
        "success": {"bg": "rgba(9, 171, 59, 0.15)", "border": "rgba(9, 171, 59, 1)"}
    }
    
    bg = tema_warna[warna]["bg"]
    brdr = tema_warna[warna]["border"]
    
    # Merakit deretan 5 gambar
    img_html = "<div style='display: flex; gap: 2%; margin-bottom: 12px;'>"
    for i in range(5):
        if i < len(combo_tuple):
            path = get_hero_path(combo_tuple[i])
            if path:
                b64 = image_to_base64(path)
                # Gambar hero HD
                img_html += f"<img src='data:image/png;base64,{b64}' style='width: 18.4%; border-radius: 8px; box-shadow: 1px 2px 5px rgba(0,0,0,0.3); object-fit: cover; aspect-ratio: 1/1;'>"
            else:
                img_html += f"<div style='width: 18.4%; background: #444; border-radius: 8px; display:flex; align-items:center; justify-content:center; font-size:10px; text-align:center; aspect-ratio: 1/1;'>{combo_tuple[i]}</div>"
        else:
            # Slot kosong transparan (agar ukurannya tetap absolut)
            img_html += "<div style='width: 18.4%; aspect-ratio: 1/1;'></div>"
    img_html += "</div>"
    
    # Merapikan Teks (Ubah markdown ke HTML)
    teks_html = teks.replace('\n', '<br>').replace('**', '<b>')
    
    # Merakit Kartu Utuh
    html_final = f"""
    <div style='background-color: {bg}; border-left: 5px solid {brdr}; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
        {img_html}
        <div style='font-size: 14.5px; line-height: 1.5; color: white;'>
            <b>{ikon}</b> {teks_html}
        </div>
    </div>
    """
    
    # Suntikkan ke layar!
    st.markdown(html_final, unsafe_allow_html=True)
# endregion

# region NAVIGASI
st.markdown("### 🎮 IKL Dashboard")

if "menu_ikl" not in st.session_state:
    st.session_state['menu_ikl'] = "🏆 Klasemen & Meta"

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
menu_utama = st.session_state['menu_ikl']
# endregion

# region HOME
if menu_utama == "🏆 Klasemen & Meta":
    col_kiri, col_kanan = st.columns([1.4, 1])
    
    with col_kiri:
        st.markdown("### 🏆 Leaderboard IKL")
        
        df_match = df_long.groupby(['Week', 'Day', 'Match', 'Team'], sort=False).agg(
            Game_W=('Win', 'sum'),
            Game_L=('Win', lambda x: (x == 0).sum())
        ).reset_index()
        
        df_match['Match_W'] = np.where(df_match['Game_W'] > df_match['Game_L'], 1, 0)
        df_match['Match_L'] = np.where(df_match['Game_W'] < df_match['Game_L'], 1, 0)
        
        klasemen_baru = df_match.groupby('Team').agg(
            Total_Match=('Match', 'count'),
            M_W=('Match_W', 'sum'),
            M_L=('Match_L', 'sum'),
            G_W=('Game_W', 'sum'),
            G_L=('Game_L', 'sum')
        ).reset_index()
        
        klasemen_baru['Match (W-L)'] = klasemen_baru['M_W'].astype(int).astype(str) + "-" + klasemen_baru['M_L'].astype(int).astype(str)
        klasemen_baru['Game (W-L)'] = klasemen_baru['G_W'].astype(int).astype(str) + "-" + klasemen_baru['G_L'].astype(int).astype(str)
        klasemen_baru['Skor Windiff'] = (klasemen_baru['G_W'] - klasemen_baru['G_L']).astype(int)
        klasemen_baru['Peringkat'] = klasemen_baru['Skor Windiff'].rank(method='min', ascending=False).astype(int)
        
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
            for idx, row in df_jadwal.iterrows():
                w_val = str(row['Week']).strip()
                d_val = str(row['Day']).strip()
                phase_key = f"{w_val} {d_val}"
                
                f_match = dict_match.get(phase_key, phase_key)
                match_num = str(row['Match']).replace('.0', '').strip()
                tgl = f"Match {match_num}" if match_num not in ['0', 'nan'] else "-"
                
                tim_a = str(row['Team_(Blue)'])
                tim_b = str(row['Opponent_(Red)'])
                tim_a = "TBD" if tim_a == "nan" else tim_a
                tim_b = "TBD" if tim_b == "nan" else tim_b
                
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; font-size: 14px; padding: 10px 0px;'>
                    <div style='width: 45%; font-weight: bold; color: #00d2ff;'>{f_match}</div>
                    <div style='width: 20%; text-align: center; color: gray;'>{tgl}</div>
                    <div style='width: 35%; text-align: right;'><b>{tim_a}</b> ⚔️ <b>{tim_b}</b></div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<hr style='margin: 0px; border-top: 1px dashed #444;'>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📰 Highlight Turnamen")
    
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
    
    threshold_global = 5 
    global_valid = {}
    for combo, freq in global_freq.items():
        if freq >= threshold_global:
            wr = (global_wins[combo] / freq) * 100
            global_valid[combo] = {'freq': freq, 'wr': wr}
            
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
                # Merender Ikon Hero
               render_combo_card(combo, warna, ikon, teks)
# endregion

# region PROFILING
elif menu_utama == "🛡️ Team Profiling":
    st.title("🛡️ Profiling Tim IKL - Honor of Kings")
    
    if 'profiling_team' not in st.session_state:
        st.session_state['profiling_team'] = None

    daftar_tim = sorted(rapor_radar['Team'].unique())

    if st.session_state['profiling_team'] is None:
        st.markdown("### 🔍 Pilih Tim untuk Dianalisis")
        st.markdown("---")
        
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                logo_path = get_logo_path(tim)
                if logo_path:
                    # Menambahkan perataan ke tengah menggunakan HTML kosong
                    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
                    with col_logo2:
                        st.image(logo_path, use_container_width=True)
                
                if st.button(tim, use_container_width=True, key=f"btn_{tim}"):
                    st.session_state['profiling_team'] = tim
                    st.rerun()

    else:
        tim_pilihan = st.session_state['profiling_team']
        
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1.5, 3.5])
        
        with col_nav1:
            if st.button("🔙 Kembali", use_container_width=True):
                st.session_state['profiling_team'] = None
                st.rerun()
                
        with col_nav2:
            if st.button("⚔️ Bandingkan (H2H)", use_container_width=True):
                st.session_state['h2h_team_A'] = tim_pilihan 
                st.session_state['h2h_team_B'] = None        
                st.session_state['menu_ikl'] = "⚔️ Versus Mode (H2H)" 
                st.rerun()
                
        with col_nav3:
            st.markdown(f"### Analisis Mendalam: {tim_pilihan}")
        
        st.markdown("---")
        data_tim = rapor_radar[rapor_radar['Team'] == tim_pilihan]

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

        st.markdown("---")
        st.subheader("🔥 Signature Hero Combo (Evolusi Taktik)")
        
        kombo_A = get_signature_combos(tim_pilihan)
        
        if not kombo_A:
            st.info(f"Tim {tim_pilihan} belum memiliki kombinasi andalan yang lolos evaluasi taktik.")
        else:
            cols = st.columns(len(kombo_A))
            for idx, k in enumerate(kombo_A):
                with cols[idx]:
                    # Merender Ikon Pahlawan
                    render_combo_card(k["combo"], k["warna"], k["ikon"], k["teks"])
# endregion

# region H2H
elif menu_utama == "⚔️ Versus Mode (H2H)":
    st.title("⚔️ H2H: Duel Mekanik & Taktik")

    if 'h2h_team_A' not in st.session_state:
        st.session_state['h2h_team_A'] = None
    if 'h2h_team_B' not in st.session_state:
        st.session_state['h2h_team_B'] = None

    daftar_tim = sorted(rapor_radar['Team'].unique())

    if st.session_state['h2h_team_A'] is None:
        st.markdown("### 🔴 Pilih Tim 1 (Sisi Kiri)")
        st.markdown("---")
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                # Render Logo
                logo_path = get_logo_path(tim)
                if logo_path:
                    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
                    with col_logo2:
                        st.image(logo_path, use_container_width=True)
                
                if st.button(tim, use_container_width=True, key=f"btn_A_{tim}"):
                    st.session_state['h2h_team_A'] = tim
                    st.rerun()

    elif st.session_state['h2h_team_B'] is None:
        tim_A = st.session_state['h2h_team_A']
        
        st.markdown("### ⚔️ Versus Mode: Pilih Lawan")
        col_slot1, col_slot2 = st.columns(2)
        
        with col_slot1:
            st.info("🔴 Sisi Kiri (Tim 1)")
            logo_A = get_logo_path(tim_A)
            if logo_A:
                col_A1, col_A2, col_A3 = st.columns([1.5, 1, 1.5])
                with col_A2:
                    st.image(logo_A, use_container_width=True)
                    
            if st.button(f"✨ {tim_A} (Klik untuk ganti)", use_container_width=True, key="btn_reset_A"):
                st.session_state['h2h_team_A'] = None
                st.rerun()
                
        with col_slot2:
            st.warning("🔵 Sisi Kanan (Tim 2)")
            st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True) # Spacer
            st.button("Menunggu pilihan...", use_container_width=True, disabled=True)
            
        st.markdown("---")
        st.markdown(f"**Pilih lawan dari daftar di bawah ini untuk menantang {tim_A}:**")
        
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                logo_path = get_logo_path(tim)
                if logo_path:
                    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
                    with col_logo2:
                        st.image(logo_path, use_container_width=True)
                        
                if tim == tim_A:
                    st.button(f"🔒 {tim}", use_container_width=True, disabled=True, key=f"btn_B_{tim}")
                else:
                    if st.button(tim, use_container_width=True, key=f"btn_B_{tim}"):
                        st.session_state['h2h_team_B'] = tim
                        st.rerun()

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
                    render_combo_card(k["combo"], k["warna"], k["ikon"], k["teks"])
                
        with divider:
            st.markdown("<div style='border-left: 2px solid gray; height: 100%; min-height: 250px;'></div>", unsafe_allow_html=True)

        with col_combo_B:
            st.markdown(f"<h4 style='text-align: center; color: magenta;'>{tim_B}</h4>", unsafe_allow_html=True)
            if not kombo_B:
                st.info("Belum ada kombinasi andalan.")
            else:
                for k in kombo_B:
                    render_combo_card(k["combo"], k["warna"], k["ikon"], k["teks"])
# endregion

# endregion