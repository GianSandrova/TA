import json
from search import vector_search_chunks

TOP_K = 5
GROUND_TRUTH_PATH = "ground_truth.json"
OUTPUT_PATH = "retrieval_results.json"

def clean_key(surah, ayat):
    surah = str(surah).replace("’", "'").replace("‘", "'").replace(" ", "").lower()
    ayat = str(ayat).strip()
    return f"{surah}:{ayat}"

def main():
    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    retrieval_results = []

    for query in ground_truth:
        results = vector_search_chunks(query, top_k=TOP_K)
        retrieved_keys = [
            clean_key(r["surah"], r["ayat_number"]) for r in results
        ]

        retrieval_results.append({
            "query": query,
            "retrieved_keys": retrieved_keys
        })

        print(f"✅ Retrieved for: {query} → {retrieved_keys}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(retrieval_results, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Saved retrieval results to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
