import requests
import json
import os
import time
from datetime import datetime

AI_API_KEY = os.getenv("GEMINI_API_KEY")

ACCOUNTS = [
    {"id": "user_tekno", "niche": "teknologi gadget, AI terbaru, dan software"},
    {"id": "user_finance", "niche": "investasi saham, crypto, dan keuangan pribadi"}
]

def get_ai_topics(niche):
    """Meminta AI generate 15 topik luas agar variasi banyak"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    # Prompt diperkuat untuk meminta lebih banyak variasi
    prompt = f"Berikan 15 topik berbeda yang sedang hangat tentang {niche}. Berikan dalam bentuk daftar kata saja dipisahkan koma, tanpa penjelasan."
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        return [t.strip() for t in text.split(",")]
    except Exception as e:
        print(f"AI Error: {e}")
        return []

def get_suggestions(query):
    """Scraping Google Autocomplete"""
    url = f"http://google.com/complete/search?client=chrome&q={query}"
    try:
        r = requests.get(url, timeout=5)
        return r.json()[1]
    except:
        return []

def main():
    if not os.path.exists('data'): os.makedirs('data')

    for acc in ACCOUNTS:
        print(f"Memproses {acc['id']}...")
        final_keywords = set() # Menggunakan set agar tidak ada keyword ganda
        
        # 1. AI Generate Topik Utama
        main_topics = get_ai_topics(acc['niche'])
        
        for topic in main_topics:
            if len(final_keywords) >= 60: break
            
            # 2. Level 1: Cari saran dari topik utama
            level1 = get_suggestions(topic)
            for sub in level1[:4]: # Ambil 4 cabang per topik
                if len(final_keywords) >= 60: break
                
                # 3. Level 2: Cari saran detail (berantai)
                level2 = get_suggestions(sub)
                for leaf in level2[:3]: # Ambil 3 detail per cabang
                    final_keywords.add(leaf)
                    if len(final_keywords) >= 60: break
                
                time.sleep(0.1) # Delay singkat agar tidak diblokir Google

        output = {
            "account_id": acc['id'],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total": len(final_keywords),
            "keywords": sorted(list(final_keywords))
        }

        with open(f"data/{acc['id']}.json", 'w') as f:
            json.dump(output, f, indent=2)
            
        print(f"Berhasil mengumpulkan {len(final_keywords)} keyword untuk {acc['id']}")

if __name__ == "__main__":
    main()
