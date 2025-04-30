from neo4j_graphrag.embeddings.base import Embedder as BaseEmbedder
from llama_cpp import Llama

class LlamaEmbedder(BaseEmbedder):
    def __init__(self, model_path="/home/kota410/chatbot-deploy/TA/gte-qwen-gguf/gte-Qwen2-7B-instruct-Q8_0.gguf"):
        self.model = Llama(
            model_path=model_path,
            embedding=True,  # Enable embedding mode
            n_ctx=8192      # Context size
        )
        self.max_tokens = 8192
        self.chunk_overlap = 128

    def embed_text(self, text: str):
        embedding = self.model.embed(text)
        return embedding.tolist()  # Convert to list for compatibility

    def embed_query(self, query: str):
        return self.embed_text(query)

Embedder = LlamaEmbedder()