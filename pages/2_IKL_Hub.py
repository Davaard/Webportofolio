# region INISIALISASI
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations
import base64

# Pindahkan fungsi ini ke paling atas agar bisa dibaca duluan oleh Streamlit
def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

st.set_page_config(page_title="IKL Dashboard", layout="wide", initial_sidebar_state="expanded")

# === SIHIR CSS: STICKY HEADER SEMPURNA ===
st.markdown("""
    <style>
    /* =========================================
       1. IMPORT FONTS DARI GOOGLE FONTS (WAJIB PALING ATAS!)
       ========================================= */
    @import url('https://fonts.googleapis.com/css2?family=Akronim&family=Londrina+Shadow&family=Rajdhani:wght@500;700&family=Montserrat:wght@400;600;800&display=swap');

    /* 2. Target spesifik HANYA untuk kontainer paling atas di halaman utama */
    .main .block-container > div:first-child {
        position: sticky;
        top: 2.875rem; 
        z-index: 999;
        background-color: #0e1117; 
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1); 
    }
    
    /* 3. KELAS FONT UNTUK RECAP */
    .recap-kill {
        font-family: 'Akronim', system-ui;
        font-size: 40px;
        color: transparent;
        -webkit-text-stroke: 1.5px #ff4b4b;
        margin-bottom: -10px;
    }
    .recap-time {
        font-family: 'Londrina Shadow', display;
        font-size: 35px;
        color: #4caf50; 
    }
    
    .main .block-container > div:first-child {
        position: sticky;
        top: 2.875rem; 
        z-index: 999;
        background-color: #0e1117; 
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1); 
    }
    
    .esports-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        color: white;
        font-size: 24px;
        margin-bottom: 5px;
    }

    .esports-text {
        font-family: 'Montserrat', sans-serif;
        font-weight: 400;
        color: #d1d1d1;
        font-size: 14px;
        line-height: 1.6;
        text-align: justify;
    }

    .highlight-text {
        color: #00d2ff;
        font-weight: 600;
    }
    
    div.stButton > button {
        background-color: transparent !important;
        border: none !important;
        color: gray !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease-in-out;
        opacity: 0.6;
    }
    div.stButton > button:hover {
        color: white !important;
        opacity: 1; 
    }
    
    .clean-table {
        width: 100%;
        border-collapse: collapse;
        color: white;
        font-family: 'Montserrat', sans-serif;
        font-size: 14px;
        text-align: center;
    }
    .clean-table th {
        border-bottom: 2px solid #555;
        padding: 12px 8px;
        color: #b0b0b0;
        font-weight: 600;
    }
    .clean-table td {
        border-bottom: 1px solid #333;
        padding: 12px 8px;
        vertical-align: middle;
    }
    .clean-table td.team-cell {
        text-align: left;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    </style>
""", unsafe_allow_html=True)
# =========================================

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

df_csv = load_and_preprocess_data("Data_Set_IKL_HOK.csv")

def urutkan_musim(s):
    bagian = str(s).strip().split()
    if len(bagian) == 2 and bagian[1].isdigit():
        musim, tahun = bagian[0].lower(), int(bagian[1])
        bobot_musim = 2 if musim == 'fall' else 1
        return (tahun, bobot_musim)
    return (0, 0)

# === PENGATURAN HEADER GLOBAL (FIXED TOP-RIGHT) ===
col_title, col_season = st.columns([3, 1])
with col_title:
    st.markdown("## 🎮 Indonesia Kings Laga (IKL) - HOK")
        
with col_season:
    if 'Season' in df_csv.columns:
        daftar_musim = sorted(df_csv['Season'].dropna().unique().tolist(), key=urutkan_musim, reverse=True)
        musim_pilihan = st.selectbox("Pilih Musim", daftar_musim, label_visibility="collapsed")
        df_master = df_csv[df_csv['Season'] == musim_pilihan].copy()
        
        if musim_pilihan == "Fall 2025":
            df_master['Team_(Blue)'] = df_master['Team_(Blue)'].replace({'VIT': 'BTR'})
            df_master['Opponent_(Red)'] = df_master['Opponent_(Red)'].replace({'VIT': 'BTR'})
    else:
        st.error("Kolom 'Season' tidak ditemukan!")
        st.stop()
# ==================================================

# region UI HELPERS
# UI Helpers dikembalikan ke bawah musim_pilihan agar tidak NameError
@st.cache_data
def get_dynamic_logo_map(season):
    if os.path.exists("IKL_Rosters.csv"):
        df_ros = pd.read_csv("IKL_Rosters.csv").dropna(subset=['Logo_File'])
        df_global = df_ros.drop_duplicates(subset=['Team', 'Logo_File'], keep='last').drop_duplicates(subset=['Team'])
        map_global = dict(zip(df_global['Team'], df_global['Logo_File']))
        
        df_season = df_ros[df_ros['Season'] == season].drop_duplicates(subset=['Team'])
        map_season = dict(zip(df_season['Team'], df_season['Logo_File']))
        
        map_global.update(map_season)
        return map_global
    return {}

TEAM_LOGO_MAP = get_dynamic_logo_map(musim_pilihan)

def get_logo_path(team_name):
    if team_name in TEAM_LOGO_MAP:
        path = os.path.join("assets", "logo_tim", str(TEAM_LOGO_MAP[team_name]))
        if os.path.exists(path): return path
    return None

def get_hero_path(hero_name):
    safe_name = hero_name.replace(" ", "_").replace(".png", "").replace(".jpg", "")
    for ext in ['.png', '.jpg', '.jpeg']:
        if os.path.exists(f"assets/heroes/{safe_name}{ext}"): return f"assets/heroes/{safe_name}{ext}"
    return None

def render_combo_card(combo_tuple, warna, ikon, teks):
    tema = {
        "error": {"bg": "rgba(255, 75, 75, 0.15)", "border": "rgba(255, 75, 75, 1)"},
        "warning": {"bg": "rgba(255, 190, 0, 0.15)", "border": "rgba(255, 190, 0, 1)"},
        "success": {"bg": "rgba(9, 171, 59, 0.15)", "border": "rgba(9, 171, 59, 1)"}
    }
    bg, brdr = tema[warna]["bg"], tema[warna]["border"]
    img_html = "<div style='display: flex; gap: 2%; margin-bottom: 12px;'>"
    for i in range(5):
        if i < len(combo_tuple):
            p = get_hero_path(combo_tuple[i])
            img_html += f"<img src='data:image/png;base64,{image_to_base64(p)}' style='width: 18.4%; border-radius: 8px; box-shadow: 1px 2px 5px rgba(0,0,0,0.3); aspect-ratio: 1/1;'>" if p else f"<div style='width: 18.4%; background: #444; border-radius: 8px; display:flex; align-items:center; justify-content:center; font-size:10px; text-align:center; aspect-ratio: 1/1;'>{combo_tuple[i]}</div>"
        else: img_html += "<div style='width: 18.4%; aspect-ratio: 1/1;'></div>"
    img_html += "</div>"
    st.markdown(f"<div style='background: {bg}; border-left: 5px solid {brdr}; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>{img_html}<div style='font-size: 14.5px; line-height: 1.5;'><b>{ikon}</b> {teks.replace(chr(10), '<br>')}</div></div>", unsafe_allow_html=True)

