# QUOT — Quary Unified Observability Tool

A modular Retrieval-Augmented Generation (RAG) system supporting multiple LLM providers.
Built with LangChain, ChromaDB, and Streamlit, with a FastAPI REST API and a React dashboard.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- **Multi-Provider Support** — OpenAI, Anthropic, Google, HuggingFace, IBM Watsonx, or all at once via `multi/`
- **Multiple Interfaces** — Streamlit UI per provider, FastAPI REST API, and Chainlit chat
- **XML-Structured Retrieval** — Retrieved chunks in `<document>` tags; full context in `<context>` tags for cleaner LLM delineation
- **Unified Logging** — Single `loggers/` module writes JSONL events; optionally forwards to Weights & Biases or MLflow
- **React Dashboard** — Real-time view of queries, sessions, errors, and response times (`dashboard/`)

---

## Supported Providers

| Provider | LLM Models | Embeddings | Local Option |
|----------|------------|------------|--------------|
| **OpenAI** | GPT-4o, GPT-4, GPT-3.5 | text-embedding-3-small | No |
| **Anthropic** | Claude 3.5 Sonnet/Haiku, Claude 3 Opus | Google or OpenAI (via `EMBEDDING_PROVIDER`) | No |
| **Google** | Gemini 2.0 Flash, Gemini 1.5 Pro | embedding-001 | No |
| **HuggingFace** | Mistral-7B, Llama-2, TinyLlama | sentence-transformers | Yes |
| **IBM Watsonx** | Mixtral-8x7B, Granite, Llama-3 | HuggingFace (local) | No |

---

## Project Structure

```text
QUOT/
├── anthropic/               # Anthropic Claude provider
│   ├── app.py               # Streamlit UI
│   ├── qa_bot.py            # RetrievalQA chain (Claude)
│   ├── embeddings.py        # Google embeddings
│   ├── embeddings_openai.py # OpenAI embeddings (alternative)
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── openai/                  # OpenAI GPT provider
│   ├── app.py
│   ├── qa_bot.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── google/                  # Google Gemini provider
│   ├── app.py
│   ├── qa_bot.py
│   ├── embeddings.py        # Google embeddings
│   ├── embeddings_openai.py # OpenAI embeddings (alternative)
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── hugging_face/            # HuggingFace (API + local)
│   ├── app.py
│   ├── qa_bot.py
│   ├── embeddings.py        # sentence-transformers (local)
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── watsonX/                 # IBM Watsonx provider
│   ├── app.py
│   ├── qa_bot.py
│   ├── embeddings.py        # HuggingFace (local)
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── multi/                   # Dynamic multi-provider mode
│   ├── app.py               # Streamlit UI
│   ├── qa_bot_multi.py      # Picks provider from PROVIDER env var
│   ├── embeddings_multi.py
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── fastAPI/                 # REST API + logging backend
│   ├── api.py               # FastAPI app (ask, ingest, dashboard endpoints)
│   ├── qa_bot.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── vectordb.py
│   ├── ingest.py
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   ├── requirements.txt
│   └── .env.example
│
├── loggers/                 # Shared unified logging module
│   ├── __init__.py          # Exports UnifiedLogger, FileLogger, WandbLogger, MLflowLogger
│   ├── unified_logger.py    # Core logger — always writes JSONL, optionally W&B / MLflow
│   ├── log_reader.py        # Reads unified_events.jsonl for the dashboard API
│   ├── file_logger.py
│   ├── mlflow_logger.py
│   └── wandb_logger.py
│
├── dashboard/               # React + Vite monitoring dashboard
│   ├── src/
│   │   ├── components/      # StatCard, QueryLog, SessionList, ErrorList
│   │   ├── pages/           # Dashboard, Sessions, Queries, Errors
│   │   └── services/api.ts  # Fetch helpers for FastAPI logging endpoints
│   ├── package.json
│   └── vite.config.ts
│
├── chainlit.py              # Chainlit chat interface (provider set via QUOT_DIR)
├── requirements.txt         # Root-level dep for chainlit.py
├── check_deps.py            # Dependency checker — reports missing/outdated packages
├── pyrightconfig.json       # Pylance/Pyright path config for VSCode
├── .pylintrc                # Pylint config (source-path init-hook)
├── .gitignore
├── README.md
└── docs/
    ├── logging_guide.md
    ├── PROVIDER_COMPARISON.md
    └── SWITCHING_GUIDE.md
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/MnkyBr8n/QUOT.git
cd QUOT
```

### 2. Choose a provider and install dependencies

```bash
cd openai          # or anthropic, google, hugging_face, watsonX, multi
pip install -r requirements.txt
```

To verify all packages (including pip itself) are installed at the required versions:

```bash
python check_deps.py            # check all providers
python check_deps.py openai     # check one provider
python check_deps.py --install  # check and auto-install missing/outdated
```

### 3. Configure environment

```bash
cp .env.example .env
# Fill in your API keys in .env
```

### 4. Ingest a PDF

```bash
python ingest.py path/to/document.pdf
```

### 5. Run the Streamlit UI

```bash
streamlit run app.py
```

---

## Configuration

### OpenAI

