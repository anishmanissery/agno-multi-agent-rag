# Agno Multi-Agent RAG System

A production-grade agentic RAG system built with [Agno](https://docs.agno.com) and Gemini. A coordinated 3-agent team handles document Q&A with hybrid vector search and autonomous web search fallback.

---

## Architecture

```
       User Query
           │
           ▼
┌─────────────────────────────────────────────┐
│              Team Coordinator               │
│  (Gemini · routing logic · session memory)  │
└──────────┬──────────────────────────────────┘
           │
           ▼ STEP 1
┌───────────────────────┐
│   Knowledge Retriever │  ── hybrid search (semantic + keyword) ──▶ LanceDB
│                       │       GeminiEmbedder
└──────────┬────────────┘
           │
           ├── If results found ─────────────────────────────────────┐
           │                                                         │
           │  If "NO_KB_RESULTS"                                     │
           ▼ STEP 2 (fallback only)                                  │
┌───────────────────────┐                                            │
│                       │  ── 2–3 targeted searches / Live Web       │
│   Web Search Agent    │                                            │
│                       │                                            │
└──────────┬────────────┘                                            │
           │                                                         │
           └───────────────────────┐                                 │
                                   ▼                                 ▼
                    ┌──────────────────────────────────────────────────────┐
                    │              Response Synthesizer                    │
                    │   (merges sources, cites KB vs. web, returns answer) │
                    └──────────────────────────┬───────────────────────────┘
                                               │
                                               ▼
                                           FastAPI /chat
```

### Key Design Decisions

**Signal-based routing** — the Knowledge Retriever returns the literal token `NO_KB_RESULTS` when nothing relevant is found in the vector store. The coordinator uses this as a routing signal to invoke the Web Search Agent. This keeps fallback logic explicit and deterministic rather than LLM-inferred.

**Hybrid retrieval** — `SearchType.hybrid` in LanceDB combines semantic similarity (dense vectors) with keyword matching (BM25-style sparse search), improving recall on queries with specific terms or acronyms that pure embedding search can miss.

**Gemini-native embeddings** — uses `GeminiEmbedder(id="gemini-embedding-001")` so the embedding space is consistent with the Gemini generation model, avoiding cross-provider embedding drift.

**Conversational memory** — `add_history_to_context=True` with `num_history_runs=5` gives the team coordinator a rolling window of prior turns, persisted in SQLite, enabling contextual follow-up questions without re-uploading documents.

**Separation of roles** — Knowledge Retriever returns raw chunks with source references only; it does not answer the question. Response Synthesizer is the only agent that generates a final answer. This prevents early synthesis from polluting retrieval quality.

---

## Tech Stack

| Layer            | Technology                                                    |
| ---------------- | ------------------------------------------------------------- |
| Agent framework  | [Agno](https://docs.agno.com)                                 |
| LLM + embeddings | Gemini (`gemini-3.1-flash-lite`, `gemini-embedding-001`)      |
| Vector database  | [LanceDB](https://lancedb.github.io/lancedb/) — hybrid search |
| Session memory   | SQLite (via Agno `SqliteDb`)                                  |
| API layer        | FastAPI + Uvicorn                                             |
| Deployment       | GCP Cloud Run                                                 |

---

## Project Structure

```
agno-multi-agent-rag/
├── agent.py          # Agent and team definitions, LanceDB setup, routing logic
├── api.py            # FastAPI app, /chat endpoint, static file serving
├── static/
│   └── index.html    # Chat UI
├── requirements.txt
└── .env              # GOOGLE_API_KEY (not committed)
```

---

## Local Setup

**Prerequisites:** Python 3.10+, a Google API key with Gemini access.

```bash
# 1. Clone the repo
git clone https://github.com/anishmanissery/agno-multi-agent-rag.git
cd agno-multi-agent-rag

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# 5. Start the server
python api.py
```

Open `http://127.0.0.1:8080` in your browser.

> On first run, the knowledge base will load documents from the configured URLs (Agno docs + Thai recipes PDF) into LanceDB. Subsequent runs skip existing documents (`skip_if_exists=True`).

---

## API

### `POST /chat`

```json
// Request
{ "query": "What are the key components of an Agno team?" }

// Response
{ "response": { ... } }   // TeamRunOutput — includes each agent's intermediate output
```

---

## Extending the Knowledge Base

To index your own documents, edit `agent.py` and add URLs or local file paths to the `knowledge.insert_many()` call:

```python
knowledge.insert_many(
    urls=[
        "https://your-domain.com/your-doc.pdf",
        "https://your-site.com/page.md",
    ],
    skip_if_exists=True
)
```

LanceDB persists the vector store to `/tmp/lancedb` by default. Change the `uri` in the `LanceDb(...)` constructor to a persistent path for production use.

---

## License

MIT