def render_logo_card(logo_path, team_name):
    if logo_path and os.path.exists(logo_path):
        st.markdown(f"<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; display: flex; justify-content: center; align-items: center; aspect-ratio: 1/1; margin-bottom: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><img src='data:image/png;base64,{image_to_base64(logo_path)}' style='max-width: 100%; max-height: 100%;'></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; display: flex; justify-content: center; align-items: center; aspect-ratio: 1/1; margin-bottom: 8px;'><span style='color: gray; font-weight: bold; font-size: 20px;'>{team_name}</span></div>", unsafe_allow_html=True)
# endregion

# region NAVIGASI INTERNAL IKL
if "menu_ikl" not in st.session_state: 
    st.session_state['menu_ikl'] = "🏆 Klasemen & Playoffs"

menu_utama = st.session_state['menu_ikl']

if menu_utama == "🏆 Klasemen & Playoffs":
    susunan = ["🛡️ Team Profiling", "🏆 Klasemen & Playoffs", "⚔️ Versus Mode (H2H)"]
elif menu_utama == "🛡️ Team Profiling":
    susunan = ["⚔️ Versus Mode (H2H)", "🛡️ Team Profiling", "🏆 Klasemen & Playoffs"]
else: 
    susunan = ["🏆 Klasemen & Playoffs", "⚔️ Versus Mode (H2H)", "🛡️ Team Profiling"]

st.markdown("<br>", unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3 = st.columns(3)

nav_bg_path = "assets/selected_mode_display.png"
nav_bg_base64 = image_to_base64(nav_bg_path) if os.path.exists(nav_bg_path) else ""

with col_nav1:
    if st.button(susunan[0], use_container_width=True): st.session_state['menu_ikl'] = susunan[0]; st.rerun()
with col_nav2:
    html_nav_active = f"""
    <div style="position: relative; margin-top: -5px; padding: 12px 0; text-align: center;">
        <div style="position: absolute; top: 0; left: -50%; width: 200%; height: 100%; 
                    background-image: url('data:image/png;base64,{nav_bg_base64}'); 
                    background-size: 100% 100%; 
                    background-repeat: no-repeat; 
                    background-position: center; 
                    z-index: 0;">
        </div>
        <span style="position: relative; z-index: 1; color: white; font-weight: 800; font-size: 18px;">
            {susunan[1]}
        </span>
    </div>
    """
    st.markdown(html_nav_active, unsafe_allow_html=True)
with col_nav3:
    if st.button(susunan[2], use_container_width=True): st.session_state['menu_ikl'] = susunan[2]; st.rerun()

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)
# endregion

# (Pre-processing Data - Berjalan senyap di latar belakang)
df_history = df_master[df_master['Status'] == 'History'].copy()

df_A = df_history.copy()
df_A = df_A[['Date', 'Time', 'Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)', 'Result', 'Duration_min', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 'Heroes_Picked', 'Opponent_Picked', 'MVP']]
kolom_standar = ['Date', 'Time', 'Week', 'Day', 'Match', 'Game', 'Team', 'Opponent', 'Win', 'Durasi', 'Gold', 'Opp_Gold', 'Kill', 'Opp_Kill', 'Ast', 'Opp_Ast', 'Obj', 'Opp_Obj', 'Heroes', 'Opp_Heroes', 'MVP']
df_A.columns = kolom_standar

df_B = df_history.copy()
df_B['Result_Red'] = 1 - df_B['Result'] 
df_B = df_B[['Date', 'Time', 'Week', 'Day', 'Match', 'Game', 'Opponent_(Red)', 'Team_(Blue)', 'Result_Red', 'Duration_min', 'O_Gold', 'T_Gold', 'O_Kill', 'T_Kill', 'O_Assist', 'T_Assist', 'O_Objective', 'T_Objective', 'Opponent_Picked', 'Heroes_Picked', 'MVP']]
df_B.columns = kolom_standar

df_long = pd.concat([df_A, df_B], ignore_index=True)
df_long = df_long.sort_values(by=['Week', 'Day', 'Match', 'Game']).reset_index(drop=True)

def aman_split(x):
    if pd.isna(x) or str(x).strip().lower() in ['nan', '-', '']: return []
    return [h.strip() for h in str(x).split(',') if h.strip()]

df_long['Heroes'] = df_long['Heroes'].apply(aman_split)
df_long['Opp_Heroes'] = df_long['Opp_Heroes'].apply(aman_split)
# endregion

# region RADAR PENILAIAN & METRIK LAINNYA
klasemen = df_long.groupby('Team')['Win'].agg(Total_Menang='sum', Total_Kalah=lambda x: (x == 0).sum()).reset_index()
klasemen['Skor_IKL'] = klasemen['Total_Menang'] - klasemen['Total_Kalah']
klasemen['Rank_Akhir'] = klasemen['Skor_IKL'].rank(method='min', ascending=False)
df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], on='Team', how='left').rename(columns={'Rank_Akhir': 'T_Rank'})
df_long = df_long.merge(klasemen[['Team', 'Rank_Akhir']], left_on='Opponent', right_on='Team', how='left', suffixes=('', '_drop')).rename(columns={'Rank_Akhir': 'O_Rank'})
df_long = df_long.drop(columns=['Team_drop'], errors='ignore') 
df_long['Points_Ratio'] = (df_long['Gold'] / df_long['Opp_Gold']) + (df_long['Kill'] / (df_long['Opp_Kill'] + 1))
df_long['Points_Won'] = np.where(df_long['Win'] == 1, df_long['Points_Ratio'], np.nan)
df_long['Points_Lost'] = np.where(df_long['Win'] == 0, df_long['Points_Ratio'], np.nan)

dominasi_df = df_long.groupby('Team').agg(
    Total_Wins=('Win', 'sum'), Total_Losses=('Win', lambda x: (x == 0).sum()),
    Sum_Points_Won=('Points_Won', 'sum'), Sum_Points_Lost=('Points_Lost', 'sum')
).reset_index()
dominasi_df.fillna(0, inplace=True)
dominasi_df['Dominance_Skor'] = ((dominasi_df['Sum_Points_Won'] / (dominasi_df['Total_Losses'] + 1)) - (dominasi_df['Sum_Points_Lost'] / (dominasi_df['Total_Wins'] + 1)))

def konversi_waktu(waktu):
    waktu = str(waktu).strip()
    if pd.isna(waktu) or waktu.lower() in ['nan', '-', '']: return 0.0
    if ':' in waktu:
        try:
            m, d = waktu.split(':')
            return float(m) + (float(d) / 60.0)
        except: return 0.0
    if '.' in waktu:
        try:
            m, d = waktu.split('.')
            return float(m) + (float(d) / 60.0)
        except: return 0.0
    try: return float(waktu)
    except ValueError: return 0.0

