# evaluate_retrieval.py

import json
from search import vector_search_chunks

TOP_K = 5
GROUND_TRUTH_PATH = "ground_truth.json"

def normalize_key(surah, ayat):
    return f"{surah}:{ayat}".replace(" ", "").lower()

def evaluate_query(query_text, relevant_set):
    retrieved = vector_search_chunks(query_text, top_k=TOP_K)
    retrieved_keys = [
        normalize_key(r['surah'], r['ayat_number']) for r in retrieved
    ]
    relevant_keys = set([k.lower() for k in relevant_set])

    # Precision@k
    relevant_retrieved = [rk for rk in retrieved_keys if rk in relevant_keys]
    precision = len(relevant_retrieved) / TOP_K if TOP_K else 0

    # Recall
    recall = len(relevant_retrieved) / len(relevant_keys) if relevant_keys else 0

    # MRR
    mrr = 0
    for i, rk in enumerate(retrieved_keys, start=1):
        if rk in relevant_keys:
            mrr = 1 / i
            break

    return precision, recall, mrr

def main():
    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    total_p, total_r, total_mrr = 0, 0, 0
    n = len(ground_truth)

    print("📊 Evaluasi Retrieval:")
    print("-" * 50)

    for query, relevant in ground_truth.items():
        print(f"\n💬 Query: {query}")
        p, r, mrr = evaluate_query(query, relevant)
        print(f"✅ Precision@{TOP_K}: {p:.4f}")
        print(f"✅ Recall@{TOP_K}: {r:.4f}")
        print(f"✅ MRR: {mrr:.4f}")

        total_p += p
        total_r += r
        total_mrr += mrr

    print("\n📈 Rata-rata Evaluasi:")
    print("-" * 50)
    print(f"📌 Mean Precision@{TOP_K}: {total_p / n:.4f}")
    print(f"📌 Mean Recall@{TOP_K}: {total_r / n:.4f}")
    print(f"📌 Mean MRR: {total_mrr / n:.4f}")

if __name__ == "__main__":
    main()
