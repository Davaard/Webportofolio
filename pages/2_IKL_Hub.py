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
    @import url('https://fonts.googleapis.com/css2?family=Condiment&family=Londrina+Shadow&family=Rajdhani:wght@500;700&family=Montserrat:wght@400;600;800&display=swap');

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
        font-family: 'Condiment', system-ui;
        font-size: 35px;
        color: transparent;
        -webkit-text-stroke: 1px #ffffff;
        margin-bottom: -10px;
    }
    .recap-time {
        font-family: 'Londrina Shadow', fantasy;
        font-size: 35px;
        color: #ffffff;
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

@st.cache_data(ttl=60)
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

# Load konfigurasi musim
@st.cache_data(ttl=86400)
def load_season_config():
    if os.path.exists("IKL_Seasons.csv"):
        return pd.read_csv("IKL_Seasons.csv")
    return pd.DataFrame(columns=['Season', 'Group_Names', 'Group_Teams'])

df_seasons = load_season_config()

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
        
        # === MESIN TRANSLASI REBRANDING TIM ===
        if os.path.exists("IKL_Rebrands.csv"):
            df_rebrand = pd.read_csv("IKL_Rebrands.csv")
            # Filter aturan ganti nama HANYA untuk musim yang sedang dipilih
            rebrand_musim = df_rebrand[df_rebrand['Season'] == musim_pilihan]
            
            if not rebrand_musim.empty:
                map_rebrand = dict(zip(rebrand_musim['Old_Name'], rebrand_musim['New_Name']))
                df_master['Team_(Blue)'] = df_master['Team_(Blue)'].replace(map_rebrand)
                df_master['Opponent_(Red)'] = df_master['Opponent_(Red)'].replace(map_rebrand)
    else:
        st.error("Kolom 'Season' tidak ditemukan!")
        st.stop()
# ==================================================

# region UI HELPERS
# UI Helpers dikembalikan ke bawah musim_pilihan agar tidak NameError
@st.cache_data(ttl=60)
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

# === HELPER FOTO PEMAIN & KOORDINAT MAP ===
def get_player_path(player_name):
    # Asumsi foto pemain ada di folder assets/players (sesuaikan jika berbeda)
    safe_name = str(player_name).replace(" ", "_")
    for ext in ['.png', '.jpg', '.jpeg']:
        path = f"assets/players/{safe_name}{ext}"
        if os.path.exists(path): return path
    return "assets/Recap/logo_background/roster_placeholder.png"

# Koordinat CSS Absolute untuk meletakkan pemain di atas Map HOK
MAP_COORDINATES = {
    # Clash Lane biasanya di area kiri atas
    'Top Lane': {'top': '25%', 'left': '25%', 'transform': 'translate(-50%, -50%)'},
    
    # Jungler biasanya mondar-mandir di area atas/tengah hutan
    'Jungler': {'top': '46%', 'left': '32%', 'transform': 'translate(-50%, -50%)'},
    
    # Mid Lane pas di tengah-tengah
    'Middle': {'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'},
    
    # Roamer biasanya di sungai area bawah
    'Roamer': {'top': '55%', 'left': '67%', 'transform': 'translate(-50%, -50%)'},
    
    # Farm Lane (Bottom) biasanya di area kanan bawah
    'Bottom Lane': {'top': '75%', 'left': '75%', 'transform': 'translate(-50%, -50%)'}
}

# Mapping Icon Role langsung ke Path Aset
ROLE_ICONS = {
    'Top Lane': 'clashlane_icon.png',
    'Jungler': 'jungle_icon.png',
    'Middle': 'midlane_icon.png',
    'Bottom Lane': 'farmlane_icon.png',
    'Roamer': 'support_icon.png'
}

# === MESIN PEMBACA PROFIL TIM (NAMA PANJANG, WARNA, & GRUP) ===
@st.cache_data(ttl=86400)
def get_team_data():
    if os.path.exists("IKL_Teams.csv"):
        df_teams = pd.read_csv("IKL_Teams.csv")
        # Ambil data paling baru untuk setiap tim agar nama & warna selalu up-to-date
        df_global = df_teams.drop_duplicates(subset=['Team'], keep='last')
        map_nama = dict(zip(df_global['Team'], df_global['Full_Name']))
        map_warna = dict(zip(df_global['Team'], df_global['Color_Hex']))
        return df_teams, map_nama, map_warna
    return pd.DataFrame(), {}, {}

DF_TEAMS_MASTER, TEAM_FULLNAME_MAP, TEAM_COLOR_MAP = get_team_data()
# ==============================================================

def get_team_bg_path(team_name):
    if team_name in TEAM_LOGO_MAP:
        filename = str(TEAM_LOGO_MAP[team_name])
        if filename.endswith(".png"): bg_filename = filename.replace(".png", "_bg.png")
        elif filename.endswith(".jpg"): bg_filename = filename.replace(".jpg", "_bg.jpg")
        else: bg_filename = filename
        path = os.path.join("assets", "Recap", "logo_background", bg_filename)
        if os.path.exists(path): return path
    return "assets/Recap/logo_background/roster_placeholder.png"

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

def render_combo_card(combo_tuple, warna, freq, wr, label):
    tema = {
        "error": {"border": "#ff4b4b"},
        "warning": {"border": "#ffc107"},
        "success": {"border": "#4caf50"}
    }
    brdr = tema.get(warna, {"border": "#4caf50"})["border"]
    combo_name = " & ".join(combo_tuple)
    
    html = f"<div style='background-color: #24242e; border-left: 5px solid {brdr}; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>"
    html += "<div style='display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;'>"
    for hero in combo_tuple:
        h_path = get_hero_path(hero)
        if h_path:
            html += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 45px; height: 45px; border-radius: 6px; object-fit: cover; border: 1px solid rgba(255,255,255,0.2);'>"
        else:
            html += f"<div style='width: 45px; height: 45px; background: #444; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:9px;'>{hero}</div>"
    html += "</div>"
    
    html += f"<div style='color: #d1d1d1; font-family: \"Montserrat\", sans-serif;'>"
    html += f"<div style='font-size: 13px; margin-bottom: 4px; line-height: 1.2;'><b>{combo_name}</b></div>"
    html += f"<div style='font-size: 12px; font-weight: 600; color: #a0a0a0;'>Pick: <b style='color: white;'>{freq}x</b> | WR: <b style='color: white;'>{wr:.0f}%</b></div>"
    html += f"<div style='font-size: 11px; font-weight: 800; color: {brdr}; margin-top: 4px;'>{label}</div>"
    html += "</div></div>"
    
    st.markdown(html, unsafe_allow_html=True)

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
        
        # Emoji dihapus dan output diubah menjadi variabel mentah
        if rasio > 25.0:
            w, s = ("error", f"Supreme Meta ({rasio:.0f}%)") if is_red else ("warning", f"Global Meta ({rasio:.0f}%)")
        else:
            w, s = ("success", "Team Signature Pick")
            
        hasil_ui.append({"warna": w, "freq": stats['freq'], "wr": stats['wr'], "label": s, "combo": combo})
        
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
                tim_panjang = TEAM_FULLNAME_MAP.get(tim_singkat, tim_singkat)
                
                html_table += f"<tr><td style='font-weight: bold;'>{row['Rank']}</td>"
                html_table += f"<td class='team-cell'>{logo_tag} <span style='font-weight: 600; font-size: 13px;'>{tim_panjang}</span></td>"
                html_table += f"<td style='font-weight: bold; font-size: 16px;'>{row['Match']}</td>"
                html_table += f"<td>{row['Match_WL']}</td><td>{row['Game_WL']}</td>"
                html_table += f"<td style='font-weight: bold; font-size: 16px;'>{row['Windiff']}</td></tr>"
            html_table += "</tbody></table>"
            st.markdown(html_table, unsafe_allow_html=True)
        
        # === SISTEM KLASEMEN MULTI-GRUP OTOMATIS ===
        if not DF_TEAMS_MASTER.empty:
            # Ambil daftar tim khusus untuk musim yang sedang dipilih
            df_season_teams = DF_TEAMS_MASTER[DF_TEAMS_MASTER['Season'] == musim_pilihan]
            
            # Cari tahu ada grup apa saja di musim ini (Abaikan yang kosong/NaN)
            grup_unik = df_season_teams['Group'].dropna().unique()
            
            if len(grup_unik) > 0:
                st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>Format {musim_pilihan}: {len(grup_unik)} Group Stage</p>", unsafe_allow_html=True)
                
                # Buat kolom sejajar otomatis sebanyak jumlah grup
                kolom_grup = st.columns(len(grup_unik))
                
                for idx, nama_grup in enumerate(grup_unik):
                    # Cari siapa saja tim yang masuk di grup ini
                    tim_di_grup = df_season_teams[df_season_teams['Group'] == nama_grup]['Team'].tolist()
                    
                    df_grup = df_tampil[df_tampil['Team'].isin(tim_di_grup)].reset_index(drop=True)
                    df_grup['Rank'] = df_grup['Windiff'].rank(method='min', ascending=False).astype(int)
                    df_grup = df_grup.sort_values('Rank')
                    
                    warna_judul = ["#00d2ff", "#ff4b4b", "#4caf50", "#ffc107"][idx % 4]
                    
                    with kolom_grup[idx]:
                        st.markdown(f"<h5 style='text-align: center; color: {warna_judul};'>Group {nama_grup}</h5>", unsafe_allow_html=True)
                        render_clean_table(df_grup)
            else:
                # Jika kolom Group kosong semua, jadikan Single League
                st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>Format {musim_pilihan}: Single Global League</p>", unsafe_allow_html=True)
                render_clean_table(df_tampil)
        else:
            # Fallback jika CSV belum dibuat
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>Format {musim_pilihan}: Single Global League</p>", unsafe_allow_html=True)
            render_clean_table(df_tampil)

    else:
        st.info("Data Regular Season belum tersedia.")

    st.markdown("<hr style='border-color: #333; margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    
    # 4. BRACKET PLAYOFFS
    st.markdown("### Playoff")
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
            
        player_avatar_path = "assets/Recap/logo_background/roster_placeholder.png"
        player_avatar_b64 = image_to_base64(player_avatar_path)
        
        # === AUTOMATIC ROLE MAPPING DARI IKL_Rosters.csv ===
        # Membaca data pemain secara otomatis untuk menentukan indeks hero mereka (0=Clash, 1=Jungle, 2=Mid, 3=Farm, 4=Roam)
        PLAYER_ROLE_MAP = {}
        try:
            df_roster_map = pd.read_csv('IKL_Rosters.csv')
            role_to_idx = {
                'Top Lane': 0,     # Clash
                'Jungler': 1,      # Jungle
                'Middle': 2,       # Mid
                'Bottom Lane': 3,  # Farm (Marksman)
                'Roamer': 4        # Roam
            }
            # Mendaftarkan setiap pemain ke dalam memori komputer
            for _, r in df_roster_map.dropna(subset=['Player_ID', 'Role']).iterrows():
                if r['Role'] in role_to_idx:
                    PLAYER_ROLE_MAP[r['Player_ID']] = role_to_idx[r['Role']]
        except Exception as e:
            # Jika file gagal dimuat, akan mengabaikan filter dan menampilkan semua hero
            pass
            
        for idx, row in mvp_counts.iterrows():
            player_name = row['Player']
            total_mvp = row['Total MVP']
            
            # Mencari tim pemain yang benar (Tim tempat dia bermain dan Menang)
            tim_pemain_df = df_long[(df_long['MVP'] == player_name) & (df_long['Win'] == 1)]
            if not tim_pemain_df.empty:
                tim_pemain = tim_pemain_df['Team'].mode()[0]
            else:
                tim_pemain = df_long[df_long['MVP'] == player_name]['Team'].mode()[0]
            
            bg_path = get_team_bg_path(tim_pemain)
            bg_b64 = image_to_base64(bg_path)
            
            hero_html = ""
            try:
                df_player_mvp = df_history[df_history['MVP'] == player_name]
                heroes_list = []
                
                # Cek role player dari file Roster
                role_index = PLAYER_ROLE_MAP.get(player_name, None)
                
                for _, p_row in df_player_mvp.iterrows():
                    if p_row['Team_(Blue)'] == tim_pemain: h_pick = aman_split(p_row['Heroes_Picked'])
                    else: h_pick = aman_split(p_row['Opponent_Picked'])
                    
                    # LOGIKA PINTAR: Jika player punya role yang valid, HANYA ambil hero di lane tersebut!
                    if role_index is not None and len(h_pick) > role_index:
                        heroes_list.append(h_pick[role_index])
                    else:
                        # Fallback jika role tidak diketahui
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
                html_mvp = f"<div style='position: relative; width: 100%; margin-bottom: 20px;'>"
                html_mvp += f"<img src='data:image/png;base64,{bg_b64}' style='width: 100%; height: auto; display: block; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);'>"
                
                html_mvp += f"<div style='position: absolute; top: 3%; left: 3%; background-color: white; color: black; font-weight: 900; font-size: 13px; padding: 2px 7px; border-radius: 4px; box-shadow: 1px 2px 4px rgba(0,0,0,0.5); z-index: 3;'>{total_mvp}</div>"
                
                html_mvp += f"<div style='position: absolute; top: 0; left: 0; width: 100%; height: 75%; z-index: 2;'><img src='data:image/png;base64,{player_avatar_b64}' style='width: 100%; height: 100%; object-fit: cover; opacity: 0.9;'></div>"
                
                html_mvp += f"<div style='position: absolute; bottom: 27%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 18px; text-shadow: 1px 1px 4px rgba(0,0,0,0.9); z-index: 3;'>{player_name}</div>"
                
                html_mvp += hero_html
                html_mvp += f"</div>"
                
                st.markdown(html_mvp, unsafe_allow_html=True)
                
    st.markdown("<br>", unsafe_allow_html=True)

    # --- C. MOST UNSTOPPABLE TEAM (WINSTREAK & DRAFT PATTERN) ---
    st.markdown("#### 🚀 Most Unstoppable Team")
    
    if not df_long.empty:
        # 1. MESIN PENCARI MATCH WINSTREAK (Akumulasi per Seri Pertandingan)
        match_df = df_long.groupby(['Week', 'Day', 'Match', 'Team'], sort=False).agg(
            Game_W=('Win', 'sum'), 
            Game_L=('Win', lambda x: (x == 0.0).sum())
        ).reset_index()
        match_df['Match_Win'] = (match_df['Game_W'] > match_df['Game_L']).astype(int)
        
        opp_df = df_long.groupby(['Week', 'Day', 'Match', 'Team'])['Opponent'].first().reset_index()
        match_df = match_df.merge(opp_df, on=['Week', 'Day', 'Match', 'Team'])

        team_match_streaks = []
        for team in match_df['Team'].dropna().unique():
            df_t = match_df[match_df['Team'] == team]
            wins = df_t['Match_Win'].tolist()
            opps = df_t['Opponent'].tolist()
            matches = df_t['Match'].tolist()
            
            max_st, curr_st = 0, 0
            best_opps = []
            curr_opps = []
            
            for w, opp, mid in zip(wins, opps, matches):
                if w == 1:
                    curr_st += 1
                    curr_opps.append((opp, mid))
                    if curr_st > max_st: 
                        max_st = curr_st
                        best_opps = list(curr_opps)
                else:
                    curr_st = 0
                    curr_opps = []
                    
            team_match_streaks.append({'Team': team, 'Max_Streak': max_st, 'Streak_Opps': best_opps, 'Total_Matches': len(wins)})
            
        team_match_streaks.sort(key=lambda x: x['Max_Streak'], reverse=True)
        top_team_data = team_match_streaks[0]
        tim_unstoppable = top_team_data['Team']
        
        tim_2 = team_match_streaks[1]['Team'] if len(team_match_streaks) > 1 else "-"
        tim_3 = team_match_streaks[2]['Team'] if len(team_match_streaks) > 2 else "-"
        
        # Mencari lawan terberat dalam streak tersebut (Berdasarkan Rank Klasemen di df_tampil)
        streak_opps = top_team_data['Streak_Opps']
        toughest_opp, match_score = "Unknown", "0-0"
        
        if streak_opps and 'df_tampil' in locals() and not df_tampil.empty:
            rank_dict = dict(zip(df_tampil['Team'], df_tampil['Rank']))
            best_opp_tuple = min(streak_opps, key=lambda x: rank_dict.get(x[0], 99))
            toughest_opp = best_opp_tuple[0]
            
            skor_data = match_df[(match_df['Team'] == tim_unstoppable) & (match_df['Opponent'] == toughest_opp)]
            if not skor_data.empty:
                skor_w = int(skor_data.iloc[0]['Game_W'])
                skor_l = int(skor_data.iloc[0]['Game_L'])
                match_score = f"{skor_w} - {skor_l}"
                
        # Menghitung Persentase Kemenangan Sisi (Blue vs Red)
        blue_wins = len(df_history[(df_history['Team_(Blue)'] == tim_unstoppable) & (df_history['Result'] == 1.0)])
        red_wins = len(df_history[(df_history['Opponent_(Red)'] == tim_unstoppable) & (df_history['Result'] == 0.0)])
        total_wins_overall = blue_wins + red_wins
        
        if total_wins_overall > 0:
            pct_blue = (blue_wins / total_wins_overall) * 100
            pct_red = (red_wins / total_wins_overall) * 100
            if pct_blue >= pct_red:
                dominant_side = "Biru (Blue)"
                dominant_pct = pct_blue
            else:
                dominant_side = "Merah (Red)"
                dominant_pct = pct_red
            teks_sisi = f" Menariknya, sebanyak <b style='color: white;'>{dominant_pct:.0f}%</b> kemenangan {tim_unstoppable} secara keseluruhan diperoleh saat mereka berada di sisi <b style='color: white;'>{dominant_side}</b>."
        else:
            teks_sisi = ""
            
        # Mencari MVP terbanyak di tim tersebut
        mvp_team = df_long[(df_long['Team'] == tim_unstoppable) & (df_long['Win'] == 1)]['MVP'].value_counts()
        most_mvp_player = mvp_team.idxmax() if not mvp_team.empty else "Pemain Kunci"
        
        kombo_andalan = get_signature_combos(tim_unstoppable)
        
        # 2. LOGIKA WARNA BORDER (GLOBAL PRESENCE) & DATA DRAFT
        total_global_matches = len(df_history)
        all_picks_global = df_long.explode('Heroes_List')['Heroes_List'].value_counts()
        
        bans_b_global = df_history['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
        bans_r_global = df_history['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
        all_bans_global = pd.concat([bans_b_global, bans_r_global]).value_counts()
             
        def get_border_color(hero_name):
            p = all_picks_global.get(hero_name, 0)
            b = all_bans_global.get(hero_name, 0)
            presence_rate = (p + b) / max(total_global_matches, 1)
            
            if presence_rate >= 0.8: return "#ff4b4b" 
            elif presence_rate >= 0.3: return "#ffc107" 
            else: return "#4caf50" 

        team_picks = df_long[df_long['Team'] == tim_unstoppable].explode('Heroes_List')['Heroes_List'].value_counts().head(5)
        
        team_bans_blue = df_history[df_history['Team_(Blue)'] == tim_unstoppable]['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
        team_bans_red = df_history[df_history['Opponent_(Red)'] == tim_unstoppable]['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
        team_bans = pd.concat([team_bans_blue, team_bans_red]).value_counts().head(5)
        
        # 3. RENDER UI 
        col_u1, col_u2 = st.columns([1, 2.5])
        
        with col_u1:
            logo_path = get_logo_path(tim_unstoppable)
            logo_b64 = image_to_base64(logo_path) if logo_path else ""
            tim_panjang = TEAM_FULLNAME_MAP.get(tim_unstoppable, tim_unstoppable)
            
            html_team = f"""
            <div style="text-align: center; margin-top: 20px;">
                <img src="data:image/png;base64,{logo_b64}" style="width: 100%; max-width: 200px; object-fit: contain;">
                <h2 style="color: white; font-family: 'Montserrat', sans-serif; font-weight: 800; margin-top: 25px; line-height: 1.3;">
                    {tim_panjang}
                </h2>
            </div>
            """
            st.markdown(html_team, unsafe_allow_html=True)
            
        with col_u2:
            narasi_unstoppable = f"""
            <div style="color: #e0e0e0; font-family: 'Montserrat', sans-serif; font-size: 14px; line-height: 1.8; text-align: justify; margin-bottom: 20px;">
                <span class="highlight-text">{tim_panjang}</span> berhasil memperoleh rekor <b style="color: white;">{top_team_data['Max_Streak']} winstreak (Kemenangan Seri Beruntun)</b> dari total {top_team_data['Total_Matches']} pertandingan mereka di musim ini, disusul oleh {tim_2} dan {tim_3}. Dalam rentetan kemenangan tersebut, lawan terberat yang berhasil mereka tumbangkan adalah <b style="color: white;">{toughest_opp}</b> dengan skor <b style="color: white;">{match_score}</b>.{teks_sisi} Selain itu, <b>{most_mvp_player}</b> menjadi pemain kunci yang paling sering bersinar di lapangan.<br><br>
                Berikut adalah strategi rancangan draft kombo yang menjadi andalan dan rahasia kemenangan {tim_unstoppable}:
            </div>
            """
            st.markdown(narasi_unstoppable, unsafe_allow_html=True)
            
            if kombo_andalan:
                cols_k = st.columns(3)
                for i, k in enumerate(kombo_andalan[:3]):
                    with cols_k[i]:
                        render_combo_card(k["combo"], k["warna"], k["freq"], k["wr"], k["label"])
                        
            html_pb = "<div style='display: flex; gap: 20px; margin-top: 10px;'>"
            
            html_pb += "<div style='flex: 1; background-color: #2a2a35; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>"
            html_pb += "<div style='color: white; font-weight: bold; margin-bottom: 10px; font-size: 14px;'>Most Picked</div>"
            html_pb += "<div style='display: flex; gap: 8px;'>"
            for hero_name, _ in team_picks.items():
                h_path = get_hero_path(hero_name)
                border_color = get_border_color(hero_name)
                if h_path: 
                    html_pb += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 48px; height: 48px; object-fit: cover; border: 2.5px solid {border_color}; border-radius: 4px;'>"
                else:
                    html_pb += f"<div style='width: 48px; height: 48px; background: #444; border: 2.5px solid {border_color}; border-radius: 4px; display:flex; align-items:center; justify-content:center; font-size:8px; text-align:center;'>{hero_name}</div>"
            html_pb += "</div></div>"
            
            html_pb += "<div style='flex: 1; background-color: #2a2a35; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>"
            html_pb += "<div style='color: white; font-weight: bold; margin-bottom: 10px; font-size: 14px;'>Most Banned</div>"
            html_pb += "<div style='display: flex; gap: 8px;'>"
            for hero_name, _ in team_bans.items():
                h_path = get_hero_path(hero_name)
                border_color = get_border_color(hero_name)
                if h_path: 
                    # Filter grayscale sudah DIHAPUS, gambar akan tampil cerah sepenuhnya
                    html_pb += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 48px; height: 48px; object-fit: cover; border: 2.5px solid {border_color}; border-radius: 4px;'>"
                else:
                    html_pb += f"<div style='width: 48px; height: 48px; background: #444; border: 2.5px solid {border_color}; border-radius: 4px; display:flex; align-items:center; justify-content:center; font-size:8px; text-align:center;'>{hero_name}</div>"
            html_pb += "</div></div>"
            
            html_pb += "</div>"
            st.markdown(html_pb, unsafe_allow_html=True)
            
    st.markdown("<hr style='border-color: #333; margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    
    #==========================================
    # BAGIAN 2: META & DRAFT (MOST EFFECTIVE TACTIC)
    # ==========================================
    st.markdown("### 📊 Most Efective Tactic Available")
    
    # 1. PERSIAPAN DATA GLOBAL
    picks_b = df_history['Heroes_Picked'].dropna().astype(str).str.split(',').explode().str.strip()
    picks_r = df_history['Opponent_Picked'].dropna().astype(str).str.split(',').explode().str.strip()
    all_picks_global = pd.concat([picks_b, picks_r]).value_counts()
    top_5_picks = all_picks_global.head(5)
    
    bans_b_global = df_history['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
    bans_r_global = df_history['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
    all_bans_global = pd.concat([bans_b_global, bans_r_global]).value_counts()
    top_5_bans = all_bans_global.head(5)
    
    # LOGIKA CERDAS: MENCARI COUNTER-PICK BERDASARKAN LANE
    from collections import Counter
    counter_pick_results = []
    
    for hero in top_5_picks.index:
        counters = []
        hero_total_matches = 0
        
        for _, row in df_history.dropna(subset=['Heroes_Picked', 'Opponent_Picked']).iterrows():
            blue_draft = [h.strip() for h in str(row['Heroes_Picked']).split(',')]
            red_draft = [h.strip() for h in str(row['Opponent_Picked']).split(',')]
            
            if len(blue_draft) == 5 and len(red_draft) == 5:
                if hero in blue_draft:
                    hero_total_matches += 1
                    idx = blue_draft.index(hero)
                    if idx in [0, 3]: 
                        counters.append(red_draft[idx])
                    elif idx in [1, 2, 4]: 
                        counters.extend([red_draft[1], red_draft[2], red_draft[4]])
                        
                elif hero in red_draft:
                    hero_total_matches += 1
                    idx = red_draft.index(hero)
                    if idx in [0, 3]: 
                        counters.append(blue_draft[idx])
                    elif idx in [1, 2, 4]: 
                        counters.extend([blue_draft[1], blue_draft[2], blue_draft[4]])
                        
        if counters:
            most_counter = Counter(counters).most_common(1)[0]
            counter_hero = most_counter[0]
            counter_pct = (most_counter[1] / max(hero_total_matches, 1)) * 100
        else:
            counter_hero = "-"
            counter_pct = 0
            
        counter_pick_results.append({
            'Target': hero,
            'Counter': counter_hero,
            'Pct': counter_pct
        })

    # 2. RENDER UI CUSTOM (Desain Card Gradasi + Border Gradasi)
    col_meta1, col_meta2 = st.columns([2.5, 1.2]) 
    
    vs_logo_path = "assets/Match/vs_full_gold.png"
    vs_b64 = image_to_base64(vs_logo_path)
    
    banned_logo_path = "assets/Match/banned.png"
    banned_b64 = image_to_base64(banned_logo_path)
    
    with col_meta1:
        html_kiri = "<div style='padding-right: 10px;'><div style='padding: 0 5px; margin-bottom: 12px;'><h4 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-size: 15px;'>Most Picked Heroes and its counter pick</h4></div>"
        
        for data in counter_pick_results:
            target_hero = data['Target']
            counter_hero = data['Counter']
            pct = data['Pct']
            pick_count = top_5_picks.get(target_hero, 0)
            
            t_path = get_hero_path(target_hero)
            c_path = get_hero_path(counter_hero)
            
            t_img = f"<img src='data:image/png;base64,{image_to_base64(t_path)}' style='width: 50px; height: 50px; border: 2px solid #d4af37; border-radius: 6px; object-fit: cover;'>" if t_path else f"<div style='width: 50px; height: 50px; background: #444; border: 2px solid #d4af37; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:9px;'>{target_hero}</div>"
            c_img = f"<img src='data:image/png;base64,{image_to_base64(c_path)}' style='width: 50px; height: 50px; border: 2px solid #d4af37; border-radius: 6px; object-fit: cover;'>" if c_path else f"<div style='width: 50px; height: 50px; background: #444; border: 2px solid #d4af37; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:9px;'>{counter_hero}</div>"
            vs_img = f"<img src='data:image/png;base64,{vs_b64}' style='height: 38px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));'>" if vs_b64 else "<span style='color:#d4af37; font-weight:900; font-style:italic;'>VS</span>"

            # Trik Wrapper untuk Border Gradasi (merah tua ke biru) & flex: 1 text-align: center untuk nama
            html_kiri += f"<div style='background: linear-gradient(to right, #7a0b0b, #10105c); padding: 2px; border-radius: 9px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><div style='background: linear-gradient(135deg, #020147 35%, #430000 65%); border-radius: 7px; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between;'><div style='display: flex; align-items: center; width: 42%;'>{t_img}<div style='flex: 1; text-align: center;'><span style='color: white; font-weight: 700; font-size: 19px; letter-spacing: 0.5px;'>{target_hero}</span></div><span style='color: white; font-weight: 800; font-size: 19px;'>{pick_count}x</span></div><div style='width: 10%; text-align: center; display: flex; align-items: center; justify-content: center;'>{vs_img}</div><div style='display: flex; align-items: center; width: 42%;'><span style='color: white; font-weight: 800; font-size: 19px;'>{pct:.0f}%</span><div style='flex: 1; text-align: center;'><span style='color: white; font-weight: 700; font-size: 19px; letter-spacing: 0.5px;'>{counter_hero}</span></div>{c_img}</div></div></div>"
            
        html_kiri += "</div>"
        st.markdown(html_kiri, unsafe_allow_html=True)
        
    with col_meta2:
        html_kanan = "<div style='padding-left: 10px;'><div style='padding: 0 5px; margin-bottom: 12px;'><h4 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-size: 15px;'>Most Banned Hero</h4></div>"
        
        for hero, count in top_5_bans.items():
            h_path = get_hero_path(hero)
            
            if h_path:
                h_img = f"<div style='position: relative; width: 50px; height: 50px;'><img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 100%; height: 100%; border-radius: 6px; object-fit: cover; border: 2px solid #d4af37; filter: contrast(0.6) brightness(0.85);'><img src='data:image/png;base64,{banned_b64}' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.9;'></div>"
            else:
                h_img = f"<div style='position: relative; width: 50px; height: 50px; background: #444; border: 2px solid #d4af37; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:9px;'><img src='data:image/png;base64,{banned_b64}' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.9;'>{hero}</div>"

            html_kanan += f"<div style='background-color: #24242e; border: 2px solid #8c3636; border-radius: 8px; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'><div style='display: flex; align-items: center; gap: 15px;'>{h_img}<span style='color: white; font-weight: 700; font-size: 19px; letter-spacing: 0.5px;'>{hero}</span></div><span style='color: white; font-weight: 800; font-size: 19px;'>{count}x</span></div>"
            
        html_kanan += "</div>"
        st.markdown(html_kanan, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # BAGIAN 3: MOST FAVORITE BANS & PICKS (GLOBAL COMBOS)
    # ==========================================
    st.markdown("### 🌍 Most Favorite Heroes Combos")
    st.markdown("<div style='color: #a0a0a0; font-size: 13px; margin-top: -10px; margin-bottom: 20px;'>*Menampilkan Top 10 kombinasi meta global berdasarkan rasio keterikatan taktik (persentase) dan keragaman tim yang menggunakannya.</div>", unsafe_allow_html=True)
    
    if not df_history.empty:
        import itertools
        from collections import Counter
        
        hero_freq = {}
        global_freq = {}
        global_wins = {}
        combo_matches = {}
        
        # 1. MESIN EKSTRAKSI FREKUENSI HERO INDIVIDU
        for _, row in df_history.dropna(subset=['Heroes_Picked', 'Opponent_Picked']).iterrows():
            b_draft = [h.strip() for h in str(row['Heroes_Picked']).split(',')]
            r_draft = [h.strip() for h in str(row['Opponent_Picked']).split(',')]
            for h in b_draft + r_draft:
                hero_freq[h] = hero_freq.get(h, 0) + 1
        
        # 2. MESIN EKSTRAKSI KOMBINASI HERO
        for _, row in df_history.dropna(subset=['Heroes_Picked', 'Opponent_Picked']).iterrows():
            b_draft = [h.strip() for h in str(row['Heroes_Picked']).split(',')]
            r_draft = [h.strip() for h in str(row['Opponent_Picked']).split(',')]
            
            b_win = 1 if row['Result'] == 1.0 else 0
            r_win = 1 if row['Result'] == 0.0 else 0
            
            def process_draft(draft, team, win):
                for size in range(2, 6):
                    for cb in itertools.combinations(sorted(draft), size):
                        global_freq[cb] = global_freq.get(cb, 0) + 1
                        global_wins[cb] = global_wins.get(cb, 0) + win
                        
                        if cb not in combo_matches:
                            combo_matches[cb] = []
                        combo_matches[cb].append(team)
                        
            process_draft(b_draft, str(row['Team_(Blue)']), b_win)
            process_draft(r_draft, str(row['Opponent_(Red)']), r_win)

        # 3. PENYARINGAN KELENGKETAN META (>25%) & MINIMAL PICK
        threshold_global = 3 
        global_valid = {}
        
        for combo, f in global_freq.items():
            if f >= threshold_global:
                if len(combo) == 2:
                    g_base = min([hero_freq.get(h, 1) for h in combo])
                else:
                    g_base = max([0] + [global_freq.get(sc, 0) for sc in itertools.combinations(combo, len(combo)-1)])
                
                rasio = (f / g_base * 100) if g_base > 0 else 0
                
                if rasio > 25.0:
                    global_valid[combo] = {
                        'freq': f, 
                        'wr': (global_wins[combo]/f)*100,
                        'rasio': rasio,
                        'unique_teams': len(set(combo_matches[combo])) 
                    }
                    
        if len(global_valid) < 10:
            for combo, f in global_freq.items():
                if f >= 2 and combo not in global_valid:
                    global_valid[combo] = {'freq': f, 'wr': (global_wins[combo]/f)*100, 'rasio': 0, 'unique_teams': len(set(combo_matches[combo]))}

        # 4. ELIMINASI SUBSET CERDAS & PENENTUAN SUPREME META
        g_combos_to_remove, g_red_combos = set(), set()
        sorted_g_combos = sorted(list(global_valid.keys()), key=len, reverse=True)
        
        for i in range(len(sorted_g_combos)):
            c_large = sorted_g_combos[i]
            if c_large in g_combos_to_remove: continue
            
            wr_large = global_valid[c_large]['wr']
            if len(c_large) == 2:
                max_trio_wr = max([0] + [(global_wins[gc]/global_freq[gc])*100 for gc in global_freq if len(gc)==3 and set(c_large).issubset(set(gc))])
                if wr_large > max_trio_wr: g_red_combos.add(c_large)
            else:
                g_base_wr = max([0] + [(global_wins.get(sc,0)/max(global_freq.get(sc,1),1))*100 for sc in itertools.combinations(c_large, len(c_large)-1)])
                if wr_large > g_base_wr: g_red_combos.add(c_large)

            for j in range(i + 1, len(sorted_g_combos)):
                c_small = sorted_g_combos[j]
                if c_small in g_combos_to_remove: continue
                
                if set(c_small).issubset(set(c_large)):
                    freq_l = global_valid[c_large]['freq']
                    freq_s = global_valid[c_small]['freq']
                    
                    # Logika Cerdas: Jika Duo cuma numpang di Trio (frekuensi mirip), HAPUS Duo-nya!
                    # Tapi jika Duo punya nyawa sendiri (sering dipakai tanpa Trio), biarkan HIDUP!
                    if (freq_s - freq_l) < 2: 
                        g_combos_to_remove.add(c_small)

        # 5. SORTING PRIORITAS RASIO (Rasio -> Unique Teams -> WR -> Length)
        top_10_combos = sorted(
            {k: v for k, v in global_valid.items() if k not in g_combos_to_remove}.items(), 
            key=lambda x: (x[1]['rasio'], x[1]['unique_teams'], x[1]['wr'], len(x[0])), 
            reverse=True
        )[:10]
        
        # 6. RENDER UI 2 KOLOM
        if not top_10_combos:
            st.info("Data pertandingan belum mencukupi untuk membentuk kombinasi hero meta.")
        else:
            cols_combo = st.columns(2)
            for idx, (combo_tuple, stats) in enumerate(top_10_combos):
                combo_name = " & ".join(combo_tuple)
                
                is_supreme = combo_tuple in g_red_combos
                border_color = "#ff4b4b" if is_supreme else "#ffc107"
                label_meta = "Supreme Meta" if is_supreme else "Global Meta"
                teks_rasio = f" ({stats['rasio']:.0f}%)" if stats['rasio'] > 0 else ""
                
                team_usage = Counter(combo_matches[combo_tuple])
                top_3_teams = team_usage.most_common(3)
                
                html = f"<div style='background-color: #24242e; border-left: 5px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); display: flex; align-items: stretch;'>"
                
                html += "<div style='flex: 1.2; border-right: 1px solid rgba(255,255,255,0.1); padding-right: 15px;'>"
                html += "<div style='display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;'>"
                for hero in combo_tuple:
                    h_path = get_hero_path(hero)
                    if h_path:
                        html += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 45px; height: 45px; border-radius: 6px; object-fit: cover; border: 1px solid rgba(255,255,255,0.2);'>"
                    else:
                        html += f"<div style='width: 45px; height: 45px; background: #444; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:9px;'>{hero}</div>"
                html += "</div>"
                
                html += f"<div style='color: #d1d1d1; font-family: \"Montserrat\", sans-serif;'>"
                html += f"<div style='font-size: 13px; margin-bottom: 4px; line-height: 1.2;'><b>{combo_name}</b></div>"
                html += f"<div style='font-size: 12px; font-weight: 600; color: #a0a0a0;'>Pick: <b style='color: white;'>{stats['freq']}x</b> | WR: <b style='color: white;'>{stats['wr']:.0f}%</b></div>"
                html += f"<div style='font-size: 11px; font-weight: 800; color: {border_color}; margin-top: 4px;'>{label_meta}{teks_rasio}</div>"
                html += "</div></div>"
                
                html += "<div style='flex: 1; padding-left: 15px; display: flex; flex-direction: column; justify-content: center;'>"
                html += "<div style='font-size: 11px; color: #a0a0a0; margin-bottom: 8px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;'>Top Users</div>"
                html += "<div style='display: flex; flex-direction: column; gap: 6px;'>"
                
                for i in range(3):
                    if i < len(top_3_teams):
                        t_name, t_count = top_3_teams[i]
                        t_logo = get_logo_path(t_name)
                        t_b64 = image_to_base64(t_logo) if t_logo else ""
                        
                        html += "<div style='display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px; height: 28px;'>"
                        html += "<div style='display: flex; align-items: center; gap: 8px;'>"
                        if t_b64:
                            html += f"<img src='data:image/png;base64,{t_b64}' style='height: 20px; width: 20px; object-fit: contain;'>"
                        html += f"<span style='color: white; font-size: 13px; font-weight: 700;'>{t_name}</span></div>"
                        html += f"<span style='color: {border_color}; font-size: 13px; font-weight: 800;'>{t_count}x</span>"
                        html += "</div>"
                    else:
                        html += "<div style='background: transparent; padding: 4px 8px; border-radius: 4px; height: 28px;'></div>"
                    
                html += "</div></div>"
                html += "</div>"
                
                col_target = cols_combo[0] if idx % 2 == 0 else cols_combo[1]
                with col_target:
                    st.markdown(html, unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #333; margin-top: 10px; margin-bottom: 40px;'>", unsafe_allow_html=True)

    # ==========================================
    # BAGIAN 4: RIWAYAT PERTANDINGAN (MATCH HISTORY)
    # ==========================================
    st.markdown("### 📜 Riwayat Pertandingan")
    st.markdown("<div style='color: #a0a0a0; font-size: 13px; margin-top: -10px; margin-bottom: 20px;'>*Rekam jejak seluruh pertandingan di musim ini.</div>", unsafe_allow_html=True)
    
    col_filter, col_kosong = st.columns([1, 3])
    with col_filter:
        tim_filter = st.selectbox("🔍 Cari Jejak Tim:", ["Semua Tim"] + sorted(df_long['Team'].dropna().unique().tolist()))
    
    hist_display = df_history[['Date', 'Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']].copy()
    
    if tim_filter != "Semua Tim":
        hist_display = hist_display[(hist_display['Team_(Blue)'] == tim_filter) | (hist_display['Opponent_(Red)'] == tim_filter)]
    
    # 1. FORMAT TANGGAL CANTIK
    hist_display['Date_Sort'] = pd.to_datetime(hist_display['Date'], errors='coerce')
    hist_display['Date'] = hist_display['Date_Sort'].dt.strftime('%d %b %Y').fillna(hist_display['Date'])
    
    # 2. LOGIKA KODE MATCH CERDAS
    def format_match_id(row):
        w = str(row['Week']).strip()
        d = str(row['Day']).strip()
        m = str(row['Match']).replace('.0', '').strip()
        g = str(row['Game']).replace('.0', '').strip()
        
        if w.isdigit():
            return f"W{w}D{d}M{m}G{g}"
        else:
            return f"{w}{d}{g}" 
            
    hist_display['Match_ID'] = hist_display.apply(format_match_id, axis=1)
    
    # 3. Visualisasi Hasil Pertandingan Cepat
    hist_display['Result'] = hist_display['Result'].apply(lambda x: "🟦 Blue Win" if x == 1.0 else ("🟥 Red Win" if x == 0.0 else "TBD"))
    
    # Urutkan secara kronologis
    hist_display = hist_display.sort_values(by=['Date_Sort', 'Match_ID'], ascending=[False, False])
    hist_display = hist_display[['Date', 'Match_ID', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']]
    
    # 4. RENDER TABEL BAWAAN STREAMLIT (Dengan Styling Rata Tengah)
    # Menyuntikkan Pandas Styler agar seluruh sel tabel menjadi rata tengah
    styled_hist = hist_display.style.set_properties(**{'text-align': 'center'})
    
    st.dataframe(
        styled_hist, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Date": st.column_config.TextColumn("Tanggal", width="medium"),
            "Match_ID": st.column_config.TextColumn("Kode Match", width="medium"), # Ubah ke medium agar tidak sesak
            "Team_(Blue)": st.column_config.TextColumn("Tim Biru (Blue)", width="medium"),
            "Result": st.column_config.TextColumn("Hasil Pemenang", width="medium"),
            "Opponent_(Red)": st.column_config.TextColumn("Tim Merah (Red)", width="medium"),
            "Duration_min": st.column_config.TextColumn("Durasi", width="small"),
            "MVP": st.column_config.TextColumn("MVP", width="medium")
        }
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
# endregion

# region PROFILING
elif menu_utama == "🛡️ Team Profiling":
    
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
        
        # === 1. HEADER PROFIL TIM (LANGSUNG LOGO & NARASI) ===
        col_prof_logo, col_prof_desc = st.columns([1.5, 3.5])
        
        logo_path = get_logo_path(tim_pilihan)
        tim_panjang = TEAM_FULLNAME_MAP.get(tim_pilihan, tim_pilihan)
        
        with col_prof_logo:
            if logo_path:
                # Render Logo
                st.markdown(f"""
                <div style="width: 100%; display: flex; justify-content: center; align-items: center; padding-top: 10px;">
                    <img src="data:image/png;base64,{image_to_base64(logo_path)}" style="width: 100%; max-width: 220px; object-fit: contain; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.8));">
                </div>
                """, unsafe_allow_html=True)
                
                # CSS khusus untuk menyulap tombol Streamlit menjadi Teks Judul H2 transparan
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button {
                    background-color: transparent !important;
                    border: none !important;
                    color: white !important;
                    font-family: 'Montserrat', sans-serif !important;
                    box-shadow: none !important;
                    padding: 0 !important;
                    margin-top: 15px !important;
                    transition: all 0.2s ease-in-out !important;
                }
                div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button:hover {
                    color: #d4af37 !important; /* Teks menyala emas saat disorot */
                    transform: scale(1.05) !important; /* Efek membesar sedikit */
                }
                div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] p {
                    font-size: 26px !important;
                    font-weight: 900 !important;
                    letter-spacing: 1px !important;
                    line-height: 1.2 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Tombol Streamlit yang menyamar sebagai Judul
                if st.button(tim_panjang, use_container_width=True, key="btn_reset_header"):
                    st.session_state['profiling_team'] = None
                    st.rerun()
                
        with col_prof_desc:
            data_tim = rapor_radar[rapor_radar['Team'] == tim_pilihan].iloc[0]
            df_hist_tim = df_long[df_long['Team'] == tim_pilihan]
            total_wins = int(df_hist_tim['Win'].sum())
            total_losses = len(df_hist_tim) - total_wins
            
            dom_score = data_tim['Dominance_100']
            if dom_score > 75: kasta = "tim papan atas (Raksasa Liga)"
            elif dom_score > 40: kasta = "tim papan tengah (Kuda Hitam)"
            else: kasta = "tim papan bawah (Underdog)"
            
            avg_durasi = df_hist_tim['Durasi'].mean()
            best_win = df_hist_tim[df_hist_tim['Win'] == 1]['O_Rank'].min()
            lawan_terkuat = df_long[(df_long['Team'] == tim_pilihan) & (df_long['O_Rank'] == best_win)]['Opponent'].mode()[0] if total_wins > 0 else "-"
            lawan_color = TEAM_COLOR_MAP.get(lawan_terkuat, "#ff4b4b")
            
            narasi_profil = f"""
            <div style="color: #d1d1d1; font-family: 'Montserrat', sans-serif; font-size: 16px; line-height: 1.8; text-align: justify; padding: 25px 30px; background: rgba(255,255,255,0.02); border-left: 4px solid {TEAM_COLOR_MAP.get(tim_pilihan, '#d4af37')}; border-radius: 8px;">
                Pada musim ini, <b style="color: white;">{tim_panjang} ({tim_pilihan})</b> tergolong dalam kelompok <b style="color: #d4af37;">{kasta}</b>. 
                Mereka mencatatkan rekor <b style="color: white;">{total_wins} Kemenangan</b> dan <b>{total_losses} Kekalahan</b> di sepanjang turnamen, 
                dengan rata-rata durasi pertandingan yang dihabiskan selama <b>{avg_durasi:.1f} menit</b> per game.
                <br><br>
                Pencapaian terbesar mereka musim ini adalah saat berhasil menumbangkan <b style="color: {lawan_color};">{lawan_terkuat}</b> (salah satu tim dengan peringkat tertinggi di klasemen) 
                dalam sebuah pertarungan yang sangat krusial.
            </div>
            """
            st.markdown(narasi_profil, unsafe_allow_html=True)

        # Hapus tag <br> dan pakai margin presisi agar jarak ke Line Up merapat sempurna
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin-top: 15px; margin-bottom: 25px;'>", unsafe_allow_html=True)
        
        # === 2. TEAM LINE UP (LAYERED MAP) & STAFF (Murni 100% Desain Manualmu) ===
        st.markdown("### 🗺️ Team Line Up")
        
        df_roster = pd.read_csv("IKL_Rosters.csv")
        df_roster_tim = df_roster[df_roster['Team'] == tim_pilihan].copy()
        
        if musim_pilihan in df_roster_tim['Season'].values:
            df_roster_tim = df_roster_tim[df_roster_tim['Season'] == musim_pilihan]
            
        df_roster_tim['Status_Score'] = df_roster_tim['Status'].astype(str).str.strip().str.lower().map({
            'main': 1, 'active': 1, 'core': 1, 'subs': 2, 'cadangan': 2
        }).fillna(3)
        df_roster_tim = df_roster_tim.sort_values('Status_Score')
        
        bg_path = get_team_bg_path(tim_pilihan)
        bg_b64 = image_to_base64(bg_path)
        
        col_map, col_staff = st.columns([2, 1])
        
        with col_map:
            map_path = "assets/HOK_map-layout.png"
            map_b64 = image_to_base64(map_path)
            
            html_container = f"""
            <div id='map_container' style='position: relative; width: 100%; max-width: 850px; aspect-ratio: 1/1; margin: 0 auto;'>
                <img src='data:image/png;base64,{map_b64}' style='width: 100%; height: 100%; object-fit: contain; display: block;'>
            """
            
            role_idx_map = {'Top Lane': 0, 'Jungler': 1, 'Middle': 2, 'Bottom Lane': 3, 'Roamer': 4}
            role_keywords = {
                'Top Lane': 'top|clash',
                'Jungler': 'jung',
                'Middle': 'mid',
                'Bottom Lane': 'bot|farm|gold',
                'Roamer': 'roam|sup'
            }
            
            df_hist_player = df_long[(df_long['Team'] == tim_pilihan) & (df_long['Win'].notna())]
            
            for role_csv, coords in MAP_COORDINATES.items():
                keyword = role_keywords.get(role_csv, '')
                pemain_data = df_roster_tim[df_roster_tim['Role'].astype(str).str.lower().str.contains(keyword, na=False)]
                
                if not pemain_data.empty:
                    nama_pemain = str(pemain_data.iloc[0]['Player_ID'])
                    foto_path = get_player_path(nama_pemain)
                    foto_b64 = image_to_base64(foto_path)
                    icon_role_b64 = image_to_base64(f"assets/{ROLE_ICONS.get(role_csv)}")
                    
                    idx_lane = role_idx_map.get(role_csv, 0)
                    hero_counts = {}
                    for _, row in df_hist_player.iterrows():
                        heroes = row['Heroes_List']
                        if isinstance(heroes, list) and len(heroes) > idx_lane:
                            h = heroes[idx_lane]
                            hero_counts[h] = hero_counts.get(h, 0) + 1
                            
                    top_3_heroes = sorted(hero_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    
                    hero_html = "<div style='position: absolute; bottom: 5%; width: 100%; display: flex; justify-content: center; gap: 3px; z-index: 4;'>"
                    for h_name, _ in top_3_heroes:
                        h_path = get_hero_path(h_name)
                        if h_path:
                            hero_html += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 15px; height: 15px; border-radius: 2px; border: 0.5px solid rgba(255,255,255,0.5); object-fit: cover; box-shadow: 1px 1px 2px rgba(0,0,0,0.8);'>"
                    hero_html += "</div>"
                    
                    style_pos = f"top: {coords['top']}; left: {coords['left']};"
                    if 'transform' in coords: style_pos += f" transform: {coords['transform']};"
                    
                    html_container += f"""
                    <div style="position: absolute; {style_pos} width: 75px; border-radius: 2px; box-shadow: 0 4px 8px rgba(0,0,0,0.7); z-index: 5;">
                        <img src="data:image/png;base64,{bg_b64}" style="width: 100%; height: auto; display: block; border-radius: 5px; filter: brightness(0.65);">
                        <img src="data:image/png;base64,{icon_role_b64}" style="position: absolute; top: 4px; left: 2px; width: 18px; height: 18px; z-index: 5; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.9));">
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 75%; z-index: 2; overflow: hidden; border-radius: 5px 5px 0 0;">
                            <img src="data:image/png;base64,{foto_b64}" style="width: 100%; height: 100%; object-fit: cover; object-position: top center; opacity: 0.95;">
                        </div>
                        <div style="position: absolute; bottom: 27%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 10px; text-shadow: 1px 1px 2px black, -1px -1px 2px black, 0px 2px 4px black; z-index: 3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 3px; letter-spacing: 0.5px;">
                            {nama_pemain}
                        </div>
                        {hero_html}
                    </div>
                    """
            
            html_container += "</div>"
            import streamlit.components.v1 as components
            components.html(html_container, height=750) # TINGGI MANUALMU AMAN
            
        with col_staff:
            path_bg_staff = "assets/Recap/logo_background/IKL_bg.png"
            path_bg_subs = "assets/Recap/logo_background/IKL_bgs.png"
            b64_bg_staff = image_to_base64(path_bg_staff) if os.path.exists(path_bg_staff) else ""
            b64_bg_subs = image_to_base64(path_bg_subs) if os.path.exists(path_bg_subs) else ""

            html_staff_col = """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
            </style>
            <div style="font-family: 'Montserrat', sans-serif;">
            <h4 style='color: #ffffff; margin-bottom: 15px; margin-top: 0;'>Management & Staff</h4>
            <div style='display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 35px;'>
            """
            
            df_staff = df_roster_tim[df_roster_tim['Status'].astype(str).str.strip().str.lower() == 'staff'].copy()
            mask_coach = df_staff['Role'].astype(str).str.lower().str.contains('coach', na=False)
            if mask_coach.sum() == 1: df_staff.loc[mask_coach, 'Role'] = 'Head Coach'
                
            def get_staff_icon(role_str):
                r = str(role_str).lower()
                if 'head' in r and 'coach' in r: return 'headcoach_icon.png'
                if 'coach' in r: return 'coach_icon.png'
                if 'manager' in r: return 'manager_icon.png'
                if 'analyst' in r: return 'analyst_icon.png'
                return 'coach_icon.png'
                
            for _, row in df_staff.iterrows():
                nama = str(row['Player_ID'])
                jabatan = str(row['Role'])
                f_path = get_player_path(nama)
                b64_foto = image_to_base64(f_path) if f_path else ""
                b64_icon = image_to_base64(f"assets/{get_staff_icon(jabatan)}")
                
                html_staff_col += f"""
                <div style="position: relative; width: 95px; border-radius: 2px; box-shadow: 0 4px 8px rgba(0,0,0,0.7); background: #222;">
                    <img src="data:image/png;base64,{b64_bg_staff}" style="width: 100%; height: auto; display: block; border-radius: 2px; filter: brightness(0.65);">
                    <img src="data:image/png;base64,{b64_icon}" style="position: absolute; top: 5px; left: 5px; width: 20px; height: 20px; z-index: 5; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.9));">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 75%; z-index: 2; overflow: hidden; border-radius: 2px 5px 0 0;">
                        <img src="data:image/png;base64,{b64_foto}" style="width: 100%; height: 100%; object-fit: cover; object-position: top center; opacity: 0.95;">
                    </div>
                    <div style="position: absolute; bottom: 28%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 9px; text-shadow: 1px 1px 2px black; z-index: 3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 3px;">{nama}</div>
                    <div style="position: absolute; bottom: 9%; width: 100%; text-align: center; color: #ffffff; font-weight: 800; font-size: 9px; z-index: 3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 2px; text-transform: uppercase;">{jabatan}</div>
                </div>
                """
            
            html_staff_col += "</div><h4 style='color: #ffffff; margin-bottom: 15px;'>Substitutes</h4><div style='display: flex; flex-wrap: wrap; gap: 15px;'>"
            
            df_subs = df_roster_tim[df_roster_tim['Status_Score'] == 2].copy()
            def get_subs_icon(role_str):
                r = str(role_str).lower()
                if 'top' in r or 'clash' in r: return 'subs_clashlane_icon.png'
                if 'jung' in r: return 'subs_jungle_icon.png'
                if 'mid' in r: return 'subs_midlane_icon.png'
                if 'bot' in r or 'farm' in r or 'gold' in r: return 'subs_farmlane_icon.png'
                if 'roam' in r or 'sup' in r: return 'subs_support_icon.png'
                return 'subs_flex_icon.png'
                
            for _, row in df_subs.iterrows():
                nama = str(row['Player_ID'])
                f_path = get_player_path(nama)
                b64_foto = image_to_base64(f_path) if f_path else ""
                b64_icon = image_to_base64(f"assets/{get_subs_icon(str(row['Role']))}")
                
                html_staff_col += f"""
                <div style="position: relative; width: 95px; border-radius: 2px; box-shadow: 0 4px 8px rgba(0,0,0,0.7); background: #222;">
                    <img src="data:image/png;base64,{b64_bg_subs}" style="width: 100%; height: auto; display: block; border-radius: 2px; filter: brightness(0.65);">
                    <img src="data:image/png;base64,{b64_icon}" style="position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; z-index: 5; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.9));">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 99%; z-index: 2; overflow: hidden; border-radius: 2px 5px 0 0;">
                        <img src="data:image/png;base64,{b64_foto}" style="width: 100%; height: 100%; object-fit: cover; object-position: top center; opacity: 0.95;">
                    </div>
                    <div style="position: absolute; bottom: 8%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 9px; text-shadow: 1px 1px 2px black; z-index: 3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 3px;">{nama}</div>
                </div>
                """
            html_staff_col += "</div></div>"
            
            import streamlit.components.v1 as components
            components.html(html_staff_col, height=750) # TINGGI MANUALMU AMAN
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin-top: 20px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 3. RADAR CHART & TEAM PERFORMANCE STATISTIC ===
        st.markdown("### 📊 Team Statistic Performance")
        
        col_radar, col_narasi = st.columns([1.5, 2.5])
        
        data_tim = rapor_radar[rapor_radar['Team'] == tim_pilihan].iloc[0]
        warna_tim = TEAM_COLOR_MAP.get(tim_pilihan, "#d4af37")
        
        kategori_keys = ['Dominance_100', 'Toughness_100', 'Discipline_100', 'Volatility_100', 'TeamFight_100', 'Flexibility_100']
        kategori_label = ['DOM', 'TOUG', 'DISC', 'STAB', 'TEAM', 'FLEX']
        
        skor_tim = data_tim[kategori_keys].values.flatten().tolist()
        skor_tim[3] = 120 - skor_tim[3] 
        
        with col_radar:
            skor_radar = skor_tim + [skor_tim[0]]
            label_radar = kategori_label + [kategori_label[0]]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=skor_radar, theta=label_radar, fill='toself', name=tim_pilihan, line_color=warna_tim, 
                fillcolor=f"rgba({int(warna_tim.lstrip('#')[0:2], 16)}, {int(warna_tim.lstrip('#')[2:4], 16)}, {int(warna_tim.lstrip('#')[4:6], 16)}, 0.2)",
                marker=dict(size=6, color="white", line=dict(width=1.5, color=warna_tim))
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(255,255,255,0.05)",
                    radialaxis=dict(visible=True, showticklabels=False, range=[0, 100], gridcolor="rgba(255,255,255,0.15)", linecolor="rgba(255,255,255,0.2)"),
                    angularaxis=dict(tickfont=dict(color="white", size=13, family="'Montserrat', sans-serif", weight="bold"), gridcolor="rgba(255,255,255,0.15)", linecolor="rgba(255,255,255,0.2)")
                ),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=30, t=40, b=30), showlegend=False, height=350
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_narasi:
            kategori_narasi_keys = ['Dominance_100', 'Toughness_100', 'Discipline_100', 'Stability_100', 'TeamFight_100', 'Flexibility_100']
            kamus_skor = dict(zip(kategori_narasi_keys, skor_tim))
            skor_diurutkan = sorted(kamus_skor.items(), key=lambda item: item[1], reverse=True)
            kekuatan_utama = skor_diurutkan[0][0]
            kelemahan_utama = skor_diurutkan[-1][0]
            
            kamus_narasi = {
                'Dominance_100': "Dominasi Pertandingan (kemampuan menekan lawan sejak *early game* dan agresif dalam menguasai perolehan *gold*).",
                'Toughness_100': "Ketangguhan Mental (kemampuan bertahan luar biasa dan memperlama durasi saat berada di posisi tertinggal).",
                'Discipline_100': "Kedisiplinan Objektif (fokus tingkat tinggi pada penghancuran *turret* dan perebutan monster epik dibandingkan sekadar mencari *kill*).",
                'Stability_100': "Stabilitas Performa (kemampuan menjaga konsistensi permainan dan meminimalisir blunder fatal saat berhadapan dengan berbagai level tim).",
                'TeamFight_100': "Kekompakan *Team Fight* (rasio *assist* yang sangat tinggi di setiap eliminasi, menandakan rotasi mereka selalu mematikan).",
                'Flexibility_100': "Fleksibilitas Draft (kekayaan jumlah variasi taktik dan *hero* yang mereka berani mainkan di panggung kompetitif)."
            }
            
            teks_analisis = f"""
            <div style="color: #e0e0e0; font-family: 'Montserrat', sans-serif; font-size: 14px; line-height: 1.8; text-align: justify; margin-top: 15px; padding-left: 10px;">
                Berdasarkan grafik performa <i>hexagonal</i> di samping, <b style="color: {warna_tim};">{tim_panjang}</b> menampilkan karakteristik permainan yang sangat khas di musim ini. 
                <br><br>
                Ujung tombak dan kekuatan utama dari tim ini terletak pada parameter <b style="color: white;">{kamus_narasi[kekuatan_utama].split(' (')[0]}</b>. 
                Hal ini mencerminkan {kamus_narasi[kekuatan_utama].split('(')[1].replace(').', '')} dengan perolehan skor memukau di angka <b style="color: #4caf50;">{kamus_skor[kekuatan_utama]:.1f}/100</b>.
                <br><br>
                Di sisi lain, parameter yang masih menjadi catatan dan ruang untuk evaluasi bagi jajaran pelatih adalah <b style="color: white;">{kamus_narasi[kelemahan_utama].split(' (')[0]}</b> (Skor: <b style="color: #ff4b4b;">{kamus_skor[kelemahan_utama]:.1f}/100</b>). 
                Musuh kerap mengeksploitasi celah ini mengingat kurangnya {kamus_narasi[kelemahan_utama].split('(')[1].replace(').', '')} mereka.
            </div>
            """
            st.markdown(teks_analisis, unsafe_allow_html=True)
            
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin-top: 20px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 4. TEAM STRATEGY (SIGNATURE HERO COMBO & DRAFTING) ===
        st.markdown("### ♟️ Team Strategy")
        
        st.markdown("<h5 style='color: white; font-family: \"Montserrat\", sans-serif; margin-bottom: 15px;'>Top Team Heroes Combination</h5>", unsafe_allow_html=True)
        kombo_A = get_signature_combos(tim_pilihan)
        
        if not kombo_A:
            st.info(f"Tim {tim_pilihan} belum memiliki rekam jejak kombinasi *hero* yang mencukupi untuk dianalisis.")
        else:
            cols = st.columns(3)
            for idx, k in enumerate(kombo_A[:3]):
                with cols[idx]:
                    render_combo_card(k["combo"], k["warna"], k["freq"], k["wr"], k["label"])
                    
        st.markdown("<br>", unsafe_allow_html=True)
        
        df_tim_semua = df_history[(df_history['Team_(Blue)'] == tim_pilihan) | (df_history['Opponent_(Red)'] == tim_pilihan)]
        total_match_tim = len(df_tim_semua)
        
        if total_match_tim > 0:
            tim_picks = df_long[df_long['Team'] == tim_pilihan].explode('Heroes_List')['Heroes_List'].value_counts().head(3)
            
            ban_as_blue = df_tim_semua[df_tim_semua['Team_(Blue)'] == tim_pilihan]['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
            ban_as_red = df_tim_semua[df_tim_semua['Opponent_(Red)'] == tim_pilihan]['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
            tim_bans = pd.concat([ban_as_blue, ban_as_red]).value_counts().head(3)
            
            resp_ban_as_blue = df_tim_semua[df_tim_semua['Team_(Blue)'] == tim_pilihan]['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
            resp_ban_as_red = df_tim_semua[df_tim_semua['Opponent_(Red)'] == tim_pilihan]['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
            respected_bans = pd.concat([resp_ban_as_blue, resp_ban_as_red]).value_counts().head(3)
            
            banned_b64 = image_to_base64("assets/Match/banned.png")
            
            def generate_draft_column_html(title, data_series, mode="pick"):
                col_html = f"<div style='flex: 1; padding: 0 10px;'>"
                col_html += f"<h4 style='color: white; margin-top: 0; margin-bottom: 20px; font-size: 18px;'>{title}</h4>"
                
                if mode == "pick":
                    border_color = "#d4af37"
                    text_color = "#4caf50"
                    img_filter = "none"
                else:
                    border_color = "#a33232" 
                    text_color = "#ff4b4b"
                    img_filter = "grayscale(100%) brightness(0.5)" 
                
                if data_series.empty:
                    col_html += "<div style='color: gray; font-size: 13px; font-style: italic;'>Data belum tersedia</div>"
                else:
                    for hero, count in data_series.items():
                        rate = (count / total_match_tim) * 100
                        h_path = get_hero_path(hero)
                        
                        if h_path:
                            h_img = f"<div style='position: relative; width: 55px; height: 55px; border-radius: 6px; border: 1.5px solid {border_color}; overflow: hidden;'>"
                            h_img += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 100%; height: 100%; object-fit: cover; filter: {img_filter};'>"
                            if mode == "respected" and banned_b64:
                                h_img += f"<img src='data:image/png;base64,{banned_b64}' style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.9;'>"
                            h_img += "</div>"
                        else:
                            h_img = f"<div style='width: 55px; height: 55px; background: #444; border: 1.5px solid {border_color}; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size:10px; text-align:center;'>{hero}</div>"
                        
                        col_html += f"""
                        <div style='background-color: #24242e; border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                            <div style='display: flex; align-items: center; gap: 15px;'>
                                {h_img}
                                <span style='color: white; font-weight: 700; font-size: 15px; letter-spacing: 0.5px;'>{hero}</span>
                            </div>
                            <span style='color: {text_color}; font-weight: 800; font-size: 16px;'>{rate:.0f}%</span>
                        </div>
                        """
                col_html += "</div>"
                return col_html

            master_draft_html = """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
            </style>
            <div style="font-family: 'Montserrat', sans-serif; display: flex; width: 100%; justify-content: space-between;">
            """
            
            master_draft_html += generate_draft_column_html("Top Picked Heroes", tim_picks, mode="pick")
            master_draft_html += generate_draft_column_html("Top Banned Heroes", tim_bans, mode="ban")
            master_draft_html += generate_draft_column_html("Top Respected Banned", respected_bans, mode="respected")
            master_draft_html += "</div>"

            import streamlit.components.v1 as components
            components.html(master_draft_html, height=320)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin-top: 10px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 5. NAVIGASI BAWAH (KEMBALI & BANDINGKAN) ===
        col_btn1, col_space, col_btn2 = st.columns([1.5, 7, 1.5])
        
        icon_kembali_b64 = image_to_base64("assets/kembali_icon.png")
        icon_banding_b64 = image_to_base64("assets/bandingkan_icon.png")
        
        with col_btn1:
            st.markdown("""
            <style>
            /* Memaksa tombol asli menjadi kotak transparan setinggi 45px */
            div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button {
                height: 45px !important;
                background-color: transparent !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: transparent !important;
                transition: all 0.3s ease !important;
            }
            div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button:hover {
                border-color: #d4af37 !important;
                box-shadow: 0 4px 12px rgba(212,175,55,0.2) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Tombol asli HANYA BERISI SPASI agar tidak ada bayangan teks sama sekali!
            if st.button(" ", key="btn_kembali", use_container_width=True):
                st.session_state['profiling_team'] = None
                st.rerun()
                
            if icon_kembali_b64:
                # Lapisan Visual: Tinggi disamakan dengan tombol (45px) agar Flexbox menjadikannya senter sempurna
                # Ditarik sejauh -56px ke atas agar pas menimpa tombol aslinya
                st.markdown(f"""
                <div style='position: relative; margin-top: -56px; height: 45px; display: flex; justify-content: center; align-items: center; gap: 8px; pointer-events: none; z-index: 10;'>
                    <img src='data:image/png;base64,{icon_kembali_b64}' style='height: 20px; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));'>
                    <span style='color: gray; font-family: "Montserrat", sans-serif; font-size: 15px; font-weight: 600;'>Kembali</span>
                </div>
                """, unsafe_allow_html=True)

        with col_btn2:
            st.markdown("""
            <style>
            /* Memaksa tombol asli menjadi kotak transparan setinggi 45px */
            div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button {
                height: 45px !important;
                background-color: transparent !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: transparent !important;
                transition: all 0.3s ease !important;
            }
            div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button:hover {
                border-color: #d4af37 !important;
                box-shadow: 0 4px 12px rgba(212,175,55,0.2) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Tombol asli BERISI 2 SPASI (agar beda key dengan tombol Kembali)
            if st.button("  ", key="btn_bandingkan", use_container_width=True):
                st.session_state['h2h_team_A'] = tim_pilihan 
                st.session_state['h2h_team_B'] = None        
                st.session_state['menu_ikl'] = "⚔️ Versus Mode (H2H)" 
                st.rerun()
                
            if icon_banding_b64:
                # Lapisan Visual ditarik ke atas agar menimpa tombol asli
                st.markdown(f"""
                <div style='position: relative; margin-top: -56px; height: 45px; display: flex; justify-content: center; align-items: center; gap: 8px; pointer-events: none; z-index: 10;'>
                    <span style='color: gray; font-family: "Montserrat", sans-serif; font-size: 15px; font-weight: 600;'>Bandingkan</span>
                    <img src='data:image/png;base64,{icon_banding_b64}' style='height: 40px; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));'>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # === 6. RIWAYAT PERTANDINGAN TIM TERPILIH ===
        st.markdown(f"### 📜 Match History: {tim_panjang}")
        st.markdown(f"<div style='color: #a0a0a0; font-size: 13px; margin-top: -10px; margin-bottom: 20px;'>*Menampilkan riwayat pertandingan eksklusif untuk tim <b>{tim_pilihan}</b> di musim ini.</div>", unsafe_allow_html=True)
        
        hist_display = df_history[(df_history['Team_(Blue)'] == tim_pilihan) | (df_history['Opponent_(Red)'] == tim_pilihan)].copy()
        
        if hist_display.empty:
            st.info(f"Belum ada riwayat pertandingan untuk {tim_pilihan} di musim ini.")
        else:
            hist_display['Date_Sort'] = pd.to_datetime(hist_display['Date'], errors='coerce')
            hist_display['Date'] = hist_display['Date_Sort'].dt.strftime('%d %b %Y').fillna(hist_display['Date'])
            
            def format_match_id(row):
                w, d = str(row['Week']).strip(), str(row['Day']).strip()
                m, g = str(row['Match']).replace('.0', '').strip(), str(row['Game']).replace('.0', '').strip()
                return f"W{w}D{d}M{m}G{g}" if w.isdigit() else f"{w}{d}{g}" 
                
            hist_display['Match_ID'] = hist_display.apply(format_match_id, axis=1)
            hist_display['Result'] = hist_display['Result'].apply(lambda x: "🟦 Blue Win" if x == 1.0 else ("🟥 Red Win" if x == 0.0 else "TBD"))
            
            hist_display = hist_display.sort_values(by=['Date_Sort', 'Match_ID'], ascending=[False, False])
            hist_display = hist_display[['Date', 'Match_ID', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']]
            
            styled_hist = hist_display.style.set_properties(**{'text-align': 'center'})
            st.dataframe(
                styled_hist, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Date": st.column_config.TextColumn("Tanggal", width="medium"),
                    "Match_ID": st.column_config.TextColumn("Kode Match", width="medium"),
                    "Team_(Blue)": st.column_config.TextColumn("Tim Biru (Blue)", width="medium"),
                    "Result": st.column_config.TextColumn("Hasil Pemenang", width="medium"),
                    "Opponent_(Red)": st.column_config.TextColumn("Tim Merah (Red)", width="medium"),
                    "Duration_min": st.column_config.TextColumn("Durasi", width="small"),
                    "MVP": st.column_config.TextColumn("MVP", width="medium")
                }
            )
# endregion

# region H2H
elif menu_utama == "⚔️ Versus Mode (H2H)":

    if 'h2h_team_A' not in st.session_state:
        st.session_state['h2h_team_A'] = None
    if 'h2h_team_B' not in st.session_state:
        st.session_state['h2h_team_B'] = None

    daftar_tim = sorted(rapor_radar['Team'].unique())
    tim_A = st.session_state['h2h_team_A']
    tim_B = st.session_state['h2h_team_B']

    # === FASE PEMILIHAN TIM (KONDISI A ATAU B BELUM TERPILIH) ===
    if tim_A is None or tim_B is None:
        
        # Load assets H2H
        ikl_silver_b64 = image_to_base64("assets/ikl_Silver.png")
        vs_gold_b64 = image_to_base64("assets/Match/vs_full_gold.png")

        # Rasio kolom disesuaikan agar terpusat sempurna seperti desain
        col_a, col_vs, col_b = st.columns([3, 1.5, 3])

        with col_a:
            if tim_A is None:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{ikl_silver_b64}' style='height: 180px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5)); opacity: 0.8; margin-bottom: 15px;'>
                    <h3 style='color: white; margin: 0; font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 22px;'>IKL {musim_pilihan}'s<br>TEAM</h3>
                    <p style='color: gray; font-size: 14px; margin-top: 5px; font-weight: 600;'>Pilih Tim</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                logo_A = get_logo_path(tim_A)
                b64_A = image_to_base64(logo_A) if logo_A else ""
                tim_panjang_A = TEAM_FULLNAME_MAP.get(tim_A, tim_A).upper()
                
                # Logika pemisahan kata "BY" untuk estetika teks bertingkat (Contoh: DOMINATOR by NEMESIS)
                if " BY " in tim_panjang_A:
                    nama_utama, nama_sub = tim_panjang_A.split(" BY ", 1)
                    html_nama_A = f"<h3 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-weight: 900; font-size: 22px;'>{nama_utama}</h3><p style='color: gray; font-size: 16px; margin: 0; font-weight: 600;'>by {nama_sub}</p>"
                else:
                    html_nama_A = f"<h3 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-weight: 900; font-size: 22px; line-height: 1.2;'>{tim_panjang_A}</h3>"

                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{b64_A}' style='height: 180px; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.8)); margin-bottom: 15px;'>
                    {html_nama_A}
                </div>
                """, unsafe_allow_html=True)

                # Menyulap tombol reset menjadi teks abu-abu yang menyatu dengan layout
                st.markdown("""
                <style>
                div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button {
                    background: transparent !important;
                    border: none !important;
                    color: #707070 !important;
                    font-family: "Montserrat", sans-serif !important;
                    font-size: 13px !important;
                    font-weight: 600 !important;
                    padding: 0 !important;
                    box-shadow: none !important;
                    margin-top: 5px !important;
                    transition: color 0.2s ease !important;
                }
                div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button:hover {
                    color: white !important;
                }
                </style>
                """, unsafe_allow_html=True)
                if st.button("Tekan untuk ganti tim", key="btn_reset_A", use_container_width=True):
                    st.session_state['h2h_team_A'] = None
                    st.rerun()

        with col_vs:
            # Menggunakan Flexbox agar logo VS emas selalu berada di tengah secara vertikal dan horizontal
            st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center; height: 100%; min-height: 250px;'>
                <img src='data:image/png;base64,{vs_gold_b64}' style='height: 100px; filter: drop-shadow(0 4px 10px rgba(212,175,55,0.4)); margin-top: -30px;'>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            if tim_B is None:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{ikl_silver_b64}' style='height: 180px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.5)); opacity: 0.8; margin-bottom: 15px;'>
                    <h3 style='color: white; margin: 0; font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 22px;'>IKL {musim_pilihan}'s<br>TEAM</h3>
                    <p style='color: gray; font-size: 14px; margin-top: 5px; font-weight: 600;'>Pilih Tim</p>
                </div>
                """, unsafe_allow_html=True)

        # Garis pembatas elegan
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 15px; margin-bottom: 30px;'>", unsafe_allow_html=True)

        # === RENDER GRID PEMILIHAN BAWAH ===
        if tim_A is None:
            st.markdown("<p style='text-align: center; color: gray; font-size: 13px; font-weight: 600; margin-bottom: 20px;'>Team selection yang sudah ada sebelumnya</p>", unsafe_allow_html=True)
            kolom_grid = st.columns(4)
            for idx, tim in enumerate(daftar_tim):
                with kolom_grid[idx % 4]:
                    logo_path = get_logo_path(tim)
                    render_logo_card(logo_path, tim)
                    if st.button(tim, use_container_width=True, key=f"btn_A_{tim}"):
                        st.session_state['h2h_team_A'] = tim
                        st.rerun()
                        
        elif tim_B is None:
            st.markdown("<p style='text-align: center; color: gray; font-size: 13px; font-weight: 600; margin-bottom: 20px;'>Team selection yang sudah ada sebelumnya</p>", unsafe_allow_html=True)
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

    # === FASE DASHBOARD H2H (KEDUA TIM TERPILIH) ===
    else:
        tim_A = st.session_state['h2h_team_A']
        tim_B = st.session_state['h2h_team_B']
        
        # === 1. HEADER KLASEMEN & RESET TIM ===
        col_a, col_vs, col_b = st.columns([3, 1.5, 3])
        vs_gold_b64 = image_to_base64("assets/Match/vs_full_gold.png")
        
        def render_h2h_header(tim_nama, key_btn):
            logo = get_logo_path(tim_nama)
            b64_logo = image_to_base64(logo) if logo else ""
            tim_panjang = TEAM_FULLNAME_MAP.get(tim_nama, tim_nama).upper()
            
            if " BY " in tim_panjang:
                nama_utama, nama_sub = tim_panjang.split(" BY ", 1)
                html_nama = f"<h3 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-weight: 900; font-size: 22px;'>{nama_utama}</h3><p style='color: gray; font-size: 16px; margin: 0; font-weight: 600;'>by {nama_sub}</p>"
            else:
                html_nama = f"<h3 style='color: white; margin: 0; font-family: \"Montserrat\", sans-serif; font-weight: 900; font-size: 22px; line-height: 1.2;'>{tim_panjang}</h3>"

            st.markdown(f"""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{b64_logo}' style='height: 140px; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.8)); margin-bottom: 10px;'>
                {html_nama}
            </div>
            """, unsafe_allow_html=True)

            # Tombol reset samar
            st.markdown(f"""
            <style>
            div[data-testid="column"] div[data-testid="stButton"] button[key="{key_btn}"] {{
                background: transparent !important; border: none !important; color: #707070 !important;
                font-family: "Montserrat", sans-serif !important; font-size: 12px !important; font-weight: 600 !important;
                padding: 0 !important; box-shadow: none !important; margin-top: 5px !important;
            }}
            div[data-testid="column"] div[data-testid="stButton"] button[key="{key_btn}"]:hover {{ color: white !important; }}
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("Tekan untuk ganti tim", key=key_btn, use_container_width=True):
                st.session_state[f'h2h_team_{key_btn[-1]}'] = None
                st.rerun()

        with col_a: render_h2h_header(tim_A, "btn_reset_A")
        with col_vs:
            st.markdown(f"""
            <div style='display: flex; justify-content: center; align-items: center; height: 100%; min-height: 180px;'>
                <img src='data:image/png;base64,{vs_gold_b64}' style='height: 80px; filter: drop-shadow(0 4px 10px rgba(212,175,55,0.4));'>
            </div>
            """, unsafe_allow_html=True)
        with col_b: render_h2h_header(tim_B, "btn_reset_B")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 15px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 2. STATISTIC COMPARISON ===
        st.markdown("### 📊 Statistic Comparison")
        
        data_A = rapor_radar[rapor_radar['Team'] == tim_A].iloc[0]
        data_B = rapor_radar[rapor_radar['Team'] == tim_B].iloc[0]

        kategori = ['Dominance_100', 'Toughness_100', 'Discipline_100', 'Volatility_100', 'TeamFight_100', 'Flexibility_100']
        kategori_label = ['DOM', 'TOUG', 'DISC', 'STAB', 'TEAM', 'FLEX']
        
        skor_A = data_A[kategori].values.flatten().tolist()
        skor_B = data_B[kategori].values.flatten().tolist()
        skor_A[3] = 120 - skor_A[3] # Inversi ke Stability
        skor_B[3] = 120 - skor_B[3] 
        
        skor_A.append(skor_A[0])
        skor_B.append(skor_B[0])
        kategori_label.append(kategori_label[0])

        col_rad_kiri, col_rad_tengah, col_rad_kanan = st.columns([1, 2, 1])
        with col_rad_tengah:
            fig_h2h = go.Figure()
            
            # Dinamis mengambil warna identitas tim dari CSV
            warna_A = TEAM_COLOR_MAP.get(tim_A, "#3b82f6")
            warna_B = TEAM_COLOR_MAP.get(tim_B, "#ef4444")
            
            # Fungsi ajaib untuk mengonversi kode warna Hex menjadi RGBA (transparan) untuk chart area
            def hex_to_rgba(hex_color, opacity=0.4):
                hex_color = hex_color.lstrip('#')
                if len(hex_color) == 6:
                    return f"rgba({int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}, {opacity})"
                return f"rgba(128, 128, 128, {opacity})"
                
            fill_A = hex_to_rgba(warna_A)
            fill_B = hex_to_rgba(warna_B)
            
            # Render Radar Chart dengan warna dinamis
            fig_h2h.add_trace(go.Scatterpolar(r=skor_A, theta=kategori_label, fill='toself', name=tim_A, line_color=warna_A, fillcolor=fill_A))
            fig_h2h.add_trace(go.Scatterpolar(r=skor_B, theta=kategori_label, fill='toself', name=tim_B, line_color=warna_B, fillcolor=fill_B))
            
            fig_h2h.update_layout(
                polar=dict(
                    bgcolor="rgba(255,255,255,0.05)",
                    radialaxis=dict(visible=True, showticklabels=False, range=[0, 100], gridcolor="rgba(255,255,255,0.15)", linecolor="rgba(255,255,255,0.2)"),
                    angularaxis=dict(tickfont=dict(color="white", size=13, family="'Montserrat', sans-serif", weight="bold"), gridcolor="rgba(255,255,255,0.15)", linecolor="rgba(255,255,255,0.2)")
                ),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=30, r=30, t=40, b=10), showlegend=False, height=350
            )
            st.plotly_chart(fig_h2h, use_container_width=True)

            # --- RENDER BAR CHART COMPARISON ---
            def calculate_h2h_bar_stats(tim):
                df_tim = df_long[(df_long['Team'] == tim) & (df_long['Win'].notna())]
                if df_tim.empty: return [0, 0, 0, 0, 0]
                
                gpm = (df_tim['Gold'] / df_tim['Durasi']).mean()
                opm = (df_tim['Obj'] / df_tim['Durasi']).mean()
                kpm = (df_tim['Kill'] / df_tim['Durasi']).mean()
                durasi = df_tim['Durasi'].mean()
                hero_pool = df_tim.explode('Heroes_List')['Heroes_List'].nunique()
                return [gpm, opm, kpm, durasi, hero_pool]

            stats_A = calculate_h2h_bar_stats(tim_A)
            stats_B = calculate_h2h_bar_stats(tim_B)
            
            bar_labels = ["Gold/min", "Objective/min", "Kill/min", "Average Duration", "Hero Pool"]
            
            html_bars = "<div style='width: 100%; max-width: 480px; margin: 15px auto 0 auto;'>"
            for i in range(5):
                val_a = stats_A[i]
                val_b = stats_B[i]
                
                if bar_labels[i] == "Gold/min":
                    str_a, str_b = f"{val_a:.0f}", f"{val_b:.0f}"
                elif bar_labels[i] in ["Objective/min", "Kill/min"]:
                    str_a, str_b = f"{val_a:.2f}", f"{val_b:.2f}"
                elif bar_labels[i] == "Average Duration":
                    str_a, str_b = f"{val_a:.1f}", f"{val_b:.1f}"
                else: 
                    str_a, str_b = f"{int(val_a)}", f"{int(val_b)}"
                    
                tot = val_a + val_b
                pct_a = (val_a / tot * 100) if tot > 0 else 50
                pct_b = (val_b / tot * 100) if tot > 0 else 50
                
                # HTML dirapatkan menjadi 1 baris string murni agar aman dari bug Markdown Streamlit
                html_bars += f"<div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;'><div style='width: 45px; text-align: right; font-weight: 800; color: white; font-family: \"Montserrat\", sans-serif; font-size: 14px;'>{str_a}</div><div style='flex: 1; margin: 0 18px; position: relative; height: 30px; border-radius: 15px; overflow: hidden; display: flex; box-shadow: 0 4px 6px rgba(0,0,0,0.4);'><div style='width: {pct_a}%; background-color: {warna_A}; height: 100%;'></div><div style='width: {pct_b}%; background-color: {warna_B}; height: 100%;'></div><div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-family: \"Montserrat\", sans-serif; font-size: 12px; letter-spacing: 0.5px; text-shadow: 1.5px 1.5px 3px rgba(0,0,0,0.9), -1px -1px 2px rgba(0,0,0,0.8); pointer-events: none;'>{bar_labels[i]}</div></div><div style='width: 45px; text-align: left; font-weight: 800; color: white; font-family: \"Montserrat\", sans-serif; font-size: 14px;'>{str_b}</div></div>"
                
            html_bars += "</div>"
            st.markdown(html_bars, unsafe_allow_html=True)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 15px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 3. LINE UP HEAD TO HEAD (MAP 10 HERO) ===
        st.markdown("### 🗺️ Line Up Head to Head")
        
        df_roster = pd.read_csv("IKL_Rosters.csv")
        df_roster = df_roster[df_roster['Season'] == musim_pilihan]
        df_roster['Status_Score'] = df_roster['Status'].astype(str).str.strip().str.lower().map({'main': 1, 'active': 1, 'core': 1, 'subs': 2, 'cadangan': 2}).fillna(3)
        df_roster = df_roster.sort_values('Status_Score')

        # === KOORDINAT H2H KHUSUS ===
        # Tim A (Kiri/Biru) ditarik sedikit ke arah markas bawah kiri
        MAP_COORDS_A = {
            'Top Lane': {'top': '30%', 'left': '20%', 'transform': 'translate(-50%, -50%)'},
            'Jungler': {'top': '49%', 'left': '29%', 'transform': 'translate(-50%, -50%)'},
            'Middle': {'top': '54%', 'left': '44%', 'transform': 'translate(-50%, -50%)'},
            'Roamer': {'top': '61%', 'left': '60%', 'transform': 'translate(-50%, -50%)'},
            'Bottom Lane': {'top': '78%', 'left': '29%', 'transform': 'translate(-50%, -50%)'}
        }
        # Tim B (Kanan/Merah) ditarik sedikit ke arah markas atas kanan
        MAP_COORDS_B = {
            'Top Lane': {'top': '21%', 'left': '33%', 'transform': 'translate(-50%, -50%)'},
            'Jungler': {'top': '37%', 'left': '35%', 'transform': 'translate(-50%, -50%)'},
            'Middle': {'top': '46%', 'left': '56%', 'transform': 'translate(-50%, -50%)'},
            'Roamer': {'top': '49%', 'left': '74%', 'transform': 'translate(-50%, -50%)'},
            'Bottom Lane': {'top': '72%', 'left': '81%', 'transform': 'translate(-50%, -50%)'}
        }

        map_path = "assets/HOK_map-layout.png"
        map_b64 = image_to_base64(map_path)
        
        # Background Warna Tim
        bg_b64_A = image_to_base64(get_team_bg_path(tim_A))
        bg_b64_B = image_to_base64(get_team_bg_path(tim_B))
        
        # max-width diturunkan menjadi 780px agar map sedikit mengecil
        html_container = f"""
        <div id='map_container' style='position: relative; width: 100%; max-width: 780px; aspect-ratio: 1/1; margin: 0 auto; border: none solid #d4af37; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.5);'>
            <img src='data:image/png;base64,{map_b64}' style='width: 100%; height: 100%; object-fit: contain; display: block;'>
        """

        role_idx_map = {'Top Lane': 0, 'Jungler': 1, 'Middle': 2, 'Bottom Lane': 3, 'Roamer': 4}
        role_keywords = {'Top Lane': 'top|clash', 'Jungler': 'jung', 'Middle': 'mid', 'Bottom Lane': 'bot|farm|gold', 'Roamer': 'roam|sup'}

        # Fungsi Builder Kartu Map (Parameter border warna sudah dibuang)
        def build_map_cards(tim_nama, coords_dict, bg_b64):
            html_cards = ""
            df_hist_player = df_long[(df_long['Team'] == tim_nama) & (df_long['Win'].notna())]
            df_roster_tim = df_roster[df_roster['Team'] == tim_nama]
            
            for role_csv, coords in coords_dict.items():
                keyword = role_keywords.get(role_csv, '')
                pemain_data = df_roster_tim[df_roster_tim['Role'].astype(str).str.lower().str.contains(keyword, na=False)]
                
                if not pemain_data.empty:
                    nama_pemain = str(pemain_data.iloc[0]['Player_ID'])
                    foto_b64 = image_to_base64(get_player_path(nama_pemain))
                    icon_role_b64 = image_to_base64(f"assets/{ROLE_ICONS.get(role_csv)}")
                    
                    idx_lane = role_idx_map.get(role_csv, 0)
                    hero_counts = {}
                    for _, row in df_hist_player.iterrows():
                        heroes = row['Heroes_List']
                        if isinstance(heroes, list) and len(heroes) > idx_lane:
                            h = heroes[idx_lane]
                            hero_counts[h] = hero_counts.get(h, 0) + 1
                            
                    # Mengembalikan kapasitas menjadi 3 Hero Teratas
                    top_3_heroes = sorted(hero_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    
                    hero_html = "<div style='position: absolute; bottom: 5%; width: 100%; display: flex; justify-content: center; gap: 3px; z-index: 4;'>"
                    for h_name, _ in top_3_heroes:
                        h_path = get_hero_path(h_name)
                        # Ukuran ikon hero disesuaikan menjadi 15px
                        if h_path: hero_html += f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 15px; height: 15px; border-radius: 2px; border: 0.5px solid rgba(255,255,255,0.5); object-fit: cover; box-shadow: 1px 1px 2px rgba(0,0,0,0.8);'>"
                    hero_html += "</div>"
                    
                    style_pos = f"top: {coords['top']}; left: {coords['left']};"
                    if 'transform' in coords: style_pos += f" transform: {coords['transform']};"
                    
                    # Kartu diperbesar kembali ke 75px, tanpa inline border warna
                    html_cards += f"""
                    <div style="position: absolute; {style_pos} width: 75px; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.7); z-index: 5;">
                        <img src="data:image/png;base64,{bg_b64}" style="width: 100%; height: auto; display: block; filter: brightness(0.65);">
                        <img src="data:image/png;base64,{icon_role_b64}" style="position: absolute; top: 3px; left: 2px; width: 17px; height: 17px; z-index: 5; filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.9));">
                        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 74%; z-index: 2; overflow: hidden; border-radius: 4px 4px 0 0;">
                            <img src="data:image/png;base64,{foto_b64}" style="width: 100%; height: 100%; object-fit: cover; object-position: top center; opacity: 0.95;">
                        </div>
                        <div style="position: absolute; bottom: 27%; width: 100%; text-align: center; color: white; font-weight: 800; font-size: 9.5px; text-shadow: 1px 1px 2px black, -1px -1px 2px black, 0px 2px 4px black; z-index: 3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 2px;">{nama_pemain}</div>
                        {hero_html}
                    </div>
                    """
            return html_cards

        # Render kartu tim tanpa mengirimkan parameter warna border
        html_container += build_map_cards(tim_A, MAP_COORDS_A, bg_b64_A)
        html_container += build_map_cards(tim_B, MAP_COORDS_B, bg_b64_B)
        html_container += "</div>"
        
        # Karena lebar map diperkecil, tinggi iframe juga disesuaikan agar proporsional
        import streamlit.components.v1 as components
        components.html(html_container, height=800)

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 15px; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        # === 4. TEAM STRATEGY COMPARISON ===
        st.markdown("### ♟️ Team Strategy")
        
        col_strat_A, col_strat_B = st.columns(2)
        
        # Mesin pencari data draft
        def get_team_draft_stats(nama_tim):
            df_semua = df_history[(df_history['Team_(Blue)'] == nama_tim) | (df_history['Opponent_(Red)'] == nama_tim)]
            tot_match = len(df_semua)
            if tot_match == 0: return pd.Series(), pd.Series(), 0
            
            picks = df_long[df_long['Team'] == nama_tim].explode('Heroes_List')['Heroes_List'].value_counts().head(5)
            ban_b = df_semua[df_semua['Team_(Blue)'] == nama_tim]['Bans_Blue'].dropna().astype(str).str.split(',').explode().str.strip()
            ban_r = df_semua[df_semua['Opponent_(Red)'] == nama_tim]['Bans_Red'].dropna().astype(str).str.split(',').explode().str.strip()
            bans = pd.concat([ban_b, ban_r]).value_counts().head(5)
            return picks, bans, tot_match

        picks_A, bans_A, match_A = get_team_draft_stats(tim_A)
        picks_B, bans_B, match_B = get_team_draft_stats(tim_B)
        
        def render_h2h_draft_column(tim_nama, border_col, picks, bans, tot_match):
            html = f"<div style='border-left: 4px solid {border_col}; padding-left: 15px; margin-bottom: 20px;'>"
            html += f"<h4 style='color: white; margin-bottom: 15px;'>{tim_nama} Strategy</h4>"
            
            if tot_match == 0:
                html += "<div style='color: gray; font-style: italic;'>Data belum tersedia</div></div>"
                return html
                
            html += "<div style='display: flex; gap: 15px;'>"
            
            # Most Picked Sub-Column
            html += "<div style='flex: 1;'><div style='color: #4caf50; font-weight: bold; font-size: 13px; margin-bottom: 10px;'>Most Picked</div>"
            for hero, count in picks.items():
                h_path = get_hero_path(hero)
                rate = (count / tot_match) * 100
                h_img = f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 35px; height: 35px; border-radius: 4px; object-fit: cover; border: 1px solid #4caf50;'>" if h_path else f"<div style='width: 35px; height: 35px; background: #444; border-radius: 4px; font-size:8px;'></div>"
                html += f"<div style='display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 5px 10px; border-radius: 6px; margin-bottom: 8px;'><div style='display: flex; align-items: center; gap: 10px;'>{h_img}<span style='color: white; font-size: 13px; font-weight: 600;'>{hero}</span></div><span style='color: #4caf50; font-weight: bold; font-size: 13px;'>{rate:.0f}%</span></div>"
            html += "</div>"
            
            # Most Banned Sub-Column
            html += "<div style='flex: 1;'><div style='color: #ef4444; font-weight: bold; font-size: 13px; margin-bottom: 10px;'>Most Banned</div>"
            for hero, count in bans.items():
                h_path = get_hero_path(hero)
                rate = (count / tot_match) * 100
                h_img = f"<img src='data:image/png;base64,{image_to_base64(h_path)}' style='width: 35px; height: 35px; border-radius: 4px; object-fit: cover; border: 1px solid #ef4444; filter: grayscale(100%);'>" if h_path else f"<div style='width: 35px; height: 35px; background: #444; border-radius: 4px; font-size:8px;'></div>"
                html += f"<div style='display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.05); padding: 5px 10px; border-radius: 6px; margin-bottom: 8px;'><div style='display: flex; align-items: center; gap: 10px;'>{h_img}<span style='color: white; font-size: 13px; font-weight: 600;'>{hero}</span></div><span style='color: #ef4444; font-weight: bold; font-size: 13px;'>{rate:.0f}%</span></div>"
            html += "</div>"
            
            html += "</div></div>"
            return html

        with col_strat_A:
            st.markdown(render_h2h_draft_column(tim_A, warna_A, picks_A, bans_A, match_A), unsafe_allow_html=True)
            kombo_A = get_signature_combos(tim_A)
            if kombo_A:
                st.markdown(f"<div style='border-left: 4px solid {warna_A}; padding-left: 15px; margin-bottom: 10px; color: white; font-weight: bold;'>Top Combos</div>", unsafe_allow_html=True)
                for k in kombo_A[:2]: render_combo_card(k["combo"], k["warna"], k["freq"], k["wr"], k["label"])
                
        with col_strat_B:
            st.markdown(render_h2h_draft_column(tim_B, warna_B, picks_B, bans_B, match_B), unsafe_allow_html=True)
            kombo_B = get_signature_combos(tim_B)
            if kombo_B:
                st.markdown(f"<div style='border-left: 4px solid {warna_B}; padding-left: 15px; margin-bottom: 10px; color: white; font-weight: bold;'>Top Combos</div>", unsafe_allow_html=True)
                for k in kombo_B[:2]: render_combo_card(k["combo"], k["warna"], k["freq"], k["wr"], k["label"])

        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 15px; margin-bottom: 30px;'>", unsafe_allow_html=True)

        # === 5. MATCH HISTORY HEAD TO HEAD ===
        st.markdown("### 📜 H2H Match History")
        
        hist_h2h = df_history[
            ((df_history['Team_(Blue)'] == tim_A) & (df_history['Opponent_(Red)'] == tim_B)) |
            ((df_history['Team_(Blue)'] == tim_B) & (df_history['Opponent_(Red)'] == tim_A))
        ].copy()
        
        if hist_h2h.empty:
            st.info(f"Belum ada riwayat pertemuan antara {tim_A} dan {tim_B} di musim ini.")
        else:
            hist_h2h['Date_Sort'] = pd.to_datetime(hist_h2h['Date'], errors='coerce')
            hist_h2h['Date'] = hist_h2h['Date_Sort'].dt.strftime('%d %b %Y').fillna(hist_h2h['Date'])
            hist_h2h['Result'] = hist_h2h['Result'].apply(lambda x: "🟦 Blue Win" if x == 1.0 else ("🟥 Red Win" if x == 0.0 else "TBD"))
            
            hist_h2h = hist_h2h.sort_values(by=['Date_Sort'], ascending=[False])
            hist_h2h = hist_h2h[['Date', 'Week', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']]
            
            st.dataframe(
                hist_h2h.style.set_properties(**{'text-align': 'center'}), 
                use_container_width=True, hide_index=True
            )
# endregion