df_long['Durasi'] = df_long['Durasi'].apply(konversi_waktu)
df_long['Kill'] = pd.to_numeric(df_long['Kill'], errors='coerce').fillna(0)
df_long['Opp_Kill'] = pd.to_numeric(df_long['Opp_Kill'], errors='coerce').fillna(0)
df_long['Defense_Multiplier'] = df_long['Opp_Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)
df_long['Offense_Multiplier'] = df_long['Kill'] / (df_long['Kill'] + df_long['Opp_Kill'] + 1)
df_long['Durasi_Menang_Berbobot'] = np.where(df_long['Win'] == 1, df_long['Durasi'] * df_long['Offense_Multiplier'], np.nan)
df_long['Durasi_Kalah_Berbobot'] = np.where(df_long['Win'] == 0, df_long['Durasi'] * df_long['Defense_Multiplier'], np.nan)

seasonal_win_dur = df_long.groupby('Team')['Durasi_Menang_Berbobot'].mean().reset_index().rename(columns={'Durasi_Menang_Berbobot': 'Seasonal_Avg_Win_Bobot'})
seasonal_win_dur['Seasonal_Avg_Win_Bobot'] = seasonal_win_dur['Seasonal_Avg_Win_Bobot'].fillna(7.5) 

series_df = df_long.groupby(['Week', 'Day', 'Match', 'Team']).agg(Avg_Win_Series=('Durasi_Menang_Berbobot', 'mean'), Avg_Loss_Series=('Durasi_Kalah_Berbobot', 'mean')).reset_index()
series_df = series_df.merge(seasonal_win_dur, on='Team', how='left')
series_df['Avg_Win_Series'] = series_df['Avg_Win_Series'].fillna(series_df['Seasonal_Avg_Win_Bobot'])
series_df['Series_Toughness'] = series_df['Avg_Loss_Series'] - series_df['Avg_Win_Series']
toughness_df = series_df.groupby('Team').agg(Toughness_Skor=('Series_Toughness', 'mean')).reset_index().fillna(0)

df_long['Obj'] = pd.to_numeric(df_long['Obj'], errors='coerce').fillna(0)
df_long['Opp_Obj'] = pd.to_numeric(df_long['Opp_Obj'], errors='coerce').fillna(0)
df_long['Discipline_Game'] = (((df_long['Obj'] ** 2) / (df_long['Obj'] + df_long['Kill'] + 1)) - ((df_long['Opp_Obj'] ** 2) / (df_long['Opp_Obj'] + df_long['Opp_Kill'] + 1))) / df_long['Durasi']
discipline_df = df_long.groupby('Team').agg(Discipline_Skor=('Discipline_Game', 'mean')).reset_index()

df_long['GPM'] = df_long['Gold'] / df_long['Durasi']
volatility_df = df_long.groupby('Team').agg(Volatility=('GPM', 'std')).reset_index().fillna(0)
best_win = df_long[df_long['Win'] == 1].groupby('Team')['O_Rank'].min().reset_index().rename(columns={'O_Rank': 'Best_Win_Rank'})
worst_loss = df_long[df_long['Win'] == 0].groupby('Team')['O_Rank'].max().reset_index().rename(columns={'O_Rank': 'Worst_Loss_Rank'})
volatility_df = volatility_df.merge(best_win, on='Team', how='left').merge(worst_loss, on='Team', how='left')
volatility_df['Best_Win_Rank'] = volatility_df['Best_Win_Rank'].fillna(10)
volatility_df['Worst_Loss_Rank'] = volatility_df['Worst_Loss_Rank'].fillna(1)
volatility_df['Volatility_Skor'] = volatility_df['Volatility'] * (volatility_df['Worst_Loss_Rank'] / volatility_df['Best_Win_Rank'])

df_long['Ast'] = pd.to_numeric(df_long['Ast'], errors='coerce').fillna(0)
df_long['Opp_Ast'] = pd.to_numeric(df_long['Opp_Ast'], errors='coerce').fillna(0)
df_long['TeamFight_Game'] = (df_long['Ast'] / (df_long['Kill'] + 1)) - (df_long['Opp_Ast'] / (df_long['Opp_Kill'] + 1))
teamfight_df = df_long.groupby('Team').agg(TeamFight_Skor=('TeamFight_Game', 'mean')).reset_index()

import ast
def parse_heroes(val):
    if isinstance(val, list): return val
    try: return ast.literal_eval(val)
    except: return [h.strip() for h in str(val).split(',') if h.strip()]
df_long['Heroes_List'] = df_long['Heroes'].apply(parse_heroes)
flexibility_df = df_long.explode('Heroes_List').groupby('Team')['Heroes_List'].nunique().reset_index().rename(columns={'Heroes_List': 'Flexibility_Skor'})

rapor_akhir = dominasi_df[['Team', 'Dominance_Skor']].merge(toughness_df[['Team', 'Toughness_Skor']], on='Team').merge(discipline_df[['Team', 'Discipline_Skor']], on='Team').merge(volatility_df[['Team', 'Volatility_Skor']], on='Team').merge(teamfight_df[['Team', 'TeamFight_Skor']], on='Team').merge(flexibility_df[['Team', 'Flexibility_Skor']], on='Team')

metrik_mentah = ['Dominance_Skor', 'Toughness_Skor', 'Discipline_Skor', 'Volatility_Skor', 'TeamFight_Skor', 'Flexibility_Skor']
for col in metrik_mentah:
    min_val, max_val = rapor_akhir[col].min(), rapor_akhir[col].max()
    rapor_akhir[col.replace('_Skor', '_100')] = 100.0 if max_val == min_val else ((rapor_akhir[col] - min_val) / (max_val - min_val)) * 80 + 20
rapor_radar = rapor_akhir[['Team'] + [c.replace('_Skor', '_100') for c in metrik_mentah]].round(2)
# endregion

# region MESIN KOMBINASI
df_combo_history = df_long.dropna(subset=['Win']).copy()
global_freq, global_wins = {}, {}
for idx, row in df_combo_history.iterrows():
    heroes = row['Heroes_List']
    w = 1 if float(row['Win']) == 1.0 else 0
    if isinstance(heroes, list) and len(heroes) > 0:
        for r in range(1, min(len(heroes) + 1, 6)):
            for combo in combinations(sorted(heroes), r):
                global_freq[combo] = global_freq.get(combo, 0) + 1
                global_wins[combo] = global_wins.get(combo, 0) + w

def get_signature_combos(tim_target):
    team_freq, team_wins = {}, {}
    for idx, row in df_combo_history[df_combo_history['Team'] == tim_target].iterrows():
        heroes = row['Heroes_List']
        w = 1 if float(row['Win']) == 1.0 else 0
        if isinstance(heroes, list) and len(heroes) >= 2:
            for r in range(2, min(len(heroes) + 1, 6)):
                for combo in combinations(sorted(heroes), r):
                    team_freq[combo] = team_freq.get(combo, 0) + 1
                    team_wins[combo] = team_wins.get(combo, 0) + w
    team_valid = {k: {'freq': f, 'wr': (team_wins[k]/f)*100} for k, f in team_freq.items() if (len(k)==2 and f>=3) or (len(k)==3 and f>=3) or (len(k)>=4 and f>=2)}
    combos_to_remove = set()
    sorted_combos = sorted(list(team_valid.keys()), key=len, reverse=True)
    for i in range(len(sorted_combos)):
        c_large = sorted_combos[i]
        if c_large in combos_to_remove: continue
        for j in range(i + 1, len(sorted_combos)):
            c_small = sorted_combos[j]
            if c_small in combos_to_remove: continue
            if set(c_small).issubset(set(c_large)):
                if team_valid[c_large]['wr'] > team_valid[c_small]['wr']: combos_to_remove.add(c_small)
                elif team_valid[c_small]['wr'] > team_valid[c_large]['wr']: combos_to_remove.add(c_large)
                elif (team_valid[c_small]['freq'] - team_valid[c_large]['freq']) < (3 if len(c_small)==2 else 2): combos_to_remove.add(c_small)
    kombo_final = {k: v for k, v in team_valid.items() if k not in combos_to_remove}
    hasil_ui = []
    for combo, stats in sorted(kombo_final.items(), key=lambda x: (x[1]['wr'], x[1]['freq']), reverse=True)[:3]:
        g_freq, g_wr = global_freq.get(combo, 0), (global_wins.get(combo, 0)/global_freq.get(combo, 1)*100)
        is_red = False
        if len(combo) == 2:
            g_base = min([global_freq.get((h,), 1) for h in combo])
            max_trio_wr = max([0] + [(global_wins[gc]/f)*100 for gc, f in global_freq.items() if len(gc)==3 and set(combo).issubset(set(gc))])
            is_red = g_wr > max_trio_wr
        else:
            g_base = max([0] + [global_freq.get(sc, 0) for sc in combinations(combo, len(combo)-1)])
            g_base_wr = max([0] + [(global_wins.get(sc,0)/max(global_freq.get(sc,1),1))*100 for sc in combinations(combo, len(combo)-1)])
            is_red = g_wr > g_base_wr
        rasio = (g_freq / g_base * 100) if g_base > 0 else 0
        if rasio > 25.0:
            w, i, s = ("error", "🌟", f"Supreme Meta ({rasio:.0f}%)") if is_red else ("warning", "🔥", f"Global Meta ({rasio:.0f}%)")
        else:
            w, i, s = "success", "🌿", "Team Signature Pick"
        hasil_ui.append({"warna": w, "ikon": i, "teks": f"**{', '.join(combo[:-1])} & {combo[-1]}**\n\n🎯 Pick: **{stats['freq']}x** | WR: **{stats['wr']:.0f}%**\n📊 **{s}**", "combo": combo})
    return hasil_ui
# endregion

# region HALAMAN 1: KLASEMEN, PLAYOFFS & HIGHLIGHTS
if menu_utama == "🏆 Klasemen & Playoffs":
    
    # === 1. LEAGUE INFO (LOGO KIRI, TEKS KANAN) ===
    st.markdown("### Indonesia Kings Laga (IKL)")
    
    col_logo, col_teks = st.columns([1, 3.5])
    with col_logo:
        logo_ikl_path = "assets/ikl_gold.png"
        if os.path.exists(logo_ikl_path):
            st.markdown(f"""<div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                <img src="data:image/png;base64,{image_to_base64(logo_ikl_path)}" style="width: 100%; max-width: 150px; object-fit: contain;">
            </div>""", unsafe_allow_html=True)
            
    with col_teks:
        # 1. Hitung Total Tim Musim Ini
        tim_biru_curr = set(df_master['Team_(Blue)'].dropna().unique())
        tim_merah_curr = set(df_master['Opponent_(Red)'].dropna().unique())
        tim_musim_ini = tim_biru_curr.union(tim_merah_curr)
        total_team = len(tim_musim_ini)
        
        # 2. Setup Variabel Sejarah Musim
        total_musim_berjalan = len(daftar_musim)
        idx_musim_ini = daftar_musim.index(musim_pilihan)
        musim_pertama = daftar_musim[-1]
        is_musim_pertama = (musim_pilihan == musim_pertama)
        
        # 3. Mencari Tim Baru
        tim_baru_list = []
        if not is_musim_pertama:
            # Ambil semua tim dari semua musim SEBELUM musim pilihan ini
            musim_sebelumnya_all = daftar_musim[idx_musim_ini + 1:]
            df_past = df_csv[df_csv['Season'].isin(musim_sebelumnya_all)]
            tim_past = set(df_past['Team_(Blue)'].dropna().unique()).union(set(df_past['Opponent_(Red)'].dropna().unique()))
            
            # Tim baru = Tim musim ini yang TIDAK ADA di tim masa lalu
            tim_baru_set = tim_musim_ini - tim_past
            tim_baru_list = list(tim_baru_set)
        
        # Format teks tim baru
        teks_tim_baru = ""
        if len(tim_baru_list) > 0:
            teks_tim_baru = f" dengan <span class='highlight-text'>{len(tim_baru_list)} tim baru</span> di antaranya adalah {', '.join(tim_baru_list)}."
        elif not is_musim_pertama:
            teks_tim_baru = " tanpa ada penambahan tim baru dari musim sebelumnya."
            
        # 4. Logika Juara Bertahan (Membaca Data Grand Final Musim Sebelumnya)
        teks_bertahan = ""
        if not is_musim_pertama:
            musim_lalu = daftar_musim[idx_musim_ini + 1]
            df_lalu = df_csv[df_csv['Season'] == musim_lalu]
            df_gr_lalu = df_lalu[df_lalu['Week'] == 'Gr'].dropna(subset=['Result'])
            
            if not df_gr_lalu.empty:
                # Ambil dua tim yang bertanding di Grand Final
                tim_gr_1 = df_gr_lalu.iloc[0]['Team_(Blue)']
                tim_gr_2 = df_gr_lalu.iloc[0]['Opponent_(Red)']
                
                # Hitung Skor
                skor_1, skor_2 = 0, 0
                for _, g in df_gr_lalu.iterrows():
                    if (g['Team_(Blue)'] == tim_gr_1 and g['Result'] == 1.0) or (g['Opponent_(Red)'] == tim_gr_1 and g['Result'] == 0.0):
                        skor_1 += 1
                    elif (g['Team_(Blue)'] == tim_gr_2 and g['Result'] == 1.0) or (g['Opponent_(Red)'] == tim_gr_2 and g['Result'] == 0.0):
                        skor_2 += 1
                
                # Tentukan Juara
                if skor_1 > skor_2:
                    juara, runner_up, skor_juara, skor_runner = tim_gr_1, tim_gr_2, skor_1, skor_2
                else:
                    juara, runner_up, skor_juara, skor_runner = tim_gr_2, tim_gr_1, skor_2, skor_1
                
                teks_bertahan = f", dengan <span class='highlight-text'><b>{juara}</b></span> sebagai juara bertahan dari {musim_lalu} setelah melawan {runner_up} dengan skor <b>{skor_juara}-{skor_runner}</b>."
            else:
                teks_bertahan = f", melanjutkan tensi kompetisi dari {musim_lalu}."
        
        # 5. Merangkai Narasi HTML Akhir
        narasi = f"""
        <div class="esports-text">
        Indonesia Kings Laga atau IKL adalah liga esports nasional untuk game Honor of Kings di Indonesia. 
        IKL pertama kali diadakan pada {musim_pertama}, dan berhasil berjalan hingga musim ke-{total_musim_berjalan}.<br><br>
        <span class="highlight-text">{musim_pilihan}</span> diikuti oleh total <span class="highlight-text">{total_team} tim</span>{teks_tim_baru}<br><br>
        Musim ini diadakan dengan dua format: <b>Single Global League (Regular Season)</b> dan <b>Double Elimination Bracket System (Playoffs)</b>{teks_bertahan}
        </div>
        """
        st.markdown(narasi, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # === 2. UPCOMING MATCH (LOGIKA HARI BERBEDA - DESAIN CANVA) ===
    st.markdown("### Upcoming Match")
    
    df_jadwal = df_master[df_master['Status'] == 'Upcoming'].copy()
    if df_jadwal.empty:
         st.markdown("<div style='text-align: center; color: gray; padding: 20px;'><i>Tidak ada jadwal pertandingan mendatang.</i></div>", unsafe_allow_html=True)
    else:
         df_up = df_jadwal.drop_duplicates(subset=['Match_ID'])
         
         # Ambil daftar hari (Date) unik yang tersisa
         tanggal_unik = df_up['Date'].dropna().unique().tolist()
         
         col_up1, col_up2 = st.columns(2)
         
         # Fungsi pembantu untuk menerjemahkan Week/Day
         def get_match_phase(row_data):
             w = str(row_data['Week']).strip()
             d = str(row_data['Day']).strip()
             fase_dict = {'Pl St': 'Play-in Stages', 'Up Sf': 'Upper Bracket<br>Semifinal', 'Lw Sf': 'Lower Bracket<br>Semifinal', 'Up Fl': 'Upper Bracket<br>Final', 'Lw Fl': 'Lower Bracket<br>Final', 'Gr Fl': 'Grand Final'}
             return fase_dict.get(f"{w} {d}", f"Week {w}<br>Day {d}").replace('\n', '<br>')
         
         def render_match_card(row_data):
             tim_biru = str(row_data['Team_(Blue)'])
             tim_merah = str(row_data['Opponent_(Red)'])
             logo_biru = get_logo_path(tim_biru) if tim_biru != "nan" else None
             logo_merah = get_logo_path(tim_merah) if tim_merah != "nan" else None
             vs_logo = "assets/Match/vs_outline_gold.png" 
             
             # Tim yang belum ada (TBD) akan menggunakan teks putih tegas
             html_biru = f"<img src='data:image/png;base64,{image_to_base64(logo_biru)}' style='height: 35px; object-fit: contain;'>" if logo_biru else "<span style='color: white; font-weight: 800; font-size: 16px;'>TBD</span>"
             html_merah = f"<img src='data:image/png;base64,{image_to_base64(logo_merah)}' style='height: 35px; object-fit: contain;'>" if logo_merah else "<span style='color: white; font-weight: 800; font-size: 16px;'>TBD</span>"
             
             # Logika Warna Waktu: Jika jam tersedia berwarna putih, jika TBA berwarna abu-abu
             if pd.notna(row_data['Time']):
                 waktu_html = f"<div style='font-size: 18px; color: white; font-weight: 800;'>{row_data['Time']}</div>"
             else:
                 waktu_html = f"<div style='font-size: 18px; color: gray; font-weight: 800;'>TBA</div>"
             
             # Format HTML murni dirangkai satu baris
             html = f"<div style='padding: 15px 0px; border-bottom: 1px solid #333; display: flex; align-items: center; justify-content: space-between;'>"
             html += f"<div style='width: 25%; text-align: left;'><div style='font-size: 11px; color: gray; font-weight: bold;'>{row_data['Date']}</div>{waktu_html}</div>"
             html += f"<div style='width: 45%; display: flex; justify-content: center; align-items: center; gap: 15px;'><div style='width: 40px; text-align: right;'>{html_biru}</div><img src='data:image/png;base64,{image_to_base64(vs_logo)}' style='height: 25px;'><div style='width: 40px; text-align: left;'>{html_merah}</div></div>"
             html += f"<div style='width: 30%; text-align: right; font-size: 11px; color: gray; line-height: 1.3; font-weight: 600;'>{get_match_phase(row_data)}</div></div>"
             return html
         
         # Render Kolom Kiri (Hari Pertama)
         if len(tanggal_unik) > 0:
             hari_1 = tanggal_unik[0]
             df_hari_1 = df_up[df_up['Date'] == hari_1].head(3) # Tampilkan max 3 per hari
             with col_up1:
                 for _, row_data in df_hari_1.iterrows():
                     st.markdown(render_match_card(row_data), unsafe_allow_html=True)
                                 
         # Render Kolom Kanan (Hari Kedua, jika ada)
         if len(tanggal_unik) > 1:
             hari_2 = tanggal_unik[1]
             df_hari_2 = df_up[df_up['Date'] == hari_2].head(3)
             with col_up2:
                 for _, row_data in df_hari_2.iterrows():
                     st.markdown(render_match_card(row_data), unsafe_allow_html=True)
                 
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # === 3. REGULAR SEASON (KLASEMEN CLEAN HTML) ===
    st.markdown("### Regular Season")
    
    df_reguler = df_long[df_long['Week'].astype(str).str.isdigit()]
    
    # Kumpulan Nama Panjang Tim (Manual Mapping)
    nama_panjang = {
        "BTR": "Bigetron by Vitality", "RRQ": "Rex Regum Qeon", "DMT": "Dominator by Nemesis",
        "AE": "Alter Ego", "ONIC": "ONIC Esports", "MHD": "Mahadewa", "VESA": "Vesakha Esports",
        "KAGE": "Kagendra", "TLN.ID": "Talon Esports ID", "NMSS": "Team Nemesis", "RVM": "Revermoin Esports", "OG": "Carstensz DuskMaven"
    }
    
    if not df_reguler.empty:
        df_match = df_reguler.groupby(['Week', 'Day', 'Match', 'Team'], sort=False).agg(Game_W=('Win', 'sum'), Game_L=('Win', lambda x: (x == 0).sum())).reset_index()
        df_match['Match_W'] = np.where(df_match['Game_W'] > df_match['Game_L'], 1, 0)
        df_match['Match_L'] = np.where(df_match['Game_W'] < df_match['Game_L'], 1, 0)
        
        klasemen_baru = df_match.groupby('Team').agg(Match=('Match', 'count'), M_W=('Match_W', 'sum'), M_L=('Match_L', 'sum'), G_W=('Game_W', 'sum'), G_L=('Game_L', 'sum')).reset_index()
        klasemen_baru['Match_WL'] = klasemen_baru['M_W'].astype(int).astype(str) + " - " + klasemen_baru['M_L'].astype(int).astype(str)
        klasemen_baru['Game_WL'] = klasemen_baru['G_W'].astype(int).astype(str) + " - " + klasemen_baru['G_L'].astype(int).astype(str)
        klasemen_baru['Windiff'] = (klasemen_baru['G_W'] - klasemen_baru['G_L']).astype(int)
        klasemen_baru['Rank'] = klasemen_baru['Windiff'].rank(method='min', ascending=False).astype(int)
        
        df_tampil = klasemen_baru.sort_values(by='Rank')[['Rank', 'Team', 'Match', 'Match_WL', 'Game_WL', 'Windiff']]
        
        def render_clean_table(df_data):
            # Penulisan HTML tanpa indentasi multi-line agar terhindar dari bug rendering Code Block Streamlit
            html_table = "<table class='clean-table'><thead><tr><th>Rank</th><th style='text-align: left;'>Team</th><th>Match</th><th>Match<br>W - L</th><th>Game<br>W - L</th><th>Windiff</th></tr></thead><tbody>"
            for _, row in df_data.iterrows():
                tim_singkat = row['Team']
                logo_tim = get_logo_path(tim_singkat)
                logo_tag = f"<img src='data:image/png;base64,{image_to_base64(logo_tim)}' style='height: 35px; width: 35px; object-fit: contain;'>" if logo_tim else f"<div style='width: 35px; height: 35px;'></div>"
                tim_panjang = nama_panjang.get(tim_singkat, tim_singkat)
                
                html_table += f"<tr><td style='font-weight: bold;'>{row['Rank']}</td>"
                html_table += f"<td class='team-cell'>{logo_tag} <span style='font-weight: 600; font-size: 13px;'>{tim_panjang}</span></td>"
                html_table += f"<td style='font-weight: bold; font-size: 16px;'>{row['Match']}</td>"
                html_table += f"<td>{row['Match_WL']}</td><td>{row['Game_WL']}</td>"
                html_table += f"<td style='font-weight: bold; font-size: 16px;'>{row['Windiff']}</td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
        
        if "2025" in musim_pilihan:
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>Format {musim_pilihan}: Double Group Stage</p>", unsafe_allow_html=True)
            if musim_pilihan == "Spring 2025":
                grup_1_tim, grup_2_tim = ['DMT', 'KAGE', 'RRQ', 'AE', 'NMSS'], ['BTR', 'TLN.ID', 'ONIC', 'MHD', 'VESA']
            else: 
                grup_1_tim, grup_2_tim = ['VESA', 'MHD', 'RRQ', 'AE', 'ONIC'], ['BTR', 'TLN.ID', 'RVM', 'DMT', 'KAGE']
                
            df_grup1 = df_tampil[df_tampil['Team'].isin(grup_1_tim)].reset_index(drop=True)
            df_grup1['Rank'] = df_grup1['Windiff'].rank(method='min', ascending=False).astype(int)
            df_grup1 = df_grup1.sort_values('Rank')
            
            df_grup2 = df_tampil[df_tampil['Team'].isin(grup_2_tim)].reset_index(drop=True)
            df_grup2['Rank'] = df_grup2['Windiff'].rank(method='min', ascending=False).astype(int)
            df_grup2 = df_grup2.sort_values('Rank')
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown(f"<h5 style='text-align: center; color: #00d2ff;'>Group Tyrant</h5>", unsafe_allow_html=True)
                render_clean_table(df_grup1)
            with col_g2:
                st.markdown(f"<h5 style='text-align: center; color: #ff4b4b;'>Group Overlord</h5>", unsafe_allow_html=True)
                render_clean_table(df_grup2)
        else:
            st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>Format 2026: Single Global League</p>", unsafe_allow_html=True)
            render_clean_table(df_tampil)
    else:
        st.info("Data Regular Season belum tersedia.")

    st.markdown("<hr style='border-color: #333; margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    
    # 4. BRACKET PLAYOFFS
    st.markdown("###Playoff")
    df_playoff = df_master[df_master['Week'].isin(['Pl', 'Up', 'Lw', 'Gr'])].copy()
    
    if df_playoff.empty:
        st.info("Babak Playoffs belum dimulai atau data belum tersedia.")
    else:
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        
        # === FUNGSI BRACKET CUSTOM CSS ===
        def render_bracket_box(df_match_filtered, title):
            st.markdown(f"<div style='text-align: center; color: white; font-size: 15px; font-weight: bold; margin-bottom: 12px;'>{title}</div>", unsafe_allow_html=True)
            
            vs_logo = "assets/Match/vs_outline_gold.png" 
            
            # Jika belum ada data (TBD)
            if df_match_filtered.empty:
                html = "<div style='display: flex; height: 45px; border-radius: 4px; overflow: hidden; margin-bottom: 20px; border-left: 4px solid #d4af37; background-color: #3b3b40;'>"
                html += "<div style='width: 20%; background-color: #55555d;'></div>"
                html += f"<div style='width: 60%; display: flex; align-items: center; justify-content: center; gap: 10px;'><span style='color: gray; font-size: 11px; font-weight: bold;'>TBD</span><img src='data:image/png;base64,{image_to_base64(vs_logo)}' style='height: 20px;'><span style='color: gray; font-size: 11px; font-weight: bold;'>TBD</span></div>"
                html += "<div style='width: 20%; background-color: #55555d;'></div></div>"
                st.markdown(html, unsafe_allow_html=True)
                return
                
            # Filter per Match (Seri)
            series_list = df_match_filtered.drop_duplicates(subset=['Week', 'Day', 'Match'])
            
            for idx, row in series_list.iterrows():
                games = df_playoff[(df_playoff['Week'] == row['Week']) & (df_playoff['Day'] == row['Day']) & (df_playoff['Match'] == row['Match'])]
                
                tim_a = str(row['Team_(Blue)'])
                tim_b = str(row['Opponent_(Red)'])
                
                logo_a = get_logo_path(tim_a) if tim_a != "nan" else None
                logo_b = get_logo_path(tim_b) if tim_b != "nan" else None
                
                html_a = f"<img src='data:image/png;base64,{image_to_base64(logo_a)}' style='height: 25px; object-fit: contain;'>" if logo_a else "<span style='color: gray; font-size: 11px; font-weight: bold;'>TBD</span>"
                html_b = f"<img src='data:image/png;base64,{image_to_base64(logo_b)}' style='height: 25px; object-fit: contain;'>" if logo_b else "<span style='color: gray; font-size: 11px; font-weight: bold;'>TBD</span>"
                
                skor_a, skor_b = "", ""
                if row['Status'] == 'History' or games['Result'].notna().any():
                    win_a, win_b = 0, 0
                    for _, g in games.dropna(subset=['Result']).iterrows():
                        if (g['Team_(Blue)'] == tim_a and g['Result'] == 1.0) or (g['Opponent_(Red)'] == tim_a and g['Result'] == 0.0): win_a += 1
                        elif (g['Team_(Blue)'] == tim_b and g['Result'] == 1.0) or (g['Opponent_(Red)'] == tim_b and g['Result'] == 0.0): win_b += 1
                    skor_a, skor_b = str(win_a), str(win_b)
                    
                # Rangkaian HTML Murni untuk membuat kotak skor
                html = "<div style='display: flex; height: 45px; border-radius: 4px; overflow: hidden; margin-bottom: 20px; border-left: 4px solid #d4af37; background-color: #3b3b40;'>"
                html += f"<div style='width: 20%; background-color: #55555d; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white;'>{skor_a}</div>"
                html += f"<div style='width: 60%; display: flex; align-items: center; justify-content: center; gap: 10px;'>{html_a}<img src='data:image/png;base64,{image_to_base64(vs_logo)}' style='height: 20px;'>{html_b}</div>"
                html += f"<div style='width: 20%; background-color: #55555d; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white;'>{skor_b}</div></div>"
                
                st.markdown(html, unsafe_allow_html=True)

        # === RENDER KOLOM BRACKET ===
        with col_b1:
            render_bracket_box(df_playoff[df_playoff['Week'] == 'Pl'], "Play-in Stages")
            
        with col_b2:
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Up') & (df_playoff['Day'] == 'Sf')], "UB Semifinals")
            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True) # Spacer vertikal
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Lw') & (df_playoff['Day'] == 'Sf')], "LB Semifinals")
            
        with col_b3:
            st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True) # Menurunkan posisi Final
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Up') & (df_playoff['Day'] == 'Fl')], "UB Final")
            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Lw') & (df_playoff['Day'] == 'Fl')], "LB Final")
            
        with col_b4:
            st.markdown("<div style='height: 90px;'></div>", unsafe_allow_html=True) # Memposisikan Grand Final di tengah
            render_bracket_box(df_playoff[df_playoff['Week'] == 'Gr'], "Grand Final")

    st.markdown("---")
    
    # === 5. SEASON RECAP (HIGHLIGHTS) ===
    st.markdown("### 📰 Season Recap")
    
    # --- A. MOST EXCITING MATCH ---
    st.markdown("#### ⚔️ Most Exciting Match")
    col_e1, col_e2, col_e3 = st.columns(3)
    
    if not df_history.empty:
        df_hist_view = df_history.copy()
        df_hist_view['Total_Kills'] = df_hist_view['T_Kill'] + df_hist_view['O_Kill']
        
        if df_hist_view['Total_Kills'].sum() > 0:
            bloodiest = df_hist_view.loc[df_hist_view['Total_Kills'].idxmax()]
            longest = df_hist_view.loc[df_hist_view['Duration_min'].apply(konversi_waktu).idxmax()]
            fastest = df_hist_view.loc[df_hist_view['Duration_min'].apply(konversi_waktu).replace(0, np.nan).idxmin()]
            
            def render_epic_card_full_img(row_data, bg_filename, metric_value, font_class):
                tim_a, tim_b = str(row_data['Team_(Blue)']), str(row_data['Opponent_(Red)'])
                logo_a = get_logo_path(tim_a) if tim_a != "nan" else None
                logo_b = get_logo_path(tim_b) if tim_b != "nan" else None
                bg_path = f"assets/Recap/{bg_filename}"
                bg_b64 = image_to_base64(bg_path)
                
                html_a = f"<img src='data:image/png;base64,{image_to_base64(logo_a)}' style='height: 38px; width: 38px; object-fit: contain;'>" if logo_a else f"<span style='color: white; font-weight: bold; font-size: 11px;'>{tim_a}</span>"
                html_b = f"<img src='data:image/png;base64,{image_to_base64(logo_b)}' style='height: 38px; width: 38px; object-fit: contain;'>" if logo_b else f"<span style='color: white; font-weight: bold; font-size: 11px;'>{tim_b}</span>"
                
                # Menggunakan tag <img> penuh agar ukuran asli gambar tidak rusak/berantakan
                html = f"<div style='position: relative; width: 100%; margin-bottom: 20px;'>"
                html += f"<img src='data:image/png;base64,{bg_b64}' style='width: 100%; height: auto; display: block; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>"
                
                # Logo Tim Kiri (Menyesuaikan posisi di sebelah kiri tulisan VS)
                html += f"<div style='position: absolute; bottom: 11%; left: 7%;'>{html_a}</div>"
                
                # Logo Tim Kanan (Menyesuaikan posisi di sebelah kanan tulisan VS)
                html += f"<div style='position: absolute; bottom: 11%; left: 36%;'>{html_b}</div>"
                
                # Teks Metrik dan Match ID di pojok kanan bawah
                html += f"<div style='position: absolute; bottom: 10%; right: 15% ; text-align: right;'><div class='{font_class}' style='line-height: 1.1; margin-bottom: 2px;'>{metric_value}</div>"
                html += f"<div style='color: #d1d1d1; font-size: 14px; font-weight: bold; font-family: sans-serif; letter-spacing: 1px;'>W{row_data['Week']}D{row_data['Day']}G{row_data['Game']}</div></div>"
                html += f"</div>"
                
                return html

            with col_e1:
                st.markdown(render_epic_card_full_img(bloodiest, "bloodbath_art.png", f"{int(bloodiest['Total_Kills'])} KILL", "recap-kill"), unsafe_allow_html=True)
            with col_e2:
                st.markdown(render_epic_card_full_img(longest, "longest_match_art.png", longest['Duration_min'], "recap-time"), unsafe_allow_html=True)
            with col_e3:
                st.markdown(render_epic_card_full_img(fastest, "fastest_match_art.png", fastest['Duration_min'], "recap-time"), unsafe_allow_html=True)
        else:
            st.info("Data Kill dan Durasi belum mencukupi untuk menampilkan Epic Matches.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- B. MVP OF THE SEASON ---
    st.markdown("#### 🎖️ MVP of The Season")
    
    mvp_counts = df_history['MVP'].dropna().value_counts().head(5).reset_index()
    mvp_counts.columns = ['Player', 'Total MVP']
    
    if not mvp_counts.empty:
        cols_mvp = st.columns(5)
        
        def get_team_bg_path(team_name):
            if team_name in TEAM_LOGO_MAP:
                filename = str(TEAM_LOGO_MAP[team_name])
                if filename.endswith(".png"): bg_filename = filename.replace(".png", "_bg.png")
                elif filename.endswith(".jpg"): bg_filename = filename.replace(".jpg", "_bg.jpg")
                else: bg_filename = filename
                path = os.path.join("assets", "Recap", "logo_background", bg_filename)
                if os.path.exists(path): return path
            return "assets/Recap/logo_background/roster_placeholder.png"
            
        player_avatar_path = "assets/Recap/logo_background/roster_placeholder.png"
        player_avatar_b64 = image_to_base64(player_avatar_path)
        
        for idx, row in mvp_counts.iterrows():
            player_name = row['Player']
            total_mvp = row['Total MVP']
            tim_pemain = df_history[df_history['MVP'] == player_name].iloc[0]['Team_(Blue)']
            bg_path = get_team_bg_path(tim_pemain)
            bg_b64 = image_to_base64(bg_path)
            
            hero_html = ""
            try:
                df_player_mvp = df_history[df_history['MVP'] == player_name]
                heroes_list = []
                for _, p_row in df_player_mvp.iterrows():
                    if p_row['Team_(Blue)'] == tim_pemain: h_pick = aman_split(p_row['Heroes_Picked'])
                    else: h_pick = aman_split(p_row['Opponent_Picked'])
                    heroes_list.extend(h_pick)
                
                from collections import Counter
                top_3_heroes = [h[0] for h in Counter(heroes_list).most_common(3)]
                
                hero_html = "<div style='position: absolute; bottom: 6%; width: 100%; display: flex; gap: 8px; justify-content: center; z-index: 3;'>"
                for h in top_3_heroes:
                    h_path = get_hero_path(h)
                    if h_path: hero_html += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='height: 42px; width: 42px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.4); object-fit: cover;'>"
                hero_html += "</div>"
            except Exception as e:
                hero_html = ""

            with cols_mvp[idx]:
                # Kartu MVP menggunakan gambar utuh (full <img>) agar rasionya tidak gepeng
                html_mvp = f"<div style='position: relative; width: 100%; margin-bottom: 20px;'>"
                html_mvp += f"<img src='data:image/png;base64,{bg_b64}' style='width: 100%; height: auto; display: block; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>"
                
                # Badge Total MVP di kiri atas
                html_mvp += f"<div style='position: absolute; top: 3%; left: 3%; background-color: white; color: black; font-weight: 900; font-size: 13px; padding: 2px 7px; border-radius: 4px; box-shadow: 1px 2px 4px rgba(0,0,0,0.5); z-index: 3;'>{total_mvp}</div>"
                
                # Siluet Player Placeholder di tengah atas
                html_mvp += f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 75%; z-index: 2;'><img src='data:image/png;base64,{player_avatar_b64}' style='width: 100%; height: 100%; object-fit: cover; opacity: 0.9;'></div>"
                
                # Nama Pemain di atas area hero
                html_mvp += f"<div style='position: absolute; bottom: 27%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 18px; text-shadow: 1px 1px 4px rgba(0,0,0,0.9); z-index: 3;'>{player_name}</div>"
                
                # Baris 3 Hero di bagian paling bawah kartu
                html_mvp += hero_html
                html_mvp += f"</div>"
                
                st.markdown(html_mvp, unsafe_allow_html=True)
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bagian 2: Meta & Draft
    st.markdown("#### 🦸 Meta & Draft")
    col_m1, col_m2 = st.columns([1, 1.5])
    with col_m1:
        st.caption("☠️ Top Picked Heroes")
        all_heroes_picked = df_long.explode('Heroes_List')['Heroes_List']
        top_heroes = all_heroes_picked.value_counts().head(5).reset_index()
        top_heroes.columns = ['Hero', 'Total Pick']
        st.dataframe(top_heroes, use_container_width=True, hide_index=True)
        
    with col_m2:
        st.caption("🧩 Supreme Combinations (Global Meta)")
        threshold_global = 5 
        global_valid = {combo: {'freq': f, 'wr': (global_wins[combo]/f)*100} for combo, f in global_freq.items() if f >= threshold_global}
        g_combos_to_remove, g_red_combos = set(), set()
        sorted_g_combos = sorted(list(global_valid.keys()), key=len, reverse=True)
        
        for i in range(len(sorted_g_combos)):
            c_large = sorted_g_combos[i]
            if c_large in g_combos_to_remove: continue
            for j in range(i + 1, len(sorted_g_combos)):
                c_small = sorted_g_combos[j]
                if c_small in g_combos_to_remove: continue
                if set(c_small).issubset(set(c_large)):
                    wr_l, wr_s = global_valid[c_large]['wr'], global_valid[c_small]['wr']
                    if wr_s > wr_l: g_combos_to_remove.add(c_large); g_red_combos.add(c_small)
                    elif wr_l > wr_s: g_combos_to_remove.add(c_small); g_red_combos.add(c_large)
                    else:
                        if (global_valid[c_small]['freq'] - global_valid[c_large]['freq']) < threshold_global: g_combos_to_remove.add(c_small)

        top_global = sorted({k: v for k, v in global_valid.items() if k not in g_combos_to_remove}.items(), key=lambda x: (len(x[0]), x[1]['wr'], x[1]['freq']), reverse=True)[:2]
        
        if not top_global:
            st.info("Belum ada kombinasi tim yang dimainkan minimal 5 kali.")
        for combo, stats in top_global:
            w, i, k = ("error", "🌟", "Supreme Meta") if combo in g_red_combos else ("warning", "🔥", "Global Meta")
            render_combo_card(combo, w, i, f"**{' & '.join(combo)}**\nPick: **{stats['freq']}x** | WR: **{stats['wr']:.0f}%**")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bagian 3: Epic Matches
    st.markdown("#### ⚔️ Epic Matches")
    col_e1, col_e2, col_e3 = st.columns(3)
    if not df_history.empty:
        df_hist_view = df_history.copy()
        df_hist_view['Total_Kills'] = df_hist_view['T_Kill'] + df_hist_view['O_Kill']
        
        if df_hist_view['Total_Kills'].sum() > 0:
            bloodiest = df_hist_view.loc[df_hist_view['Total_Kills'].idxmax()]
            longest = df_hist_view.loc[df_hist_view['Duration_min'].apply(konversi_waktu).idxmax()]
            fastest = df_hist_view.loc[df_hist_view['Duration_min'].apply(konversi_waktu).replace(0, np.nan).idxmin()]
            
            with col_e1:
                st.info(f"**🩸 Bloodbath Match**\n\n{bloodiest['Team_(Blue)']} vs {bloodiest['Opponent_(Red)']}\n\nTotal Kills: **{bloodiest['Total_Kills']}**\n\n(W{bloodiest['Week']} - Game {bloodiest['Game']})")
            with col_e2:
                st.warning(f"**⏳ Longest Match**\n\n{longest['Team_(Blue)']} vs {longest['Opponent_(Red)']}\n\nDurasi: **{longest['Duration_min']}**\n\n(W{longest['Week']} - Game {longest['Game']})")
            with col_e3:
                st.success(f"**⚡ Fastest Match**\n\n{fastest['Team_(Blue)']} vs {fastest['Opponent_(Red)']}\n\nDurasi: **{fastest['Duration_min']}**\n\n(W{fastest['Week']} - Game {fastest['Game']})")
        else:
            st.info("Data Kill dan Durasi belum mencukupi untuk menampilkan Epic Matches.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bagian 4: Riwayat Pertandingan
    st.markdown("#### 📜 Riwayat Pertandingan")
    tim_filter = st.selectbox("Cari Jejak Tim:", ["Semua Tim"] + sorted(df_long['Team'].unique().tolist()))
    
    hist_display = df_history[['Date', 'Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']].copy()
    if tim_filter != "Semua Tim":
        hist_display = hist_display[(hist_display['Team_(Blue)'] == tim_filter) | (hist_display['Opponent_(Red)'] == tim_filter)]
        
    hist_display['Result'] = hist_display['Result'].apply(lambda x: "Blue Win" if x == 1 else "Red Win")
    
    # [+] FIX: Ubah string menjadi datetime murni khusus untuk logika pengurutan
    hist_display['Date_Sort'] = pd.to_datetime(hist_display['Date'], errors='coerce')
    
    # Urutkan secara KRONOLOGIS murni (Tanggal terlama ke terbaru, lalu Match 1, 2, Game 1, 2)
    # Jika ingin dari yang TERBARU (Hari ini) di atas, ganti ascending menjadi [False, False, True, True]
    hist_display = hist_display.sort_values(
        by=['Date_Sort', 'Week', 'Match', 'Game'], 
        ascending=[False, False, False, True] 
    ).drop(columns=['Date_Sort'])
    
    st.dataframe(hist_display, use_container_width=True, hide_index=True)

# endregion

# region PROFILING
elif menu_utama == "🛡️ Team Profiling":
    st.title(f"🛡️ Profiling Tim IKL - {musim_pilihan}")
    
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
                render_logo_card(logo_path, tim)
                
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
                    render_combo_card(k["combo"], k["warna"], k["ikon"], k["teks"])
# endregion

# region H2H
elif menu_utama == "⚔️ Versus Mode (H2H)":
    st.title(f"⚔️ H2H: Duel Mekanik & Taktik ({musim_pilihan})")

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
                logo_path = get_logo_path(tim)
                render_logo_card(logo_path, tim)
                
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
            st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
            st.button("Menunggu pilihan...", use_container_width=True, disabled=True)
            
        st.markdown("---")
        st.markdown(f"**Pilih lawan dari daftar di bawah ini untuk menantang {tim_A}:**")
        
        kolom_grid = st.columns(4)
        for idx, tim in enumerate(daftar_tim):
            with kolom_grid[idx % 4]:
                logo_path = get_logo_path(tim)
                render_logo_card(logo_path, tim)
                        
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