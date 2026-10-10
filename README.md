# 🚀 AstroRAG — A Retrieval-Augmented Space Research Assistant

An AI assistant that answers space-science questions using Retrieval-Augmented Generation (RAG): it searches a knowledge base with semantic search, then uses an LLM to generate accurate, grounded answers — instead of relying on the model's memory alone.

**Live demo:** https://astrorag-space-research-assistant-kz6ztfy4xlbzwcaqtsy8ot.streamlit.app/

## What it does

- Answers natural-language questions about space topics (planets, telescopes, the ISS, galaxies, Mars missions, and more) using a pre-loaded knowledge base
- Lets users upload their own PDF or TXT documents to extend the knowledge base on top of the built-in one
- Retrieves the most relevant content for each question using semantic similarity search, not just keyword matching
- Cites the source document(s) used for every answer
- Keeps conversation history visible in a chat-style interface
- Handles greetings and casual conversation naturally, alongside factual questions

## Why RAG?

A plain chatbot can only answer from what the underlying language model already "knows," which can be outdated, generic, or simply wrong. RAG fixes this by retrieving real, relevant content from a trusted knowledge base first, then asking the model to answer using that retrieved content as grounding. This is the same architecture used in real-world AI products such as enterprise search tools, internal documentation assistants, and customer support systems.

## How it works

1. **Preloaded knowledge base** — space-science PDFs and text files are loaded, split into chunks, and converted into vector embeddings using a local sentence-transformer model.
2. **Vector indexing** — the embeddings are stored in a FAISS index for fast similarity search.
3. **User uploads (optional)** — users can upload their own PDF/TXT files, which are processed the same way and searched alongside the preloaded knowledge.
4. **Retrieval** — when a question is asked, it's embedded and compared against the index to find the most relevant chunks of text.
5. **Generation** — the retrieved chunks are passed to the Google Gemini API as context, which generates a natural, direct answer grounded in that content.
6. **Source citation** — the document(s) the answer was drawn from are shown underneath the response.

## Tech stack

- **Python**
- **Streamlit** — web interface
- **Google Gemini API** — answer generation
- **sentence-transformers** (`all-MiniLM-L6-v2`) — local, free text embeddings
- **FAISS** — vector similarity search
- **pypdf** — PDF text extraction
- **python-dotenv** — API key management

## Run it locally

1. Clone the repository and open the folder:

```
git clone https://github.com/alisha-tabassum/astrorag-space-research-assistant.git
cd astrorag-space-research-assistant
```

2. Install the dependencies:

```
pip install -r requirements.txt
```

3. Create a file named `.env` in the project folder and add your Gemini API key (free from Google AI Studio):

```
GEMINI_API_KEY=your_key_here
```

4. Start the app:

```
streamlit run app.py
```

## Project structure

```
astrorag-space-research-assistant/
├── app.py                  # Streamlit app: UI, RAG pipeline, chat logic
├── preloaded_docs/         # Built-in space-science knowledge base (PDF + TXT)
├── slider_images/          # Header slideshow images
├── requirements.txt        # Python dependencies
├── .streamlit/config.toml  # Streamlit configuration
└── .gitignore               # Keeps the API key out of GitHub
```

## Adding to the knowledge base

Drop additional `.pdf` or `.txt` files into `preloaded_docs/` and restart the app — they'll be automatically indexed and searchable.

## Author

Alisha Tabassum, Computer Engineer
[LinkedIn](https://linkedin.com/in/alisha-tabassum)
