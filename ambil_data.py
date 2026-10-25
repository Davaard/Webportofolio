import os, time, requests
from bs4 import BeautifulSoup

folder_simpan = "assets/logos"
os.makedirs(folder_simpan, exist_ok=True)

headers = {'User-Agent': 'IKL_Dashboard_App/1.0 (Kontak: daryadarendra@gmail.com)', 'Accept-Encoding': 'gzip'}
url_api = "https://liquipedia.net/honorofkings/api.php"
params = {"action": "parse", "page": "Indonesia_Kings_Laga/2026/Fall", "format": "json"}

print("Memburu Logo HD...")
response = requests.get(url_api, params=params, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.json()["parse"]["text"]["*"], 'html.parser')
    elemen_tim = soup.find_all('span', class_='team-template-team-standard')
    
    for elemen in elemen_tim:
        tag_teks = elemen.find('span', class_='team-template-text')
        tag_gambar = elemen.find('img')
        
        if tag_teks and tag_gambar and tag_gambar.has_attr('src'):
            nama_tim = tag_teks.text.strip().replace(" ", "_")
            url_logo = tag_gambar['src']
            
            # --- TRIK RAHASIA MEMAKSA RESOLUSI HD ---
            if '/thumb/' in url_logo:
                url_logo = url_logo.replace('/thumb/', '/')
                url_logo = url_logo.rsplit('/', 1)[0]
            # ----------------------------------------
            
            if url_logo.startswith('//'): url_logo = 'https:' + url_logo
            elif url_logo.startswith('/'): url_logo = 'https://liquipedia.net' + url_logo
            
            path_file = os.path.join(folder_simpan, f"{nama_tim}.png")
            
            if not os.path.exists(path_file):
                print(f"⬇️ Mengunduh HD: {nama_tim}")
                try:
                    res = requests.get(url_logo, headers=headers)
                    with open(path_file, 'wb') as f: f.write(res.content)
                    time.sleep(0.5)
                except: pass
    print("✅ Selesai! Cek folder logomu, sekarang pasti HD semua.")