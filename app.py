import os
import streamlit as st

import config
from ingest import ingest_pdf, load_and_split
from rag_chain import answer_question, summarize_document, generate_flashcards, stream_chat

st.set_page_config(
    page_title="Ders Çalışma Asistanı",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# ÖZEL CSS — daha profesyonel görünüm için
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Streamlit'in varsayılan üst boşluğunu daralt, gereksiz chrome'u sadeleştir */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}
#MainMenu, footer {visibility: hidden;}

/* ---------------- ÜST BAŞLIK ---------------- */
.app-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0 0 1.5rem 0;
    margin-bottom: 1.75rem;
    border-bottom: 1px solid #ECECF2;
}
.app-header .icon-badge {
    width: 52px;
    height: 52px;
    min-width: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.28);
}
.app-header .title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #16161F;
    margin: 0;
    letter-spacing: -0.01em;
}
.app-header .subtitle {
    font-size: 0.88rem;
    color: #6B7280;
    margin: 0.1rem 0 0 0;
}

/* ---------------- SIDEBAR ---------------- */
section[data-testid="stSidebar"] {
    border-right: 1px solid #ECECF2;
    background: #FBFBFD;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.75rem;
}
.sidebar-brand-row {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin-bottom: 0.15rem;
}
.sidebar-brand-row .badge {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
}
.sidebar-brand {
    font-size: 1.02rem;
    font-weight: 700;
    color: #16161F;
}
.sidebar-caption {
    font-size: 0.78rem;
    color: #8B8D98;
    margin: 0.15rem 0 1.1rem 2.35rem;
}
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #9296A3;
    margin: 0.2rem 0 0.6rem 0;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #EEF2FF;
    color: #4338CA;
    padding: 0.32rem 0.75rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    border: 1px solid #E0E4FF;
}
.status-pill .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22C55E;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.18);
}

/* Aktif doküman kartı */
.doc-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EF;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-top: 0.6rem;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}
.doc-card .doc-name {
    font-weight: 600;
    font-size: 0.86rem;
    color: #16161F;
    margin-bottom: 0.45rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.doc-stats {
    display: flex;
    gap: 0.5rem;
}
.doc-stat-chip {
    background: #F4F5FA;
    border-radius: 8px;
    padding: 0.3rem 0.55rem;
    font-size: 0.72rem;
    color: #4B4F5C;
    font-weight: 600;
}

/* ---------------- SEKMELER ---------------- */
button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.93rem;
    padding-top: 0.5rem;
    padding-bottom: 0.9rem;
}
div[data-baseweb="tab-list"] {
    gap: 1.5rem;
    border-bottom: 1px solid #ECECF2;
}
div[data-baseweb="tab-highlight"] {
    background-color: #4F46E5 !important;
    height: 2.5px !important;
}

/* ---------------- BUTONLAR ---------------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: transform 0.08s ease, box-shadow 0.15s ease;
    border: 1px solid #E5E7EF;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(16, 24, 40, 0.08);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #6D5AE8 100%) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35) !important;
}

/* ---------------- DOSYA YÜKLEYİCİ ---------------- */
section[data-testid="stFileUploaderDropzone"] {
    border-radius: 12px;
    border: 1.5px dashed #C7CAD9;
    background: #FFFFFF;
    transition: border-color 0.15s ease, background 0.15s ease;
}
section[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #4F46E5;
    background: #FAFAFF;
}

/* ---------------- KART / CONTAINER ---------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
}

/* ---------------- CHAT ---------------- */
div[data-testid="stChatMessage"] {
    padding: 0.9rem 1.15rem;
    border-radius: 14px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
}

/* ---------------- ÖZET İÇERİĞİ ---------------- */
div[data-testid="stVerticalBlockBorderWrapper"] h2 {
    font-size: 1.12rem;
    font-weight: 700;
    border-left: 4px solid #4F46E5;
    padding-left: 0.65rem;
    margin-top: 1.3rem;
}
div[data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-size: 1rem;
    font-weight: 700;
    color: #2E2F3A;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 1.4rem 1.6rem !important;
}

