import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime

# ==========================================
# 1. KONFIGURASI & KAMUS PEMETAAN
# ==========================================
SEASON_NAME = "Fall 2026"
HEADERS = {
    'User-Agent': 'IKL_Hub_Master_Bot/2.0 (Contact: daryadarendra@gmail.com)',
    'Accept-Encoding': 'gzip'
}
URL_API = "https://liquipedia.net/honorofkings/api.php"

TEAM_MAP = {
    "Rex Regum Qeon": "RRQ",
    "Deuscard x Sriwijaya Esports": "DESJ",
    "Deuscard x Sriwijaya": "DESJ",
    "ONIC": "ONIC",
    "Carstensz DuskMaven": "CARS",
    "OG Esports": "OG",
    "Bigetron by Vitality": "BTR",
    "Alter Ego Esports": "AE",
    "Mahadewa Vesakha": "MAVE",
    "Vesakha Esports": "MAVE",
    "Kagendra": "KAGE",
    "DOMINATOR by NEMESIS": "DMT",
    "DMT by NMSS": "DMT",
    "TBD": np.nan
}

HERO_MAP = {
    "Ao'yin": "Loong",
    "Garuda Khageswara": "Garuda"
}

def clean_team(name):
    if not name:
        return np.nan
    name = name.replace(" (page does not exist)", "").strip()
    return TEAM_MAP.get(name, name)

def clean_hero(name):
    name = name.replace(" (page does not exist)", "").strip()
    return HERO_MAP.get(name, name)

def fetch_api_soup(page_title):
    params = {"action": "parse", "page": page_title, "format": "json", "disabletoc": 1}
    print(f"📡 Menarik API Liquipedia: {page_title}...")
    try:
        res = requests.get(URL_API, params=params, headers=HEADERS, timeout=15)
        if res.status_code == 200 and "parse" in res.json():
            time.sleep(2)  # Jeda aman anti-block
            return BeautifulSoup(res.json()["parse"]["text"]["*"], 'html.parser')
    except Exception as e:
        print(f"❌ Gagal koneksi ke {page_title}: {e}")
    return None

def parse_datetime(timer_tag):
    """Mengekstrak Tanggal (M/D/YYYY) dan Jam (HH:MM) dari tag timer Liquipedia"""
    if not timer_tag or not timer_tag.text.strip():
        return "", ""
    raw_text = timer_tag.text.strip()
    for tz in ["WIB", "UTC", "ICT", "SGT"]:
        raw_text = raw_text.replace(tz, "").strip()
    
    parts = [p.strip() for p in raw_text.split('-')]
    date_part = parts[0]
    time_part = parts[1] if len(parts) > 1 else ""

    date_str = date_part
    for fmt in ["%B %d, %Y", "%b %d, %Y", "%B %d"]:
        try:
            dt = datetime.strptime(date_part, fmt)
            year = dt.year if fmt != "%B %d" else 2026
            date_str = f"{dt.month}/{dt.day}/{year}"
            break
        except:
            continue
    return date_str, time_part

