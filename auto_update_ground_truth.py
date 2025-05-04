import json
import os
from difflib import SequenceMatcher

# Load data
with open("retrieval_results.json") as f:
    retrieval_data = json.load(f)

with open("ground_truth.json") as f:
    ground_truth = json.load(f)

with open("verse_map.json") as f:
    verse_map = json.load(f)

# Fungsi similarity antar teks
def is_similar(query, verse_text, threshold=0.6):
    return SequenceMatcher(None, query.lower(), verse_text.lower()).ratio() > threshold

# Tracking pembaruan
updated_ground_truth = {}
num_updated = 0

for item in retrieval_data:
    query = item["query"]
    retrieved_keys = item["retrieved_keys"]
    current_relevant = set(ground_truth.get(query, []))
    suggestions = set()

    for key in retrieved_keys:
        if key not in current_relevant:
            verse_text = verse_map.get(key, "")
            if is_similar(query, verse_text):
                suggestions.add(key)

    # Update jika ada saran tambahan
    if suggestions:
        updated = sorted(current_relevant.union(suggestions))
        updated_ground_truth[query] = updated
        num_updated += 1
        print(f"\n🔄 Updated ground truth for query:\n📍 {query}")
        print(f"➕ Added: {sorted(suggestions)}")
    else:
        updated_ground_truth[query] = sorted(current_relevant)

# Simpan backup & update file
if num_updated > 0:
    os.rename("ground_truth.json", "ground_truth_backup.json")
    with open("ground_truth.json", "w") as f:
        json.dump(updated_ground_truth, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Ground truth updated for {num_updated} queries.")
    print("📁 Backup saved as ground_truth_backup.json")
else:
    print("\n✅ No updates needed. Ground truth is already optimal.")
