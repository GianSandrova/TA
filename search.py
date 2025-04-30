# search.py

import json
import traceback
import requests
import re
from config import driver, INDEX_NAME, GROQ_API_KEY, GROQ_MODEL
from groq_embedder import Embedder


def vector_search_chunks(query_text, top_k=20, min_score=0.6):
    try:
        vector = Embedder.embed_text(query_text)

        result = driver.execute_query(
            """
            CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $query_vector)
            YIELD node, score
            RETURN node.text AS chunk_text,
                   node.source AS source,
                   node.ayat_number AS ayat_number,
                   node.surah_name AS surah,
                   score
            ORDER BY score DESC
            """,
            {"query_vector": vector, "top_k": top_k}
        )

        records = result.records if result.records else []
        filtered = [r for r in records if r["score"] >= min_score]

        return filtered

    except Exception as e:
        print(f"❌ Vector search chunk error: {traceback.format_exc()}")
        return []


def extract_surah_ayah_from_query(query_text):
    """Coba ekstrak surah dan ayat dari pertanyaan seperti: 'apa arti surat Al-Lahab ayat 2'."""
    match = re.search(r'surat\s+([a-zA-Z\-]+)\s+ayat\s+(\d+)', query_text.lower())
    if match:
        surah = match.group(1).replace('-', ' ').title()
        ayat = int(match.group(2))
        return surah, ayat
    return None, None


def build_chunk_context(records):
    context = ""
    for r in records:
        context += f"""
📖 Surah: {r.get('surah')}
Ayat {r.get('ayat_number')} | Sumber: {r.get('source')}
➷ "{r.get('chunk_text')}"
"""
    return context


def call_groq_api(prompt, api_key, model):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"❌ Groq API error: {str(e)}")
        return "⚠️ Gagal mendapatkan respons dari AI."


def process_query(query_text):
    print(f"\n💬 Query: '{query_text}'")
    records = vector_search_chunks(query_text, top_k=20, min_score=0.6)

    # Coba deteksi permintaan spesifik surah dan ayat
    surah, ayat = extract_surah_ayah_from_query(query_text)
    if surah and ayat:
        records = [r for r in records if r["surah"].lower() == surah.lower() and r["ayat_number"] == ayat]
        print(f"🔍 Filter: Hanya ambil chunk dari Surah '{surah}' Ayat {ayat}.")

    if not records:
        return "❌ Maaf, saya tidak menemukan potongan yang relevan untuk menjawab pertanyaan ini."

    context = build_chunk_context(records)
    prompt = f"""
**Instruksi Sistem**
Berikan penjelasan tafsir berdasarkan potongan konten berikut:

{context}

**Pertanyaan**:
{query_text}

Jika potongan konten tidak relevan dengan pertanyaan, mohon jawab bahwa Anda tidak dapat menjawab.
"""
    return call_groq_api(prompt, GROQ_API_KEY, GROQ_MODEL)


def main():
    print("💡 Tafsir Al-Qur'an - Pencarian Berdasarkan Chunk")
    while True:
        query = input("\n📅 Masukkan pertanyaan: ").strip()
        if query.lower() in ["exit", "keluar"]:
            break
        if query:
            answer = process_query(query)
            print("\n🧐 Jawaban:")
            print(answer)


if __name__ == "__main__":
    main()