# ==========================================
# 2. EKSTRAKTOR POPUP (BERLAKU UNTUK REG & PLAYOFFS)
# ==========================================
def extract_popup_data(popup, week_code, day_code, match_num):
    rows = []
    timer = popup.find('span', class_='timer-object')
    date_str, time_str = parse_datetime(timer)

    left_tag = popup.find('div', class_='match-info-header-opponent-left')
    right_tags = popup.find_all('div', class_='match-info-header-opponent')
    right_tag = right_tags[-1] if right_tags else None

    left_team = clean_team(left_tag.find('span', class_='name').text) if left_tag and left_tag.find('span', class_='name') else np.nan
    right_team = clean_team(right_tag.find('span', class_='name').text) if right_tag and right_tag.find('span', class_='name') else np.nan

    mvp_tag = popup.find('div', class_='brkts-popup-mvp')
    mvp_list = [a.text.strip() for a in mvp_tag.find_all('a')] if mvp_tag else []

    bans_per_round = []
    veto = popup.find('div', class_='brkts-popup-veto')
    if veto:
        for v_row in veto.find_all('div', class_='brkts-popup-veto-row'):
            b_cols = v_row.find_all('div', class_='brkts-popup-body-element-thumbs')
            if len(b_cols) >= 2:
                b_left = [clean_hero(a['title']) for a in b_cols[0].find_all('a', title=True)]
                b_right = [clean_hero(a['title']) for a in b_cols[1].find_all('a', title=True)]
                bans_per_round.append({'left': b_left, 'right': b_right})

    games = popup.find_all('div', class_='brkts-popup-body-grid-row')
    valid_games_extracted = 0

    for g_idx, game in enumerate(games):
        cols = game.find_all('div', class_='brkts-popup-spaced')
        labels = game.find_all('div', class_='generic-label')

        if len(cols) >= 3:
            durasi = cols[1].text.strip()
            if "Game" in durasi or ":" not in durasi:
                continue  # Lewati jika game belum punya durasi valid

            picks_left = [clean_hero(a['title']) for a in cols[0].find_all('a', title=True)]
            picks_right = [clean_hero(a['title']) for a in cols[2].find_all('a', title=True)]

            if not picks_left or not picks_right:
                continue

            valid_games_extracted += 1
            left_win = 1.0 if len(labels) > 0 and 'result-win' in labels[0].get('data-label-type', '') else 0.0
            b_left = bans_per_round[g_idx]['left'] if g_idx < len(bans_per_round) else []
            b_right = bans_per_round[g_idx]['right'] if g_idx < len(bans_per_round) else []
            mvp = mvp_list[g_idx] if g_idx < len(mvp_list) else np.nan

            # Cek posisi sebenarnya: Blue Side vs Red Side
            left_is_blue = cols[0].find('div', class_='brkts-popup-side-color--blue') is not None

            if left_is_blue:
                t_blue, o_red = left_team, right_team
                res_blue = left_win
                h_blue, h_red = picks_left, picks_right
                ban_blue, ban_red = b_left, b_right
            else:
                t_blue, o_red = right_team, left_team
                res_blue = 1.0 - left_win
                h_blue, h_red = picks_right, picks_left
                ban_blue, ban_red = b_right, b_left

            rows.append({
                'Season': SEASON_NAME,
                'Date': date_str,
                'Time': time_str,
                'Week': str(week_code),
                'Day': str(day_code),
                'Match': int(match_num),
                'Game': float(g_idx + 1),
                'Team_(Blue)': t_blue,
                'Opponent_(Red)': o_red,
                'T_Rank': np.nan, 'O_Rank': np.nan,
                'Result': res_blue,
                'Duration_min': durasi,
                'T_Gold': np.nan, 'O_Gold': np.nan,
                'T_Kill': np.nan, 'O_Kill': np.nan,
                'T_Assist': np.nan, 'O_Assist': np.nan,
                'T_Objective': np.nan, 'O_Objective': np.nan,
                'Heroes_Picked': ','.join(h_blue),
                'Opponent_Picked': ','.join(h_red),
                'Bans_Blue': ','.join(ban_blue) if ban_blue else np.nan,
                'Bans_Red': ','.join(ban_red) if ban_red else np.nan,
                'MVP': mvp
            })

    # JIKA BELUM ADA GAME DIMAINKAN -> Simpan sebagai 1 baris UPCOMING MATCH
    if valid_games_extracted == 0:
        rows.append({
            'Season': SEASON_NAME,
            'Date': date_str,
            'Time': time_str,
            'Week': str(week_code),
            'Day': str(day_code),
            'Match': int(match_num),
            'Game': np.nan,
            'Team_(Blue)': left_team,
            'Opponent_(Red)': right_team,
            'T_Rank': np.nan, 'O_Rank': np.nan,
            'Result': np.nan,
            'Duration_min': np.nan,
            'T_Gold': np.nan, 'O_Gold': np.nan,
            'T_Kill': np.nan, 'O_Kill': np.nan,
            'T_Assist': np.nan, 'O_Assist': np.nan,
            'T_Objective': np.nan, 'O_Objective': np.nan,
            'Heroes_Picked': np.nan,
            'Opponent_Picked': np.nan,
            'Bans_Blue': np.nan,
            'Bans_Red': np.nan,
            'MVP': np.nan
        })

    return rows

# ==========================================
# 3. PARSER REGULAR SEASON & PLAYOFFS
# ==========================================
def parse_regular_season(soup):
    all_rows = []
    if not soup:
        return all_rows

    matchlists = soup.find_all('div', class_='brkts-matchlist')
    for w_idx, mlist in enumerate(matchlists):
        week_num = w_idx + 1
        collapse_area = mlist.find('div', class_='brkts-matchlist-collapse-area')
        if not collapse_area:
            continue

        day_num = 0
        match_in_day = 0
        for child in collapse_area.children:
            if not getattr(child, 'name', None):
                continue
            classes = child.get('class', [])
            if 'brkts-matchlist-header' in classes:
                day_num += 1
                match_in_day = 0
            elif 'brkts-matchlist-match' in classes:
                match_in_day += 1
                popup = child.find('div', class_='brkts-match-info-popup')
                if popup:
                    all_rows.extend(extract_popup_data(popup, week_num, day_num, match_in_day))
    return all_rows

