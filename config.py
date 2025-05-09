from neo4j import GraphDatabase

# Konfigurasi Neo4j
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "12345678")

# Konfigurasi index embedding
INDEX_NAME = "ayat_embeddings"  # Nama indeks di Neo4j
DIMENSION = 3584  # Disesuaikan dengan model embedding yang digunakan
LABEL = "Tafsir"  # Label node di Neo4j
EMBEDDING_PROPERTY = "embedding"  # Properti yang menyimpan embedding

# Koneksi ke Neo4j
driver = GraphDatabase.driver(URI, auth=AUTH)

GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Pastikan model ini benar