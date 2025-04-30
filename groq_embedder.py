# embedder.py
from neo4j_graphrag.embeddings.base import Embedder as BaseEmbedder
from sentence_transformers import SentenceTransformer
import torch

class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model_name="Alibaba-NLP/gte-Qwen2-7B-instruct"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load tokenizer and model manually with quantization
        from transformers import AutoTokenizer, AutoModel
        from transformers import BitsAndBytesConfig

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        model = AutoModel.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            quantization_config=quantization_config
        )

        self.model = SentenceTransformer(modules=[tokenizer, model])
        self.max_tokens = 8192
        self.chunk_overlap = 128

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def embed_text(self, text: str):
        with torch.inference_mode():
            embeddings = self.model.encode(text)
        return embeddings.tolist()

    def embed_query(self, query: str):
        return self.embed_text(query)
