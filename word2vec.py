from neo4j_graphrag.embeddings.base import Embedder as BaseEmbedder
import gensim.downloader as api
import numpy as np
import re

class FastTextEmbedder(BaseEmbedder):
    def __init__(self):
        super().__init__()  # Inisialisasi parent class
        # Memuat model fastText yang sudah dilatih (multilingual)
        self.model = api.load('fasttext-wiki-news-subwords-300')  # Gunakan fastText model yang multilingual
        self.avg_embedding = np.mean(self.model.vectors, axis=0)  # Hitung rata-rata embedding untuk kata yang tidak ada
    
    def embed_text(self, text):
        words = text.split()
        embeddings = []
        for word in words:
            try:
                embeddings.append(self.model[word])  # Ambil embedding untuk kata jika ada
            except KeyError:
                embeddings.append(self.avg_embedding)  # Gunakan vektor rata-rata jika kata tidak ada di model
        return np.mean(embeddings, axis=0).tolist()
    
    def embed_query(self, text):  # Implementasi wajib untuk embed_query
        return self.embed_text(text)
