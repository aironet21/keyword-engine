import requests
import json
import os
import time
import random
from datetime import datetime

# Ambil API Key dari GitHub Secrets
AI_API_KEY = os.getenv("GEMINI_API_KEY")

# Daftar Akun dan Niche (Bisa ditambah sesuka hati)
ACCOUNTS = [
    {"id": "user_tekno", "niche": "teknologi gadget, AI terbaru, dan software"},
    {"id": "user_finance", "niche": "investasi saham, crypto, dan keuangan pribadi"}
]

def get_ai_topics(niche):
    """Meminta AI generate 15 topik unik setiap hari"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    
    # Menambahkan random integer agar AI tidak memberi jawaban cache yang sama
    seed = random.randint(1, 9999)
    prompt = f"Berikan 15 topik pencarian singkat yang sangat spesifik dan tren hari ini tentang {niche}. Berikan hasil dalam daftar kata saja dipisahkan koma. Unique ID: {seed}"
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return [t.strip() for t in text.split(",")]
    except Exception as e:
        print(f"AI Error: {e}")
        return []

def get_suggestions(query):
    """Scraping Google Autocomplete secara aman"""
    url = f"http://google.com/complete/search?client=chrome&q={query}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()[1]
    except:
        pass
    return []

def main():
    if not os.path.exists('data'):
        os.makedirs('data')

    for acc in ACCOUNTS:
        print(f"--- Memproses Akun: {acc['id']} ---")
        final_keywords = set()
        
        # 1. Dapatkan ide topik dari AI
        main_topics = get_ai_topics(acc['niche'])
        print(f"AI menghasilkan {len(main_topics)} topik utama.")
        
        for topic in main_topics:
            if len(final_keywords) >= 60: break
            
            # 2. Cari cabang topik di Google
            level1 = get_suggestions(topic)
            time.sleep(0.3) # Anti-block
            
            for sub in level1[:5]: # Ambil 5 cabang
                if len(final_keywords) >= 60: break
                
                # 3. Cari detail keyword (berantai)
                level2 = get_suggestions(sub)
                for leaf in level2[:3]: # Ambil 3 detail
                    if len(final_keywords) >= 60: break
                    final_keywords.add(leaf)
                
                time.sleep(0.2)

        # Simpan ke JSON
        result = {
            "account_id": acc['id'],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(final_keywords),
            "keywords": sorted(list(final_keywords))
        }

        file_path = f"data/{acc['id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"Berhasil menyimpan {len(final_keywords)} keyword ke {file_path}")

if __name__ == "__main__":
    main()
