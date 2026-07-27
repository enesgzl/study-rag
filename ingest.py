"""
PDF -> metin -> chunk -> embedding -> ChromaDB akışını yönetir.
Her PDF, dosya adına göre ayrı bir Chroma collection'ında tutulur,
böylece dersleri/konuları birbirine karıştırmadan yönetebilirsin.
"""

import os
import hashlib

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

import config


def _collection_name(pdf_path: str) -> str:
    """Dosya adından güvenli, benzersiz bir collection adı üretir."""
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    safe = "".join(c if c.isalnum() else "_" for c in base).lower()
    short_hash = hashlib.md5(pdf_path.encode()).hexdigest()[:6]
    return f"{safe}_{short_hash}"[:63]  # chroma collection adı sınırı


def get_embeddings():
    return OllamaEmbeddings(
        model=config.EMBEDDING_MODEL,
        base_url=config.OLLAMA_BASE_URL,
    )


def load_and_split(pdf_path: str):
    """PDF'i sayfa sayfa yükler ve chunk'lara böler. Sayfa numarası metadata'da kalır."""
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    # metadata'yı temizle/zenginleştir
    source_name = os.path.basename(pdf_path)
    for c in chunks:
        c.metadata["source"] = source_name
        # PyMuPDFLoader sayfaları 0-index veriyor, kullanıcıya 1-index gösterelim
        if "page" in c.metadata:
            c.metadata["page"] = c.metadata["page"] + 1

    return chunks


def ingest_pdf(pdf_path: str, force_reindex: bool = False) -> Chroma:
    """
    PDF'i işleyip Chroma'ya yazar ve o dokümana ait vectorstore'u döndürür.
    Aynı PDF tekrar yüklenirse (force_reindex=False) mevcut index kullanılır.
    """
    collection = _collection_name(pdf_path)
    persist_path = os.path.join(config.CHROMA_DIR, collection)

    embeddings = get_embeddings()

    already_exists = os.path.exists(persist_path) and os.listdir(persist_path)

    if already_exists and not force_reindex:
        vectorstore = Chroma(
            collection_name=collection,
            embedding_function=embeddings,
            persist_directory=persist_path,
        )
        return vectorstore

    chunks = load_and_split(pdf_path)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection,
        persist_directory=persist_path,
    )
    return vectorstore


def list_indexed_pdfs():
    """data/chroma_db altında daha önce indexlenmiş dokümanları listeler."""
    if not os.path.exists(config.CHROMA_DIR):
        return []
    return [d for d in os.listdir(config.CHROMA_DIR)
            if os.path.isdir(os.path.join(config.CHROMA_DIR, d))]