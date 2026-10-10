import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import glob
import base64
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

slide_images_b64 = []
for i in range(1, 5):
    path = f"slider_images/slide{i}.jpg"
    if os.path.exists(path):
        slide_images_b64.append(get_base64_image(path))

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

st.set_page_config(page_title="AstroRAG", page_icon="🚀", layout="wide")

USER_AVATAR = "👨‍🚀"
BOT_AVATAR = "🛰️"
ORANGE = "#FFB74D"
CYAN = "#4FD8EB"
USER_TEXT_COLOR = "#FFFFFF"
BOT_TEXT_COLOR = "#CFE8FF"

# ---------- Build slide CSS with proper crossfade timing ----------
n_slides = max(len(slide_images_b64), 1)
seconds_per_slide = 5
duration = n_slides * seconds_per_slide
percent_per_slide = 100 / n_slides
fade_pct = percent_per_slide * 0.25

slide_css = ""
for i, img in enumerate(slide_images_b64):
    delay = i * seconds_per_slide
    slide_css += f"""
    .slide-{i} {{
        background-image: linear-gradient(rgba(5,8,20,0.5), rgba(5,8,20,0.7)), url(data:image/jpeg;base64,{img});
        animation: slideFade {duration}s infinite;
        animation-delay: {delay}s;
    }}
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Poppins:wght@400;500&display=swap');

html, body, .stApp {{
    background-color: #060914;
    font-family: 'Poppins', sans-serif;
}}

/* Remove default Streamlit side padding so header can go edge-to-edge */
.block-container {{
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}}

/* ---------- SMALL BLURRY TWINKLING STARS ---------- */
.stars-layer {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    filter: blur(1.1px);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='150' height='150'%3E%3Cpath d='M15 10 L16.5 14 L20 15 L16.5 16 L15 20 L13.5 16 L10 15 L13.5 14 Z' fill='%23ffffff'/%3E%3Cpath d='M90 50 L91.2 53 L94 54 L91.2 55 L90 58 L88.8 55 L86 54 L88.8 53 Z' fill='%2399d6ff'/%3E%3Cpath d='M50 110 L51.2 113 L54 114 L51.2 115 L50 118 L48.8 115 L46 114 L48.8 113 Z' fill='%23FFB74D'/%3E%3Cpath d='M125 125 L126 127.5 L128.5 128.5 L126 129.5 L125 132 L124 129.5 L121.5 128.5 L124 127.5 Z' fill='%23ffffff'/%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 150px 150px;
    animation: twinkle 3.5s ease-in-out infinite;
}}

@keyframes twinkle {{
    0%, 100% {{ opacity: 0.2; }}
    50% {{ opacity: 0.55; }}
}}

/* ---------- HERO SLIDER: true edge-to-edge, full width ---------- */
.hero-slider {{
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    width: 100vw;
    height: 340px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
}}

.slide-0, .slide-1, .slide-2, .slide-3 {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-size: cover;
    background-position: center;
    opacity: 0;
}}

{slide_css}

@keyframes slideFade {{
    0% {{ opacity: 0; }}
    {fade_pct}% {{ opacity: 1; }}
    {percent_per_slide - fade_pct}% {{ opacity: 1; }}
    {percent_per_slide}% {{ opacity: 0; }}
    100% {{ opacity: 0; }}
}}

.hero-text {{
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 2;
    width: 90%;
}}

.hero-text h1 {{
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-size: 2.8em;
    margin-bottom: 10px;
    text-shadow: 0 0 20px rgba(79,216,235,0.8), 0 0 40px rgba(255,183,77,0.4);
}}

.hero-text p {{
    color: #c9d6f0;
    font-size: 17px;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.6;
}}

/* ---------- SUBHEADINGS: Documents / Ask a question, in orange ---------- */
h3 {{
    color: {ORANGE} !important;
}}

p, span, label {{
    color: #c9d6f0;
}}

/* ---------- DOCUMENT CARDS ---------- */
[data-testid="stContainer"] {{
    background-color: rgba(79,216,235,0.08);
    border: 1px solid rgba(79,216,235,0.3) !important;
    border-radius: 10px;
}}

/* ---------- LABEL TEXT (sources / word counts) ---------- */
.label-orange {{
    color: {ORANGE} !important;
    font-size: 13px;
    margin: 2px 0;
}}

/* ---------- UPLOAD BOX ---------- */
[data-testid="stFileUploader"] section {{
    background-color: #0d1326 !important;
    border: 2px dashed {CYAN} !important;
    border-radius: 12px !important;
}}

[data-testid="stFileUploaderDropzoneInstructions"] span {{
    color: #e8ecff !important;
}}

[data-testid="stFileUploaderDropzoneInstructions"] div span {{
    color: {ORANGE} !important;
}}

[data-testid="stFileUploader"] section button {{
    background-color: #1a4087 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}

[data-testid="stFileUploader"] section button:hover {{
    background-color: #b57312 !important;
}}

/* Uploaded file row + its remove (x) button, theme-colored */
[data-testid="stFileUploaderFile"] {{
    background-color: rgba(79,216,235,0.07) !important;
    border: 1px solid rgba(79,216,235,0.25) !important;
    border-radius: 8px !important;
}}

[data-testid="stFileUploaderFile"] button,
[data-testid="stFileUploaderDeleteBtn"] {{
    background-color: transparent !important;
    color: {ORANGE} !important;
}}

[data-testid="stFileUploaderFile"] svg,
[data-testid="stFileUploaderDeleteBtn"] svg {{
    fill: {ORANGE} !important;
    color: {ORANGE} !important;
}}

/* ---------- BUTTONS ---------- */
.stButton button, .stFormSubmitButton button {{
    background-color: #1a4087 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    transition: 0.2s !important;
}}

.stButton button:hover, .stFormSubmitButton button:hover {{
    background-color: #b57312 !important;
    color: #ffffff !important;
    box-shadow: 0 0 15px rgba(255,183,77,0.6);
}}

/* ---------- CHAT MESSAGES ---------- */
[data-testid="stChatMessage"] {{
    background-color: rgba(255,255,255,0.03);
    border: 1px solid rgba(79,216,235,0.2);
    border-radius: 14px;
    padding: 8px;
}}

.user-msg {{
    color: {USER_TEXT_COLOR} !important;
}}

.bot-msg {{
    color: {BOT_TEXT_COLOR} !important;
}}

/* ---------- INPUT FIELD (clean outline, no stray edge) ---------- */
[data-baseweb="input"] {{
    border: none !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    background-color: #0d1326 !important;
}}

[data-testid="stTextInput"] input {{
    background-color: #0d1326 !important;
    border: 2px solid #1a4087 !important;
    border-radius: 10px !important;
    color: {ORANGE} !important;
    caret-color: {ORANGE} !important;
    outline: none !important;
    box-shadow: none !important;
}}

[data-testid="stTextInput"] input:focus {{
    border: 2px solid #b57312 !important;
    box-shadow: 0 0 10px rgba(255,183,77,0.4) !important;
    outline: none !important;
}}

[data-testid="stTextInput"] input::placeholder {{
    color: #7a85a8 !important;
}}

/* ---------- INDEPENDENT SCROLL PER COLUMN ---------- */
div[data-testid="column"]:nth-of-type(1) {{
    position: sticky;
    top: 1.5rem;
    max-height: calc(100vh - 3rem);
    overflow-y: auto;
    align-self: flex-start;
    padding-right: 0.5rem;
}}

div[data-testid="column"]:nth-of-type(2) {{
    max-height: calc(100vh - 3rem);
    overflow-y: auto;
    padding-left: 0.5rem;
}}

/* ---------- FOOTER ---------- */
.footer-text {{
    text-align: center;
    color: {ORANGE};
    font-size: 13px;
}}
</style>

<div class="stars-layer"></div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedder = load_embedding_model()

def extract_text(file_path_or_obj, is_path=False):
    if is_path:
        if file_path_or_obj.endswith(".txt"):
            with open(file_path_or_obj, "r", encoding="utf-8") as f:
                return f.read()
        reader = PdfReader(file_path_or_obj)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        file = file_path_or_obj
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            return file.read().decode("utf-8")

def chunk_text(text, chunk_size=200):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def build_index(chunks):
    embeddings = embedder.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

@st.cache_resource
def load_preloaded_knowledge():
    all_chunks = []
    all_sources = []
    file_info = []
    pdf_paths = glob.glob("preloaded_docs/*.pdf") + glob.glob("preloaded_docs/*.txt")
    for path in pdf_paths:
        text = extract_text(path, is_path=True)
        chunks = chunk_text(text)
        filename = os.path.basename(path)
        file_info.append({"name": filename, "words": len(text.split())})
        for chunk in chunks:
            all_chunks.append(chunk)
            all_sources.append(filename)
    index = build_index(all_chunks) if all_chunks else None
    return all_chunks, all_sources, index, file_info

preloaded_chunks, preloaded_sources, preloaded_index, preloaded_file_info = load_preloaded_knowledge()

# ---------- Session state ----------
if "extra_chunks" not in st.session_state:
    st.session_state.extra_chunks = []
if "extra_sources" not in st.session_state:
    st.session_state.extra_sources = []
if "extra_index" not in st.session_state:
    st.session_state.extra_index = None
if "extra_file_info" not in st.session_state:
    st.session_state.extra_file_info = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Header slider (edge-to-edge) ----------
slides_html = "".join([f'<div class="slide-{i}"></div>' for i in range(len(slide_images_b64))])

st.markdown(f"""
<div class="hero-slider">
    {slides_html}
    <div class="hero-text">
        <h1>🚀 AstroRAG</h1>
        <p>A Retrieval-Augmented Space Research Assistant — ask questions grounded in real space-science data, pre-loaded, with room to add your own documents.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------- Two-column layout: 30 / 70 ----------
