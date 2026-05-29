## Agno Multi Agent RAG

### How to Run

1. Create and activate virtual environment

```bash
python3 -m venv .venv

source .venv/bin/activate
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Add your `GOOGLE_API_KEY` to the `.env` file.

4. Start the FastAPI server:

```bash
python api.py
```

5. Open your browser and go to http://127.0.0.1:8080

---

### Core Components

- `agent.py`: Defines the agent's instructions and model (e.g., Gemini).
- `api.py`: The FastAPI wrapper initializes the ADK runner and exposes endpoints like `/chat`.
- `.env`: Stores the `GOOGLE_API_KEY` and other configurations.
- `index.html`: It includes a basic chat interface with an input field and a display area.
