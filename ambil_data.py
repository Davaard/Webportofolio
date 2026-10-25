import os
import time
import requests
from bs4 import BeautifulSoup

folder_simpan = "assets/heroes"
os.makedirs(folder_simpan, exist_ok=True)

headers = {
    'User-Agent': 'IKL_Dashboard_App/1.0 (Kontak: daryadarendra@gmail.com)',
    'Accept-Encoding': 'gzip'
}

url_api = "https://liquipedia.net/honorofkings/api.php"
params = {
    "action": "parse",
    "page": "Indonesia_Kings_Laga/2026/Fall/Statistics", 
    "format": "json"
}

print("Membidik halaman Statistik IKL untuk sinkronisasi nama hero (Resolusi Tinggi)...")
response = requests.get(url_api, params=params, headers=headers)

if response.status_code == 200:
    data_json = response.json()
    
    if "parse" in data_json:
        html_content = data_json["parse"]["text"]["*"]
        soup = BeautifulSoup(html_content, 'html.parser')
        
        elemen_gambar = soup.find_all('img')
        
        ditemukan_baru = 0
        dilewati = 0
        
        for img in elemen_gambar:
            if img.has_attr('src') and ('Square' in img['src'] or 'Icon' in img['src']):
                parent_a = img.find_parent('a')
                if parent_a and parent_a.has_attr('title'):
                    nama_hero = parent_a['title']
                else:
                    nama_hero = img.get('alt', 'Unknown')
                    
                nama_hero = nama_hero.replace(" ", "_").replace("Square", "").replace(".png", "")
                
                if "logo" in img['src'].lower() or "esports" in nama_hero.lower():
                    continue
                    
                url_gambar = img['src']
                
                # --- TRIK MENGUBAH THUMBNAIL JADI GAMBAR HD ---
                if '/thumb/' in url_gambar:
                    # Hapus kata '/thumb/'
                    url_gambar = url_gambar.replace('/thumb/', '/')
                    # Potong bagian akhir URL yang menentukan ukuran (misal: /50px-Ata.png)
                    url_gambar = url_gambar.rsplit('/', 1)[0]
                # -----------------------------------------------

                if url_gambar.startswith('//'):
                    url_gambar = 'https:' + url_gambar
                elif url_gambar.startswith('/'):
                    url_gambar = 'https://liquipedia.net' + url_gambar
                    
                path_file = os.path.join(folder_simpan, f"{nama_hero}.png")
                
                if os.path.exists(path_file):
                    dilewati += 1
                else:
                    print(f"⬇️ Mengunduh Hero HD: {nama_hero}")
                    try:
                        res = requests.get(url_gambar, headers=headers)
                        if res.status_code == 200:
                            with open(path_file, 'wb') as f:
                                f.write(res.content)
                            time.sleep(0.5) 
                            ditemukan_baru += 1
                    except Exception as e:
                        print(f"Error pada {nama_hero}: {e}")
                        
        print(f"\n✅ Operasi Selesai!")
        print(f"   - Hero HD baru diunduh : {ditemukan_baru}")
        print(f"   - Hero dilewati        : {dilewati}")
    else:
        print("Halaman 'Statistics' tidak ditemukan.")
else:
    print(f"Gagal akses API! Status Code: {response.status_code}")