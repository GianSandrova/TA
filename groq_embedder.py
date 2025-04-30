# embedder.py
from neo4j_graphrag.embeddings.base import Embedder as BaseEmbedder
from sentence_transformers import SentenceTransformer
import torch

class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name="Alibaba-NLP/gte-Qwen2-7B-instruct"):
        # Memory optimization settings
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the model with 8-bit quantization
        model_kwargs = {
            'device_map': 'auto',  # Automatically manage device placement
            'torch_dtype': torch.float16,  # Use half precision
            'load_in_8bit': True,  # Use 8-bit quantization instead of 4-bit
        }
        
        self.model = SentenceTransformer(model_name, **model_kwargs)
        self.max_tokens = 8192
        self.chunk_overlap = 128
        # Clear CUDA cache after model loading
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def embed_text(self, text: str):
        with torch.inference_mode():
            embeddings = self.model.encode(text)
        return embeddings.tolist()

    def embed_query(self, query: str):
        return self.embed_text(query)

Embedder = SentenceTransformerEmbedder()