def parse_playoffs(soup):
    all_rows = []
    if not soup:
        return all_rows

    # Urutan 8 kotak bracket di halaman Playoffs IKL Fall 2026 sesuai kode di CSV-mu
    playoff_map = [
        ('Pl', 'St', 1),  # Play-In Match 1 (KAGE vs MAVE)
        ('Up', 'Sf', 1),  # Upper Semifinal 1 (BTR vs TBD)
        ('Pl', 'St', 2),  # Play-In Match 2 (DMT vs OG)
        ('Up', 'Sf', 2),  # Upper Semifinal 2 (RRQ vs TBD)
        ('Up', 'Fl', 0),  # Upper Bracket Final
        ('Lw', 'Sf', 0),  # Lower Bracket Semifinal
        ('Lw', 'Fl', 0),  # Lower Bracket Final
        ('Gr', 'Fl', 0),  # Grand Final
    ]

    popups = soup.find_all('div', class_='brkts-match-info-popup')
    for idx, popup in enumerate(popups):
        if idx < len(playoff_map):
            w_code, d_code, m_num = playoff_map[idx]
        else:
            w_code, d_code, m_num = ('Pl', 'Ex', idx + 1)
        all_rows.extend(extract_popup_data(popup, w_code, d_code, m_num))
    return all_rows

# ==========================================
# 4. PARSER ROSTER MULTI-SEASON (DENGAN STATUS FORMER)
# ==========================================
def parse_rosters(soup):
    rosters = []
    if not soup:
        return rosters

    tab_status_map = {"1": "Main", "2": "Subs", "3": "Former/Staff", "4": "Staff"}

    for card in soup.find_all('div', class_='team-participant-card'):
        t_name_tag = card.find('span', class_='name')
        t_code = clean_team(t_name_tag.text) if t_name_tag else "UNK"

        # Ambil catatan transfer pemain (Notes)
        notes_list = [n.text.strip().replace('\n', ' ') for n in card.find_all('div', class_='team-participant-card__notification')]
        notes_str = " | ".join(notes_list) if notes_list else np.nan

        # Cek label tab (Main, Subs, Former, Staff)
        pill_map = {}
        for pill in card.find_all('div', class_='switch-pill-option'):
            btn_id = pill.get('data-toggle-area-btn')
            if btn_id:
                pill_map[btn_id] = pill.text.strip()

        for content_div in card.find_all('div', attrs={'data-toggle-area-content': True}):
            area_id = content_div.get('data-toggle-area-content')
            status_label = pill_map.get(area_id, tab_status_map.get(area_id, "Active"))

            for member in content_div.find_all('div', class_='team-participant-card__member'):
                p_name_tag = member.find('span', class_='name')
                if not p_name_tag:
                    continue
                p_name = p_name_tag.text.strip()
                p_title = p_name_tag.find('a')['title'].replace(" (page does not exist)", "") if p_name_tag.find('a') and p_name_tag.find('a').has_attr('title') else p_name

                flag_img = member.find('span', class_='flag').find('img') if member.find('span', class_='flag') else None
                country = flag_img['alt'] if flag_img and flag_img.has_attr('alt') else "Unknown"

                role_left = member.find('div', class_='team-participant-card__member-role-left')
                role_right = member.find('div', class_='team-participant-card__member-role-right')

                role = "Player"
                if role_left and role_left.find('img') and role_left.find('img').has_attr('title'):
                    role = role_left.find('img')['title']
                elif role_right:
                    role = role_right.text.strip()

                final_status = "Former" if (role_right and "Left" in role_right.text) else status_label

                rosters.append({
                    'Season': SEASON_NAME,
                    'Team': t_code,
                    'Player_ID': p_name,
                    'Player_Wiki_Title': p_title,
                    'Role': role,
                    'Status': final_status,
                    'Country': country,
                    'Team_Notes': notes_str
                })
    return rosters

