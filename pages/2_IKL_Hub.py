# region INISIALISASI
import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="IKL Dashboard", layout="wide", initial_sidebar_state="expanded")

# === SIHIR CSS: STICKY HEADER SEMPURNA ===
st.markdown("""
    <style>
    /* Target spesifik HANYA untuk kontainer paling atas di halaman utama */
    .main .block-container > div:first-child {
        position: sticky;
        top: 2.875rem; /* Menempel persis di bawah header bawaan Streamlit */
        z-index: 999;
        background-color: #0e1117; /* Latar gelap pekat agar elemen di bawahnya tertutup */
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1); /* Garis batas tipis nan elegan */
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

# [+] FUNGSI GLOBAL PEMBOBOT MUSIM
def urutkan_musim(s):
    bagian = str(s).strip().split()
    if len(bagian) == 2 and bagian[1].isdigit():
        musim, tahun = bagian[0].lower(), int(bagian[1])
        # Fall berbobot 2 (akhir tahun), Spring berbobot 1 (awal tahun)
        bobot_musim = 2 if musim == 'fall' else 1
        return (tahun, bobot_musim)
    return (0, 0)

# === PENGATURAN HEADER GLOBAL (FIXED TOP-RIGHT) ===
col_title, col_season = st.columns([3, 1])
with col_title:
    st.markdown("## 🎮 Indonesia Kings Laga (IKL) - HOK")
        
with col_season:
    if 'Season' in df_csv.columns:
        # Panggil fungsi global untuk mengurutkan musim
        daftar_musim = sorted(df_csv['Season'].dropna().unique().tolist(), key=urutkan_musim, reverse=True)
        musim_pilihan = st.selectbox("Pilih Musim", daftar_musim, label_visibility="collapsed")
        df_master = df_csv[df_csv['Season'] == musim_pilihan].copy()
        
        # [+] INJEKSI ANTI-ALIAS TERISOLASI KHUSUS FALL 2025
        if musim_pilihan == "Fall 2025":
            df_master['Team_(Blue)'] = df_master['Team_(Blue)'].replace({'VIT': 'BTR'})
            df_master['Opponent_(Red)'] = df_master['Opponent_(Red)'].replace({'VIT': 'BTR'})
        # [+] ===============================================
    else:
        st.error("Kolom 'Season' tidak ditemukan!")
        st.stop()
# ==================================================

# region NAVIGASI INTERNAL IKL
if "menu_ikl" not in st.session_state: st.session_state['menu_ikl'] = "🏆 Klasemen & Playoffs"
col_nav1, col_nav2, col_nav3 = st.columns(3)
if col_nav1.button("🏆 Klasemen & Playoffs", use_container_width=True): st.session_state['menu_ikl'] = "🏆 Klasemen & Playoffs"
if col_nav2.button("🛡️ Team Profiling", use_container_width=True): st.session_state['menu_ikl'] = "🛡️ Team Profiling"
if col_nav3.button("⚔️ Versus Mode (H2H)", use_container_width=True): st.session_state['menu_ikl'] = "⚔️ Versus Mode (H2H)"
menu_utama = st.session_state['menu_ikl']
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

# region UI HELPERS
@st.cache_data
def get_dynamic_logo_map(season):
    if os.path.exists("IKL_Rosters.csv"):
        df_ros = pd.read_csv("IKL_Rosters.csv").dropna(subset=['Logo_File'])
        
        # 1. Ambil logo fallback/global (jaga-jaga jika ada tim yang logonya kosong di musim tertentu)
        df_global = df_ros.drop_duplicates(subset=['Team', 'Logo_File'], keep='last').drop_duplicates(subset=['Team'])
        map_global = dict(zip(df_global['Team'], df_global['Logo_File']))
        
        # 2. Ambil logo SPESIFIK untuk musim yang sedang dibuka pengguna
        df_season = df_ros[df_ros['Season'] == season].drop_duplicates(subset=['Team'])
        map_season = dict(zip(df_season['Team'], df_season['Logo_File']))
        
        # 3. Timpa logo global dengan logo spesifik musim tersebut
        map_global.update(map_season)
        return map_global
    return {}

# Panggil fungsinya dengan menyuntikkan variabel musim_pilihan dari header
TEAM_LOGO_MAP = get_dynamic_logo_map(musim_pilihan)

def get_hero_path(hero_name):
    safe_name = hero_name.replace(" ", "_").replace(".png", "").replace(".jpg", "")
    for ext in ['.png', '.jpg', '.jpeg']:
        if os.path.exists(f"assets/heroes/{safe_name}{ext}"): return f"assets/heroes/{safe_name}{ext}"
    return None

import base64
def image_to_base64(img_path):
    if img_path and os.path.exists(img_path):
        with open(img_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

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

# region HALAMAN 1: KLASEMEN, PLAYOFFS & HIGHLIGHTS
if menu_utama == "🏆 Klasemen & Playoffs":
    
    # 1. KLASEMEN REGULAR SEASON & OVERVIEW/UPCOMING
    col_kiri, col_kanan = st.columns([1.5, 1])
    with col_kiri:
        st.markdown(f"### 📊 Standings Regular Season")
        df_reguler = df_long[df_long['Week'].astype(str).str.isdigit()]
        if not df_reguler.empty:
            df_match = df_reguler.groupby(['Week', 'Day', 'Match', 'Team'], sort=False).agg(Game_W=('Win', 'sum'), Game_L=('Win', lambda x: (x == 0).sum())).reset_index()
            df_match['Match_W'] = np.where(df_match['Game_W'] > df_match['Game_L'], 1, 0)
            df_match['Match_L'] = np.where(df_match['Game_W'] < df_match['Game_L'], 1, 0)
            
            klasemen_baru = df_match.groupby('Team').agg(Match=('Match', 'count'), M_W=('Match_W', 'sum'), M_L=('Match_L', 'sum'), G_W=('Game_W', 'sum'), G_L=('Game_L', 'sum')).reset_index()
            klasemen_baru['Match (W-L)'] = klasemen_baru['M_W'].astype(int).astype(str) + "-" + klasemen_baru['M_L'].astype(int).astype(str)
            klasemen_baru['Game (W-L)'] = klasemen_baru['G_W'].astype(int).astype(str) + "-" + klasemen_baru['G_L'].astype(int).astype(str)
            klasemen_baru['Net Point'] = (klasemen_baru['G_W'] - klasemen_baru['G_L']).astype(int)
            klasemen_baru['Rank'] = klasemen_baru['Net Point'].rank(method='min', ascending=False).astype(int)
            
            # JANGAN gunakan set_index('Rank') agar terhindar dari Error Indeks Kembar
            df_tampil = klasemen_baru.sort_values(by='Rank')[['Rank', 'Team', 'Match', 'Match (W-L)', 'Game (W-L)', 'Net Point']]
            
            # Kembalikan indeks ke angka normal (0, 1, 2, 3) 
            df_tampil = df_tampil.reset_index(drop=True)
            
            # === LOGIKA PERCABANGAN FORMAT MUSIM (GROUP VS GLOBAL) ===
            if "2025" in musim_pilihan:
                st.markdown(f"<p style='text-align: center; color: gray; font-size: 13px;'>Format {musim_pilihan}: Double Group Stage</p>", unsafe_allow_html=True)
                
                # Kamus Grup Dinamis
                if musim_pilihan == "Spring 2025":
                    grup_1_nama = "Group Tyrant"
                    grup_1_tim = ['DMT', 'KAGE', 'RRQ', 'AE', 'NMSS']
                    grup_2_nama = "Group Overlord"
                    grup_2_tim = ['BTR', 'TLN.ID', 'ONIC', 'MHD', 'VESA']
                else: # Fall 2025
                    grup_1_nama = "Group Tyrant"
                    grup_1_tim = ['VESA', 'MHD', 'RRQ', 'AE', 'ONIC'] 
                    grup_2_nama = "Group Overlord"
                    grup_2_tim = ['BTR', 'TLN.ID', 'RVM', 'DMT', 'KAGE']
                
                # Membelah DataFrame utama menjadi dua
                df_grup1 = df_tampil[df_tampil['Team'].isin(grup_1_tim)].reset_index(drop=True)
                df_grup2 = df_tampil[df_tampil['Team'].isin(grup_2_tim)].reset_index(drop=True)
                
                # Hitung ulang peringkat (1-5) di dalam masing-masing grup
                df_grup1['Rank'] = df_grup1['Net Point'].rank(method='min', ascending=False).astype(int)
                df_grup2['Rank'] = df_grup2['Net Point'].rank(method='min', ascending=False).astype(int)
                
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown(f"<h5 style='text-align: center; color: #00d2ff;'>{grup_1_nama}</h5>", unsafe_allow_html=True)
                    st.dataframe(df_grup1.sort_values('Rank').style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
                with col_g2:
                    st.markdown(f"<h5 style='text-align: center; color: #ff4b4b;'>{grup_2_nama}</h5>", unsafe_allow_html=True)
                    st.dataframe(df_grup2.sort_values('Rank').style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
                    
            else:
                # Format 2026 (Single Global League)
                st.markdown("<p style='text-align: center; color: gray; font-size: 13px;'>Format 2026: Single Global League</p>", unsafe_allow_html=True)
                st.dataframe(df_tampil.style.set_properties(**{'text-align': 'center'}), use_container_width=True, hide_index=True)
            # =========================================================
        else:
            st.info("Data Regular Season belum tersedia.")

    with col_kanan:
        st.markdown(f"### 📋 Overview")
        tot_tim = df_long['Team'].nunique()
        tot_match = df_master['Match_ID'].nunique()
        st.markdown(f"""
        <div style='background: rgba(0, 180, 255, 0.1); border: 1px solid #00d2ff; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>
            <b>Tim Peserta:</b> {tot_tim} Tim<br>
            <b>Total Seri:</b> {tot_match} Matches
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### 📅 Upcoming Matches")
        df_jadwal = df_master[df_master['Status'] == 'Upcoming'].copy()
        if df_jadwal.empty:
            st.info("Tidak ada jadwal tayang dalam waktu dekat.")
        else:
            dict_match = {'Pl St': 'Play-ins', 'Up Sf': 'UB Semifinal', 'Lw Sf': 'LB Semifinal', 'Up Fl': 'UB Final', 'Lw Fl': 'LB Final', 'Gr Fl': 'Grand Final'}
            st.markdown("<hr style='margin: 0px; border-top: 2px solid #555;'>", unsafe_allow_html=True)
            for idx, row in df_jadwal.drop_duplicates(subset=['Match_ID']).head(5).iterrows():
                f_match = dict_match.get(f"{str(row['Week']).strip()} {str(row['Day']).strip()}", f"Week {row['Week']}")
                waktu = f"{row['Time']}" if pd.notna(row['Time']) and row['Time'] != "" else "TBA"
                tgl = f"{row['Date']} - {waktu}"
                
                tim_a = str(row['Team_(Blue)']) if str(row['Team_(Blue)']) != "nan" else "TBD"
                tim_b = str(row['Opponent_(Red)']) if str(row['Opponent_(Red)']) != "nan" else "TBD"
                
                st.markdown(f"""
                <div style='font-size: 13.5px; padding: 8px 0px;'>
                    <div style='color: gray; font-size: 11px; margin-bottom: 2px;'>{tgl} | {f_match}</div>
                    <div style='display: flex; justify-content: space-between;'>
                        <div style='width: 45%; text-align: right; font-weight: bold;'>{tim_a}</div>
                        <div style='width: 10%; text-align: center; color: #00d2ff;'>⚔️</div>
                        <div style='width: 45%; text-align: left; font-weight: bold;'>{tim_b}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<hr style='margin: 0px; border-top: 1px dashed #444;'>", unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. BRACKET PLAYOFFS
    st.markdown("### 🏆 Playoff Bracket")
    df_playoff = df_master[df_master['Week'].isin(['Pl', 'Up', 'Lw', 'Gr'])].copy()
    
    if df_playoff.empty:
        st.info("Babak Playoffs belum dimulai atau data belum tersedia.")
    else:
        po_matches = df_playoff.drop_duplicates(subset=['Match_ID'])
        col_b1, col_b2, col_b3 = st.columns(3)
        
        # === FUNGSI BRACKET YANG SUDAH DIPERBAIKI (PER MATCH) ===
        def render_bracket_box(df_match_filtered, title):
            st.markdown(f"<div style='text-align: center; color: #00d2ff; font-size: 14px; font-weight: bold; margin-bottom: 5px;'>{title}</div>", unsafe_allow_html=True)
            if df_match_filtered.empty:
                st.markdown("<div style='background: #222; border: 1px dashed #555; border-radius: 5px; padding: 10px; text-align: center; color: gray; margin-bottom: 15px;'>TBD</div>", unsafe_allow_html=True)
                return
                
            # Filter agar yang tampil HANYA 1 kotak per Match (Seri)
            series_list = df_match_filtered.drop_duplicates(subset=['Week', 'Day', 'Match'])
            
            for idx, row in series_list.iterrows():
                # Ambil semua game yang terjadi di dalam seri pertandingan ini
                games = df_playoff[(df_playoff['Week'] == row['Week']) & (df_playoff['Day'] == row['Day']) & (df_playoff['Match'] == row['Match'])]
                
                # Tentukan tim kiri dan kanan dari game pertama
                tim_a = str(row['Team_(Blue)']) if pd.notna(row['Team_(Blue)']) and str(row['Team_(Blue)']) != "nan" else "TBD"
                tim_b = str(row['Opponent_(Red)']) if pd.notna(row['Opponent_(Red)']) and str(row['Opponent_(Red)']) != "nan" else "TBD"
                
                skor = ""
                # Kalkulasi skor jika pertandingan sudah berjalan
                if row['Status'] == 'History' or games['Result'].notna().any():
                    win_a = 0
                    win_b = 0
                    for _, g in games.dropna(subset=['Result']).iterrows():
                        if g['Team_(Blue)'] == tim_a and g['Result'] == 1.0: win_a += 1
                        elif g['Team_(Blue)'] == tim_b and g['Result'] == 1.0: win_b += 1
                        elif g['Opponent_(Red)'] == tim_a and g['Result'] == 0.0: win_a += 1
                        elif g['Opponent_(Red)'] == tim_b and g['Result'] == 0.0: win_b += 1
                        
                    skor = f"<span style='float: right; color: #00d2ff;'>{win_a} - {win_b}</span>"
                    
                st.markdown(f"""
                <div style='background: #222; border-left: 3px solid #00d2ff; border-radius: 5px; padding: 10px; margin-bottom: 15px;'>
                    <div style='font-size: 13px;'><b>{tim_a}</b> vs <b>{tim_b}</b> {skor}</div>
                    <div style='font-size: 10px; color: gray; margin-top: 5px;'>{row['Date']}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_b1:
            render_bracket_box(df_playoff[df_playoff['Week'] == 'Pl'], "Play-In Stages")
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Lw') & (df_playoff['Day'] == 'Sf')], "LB Semifinal")
        with col_b2:
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Up') & (df_playoff['Day'] == 'Sf')], "UB Semifinal")
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Lw') & (df_playoff['Day'] == 'Fl')], "LB Final")
        with col_b3:
            render_bracket_box(df_playoff[(df_playoff['Week'] == 'Up') & (df_playoff['Day'] == 'Fl')], "UB Final")
            render_bracket_box(df_playoff[df_playoff['Week'] == 'Gr'], "Grand Final 🏆")
        # ==========================================================

    st.markdown("---")
    
    # 3. HIGHLIGHT & ANALITIK (GAYA ARTIKEL ONE-PAGER)
    st.markdown("### 📰 Highlight & Analisis Kinerja")
    
    # Bagian 1: MVP & Winstreak
    st.markdown("#### 🌟 Top Players & Teams")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.caption("🎖️ MVP Leaderboard")
        mvp_counts = df_history['MVP'].dropna().value_counts().head(5).reset_index()
        mvp_counts.columns = ['Player', 'Total MVP']
        st.dataframe(mvp_counts, use_container_width=True, hide_index=True)
        
    with col_t2:
        st.caption("🔥 Longest Winstreak")
        winstreak_record = {}
        for team in df_long['Team'].unique():
            wins = df_long[df_long['Team'] == team]['Win'].tolist()
            max_st, curr_st = 0, 0
            for w in wins:
                if w == 1: curr_st += 1; max_st = max(max_st, curr_st)
                else: curr_st = 0
            winstreak_record[team] = max_st
        ws_df = pd.DataFrame(list(winstreak_record.items()), columns=['Team', 'Max Winstreak']).sort_values('Max Winstreak', ascending=False).head(5)
        st.dataframe(ws_df, use_container_width=True, hide_index=True)

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
    
    hist_display = df_history[['Date', 'Week', 'Match', 'Game', 'Team_(Blue)', 'Result', 'Opponent_(Red)', 'Duration_min', 'MVP']].copy()
    if tim_filter != "Semua Tim":
        hist_display = hist_display[(hist_display['Team_(Blue)'] == tim_filter) | (hist_display['Opponent_(Red)'] == tim_filter)]
        
    hist_display['Result'] = hist_display['Result'].apply(lambda x: "Blue Win" if x == 1 else "Red Win")
    st.dataframe(hist_display.sort_values(by=['Date', 'Match', 'Game'], ascending=[False, False, True]), use_container_width=True, hide_index=True)

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