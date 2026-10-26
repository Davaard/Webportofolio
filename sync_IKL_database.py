import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import os
import urllib.parse
from datetime import datetime
import re

# ==========================================
# 1. KONFIGURASI UTAMA
# ==========================================
TAHUN = "2025"
MUSIM = "Fall"
HALAMAN_DASAR = f"Indonesia_Kings_Laga/{TAHUN}/{MUSIM}"
SEASON_NAME = f"{MUSIM} {TAHUN}"
DIR_LOGO = "assets/logo_tim"

HEADERS = {
    'User-Agent': 'IKL_Hub_Master_Bot/5.2_Final (Contact: daryadarendra@gmail.com)',
    'Accept-Encoding': 'gzip'
}
URL_API = "https://liquipedia.net/honorofkings/api.php"
os.makedirs(DIR_LOGO, exist_ok=True)

TEAM_MAP_DINAMIS = {"TBD": np.nan}
TEAM_LOGO_MAP = {}
HERO_MAP = {"Ao'yin": "Loong", "Garuda Khageswara": "Garuda"}

# ==========================================
# 2. FUNGSI UTILITAS & AUTO-MAPPER
# ==========================================
def unduh_logo_hd(singkatan_tim, url_gambar_mentah):
    if not singkatan_tim or singkatan_tim == "TBD" or not url_gambar_mentah: return
    if "/thumb/" in url_gambar_mentah:
        filename = urllib.parse.unquote(url_gambar_mentah.split('/')[-2])
        url_hd = f"https://liquipedia.net{url_gambar_mentah.replace('/thumb', '').rsplit('/', 1)[0]}"
    else:
        filename = urllib.parse.unquote(url_gambar_mentah.split('/')[-1])
        url_hd = f"https://liquipedia.net{url_gambar_mentah}"
        
    TEAM_LOGO_MAP[singkatan_tim] = filename
    jalur_simpan = os.path.join(DIR_LOGO, filename)
    
    if not os.path.exists(jalur_simpan):
        try:
            res = requests.get(url_hd, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                with open(jalur_simpan, 'wb') as f: f.write(res.content)
        except: pass

def bangun_kamus_dinamis(soup):
    if not soup: return
    for blok in soup.find_all('div', class_='block-team'):
        t_short = blok.find('div', class_='team-shortname')
        t_bracket = blok.find('div', class_='team-bracketname')
        t_full = blok.find('div', class_='team-name')
        t_link = blok.find('a', title=True)
        
        if t_short:
            singkatan = t_short.text.strip()
            if t_bracket: TEAM_MAP_DINAMIS[t_bracket.text.strip()] = singkatan
            if t_full: TEAM_MAP_DINAMIS[t_full.text.strip()] = singkatan
            if t_link: TEAM_MAP_DINAMIS[t_link['title'].replace(" (page does not exist)", "").strip()] = singkatan
            
            img_tag = blok.find('img')
            if img_tag and img_tag.has_attr('src'):
                unduh_logo_hd(singkatan, img_tag['src'])

def clean_team(name):
    if not name: return np.nan
    return TEAM_MAP_DINAMIS.get(name.replace(" (page does not exist)", "").strip(), name.strip())

# === 🦸 FUNGSI BARU: PENCARI HERO AGRESIF ===
def clean_hero(nama):
    # Membersihkan anomali '(page does not exist)' dan memetakan ke nama global (seperti Loong)
    nama_bersih = str(nama).replace(" (page does not exist)", "").strip()
    return HERO_MAP.get(nama_bersih, nama_bersih)

def get_heroes_agresif(kolom_html):
    # Langkah 1: Coba ambil dari tag <a> bertitel
    heroes = [clean_hero(a['title']) for a in kolom_html.find_all('a', title=True) if 'Hero' not in a['title']]
    # Langkah 2: Jika gagal, paksa ambil dari tag <img> 
    if not heroes:
        for img in kolom_html.find_all('img'):
            val = img.get('alt') or img.get('title')
            if val: heroes.append(clean_hero(val))
    return heroes
# ============================================

def fetch_api_soup(page_title):
    print(f"📡 Menarik API: {page_title}...")
    try:
        res = requests.get(URL_API, params={
            "action": "parse",
            "page": page_title, 
            "format": "json", 
            "disabletoc": 1
            # BOM CACHE BUSTER TELAH DIMATIKAN
        }, headers=HEADERS, timeout=15)
        if res.status_code == 200 and "parse" in res.json():
            time.sleep(1.5)
            return BeautifulSoup(res.json()["parse"]["text"]["*"], 'html.parser')
    except Exception as e: print(f"❌ Gagal: {e}")
    return None

def parse_datetime(timer_tag):
    if not timer_tag or not timer_tag.text.strip(): return "", ""
    raw = timer_tag.text.strip()
    for tz in ["WIB", "UTC", "ICT", "SGT"]: raw = raw.replace(tz, "").strip()
    parts = [p.strip() for p in raw.split('-')]
    d_str, t_str = parts[0], parts[1] if len(parts) > 1 else ""
    for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %d"]:
        try:
            dt = datetime.strptime(d_str, fmt)
            d_str = f"{dt.month}/{dt.day}/{dt.year if fmt != '%B %d' else int(TAHUN)}"
            break
        except: continue
    return d_str, t_str

# ==========================================
# 3. EKSTRAKTOR DENGAN LOGIKA SELF-HEALING
# ==========================================
def extract_popup_data(popup, week_code, day_code, match_num, player_to_team):
    rows = []
    timer = popup.find('span', class_='timer-object')
    date_str, time_str = parse_datetime(timer)

    l_tag = popup.find('div', class_='match-info-header-opponent-left')
    r_tags = popup.find_all('div', class_='match-info-header-opponent')
    r_tag = r_tags[-1] if r_tags else None

    t_kiri = clean_team(l_tag.find('span', class_='name').text) if l_tag and l_tag.find('span', class_='name') else np.nan
    t_kanan = clean_team(r_tag.find('span', class_='name').text) if r_tag and r_tag.find('span', class_='name') else np.nan

    mvps = [a.text.strip() for a in (popup.find('div', class_='brkts-popup-mvp') or BeautifulSoup("", 'html.parser')).find_all('a')]
    
    bans_per_round = []
    if veto := popup.find('div', class_='brkts-popup-veto'):
        for v_row in veto.find_all('div', class_='brkts-popup-veto-row'):
            b_cols = v_row.find_all('div', class_='brkts-popup-body-element-thumbs')
            if len(b_cols) >= 2:
                bans_per_round.append({
                    'left': get_heroes_agresif(b_cols[0]),
                    'right': get_heroes_agresif(b_cols[1])
                })

    games = popup.find_all('div', class_='brkts-popup-body-grid-row')
    valid_games = 0

    for i, game in enumerate(games):
        cols = game.find_all('div', class_='brkts-popup-spaced')
        if len(cols) < 3: continue 

        # === 🦸 PENGGUNAAN PENCARI HERO AGRESIF ===
        p_left = get_heroes_agresif(cols[0])
        p_right = get_heroes_agresif(cols[2])

        valid_games += 1
        
        # === ⏱️ TOLERANSI TYPO ADMIN (. atau :) ===
        durasi_teks = cols[1].text.strip()
        if ":" in durasi_teks or "." in durasi_teks or durasi_teks.isdigit():
            durasi = durasi_teks
        else:
            durasi = "-"
        
        labels = game.find_all('div', class_='generic-label')
        win_left = 1.0 if len(labels) > 0 and 'result-win' in labels[0].get('data-label-type', '') else 0.0
        
        is_blue_left = cols[0].find('div', class_='brkts-popup-side-color--blue') is not None
        if is_blue_left:
            t_blue, o_red, res = t_kiri, t_kanan, win_left
            h_blue, h_red = p_left, p_right
            b_blue = bans_per_round[i]['left'] if i < len(bans_per_round) else []
            b_red = bans_per_round[i]['right'] if i < len(bans_per_round) else []
        else:
            t_blue, o_red, res = t_kanan, t_kiri, 1.0 - win_left
            h_blue, h_red = p_right, p_left
            b_blue = bans_per_round[i]['right'] if i < len(bans_per_round) else []
            b_red = bans_per_round[i]['left'] if i < len(bans_per_round) else []

        mvp_player = mvps[i] if i < len(mvps) else np.nan
        
        if pd.notna(mvp_player) and mvp_player.lower() in player_to_team:
            mvp_team = player_to_team[mvp_player.lower()]
            if mvp_team == t_blue:
                res = 1.0
            elif mvp_team == o_red:
                res = 0.0

        rows.append({
            'Season': SEASON_NAME, 'Date': date_str, 'Time': time_str, 'Week': str(week_code), 'Day': str(day_code),
            'Match': int(match_num), 'Game': float(i + 1), 'Team_(Blue)': t_blue, 'Opponent_(Red)': o_red,
            'T_Rank': np.nan, 'O_Rank': np.nan, 'Result': res, 'Duration_min': durasi,
            'T_Gold': np.nan, 'O_Gold': np.nan, 'T_Kill': np.nan, 'O_Kill': np.nan,
            'T_Assist': np.nan, 'O_Assist': np.nan, 'T_Objective': np.nan, 'O_Objective': np.nan,
            'Heroes_Picked': ','.join(h_blue), 'Opponent_Picked': ','.join(h_red),
            'Bans_Blue': ','.join(b_blue) if b_blue else np.nan, 'Bans_Red': ','.join(b_red) if b_red else np.nan,
            'MVP': mvp_player
        })

    if valid_games == 0:
        rows.append({
            'Season': SEASON_NAME, 'Date': date_str, 'Time': time_str, 'Week': str(week_code), 'Day': str(day_code),
            'Match': int(match_num), 'Game': np.nan, 'Team_(Blue)': t_kiri, 'Opponent_(Red)': t_kanan,
            'Result': np.nan, 'Duration_min': np.nan
        })
    return rows

# ==========================================
# 4. PARSER MENGGUNAKAN KAMUS ROSTER
# ==========================================
def parse_rosters(soup):
    rosters = []
    if not soup: return rosters
    tab_map = {"1": "Main", "2": "Subs", "3": "Former/Staff", "4": "Staff"}

    for card in soup.find_all('div', class_='team-participant-card'):
        t_name = card.find('span', class_='name')
        t_code = clean_team(t_name.text) if t_name else "UNK"
        notes = " | ".join([n.text.strip().replace('\n', ' ') for n in card.find_all('div', class_='team-participant-card__notification')])
        pill_map = {p.get('data-toggle-area-btn'): p.text.strip() for p in card.find_all('div', class_='switch-pill-option')}

        for c_div in card.find_all('div', attrs={'data-toggle-area-content': True}):
            a_id = c_div.get('data-toggle-area-content')
            s_label = pill_map.get(a_id, tab_map.get(a_id, "Active"))

            for mem in c_div.find_all('div', class_='team-participant-card__member'):
                p_tag = mem.find('span', class_='name')
                if not p_tag: continue
                p_name = p_tag.text.strip()
                p_title = p_tag.find('a')['title'].replace(" (page does not exist)", "") if p_tag.find('a') and p_tag.find('a').has_attr('title') else p_name
                
                f_img = mem.find('span', class_='flag').find('img') if mem.find('span', class_='flag') else None
                country = f_img['alt'] if f_img and f_img.has_attr('alt') else "Unknown"

                r_left = mem.find('div', class_='team-participant-card__member-role-left')
                r_right = mem.find('div', class_='team-participant-card__member-role-right')
                role = r_left.find('img')['title'] if r_left and r_left.find('img') and r_left.find('img').has_attr('title') else (r_right.text.strip() if r_right else "Player")
                
                final_status = "Former" if (r_right and "Left" in r_right.text) else s_label
                rosters.append({
                    'Season': SEASON_NAME, 'Team': t_code, 'Player_ID': p_name, 'Player_Wiki_Title': p_title,
                    'Role': role, 'Status': final_status, 'Country': country, 
                    'Logo_File': TEAM_LOGO_MAP.get(t_code, np.nan), 'Team_Notes': notes if notes else np.nan
                })
    return rosters

def parse_all_matches(soup_reg, soup_po, player_to_team):
    all_rows = []
    if soup_reg:
        for w_idx, mlist in enumerate(soup_reg.find_all('div', class_='brkts-matchlist')):
            
            # === 🛡️ BENTENG PENJAGA GERBANG RIGID ===
            title_tag = mlist.find(class_=re.compile('brkts-matchlist-title'))
            if not title_tag:
                continue
                
            header_text = title_tag.text.strip().lower()
            valid_keywords = ['week', 'play-in', 'play', 'upper', 'lower', 'grand']
            if not any(k in header_text for k in valid_keywords):
                continue
            # ========================================
            
            if area := mlist.find('div', class_='brkts-matchlist-collapse-area'):
                d_num, m_in_day = 0, 0
                for child in area.children:
                    if not getattr(child, 'name', None): continue
                    cls = child.get('class', [])
                    if 'brkts-matchlist-header' in cls: d_num += 1; m_in_day = 0
                    elif 'brkts-matchlist-match' in cls:
                        m_in_day += 1
                        if popup := child.find('div', class_='brkts-match-info-popup'):
                            all_rows.extend(extract_popup_data(popup, w_idx + 1, d_num, m_in_day, player_to_team))

    if soup_po:
        playoff_map = [
            ('Pl', 'St', 1), ('Up', 'Sf', 1), ('Pl', 'St', 2), ('Up', 'Sf', 2),
            ('Up', 'Fl', 0), ('Lw', 'Sf', 0), ('Lw', 'Fl', 0), ('Gr', 'Fl', 0)
        ]
        for idx, popup in enumerate(soup_po.find_all('div', class_='brkts-match-info-popup')):
            w_code, d_code, m_num = playoff_map[idx] if idx < len(playoff_map) else ('Po', 'Xx', idx + 1)
            all_rows.extend(extract_popup_data(popup, w_code, d_code, m_num, player_to_team))
            
    df_bersih = pd.DataFrame(all_rows)
    if not df_bersih.empty:
        df_bersih.drop_duplicates(subset=['Season', 'Week', 'Day', 'Match', 'Game'], keep='first', inplace=True)
    return df_bersih.to_dict('records')

# ==========================================
# 5. EKSEKUSI & SMART MERGE
# ==========================================
if __name__ == "__main__":
    soup_ov = fetch_api_soup(f"{HALAMAN_DASAR}")
    soup_reg = fetch_api_soup(f"{HALAMAN_DASAR}/Regular_Season")
    soup_po = fetch_api_soup(f"{HALAMAN_DASAR}/Playoffs")

    bangun_kamus_dinamis(soup_ov)
    bangun_kamus_dinamis(soup_reg)

    rosters = parse_rosters(soup_ov)
    player_to_team_map = {r['Player_ID'].lower(): r['Team'] for r in rosters}
    player_to_team_map.update({r['Player_Wiki_Title'].lower(): r['Team'] for r in rosters})

    if rosters:
        df_roster_new = pd.DataFrame(rosters)
        ros_path = "IKL_Rosters.csv"
        if os.path.exists(ros_path):
            df_roster_old = pd.read_csv(ros_path)
            df_roster_final = pd.concat([df_roster_old[df_roster_old['Season'] != SEASON_NAME], df_roster_new], ignore_index=True)
        else: 
            df_roster_final = df_roster_new
        
        df_roster_final.sort_values(by=['Season', 'Team', 'Status', 'Player_ID'], inplace=True, na_position='last')
        df_roster_final.to_csv(ros_path, index=False)
        print(f"✅ Data Roster Diperbarui & Tersusun Rapi!")

    scraped_matches = parse_all_matches(soup_reg, soup_po, player_to_team_map)
    df_scraped = pd.DataFrame(scraped_matches)
    
    csv_path = "Data_Set_IKL_HOK.csv"
    if os.path.exists(csv_path) and not df_scraped.empty:
        df_old = pd.read_csv(csv_path)
        df_old['Week'], df_old['Day'] = df_old['Week'].astype(str), df_old['Day'].astype(str)
        if 'Season' not in df_old.columns: df_old['Season'] = SEASON_NAME

        # === 💎 SMART MERGE ULTIMATE ===
        # Ubah kosong dari scraper menjadi NaN
        df_scraped.replace(['', '-', 'nan', 'NaN', 'TBD'], np.nan, inplace=True)
        
        # Lindungi semua kolom manual, hero, dan durasi
        metric_cols = [
            'T_Rank', 'O_Rank', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 
            'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 
            'Heroes_Picked', 'Opponent_Picked', 'Bans_Blue', 'Bans_Red', 'Duration_min'
        ]
        key_cols = ['Season', 'Week', 'Day', 'Match', 'Game']
        
        # [+] INJEKSI ANTI-ERROR: Pastikan CSV lama punya semua kolom sebelum di-merge
        for col in metric_cols:
            if col not in df_old.columns:
                df_old[col] = np.nan
        # [+] =========================================================================
        
        df_old_games = df_old[df_old['Game'].notna()].copy()
        df_merged = pd.merge(df_scraped, df_old_games[key_cols + metric_cols], on=key_cols, how='left', suffixes=('', '_old'))
        
        for col in metric_cols:
            if f"{col}_old" in df_merged.columns:
                # Kombinasi Prioritas: Scraper -> Manual (Old)
                df_merged[col] = df_merged[col].combine_first(df_merged[f"{col}_old"])
                df_merged.drop(columns=[f"{col}_old"], inplace=True)
        # ===============================

        scraped_valid = set(df_scraped[df_scraped['Game'].notna()][['Season', 'Week', 'Day', 'Match']].itertuples(index=False, name=None))
        preserved_rows = [row.to_dict() for _, row in df_old_games.iterrows() if (row['Season'], str(row['Week']), str(row['Day']), int(row['Match'])) not in scraped_valid]
        
        if preserved_rows:
            df_preserved = pd.DataFrame(preserved_rows)
            df_merged = df_merged[~df_merged.apply(lambda r: pd.isna(r['Game']) and (r['Season'], str(r['Week']), str(r['Day']), int(r['Match'])) in set(df_preserved[['Season', 'Week', 'Day', 'Match']].itertuples(index=False, name=None)), axis=1)]
            df_cs = pd.concat([df_merged, df_preserved], ignore_index=True)
        else: df_cs = df_merged

        df_final = pd.concat([df_old[df_old['Season'] != SEASON_NAME], df_cs], ignore_index=True)
        
        df_final['Tgl_Sort'] = pd.to_datetime(df_final['Date'], format='mixed', errors='coerce')
        
        def sort_week(w):
            w = str(w).strip()
            if w.isdigit(): return int(w)
            return {'Pl': 100, 'Up': 101, 'Lw': 102, 'Gr': 103}.get(w, 999)
            
        def sort_day(d):
            d = str(d).strip()
            if d.isdigit(): return int(d)
            return {'St': 10, 'Sf': 11, 'Fl': 12}.get(d, 99)
            
        df_final['_w_sort'] = df_final['Week'].apply(sort_week)
        df_final['_d_sort'] = df_final['Day'].apply(sort_day)
        
        df_final.sort_values(by=['Tgl_Sort', '_w_sort', '_d_sort', 'Match', 'Game'], inplace=True, na_position='first')
        df_final.drop_duplicates(subset=['Season', 'Week', 'Day', 'Match', 'Game'], keep='first', inplace=True)

        final_cols = ['Season', 'Date', 'Time', 'Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)', 'T_Rank', 'O_Rank', 'Result', 'MVP', 'Duration_min', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective', 'Heroes_Picked', 'Bans_Blue', 'Opponent_Picked', 'Bans_Red']
        df_final[[c for c in final_cols if c in df_final.columns]].to_csv(csv_path, index=False)
        print(f"📊 Selesai! Data CSV telah diperbarui (Total: {len(df_final)} baris).")