# groq_llm.py
import requests
import time
import random
from config import GROQ_API_KEY, GROQ_MODEL

def detect_semantic_breaks(sentences, max_retries=5):
    prompt = f"""
    Berikut adalah daftar kalimat dari sebuah tafsir. Tandai kalimat keberapa yang merupakan akhir dari satu unit makna/penjelasan. Kembalikan hanya daftar angka.

    Kalimat-kalimat:
    {chr(10).join([f"{i+1}. {s}" for i, s in enumerate(sentences)])}

    Contoh output:
    [2, 5, 9]

    Jawaban:
    """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 429:
                wait_time = 60 + random.randint(5, 15)
                print(f"⏳ Rate limit tercapai (429), menunggu {wait_time} detik... [Percobaan ke-{attempt+1}]")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Ekstrak angka dari respons LLM
            try:
                breaks = [int(num.strip()) for num in content.split('\n') if num.strip().isdigit()]
                return breaks
            except Exception as e:
                print("❌ Gagal parse response LLM:", content)
                return []
        except requests.RequestException as e:
            print(f"❌ Error saat akses Groq API: {str(e)}")
            time.sleep(5 + attempt * 2)

    print("❌ Gagal mendapatkan respons setelah beberapa kali percobaan.")
    return []
