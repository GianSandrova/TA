import json

with open("quran.json", encoding="utf-8") as f:
    quran_data = json.load(f)

verse_map = {}

for surah in quran_data:
    surah_name = surah["name_latin"].lower().replace("'", "").replace(" ", "-")
    for ayah_number, tafsir_text in surah["tafsir"]["id"]["kemenag"]["text"].items():
        key = f"{surah_name}:{ayah_number}"
        verse_map[key] = tafsir_text.strip()

with open("verse_map.json", "w", encoding="utf-8") as f:
    json.dump(verse_map, f, indent=2, ensure_ascii=False)

print("✅ verse_map.json berhasil dibuat.")