```env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

### Anthropic

```env
ANTHROPIC_API_KEY=sk-ant-...
EMBEDDING_PROVIDER=openai          # or: google (Anthropic has no embedding API)
OPENAI_API_KEY=sk-...              # required when EMBEDDING_PROVIDER=openai
# GOOGLE_API_KEY=...               # required when EMBEDDING_PROVIDER=google
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_MODEL=text-embedding-3-small
```

### Google

```env
GOOGLE_API_KEY=...
LLM_MODEL=gemini-2.0-flash
EMBEDDING_MODEL=models/embedding-001
```

### HuggingFace

```env
# API mode (recommended)
HUGGINGFACE_API_KEY=hf_...
USE_LOCAL_MODEL=false
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Local mode (no API key needed)
USE_LOCAL_MODEL=true
LLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
DEVICE=cpu
```

### IBM Watsonx

```env
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_APIKEY=...
WATSONX_PROJECT_ID=...
LLM_MODEL=mistralai/mixtral-8x7b-instruct-v01
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Multi-Provider

```env
PROVIDER=openai    # openai | anthropic | google | watsonx
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small

# When PROVIDER=anthropic, also set:
# EMBEDDING_PROVIDER=openai   # or: google
```

---

## FastAPI Service

The FastAPI module exposes a REST API and serves data for the React dashboard.

### Run the server

```bash
cd fastAPI
pip install -r requirements.txt
cp .env.example .env
# Ingest a PDF first, then:
uvicorn api:app --reload
```

### CORS

Allowed origins are controlled by `ALLOWED_ORIGINS` in `.env` (comma-separated).
Default: `http://localhost:5173,http://localhost:3000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/ask` | Submit a question |
| `POST` | `/ingest` | Upload and index a PDF |
| `GET` | `/status` | System status |
| `GET` | `/logs/stats` | Aggregated dashboard stats |
| `GET` | `/logs/sessions` | All sessions with summaries |
| `GET` | `/logs/sessions/{id}` | Detail for a specific session |
| `GET` | `/logs/events` | Log events (filterable) |
| `GET` | `/logs/queries` | Query events |
| `GET` | `/logs/errors` | Error events |
| `GET` | `/logs/response-times` | Response time series |

### Example

```bash
# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'

# Upload a PDF
curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

---

## React Dashboard

The dashboard reads from the FastAPI logging endpoints.

```bash
cd dashboard
npm install
npm run dev        # Connects to http://localhost:8000 by default
```

To point at a different API, update `API_BASE` in [dashboard/src/services/api.ts](dashboard/src/services/api.ts).

---

## Chainlit Interface

```bash
# Default provider: openai
chainlit run chainlit.py

# Use a different provider
QUOT_DIR=anthropic chainlit run chainlit.py
```

`QUOT_DIR` must be the name of a provider folder (`openai`, `anthropic`, `google`, `hugging_face`, `watsonX`).
Make sure the provider's `chroma_db` is already populated via `ingest.py`.

---

## Unified Logging

All providers can use the shared `loggers/` module. It always writes a JSONL file and optionally forwards events to W&B or MLflow.

```python
from loggers import UnifiedLogger

logger = UnifiedLogger(
    log_dir="logs",
    vendor="openai",
    app="my-app",
    enable_wandb=False,   # set True + WANDB_API_KEY to enable
    enable_mlflow=False,  # set True to enable
)

# Wrap your QA chain
logger.log_query(query="...", answer="...", sources=[], response_time=1.2)
logger.finish()
```

Events are written to `logs/unified_events.jsonl` and consumed by both the FastAPI dashboard endpoints and the React dashboard.

---

## Cost Reference

| Provider | Input (per 1M tokens) | Output (per 1M tokens) | Context |
|----------|----------------------|------------------------|---------|
| GPT-4o | $2.50 | $10.00 | 128K |
| GPT-3.5 Turbo | $0.50 | $1.50 | 16K |
| Claude 3.5 Sonnet | $3.00 | $15.00 | 200K |
| Claude 3 Haiku | $0.25 | $1.25 | 200K |
| Gemini 2.0 Flash | $0.075 | $0.30 | 1M |
| Gemini 1.5 Pro | $1.25 | $5.00 | 2M |
| HuggingFace API | Free tier | Free tier | Varies |
| IBM Watsonx | Pay-per-token | Pay-per-token | Varies |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Missing API key` | Ensure `.env` exists in the provider folder with a real key |
| `Vector database not found` | Run `python ingest.py document.pdf` first |
| `Module not found` | Run `pip install -r requirements.txt` from the provider folder |
| `CORS error in dashboard` | Add your origin to `ALLOWED_ORIGINS` in `fastAPI/.env` |
| `chainlit: cannot import qa_bot` | Set `QUOT_DIR=<provider>` before running |
| Rate limit / quota exhausted | Wait or switch provider via `multi/` |

### Reset the vector database

```bash
rm -rf chroma_db
python ingest.py document.pdf
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-provider`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Built With

- [LangChain](https://langchain.com/) — LLM application framework
- [ChromaDB](https://www.trychroma.com/) — Vector database
- [Streamlit](https://streamlit.io/) — Web UI
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [Chainlit](https://chainlit.io/) — Chat interface
- [Vite + React](https://vitejs.dev/) — Dashboard frontend