/* ---------------- BOŞ DURUM ---------------- */
.empty-state {
    background: #FBFBFD;
    border: 1.5px dashed #D9DBE5;
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
    color: #6B7280;
}
.empty-state .emoji {
    font-size: 2.4rem;
    margin-bottom: 0.6rem;
    opacity: 0.85;
}
.empty-state .title {
    font-weight: 700;
    color: #16161F;
    font-size: 1rem;
    margin-bottom: 0.25rem;
}

/* ---------------- SCROLLBAR ---------------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D9DBE5; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: #B7BACD; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
defaults = {
    "vectorstore": None,
    "chunks": None,
    "pdf_name": None,
    "summary": None,
    "flashcards": None,
    "qa_history": [],
    "chat_messages": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# SOL PANEL
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand-row">'
        '<div class="badge">📚</div>'
        '<div class="sidebar-brand">Ders Çalışma Asistanı</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-caption">Local RAG · verin dışarı çıkmaz</div>', unsafe_allow_html=True)

    st.markdown(
        f'<span class="status-pill"><span class="dot"></span>{config.LLM_MODEL} çalışıyor</span>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label" style="margin-top:1.4rem;">Doküman</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("PDF yükle", type=["pdf"], label_visibility="collapsed")
    force_reindex = st.checkbox("Yeniden indexle (dosya değiştiyse)", value=False)

    if uploaded_file is not None:
        pdf_path = os.path.join(config.PDF_DIR, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("İşle / Yükle", type="primary", use_container_width=True):
            with st.spinner("PDF okunuyor ve indexleniyor..."):
                st.session_state.vectorstore = ingest_pdf(pdf_path, force_reindex=force_reindex)
                st.session_state.chunks = load_and_split(pdf_path)
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.summary = None
                st.session_state.flashcards = None
                st.session_state.qa_history = []
            st.rerun()

    if st.session_state.pdf_name:
        page_count = len({c.metadata.get("page") for c in st.session_state.chunks})
        chunk_count = len(st.session_state.chunks)
        st.markdown(
            f"""
            <div class="doc-card">
                <div class="doc-name">📄 {st.session_state.pdf_name}</div>
                <div class="doc-stats">
                    <span class="doc-stat-chip">{page_count} sayfa</span>
                    <span class="doc-stat-chip">{chunk_count} parça</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="margin-top:1.4rem;"></div>', unsafe_allow_html=True)
    with st.expander("⚙️ Model ayarları"):
        st.caption(f"LLM: `{config.LLM_MODEL}`")
        st.caption(f"Embedding: `{config.EMBEDDING_MODEL}`")
        st.caption(f"Chunk boyutu: `{config.CHUNK_SIZE}` / overlap: `{config.CHUNK_OVERLAP}`")
        st.caption("Değiştirmek için `config.py` dosyasını düzenle.")

    if st.session_state.chat_messages or st.session_state.qa_history:
        st.divider()
        if st.button("🗑️ Sohbet geçmişini temizle", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.qa_history = []
            st.rerun()

# ---------------------------------------------------------------------------
# ÜST BAŞLIK
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-header">
        <div class="icon-badge">📚</div>
        <div>
            <p class="title">Ders Çalışma Asistanı</p>
            <p class="subtitle">Özet çıkar, soru sor, flashcard üret ya da doğrudan modelle sohbet et.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SEKMELER
# ---------------------------------------------------------------------------
tab_summary, tab_qa, tab_chat, tab_cards = st.tabs(
    ["📝 Özet", "🔎 Dokümana Sor", "💬 Sohbet", "🃏 Flashcard"]
)

# --- ÖZET TAB ---
with tab_summary:
    if st.session_state.vectorstore is None:
        st.markdown(
            '<div class="empty-state"><div class="emoji">📄</div>'
            '<div class="title">Henüz doküman yok</div>'
            'Özet çıkarmak için soldan bir PDF yükle.</div>',
            unsafe_allow_html=True,
        )
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("#### Doküman Özeti")
        with col2:
            gen = st.button("✨ Özet Oluştur", use_container_width=True, type="primary")

        if gen:
            progress_bar = st.progress(0.0, text="Özetleniyor...")

            def _update(done, total):
                progress_bar.progress(done / total, text=f"Bölüm {done}/{total} özetleniyor...")

            with st.spinner("Bu birkaç dakika sürebilir..."):
                st.session_state.summary = summarize_document(
                    st.session_state.chunks, progress_callback=_update
                )
            progress_bar.empty()

        if st.session_state.summary:
            with st.container(border=True):
                st.markdown(st.session_state.summary)
            st.download_button(
                "⬇️ Özeti indir (.md)",
                data=st.session_state.summary,
                file_name=f"{st.session_state.pdf_name}_ozet.md",
            )

# --- DOKÜMANA SOR TAB ---
with tab_qa:
    if st.session_state.vectorstore is None:
        st.markdown(
            '<div class="empty-state"><div class="emoji">🔎</div>'
            '<div class="title">Henüz doküman yok</div>'
            'Dokümana soru sorabilmek için önce bir PDF yükle.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"'{st.session_state.pdf_name}' üzerinden, kaynak sayfa numarasıyla cevap alırsın.")

        for item in st.session_state.qa_history:
            with st.chat_message("user"):
                st.markdown(item["q"])
            with st.chat_message("assistant", avatar="📚"):
                st.markdown(item["answer"])
                if item["sources"]:
                    st.caption(f"📄 Kaynak sayfa(lar): {', '.join(map(str, item['sources']))}")

        question = st.chat_input("Dokümanla ilgili bir şey sor...")
        if question:
            with st.chat_message("user"):
                st.markdown(question)
            with st.chat_message("assistant", avatar="📚"):
                with st.spinner("Cevap aranıyor..."):
                    result = answer_question(st.session_state.vectorstore, question)
                st.markdown(result["answer"])
                if result["sources"]:
                    st.caption(f"📄 Kaynak sayfa(lar): {', '.join(map(str, result['sources']))}")
            st.session_state.qa_history.append({"q": question, **result})

# --- SOHBET TAB ---
with tab_chat:
    st.caption("Bu sekme dokümana bağlı değil — modelle serbestçe sohbet edebilirsin.")

    for msg in st.session_state.chat_messages:
        avatar = "🧑" if msg["role"] == "user" else "📚"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Bir şey yaz...")
    if user_msg:
        st.session_state.chat_messages.append({"role": "user", "content": user_msg})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_msg)

        with st.chat_message("assistant", avatar="📚"):
            response_text = st.write_stream(stream_chat(st.session_state.chat_messages))

        st.session_state.chat_messages.append({"role": "assistant", "content": response_text})

# --- FLASHCARD TAB ---
with tab_cards:
    if st.session_state.vectorstore is None:
        st.markdown(
            '<div class="empty-state"><div class="emoji">🃏</div>'
            '<div class="title">Henüz doküman yok</div>'
            'Flashcard üretmek için önce bir PDF yükle.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("#### Flashcard Üret")
        n_cards = st.slider("Kart sayısı", min_value=4, max_value=20, value=8)

        source_text = None
        if st.session_state.summary:
            source_text = st.session_state.summary
            st.caption("✅ Kartlar mevcut özetten üretilecek.")
        else:
            st.caption(
                "💡 Önce 'Özet' sekmesinden özet oluşturursan kartlar daha isabetli olur. "
                "Yine de tüm doküman üzerinden üretebilirsin."
            )

        if st.button("✨ Flashcard Oluştur", type="primary"):
            with st.spinner("Kartlar üretiliyor..."):
                if source_text:
                    content = source_text
                else:
                    content = "\n\n".join(c.page_content for c in st.session_state.chunks[:15])
                st.session_state.flashcards = generate_flashcards(content, n=n_cards)

        if st.session_state.flashcards:
            cols = st.columns(2)
            for i, card in enumerate(st.session_state.flashcards):
                with cols[i % 2]:
                    with st.expander(f"🃏 {card.get('question', '')}"):
                        st.markdown(card.get("answer", ""))