"""
RAG üzerine kurulu 3 ana işlev:
  - answer_question: dokümana soru sorma (kaynak sayfa ile)
  - summarize_document: map-reduce ile tüm dokümanı özetleme
  - generate_flashcards: özet/dokümandan soru-cevap kartı üretme
"""

import json
import re

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config


def get_llm(temperature: float = 0.2):
    return ChatOllama(
        model=config.LLM_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# 1) SORU-CEVAP
# ---------------------------------------------------------------------------

QA_PROMPT = ChatPromptTemplate.from_template(
    """Sen bir ders çalışma asistanısın. Aşağıdaki doküman parçalarını kullanarak
soruyu Türkçe, net ve anlaşılır şekilde cevapla. Eğer cevap verilen parçalarda
yoksa, bunu açıkça belirt; uydurma bilgi verme.

Doküman parçaları:
{context}

Soru: {question}

Cevap (varsa hangi sayfadan geldiğini de belirt):"""
)


def answer_question(vectorstore, question: str) -> dict:
    retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
    docs = retriever.invoke(question)

    context = "\n\n".join(
        f"[Sayfa {d.metadata.get('page', '?')}]\n{d.page_content}" for d in docs
    )

    chain = QA_PROMPT | get_llm() | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = sorted({d.metadata.get("page", "?") for d in docs})
    return {"answer": answer, "sources": sources}


# ---------------------------------------------------------------------------
# 2) ÖZET (map-reduce)
# ---------------------------------------------------------------------------

MAP_PROMPT = ChatPromptTemplate.from_template(
    """Aşağıdaki ders notu parçasını Türkçe, kısa ve öz maddeler halinde özetle.
Sadece önemli kavram ve bilgileri al, gereksiz detayı atla.

Parça:
{chunk}

Kısa özet (madde madde):"""
)

REDUCE_PROMPT = ChatPromptTemplate.from_template(
    """Aşağıda aynı dokümanın farklı bölümlerinden çıkarılmış kısa özetler var.
Bunları birleştirip tutarlı, akılda kalıcı, başlıklı ve madde işaretli TEK bir
özet haline getir. Tekrarları çıkar, mantıklı bir sıraya koy.

Bölüm özetleri:
{summaries}

Nihai özet (başlıklar ve alt maddeler halinde, Türkçe):"""
)


def summarize_document(chunks, progress_callback=None) -> str:
    """
    chunks: ingest.load_and_split() çıktısı gibi Document listesi.
    Uzun dokümanlarda önce her chunk özetlenir (map), sonra birleştirilir (reduce).
    """
    llm = get_llm(temperature=0.1)
    map_chain = MAP_PROMPT | llm | StrOutputParser()

    partial_summaries = []
    for i, chunk in enumerate(chunks):
        summary = map_chain.invoke({"chunk": chunk.page_content})
        partial_summaries.append(summary)
        if progress_callback:
            progress_callback(i + 1, len(chunks))

    reduce_chain = REDUCE_PROMPT | llm | StrOutputParser()
    final_summary = reduce_chain.invoke(
        {"summaries": "\n\n---\n\n".join(partial_summaries)}
    )
    return final_summary


# ---------------------------------------------------------------------------
# 3) SERBEST SOHBET (dokümana bağlı olmayan genel chat)
# ---------------------------------------------------------------------------

CHAT_SYSTEM_PROMPT = (
    "Sen bir ders çalışma asistanısın. Kullanıcıya konuları açıklarken sabırlı, "
    "net ve teşvik edici ol. Türkçe cevap ver, gerektiğinde örneklerle veya "
    "adım adım açıklamalarla anlat. Kısa sorulara kısa, kavramsal sorulara "
    "yeterince detaylı cevap ver."
)


def stream_chat(messages: list[dict]):
    """
    messages: [{"role": "user" | "assistant", "content": "..."}]
    Belirli bir dokümana bağlı olmadan, genel sohbet/soru-cevap için
    kelime kelime (streaming) cevap üretir.
    """
    llm = get_llm(temperature=0.6)

    lc_messages = [("system", CHAT_SYSTEM_PROMPT)]
    for m in messages:
        role = "human" if m["role"] == "user" else "ai"
        lc_messages.append((role, m["content"]))

    for chunk in llm.stream(lc_messages):
        if chunk.content:
            yield chunk.content


# ---------------------------------------------------------------------------
# 4) FLASHCARD ÜRETİMİ
# ---------------------------------------------------------------------------

FLASHCARD_PROMPT = ChatPromptTemplate.from_template(
    """Aşağıdaki ders içeriğinden {n} adet flashcard (soru-cevap kartı) üret.
Sorular test/sınav çalışmasına uygun, kavrayışı ölçen sorular olsun.
Cevaplar kısa ve net olsun.

SADECE aşağıdaki JSON formatında, başka hiçbir açıklama eklemeden cevap ver:
[
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}}
]

İçerik:
{content}
"""
)


def generate_flashcards(content: str, n: int = 8) -> list[dict]:
    chain = FLASHCARD_PROMPT | get_llm(temperature=0.3) | StrOutputParser()
    raw = chain.invoke({"content": content, "n": n})

    # Model bazen ```json ... ``` bloğuyla dönebiliyor, temizleyelim
    cleaned = re.sub(r"```json|```", "", raw).strip()

    try:
        cards = json.loads(cleaned)
        return cards if isinstance(cards, list) else []
    except json.JSONDecodeError:
        # JSON parse edilemezse ham metni tek kart olarak döndür (hata ayıklama için)
        return [{"question": "Ayrıştırma hatası", "answer": raw}]