# ==========================================
# 5. SMART SYNC KE CSV UTAMA
# ==========================================
if __name__ == "__main__":
    soup_ov = fetch_api_soup("Indonesia_Kings_Laga/2026/Fall")
    soup_reg = fetch_api_soup("Indonesia_Kings_Laga/2026/Fall/Regular_Season")
    soup_po = fetch_api_soup("Indonesia_Kings_Laga/2026/Fall/Playoffs")

    # 1. Sinkronisasi Roster Multi-Season
    roster_data = parse_rosters(soup_ov)
    if roster_data:
        df_roster_new = pd.DataFrame(roster_data)
        roster_path = "IKL_Rosters.csv"
        if os.path.exists(roster_path):
            df_roster_old = pd.read_csv(roster_path)
            df_roster_old = df_roster_old[df_roster_old['Season'] != SEASON_NAME]
            df_roster_final = pd.concat([df_roster_old, df_roster_new], ignore_index=True)
        else:
            df_roster_final = df_roster_new
        df_roster_final.to_csv(roster_path, index=False)
        print(f"✅ Roster Multi-Season diperbarui: '{roster_path}' ({len(df_roster_final)} pemain/staf)")

    # 2. Sinkronisasi Match (Regular + Playoffs + Upcoming) ke Data_Set_IKL_HOK.csv
    scraped_matches = parse_regular_season(soup_reg) + parse_playoffs(soup_po)
    df_scraped = pd.DataFrame(scraped_matches)

    csv_path = "Data_Set_IKL_HOK.csv"
    if os.path.exists(csv_path) and not df_scraped.empty:
        df_old = pd.read_csv(csv_path)
        df_old['Week'] = df_old['Week'].astype(str)
        df_old['Day'] = df_old['Day'].astype(str)

        if 'Season' not in df_old.columns:
            df_old['Season'] = SEASON_NAME

        # Kolom metrik manual/OCR yang wajib diselamatkan dari CSV lama
        metric_cols = ['T_Rank', 'O_Rank', 'T_Gold', 'O_Gold', 'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective']
        
        # Kunci pencocokan level Game
        game_key = ['Season', 'Week', 'Day', 'Match', 'Game']
        df_old_games = df_old[df_old['Game'].notna()].copy()

        # Gabungkan metrik Gold/Kill lama ke hasil scrape terbaru
        df_merged = pd.merge(
            df_scraped,
            df_old_games[game_key + metric_cols],
            on=game_key,
            how='left',
            suffixes=('', '_old')
        )
        for col in metric_cols:
            df_merged[col] = df_merged[f"{col}_old"].combine_first(df_merged[col])
            df_merged.drop(columns=[f"{col}_old"], inplace=True)

        # Pertahankan juga baris dariCSV lama (misal Match 39-44 yang di Liquipedia detailnya kosong, tapi di CSV-mu sudah lengkap)
        scraped_valid_matches = set(
            df_scraped[df_scraped['Game'].notna()][['Season', 'Week', 'Day', 'Match']].itertuples(index=False, name=None)
        )
        
        preserved_rows = []
        for _, row in df_old_games.iterrows():
            m_tuple = (row['Season'], str(row['Week']), str(row['Day']), int(row['Match']))
            if m_tuple not in scraped_valid_matches:
                preserved_rows.append(row.to_dict())

        if preserved_rows:
            df_preserved = pd.DataFrame(preserved_rows)
            # Hapus baris placeholder kosong dari df_merged untuk match yang sudah di-preserve dari CSV lama
            df_merged = df_merged[~df_merged.apply(lambda r: (r['Season'], str(r['Week']), str(r['Day']), int(r['Match'])) not in scraped_valid_matches and pd.isna(r['Game']) and (r['Season'], str(r['Week']), str(r['Day']), int(r['Match'])) in set(df_preserved[['Season', 'Week', 'Day', 'Match']].itertuples(index=False, name=None)), axis=1)]
            df_current_season = pd.concat([df_merged, df_preserved], ignore_index=True)
        else:
            df_current_season = df_merged

        # Urutkan agar Regular Season (1-4) di atas dan Playoffs (Pl, Up, Lw, Gr) di bawah
        week_order = {'1': 1, '2': 2, '3': 3, '4': 4, 'Pl': 5, 'Up': 6, 'Lw': 7, 'Gr': 8}
        df_current_season['_w_sort'] = df_current_season['Week'].map(lambda x: week_order.get(str(x), 99))
        df_current_season.sort_values(by=['_w_sort', 'Day', 'Match', 'Game'], inplace=True)
        df_current_season.drop(columns=['_w_sort'], inplace=True)

        # Pastikan 21 kolom asli tetap berada di urutan depan, diikuti kolom baru
        original_21_cols = [
            'Date', 'Week', 'Day', 'Match', 'Game', 'Team_(Blue)', 'Opponent_(Red)',
            'T_Rank', 'O_Rank', 'Result', 'Duration_min', 'T_Gold', 'O_Gold',
            'T_Kill', 'O_Kill', 'T_Assist', 'O_Assist', 'T_Objective', 'O_Objective',
            'Heroes_Picked', 'Opponent_Picked'
        ]
        extra_cols = ['Season', 'Time', 'Bans_Blue', 'Bans_Red', 'MVP']
        final_cols = original_21_cols + [c for c in extra_cols if c in df_current_season.columns]
        
        df_other_seasons = df_old[df_old['Season'] != SEASON_NAME]
        df_final = pd.concat([df_other_seasons, df_current_season], ignore_index=True)[final_cols]

        df_final.to_csv(csv_path, index=False)
        print(f"🎉 Sinkronisasi Selesai! '{csv_path}' kini memuat {len(df_final)} baris (Histori + Playoff + Upcoming)!")