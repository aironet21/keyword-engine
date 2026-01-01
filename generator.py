import requests
import json
import os
import time
import random
from datetime import datetime

AI_API_KEY = os.getenv("GEMINI_API_KEY")

ACCOUNTS = [
    {"id": "user_tekno", "niche": "teknologi gadget dan AI"},
    {"id": "user_finance", "niche": "investasi dan crypto"}
]

def get_ai_topics(niche):
    # Jika API Key tidak ada, langsung gunakan fallback
    if not AI_API_KEY:
        return [niche]
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    prompt = f"Berikan 10 topik singkat tentang {niche} yang sedang tren. Hanya berikan kata kunci dipisahkan koma saja tanpa kalimat pembuka."
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        res_json = response.json()
        # Mengambil teks dengan lebih aman
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        topics = [t.strip() for t in text.split(",") if len(t.strip()) > 2]
        return topics if topics else [niche]
    except Exception as e:
        print(f"AI Error: {e}")
        return [niche] # Gunakan niche sebagai topik utama jika AI gagal

def get_suggestions(query):
    # Menggunakan User-Agent agar tidak dianggap bot oleh Google
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    url = f"http://google.com/complete/search?client=chrome&q={query}"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json()[1]
    except:
        pass
    return []

def main():
    if not os.path.exists('data'): os.makedirs('data')

    for acc in ACCOUNTS:
        final_keywords = set()
        topics = get_ai_topics(acc['niche'])
        
        # Tambahkan niche asli ke daftar topik untuk memastikan hasil tidak nol
        topics.append(acc['niche'])
        
        for t in topics:
            if len(final_keywords) >= 60: break
            
            # Ambil level 1
            suggs = get_suggestions(t)
            for s in suggs[:6]: # Perbanyak cabang di level 1
                final_keywords.add(s)
                
                # Ambil level 2 (Berantai)
                details = get_suggestions(s)
                for d in details[:3]:
                    final_keywords.add(d)
                    if len(final_keywords) >= 60: break
                
                time.sleep(0.2) 

        result = {
            "account_id": acc['id'],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(final_keywords),
            "keywords": sorted(list(final_keywords))[:60]
        }

        with open(f"data/{acc['id']}.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Selesai {acc['id']}: {len(final_keywords)} keywords.")

if __name__ == "__main__":
    main()
