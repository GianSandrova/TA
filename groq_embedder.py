# embedder.py
from neo4j_graphrag.embeddings.base import Embedder as BaseEmbedder
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name="intfloat/multilingual-e5-large-instruct"):
        self.model = SentenceTransformer(model_name)
        self.max_tokens = 514
        self.chunk_overlap = 50

    def embed_text(self, text: str):
        return self.model.encode(text).tolist()

    def embed_query(self, query: str):
        return self.embed_text(query)

Embedder = SentenceTransformerEmbedder()
