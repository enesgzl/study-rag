# 📚 AI Study Assistant (Local RAG)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=flat-square)

A privacy-first, **100% local** AI-powered study assistant built with Ollama, LangChain, and Streamlit. Upload your course PDFs to generate concise summaries, ask questions with exact page references, and practice with 3D interactive flashcards.

> 🔒 **Privacy First:** All documents and LLM processes run locally on your machine via Ollama. No data ever leaves your device.

---

## ✨ Features

* 📝 **Smart Summarization:** Automatically breaks down and summarizes complex lecture notes into key takeaways.
* 🔎 **Page-Referenced Q&A:** Query your documents and receive accurate answers with exact page citations.
* 🃏 **3D Flip Flashcards:** Test your knowledge with interactive, 3D animated study cards generated from your notes.
* 💬 **Free Chat Mode:** Brainstorm or chat freely with the local LLM independently of the document.
* 🎨 **SaaS-like UI:** Clean, responsive, and modern user interface enhanced with custom CSS.

---

## 🛠️ Tech Stack

* **UI:** Streamlit (Custom CSS & 3D Flip Card components)
* **Local LLM:** Ollama (`qwen2.5:4b`)
* **Embeddings:** `nomic-embed-text`
* **Vector Database:** ChromaDB
* **Orchestration:** LangChain / LangChain Community
* **Document Parser:** PyPDF

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [Python 3.10+](https://www.python.org/) and [Ollama](https://ollama.com/) installed. Pull the required models:

```bash
ollama run qwen2.5:4b
ollama pull nomic-embed-text
