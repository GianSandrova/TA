# insert_data.py

import json
import numpy as np
from uuid import uuid4
from tqdm import tqdm
from config import driver, DIMENSION
from groq_embedder import Embedder
from utils import chunk_text


def embed_chunk(text):
    vector = Embedder.embed_text(text)
    if not isinstance(vector, list) or len(vector) != DIMENSION:
        raise ValueError("❌ Invalid embedding vector")
    return vector


def extract_ayah_number(ayah_key: str) -> int:
    """Ekstrak angka dari key seperti 'Ayat 1'."""
    try:
        return int(''.join(filter(str.isdigit, ayah_key)))
    except Exception:
        raise ValueError(f"❌ Gagal parsing ayat: {ayah_key}")


def insert_quran_chunks():
    with open("quran.json", "r", encoding="utf-8") as file:
        quran_data = json.load(file)

    try:
        with driver.session() as session:
            # Hapus semua data sebelumnya
            session.run("MATCH (n) DETACH DELETE n")
            session.run("CREATE (:Quran {name: 'Al-Quran'})")

            total_ayat = sum(len(surah["text"]) for surah in quran_data)
            progress = tqdm(total=total_ayat, desc="Memproses Ayat")

            for surah in quran_data:
                surah_id = int(surah["number"])
                surah_name = surah["name"]
                surah_name_latin = surah["name_latin"]
                number_of_ayah = int(surah["number_of_ayah"])

                # Simpan node Surah
                session.run(
                    """
                    MATCH (q:Quran {name: 'Al-Quran'})
                    CREATE (s:Surah {
                        number: $number,
                        name: $name,
                        name_latin: $name_latin,
                        number_of_ayah: $number_of_ayah
                    })
                    CREATE (q)-[:HAS_SURAH]->(s)
                    """,
                    {
                        "number": surah_id,
                        "name": surah_name,
                        "name_latin": surah_name_latin,
                        "number_of_ayah": number_of_ayah
                    }
                )

                for ayah_key, ayah_text in surah["text"].items():
                    try:
                        ayah_num = extract_ayah_number(ayah_key)
                    except ValueError as e:
                        print(str(e))
                        continue

                    translation = surah.get("translations", {}).get("id", {}).get("text", {}).get(ayah_key, "")
                    tafsir = surah.get("tafsir", {}).get("id", {}).get("kemenag", {}).get("text", {}).get(ayah_key, "")

                    # Simpan node Ayat
                    session.run(
                        """
                        MATCH (s:Surah {number: $surah_number})
                        CREATE (a:Ayat {
                            number: $number,
                            text: $text,
                            translation: $translation,
                            tafsir: $tafsir
                        })
                        CREATE (s)-[:HAS_AYAT]->(a)
                        """,
                        {
                            "surah_number": surah_id,
                            "number": ayah_num,
                            "text": ayah_text,
                            "translation": translation,
                            "tafsir": tafsir
                        }
                    )

                    # Proses setiap sumber (teks asli, terjemahan, tafsir)
                    for source, content in {
                        "text": ayah_text,
                        "translation": translation,
                        "tafsir": tafsir
                    }.items():
                        if content.strip():
                            chunks = chunk_text(content)
                            for chunk in chunks:
                                prefixed_chunk = f"[{source} {surah_name_latin}:{ayah_num}] {chunk}"
                                embedding = embed_chunk(prefixed_chunk)
                                session.run(
                                    """
                                    MATCH (s:Surah {number: $surah_number})-[:HAS_AYAT]->(a:Ayat {number: $ayat_number})
                                    CREATE (c:Chunk {
                                        id: $id,
                                        text: $chunk_text,
                                        embedding: $embedding,
                                        source: $source,
                                        ayat_number: $ayat_number,
                                        surah_name: $surah_name,
                                        surah_number: $surah_number
                                    })
                                    CREATE (a)-[:HAS_CHUNK]->(c)
                                    """,
                                    {
                                        "id": str(uuid4()),
                                        "chunk_text": prefixed_chunk,
                                        "embedding": embedding,
                                        "source": source,
                                        "ayat_number": ayah_num,
                                        "surah_name": surah_name_latin,
                                        "surah_number": surah_id
                                    }
                                )


                    progress.update(1)

            progress.close()
            print("\n✅ Semua data Al-Quran dan chunk embedding berhasil dimasukkan ke Neo4j.")

    except Exception as e:
        print(f"❌ Error saat insert: {str(e)}")
    finally:
        driver.close()


if __name__ == "__main__":
    insert_quran_chunks()
