## Agno Multi Agent RAG

### How to Run

1. Create and activate virtual environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

2. Install all packages listed in `requirements.txt` file

```bash
pip install -r requirements.txt
```

3. Add your `GOOGLE_API_KEY` in `.env` file

4. **Start your FastAPI server**: Run your `api.py` with:

```bash
uvicorn api:app --reload
```

5. **Open the frontend**: Simply double-click your `index.html` file to open it in a browser, or serve it using a local server like `python -m http.server 3000`.

---

### Core Components

- `agent.py`: Defines the agent's instructions and model (e.g., Gemini).
- `api.py`: The FastAPI wrapper initializes the ADK runner and exposes endpoints like `/chat`.
- `.env`: Stores the `GOOGLE_API_KEY` and other configurations.
- `index.html`: It includes a basic chat interface with an input field and a display area.

---

### Points

Since the frontend will likely be served from a different origin (or a local file), you must enable **CORS (Cross-Origin Resource Sharing)** in the FastAPI app.
