# search.py

import json
import traceback
import requests
import os
from config import driver, INDEX_NAME, GROQ_API_KEY, GROQ_MODEL
from groq_embedder import Embedder

def vector_search_chunks(query_text, top_k=5, min_score=0.6):
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

        # Filter by score threshold
        filtered = [r for r in records if r["score"] >= min_score]

        if not filtered:
            print("⚠️ Tidak ada chunk yang melewati ambang skor minimal.")
        else:
            print("📦 Chunk relevan ditemukan:")
            for r in filtered:
                print(f"- ({r['surah']}:{r['ayat_number']}) [{r['source']}] | score={r['score']:.4f}")

        return filtered

    except Exception as e:
        print(f"❌ Vector search chunk error: {traceback.format_exc()}")
        return []


def build_chunk_context(records):
    context = ""
    for r in records:
        context += f"""
📖 Surah: {r.get('surah')}
Ayat {r.get('ayat_number')} | Sumber: {r.get('source')}
➷ \"{r.get('chunk_text')}\"
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
    records = vector_search_chunks(query_text, top_k=10, min_score=0.6)

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