col_left, col_right = st.columns([3, 7])

with col_left:
    st.subheader("Documents")

    uploaded_files = st.file_uploader(
        "Add your own PDF or TXT",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process Uploaded Documents", use_container_width=True):
        new_chunks = []
        new_sources = []
        new_file_info = []
        with st.spinner("Reading and chunking..."):
            for file in uploaded_files:
                text = extract_text(file)
                chunks = chunk_text(text)
                new_file_info.append({"name": file.name, "words": len(text.split())})
                for chunk in chunks:
                    new_chunks.append(chunk)
                    new_sources.append(file.name)
        with st.spinner("Creating embeddings..."):
            new_index = build_index(new_chunks)

        st.session_state.extra_chunks = new_chunks
        st.session_state.extra_sources = new_sources
        st.session_state.extra_index = new_index
        st.session_state.extra_file_info = new_file_info
        st.success(f"Added {len(uploaded_files)} document(s).")

    if st.session_state.extra_file_info:
        st.markdown("<p class='label-orange'>Your uploaded sources:</p>", unsafe_allow_html=True)
        for info in st.session_state.extra_file_info:
            with st.container(border=True):
                st.write(f"📄 {info['name']}")
                st.markdown(f"<p class='label-orange'>{info['words']} words</p>", unsafe_allow_html=True)

def search_all(question, k=3):
    results = []
    if preloaded_index is not None:
        q_emb = embedder.encode([question]).astype("float32")
        distances, indices = preloaded_index.search(q_emb, k)
        for idx in indices[0]:
            results.append((preloaded_chunks[idx], preloaded_sources[idx]))
    if st.session_state.extra_index is not None:
        q_emb = embedder.encode([question]).astype("float32")
        distances, indices = st.session_state.extra_index.search(q_emb, k)
        for idx in indices[0]:
            results.append((st.session_state.extra_chunks[idx], st.session_state.extra_sources[idx]))
    return results

with col_right:
    st.subheader("Ask a question")

    for entry in st.session_state.chat_history:
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(f"<span class='user-msg'>{entry['question']}</span>", unsafe_allow_html=True)
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            st.markdown(f"<span class='bot-msg'>{entry['answer']}</span>", unsafe_allow_html=True)
            if entry["sources"]:
                st.markdown(f"<p class='label-orange'>Sources: {', '.join(entry['sources'])}</p>", unsafe_allow_html=True)

    with st.form("question_form", clear_on_submit=True):
        input_col, button_col = st.columns([6, 1])
        with input_col:
            user_question = st.text_input("Type your question:", label_visibility="collapsed")
        with button_col:
            submitted = st.form_submit_button("➤", use_container_width=True)

    if submitted and user_question:
        retrieved = search_all(user_question)
        context = "\n\n".join([chunk for chunk, source in retrieved])
        sources_used = list(set([source for chunk, source in retrieved]))

        prompt = f"""You are a knowledgeable space research assistant. Answer the question naturally and confidently, as if you simply know this information — do not say phrases like "based on the provided text," "according to the document," or reference "image 1" or "image 2" or any figure numbers. Just answer directly and clearly.

If something in the context isn't enough to fully answer, briefly mention that more detail may be available in the source document, without naming specific page numbers.

Context:
{context}

Question: {user_question}"""

        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(prompt)
                answer = response.text
            except Exception:
                answer = "Something went wrong. Please try again."
                sources_used = []

        st.session_state.chat_history.append({
            "question": user_question,
            "answer": answer,
            "sources": sources_used
        })
        st.rerun()

# ---------- Footer ----------
st.divider()
st.markdown("<p class='footer-text'>© 2026 AstroRAG — Built with Python, Streamlit, Sentence-Transformers, FAISS & Google Gemini API</p>", unsafe_allow_html=True)





