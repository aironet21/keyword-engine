import requests
import json
import os
import time
from datetime import datetime

# Ambil Key dari sistem keamanan GitHub
AI_API_KEY = os.getenv("GEMINI_API_KEY")

# Konfigurasi Akun & Niche
ACCOUNTS = [
    {"id": "user_tekno", "niche": "teknologi gadget dan AI"},
    {"id": "user_finance", "niche": "investasi saham dan crypto"}
]

def get_ai_topics(niche):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    prompt = f"Berikan 10 topik pencarian singkat yang sedang tren tentang {niche}. Pisahkan dengan koma saja."
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return [t.strip() for t in response.json()['candidates'][0]['content']['parts'][0]['text'].split(",")]
    except:
        return []

def get_suggestions(query):
    url = f"http://google.com/complete/search?client=chrome&q={query}"
    try:
        return requests.get(url).json()[1]
    except:
        return []

def main():
    if not os.path.exists('data'): os.makedirs('data')

    for acc in ACCOUNTS:
        final_keywords = []
        topics = get_ai_topics(acc['niche'])
        
        for t in topics:
            subs = get_suggestions(t)[:5]
            for s in subs:
                leafs = get_suggestions(s)[:3]
                final_keywords.extend(leafs)
                if len(final_keywords) >= 60: break
            if len(final_keywords) >= 60: break

        output = {
            "account_id": acc['id'],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "keywords": list(set(final_keywords[:60])) # Hapus duplikat
        }

        with open(f"data/{acc['id']}.json", 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
