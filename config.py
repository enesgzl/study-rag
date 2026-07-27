"""
Proje genelinde kullanılan ayarlar.
Modelleri Ollama'dan çekmeyi unutma:
    ollama pull qwen2.5:7b
    ollama pull nomic-embed-text
"""

import os

# --- Ollama ayarları ---
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:3b"          # Cevap/özet üretimi için. Daha hızlı istersen "qwen2.5:3b" dene.
EMBEDDING_MODEL = "nomic-embed-text"  # Embedding için

# --- Chunking ayarları ---
CHUNK_SIZE = 1000        # karakter bazlı chunk boyutu
CHUNK_OVERLAP = 150       # chunk'lar arası örtüşme (bağlamı korumak için)

# --- Retrieval ayarları ---
TOP_K = 4                # her sorguda getirilecek chunk sayısı

# --- Klasörler ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "data", "pdfs")
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)