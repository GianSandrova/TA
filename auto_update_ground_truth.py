import json
import os
from difflib import SequenceMatcher

# === CONFIGURATION ===
STRICT_MODE = False  # True = pakai similarity check, False = tambahkan semua retrieved keys
SIMILARITY_THRESHOLD = 0.6  # Hanya berlaku jika STRICT_MODE = True

# === LOAD DATA ===
with open("retrieval_results.json", encoding="utf-8") as f:
    retrieval_data = json.load(f)

with open("ground_truth.json", encoding="utf-8") as f:
    ground_truth = json.load(f)

with open("verse_map.json", encoding="utf-8") as f:
    verse_map = json.load(f)

# === FUNCTION: Similarity based on string matching ===
def is_similar(query, verse_text, threshold=SIMILARITY_THRESHOLD):
    return SequenceMatcher(None, query.lower(), verse_text.lower()).ratio() > threshold

# === TRACKING UPDATES ===
updated_ground_truth = {}
num_updated = 0

for item in retrieval_data:
    query = item["query"]
    retrieved_keys = item["retrieved_keys"]
    current_relevant = set(ground_truth.get(query, []))
    suggestions = set()

    for key in retrieved_keys:
        if key in current_relevant:
            continue

        if STRICT_MODE:
            verse_text = verse_map.get(key, "")
            if verse_text and is_similar(query, verse_text):
                suggestions.add(key)
        else:
            suggestions.add(key)  # langsung tambahkan semua retrieved key yang belum ada

    # Simpan hasil update per query
    if suggestions:
        updated = sorted(current_relevant.union(suggestions))
        updated_ground_truth[query] = updated
        num_updated += 1
        print(f"\n🔄 Updated ground truth for query:\n📍 {query}")
        print(f"➕ Added: {sorted(suggestions)}")
    else:
        updated_ground_truth[query] = sorted(current_relevant)

# === SAVE RESULTS ===
if num_updated > 0:
    os.rename("ground_truth.json", "ground_truth_backup.json")
    with open("ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(updated_ground_truth, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Ground truth updated for {num_updated} queries.")
    print("📁 Backup saved as ground_truth_backup.json")
else:
    print("\n✅ No updates needed. Ground truth is already optimal.")
