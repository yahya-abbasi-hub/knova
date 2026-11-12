# KNOVA — AI Knowledge Intelligence Platform

KNOVA is a full-stack, production-style Retrieval-Augmented Generation (RAG)
platform. Users create workspaces, upload documents, and ask natural-language
questions that are answered using their own content — with citations, and
with honest "I don't have enough information" responses when evidence is
insufficient, instead of hallucinated answers.

## Features

- **Authentication**: JWT-based register/login, password reset
- **Multi-user workspaces**: role-based permissions (owner/admin/member/viewer),
  enforced at the backend/database level, not just hidden in the UI
- **Document ingestion**: PDF, DOCX, TXT, CSV, XLSX, PPTX, and images (via OCR),
  with automatic background processing (extract → chunk → embed → store)
- **Hybrid retrieval**: vector search (semantic) + BM25 (keyword), combined
  and reranked with a cross-encoder for higher-quality results
- **Query rewriting**: vague questions are clarified by the LLM before retrieval
- **Grounded generation**: answers are built only from retrieved context, with
  real source citations (document + chunk), never fabricated
- **Hallucination control**: the system explicitly declines to answer when
  retrieval confidence is too low, rather than guessing
- **Prompt injection hardening**: retrieved document content is treated as
  untrusted data, never as instructions — tested against real injection attempts
- **Evaluation system**: a scripted eval pipeline measuring retrieval accuracy,
  grounding correctness, and latency — not just manual spot-checks
- **Automated tests**: pytest suite covering auth and workspace isolation
- **Full Streamlit frontend**: login, workspace/document management, chat
  with citations, member management — all role-aware

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL (via SQLAlchemy + Alembic migrations) |
| Vector DB | Qdrant |
| Embeddings | BGE (`bge-small-en-v1.5`) via sentence-transformers |
| Reranking | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| Keyword search | BM25 (`rank-bm25`) |
| LLM | Groq (pluggable provider abstraction — easy to swap) |
| Auth | JWT (`python-jose`) + bcrypt (`passlib`) |
| Frontend | Streamlit |
| Testing | pytest |
| Containerization | Docker / docker-compose (see note below) |

## Project Structure
KNOVA/
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── api/routes/ # auth, workspaces, documents, chat, members
│ ├── core/ # config, logging, security, exceptions, permissions
│ ├── models/ # SQLAlchemy models (User, Workspace, Document, Chunk, ...)
│ ├── schemas/ # Pydantic request/response schemas
│ ├── services/ # business logic
│ ├── ingestion/ # extraction + chunking pipeline
│ └── rag/ # embeddings, retrieval, reranking, generation, evaluation
├── frontend/ # Streamlit app
├── alembic/ # database migrations
├── tests/ # pytest suite
├── scripts/ # evaluation runner
├── data/ # uploaded files + evaluation sets
└── docs/ # progress log + roadmap

## Setup (local, manual — recommended)

### Prerequisites
- Python 3.12
- PostgreSQL (installed locally, running on port 5432)
- Docker (for running Qdrant)
- Tesseract OCR (for image text extraction) — [installer here](https://github.com/UB-Mannheim/tesseract/wiki), add to PATH
- A free [Groq API key](https://console.groq.com)

### Steps

1. **Clone and set up the virtual environment**
   ```bash
   git clone https://github.com/YOUR_USERNAME/knova.git
   cd knova
   python -m venv venv
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

2. **Create the PostgreSQL database**
   ```bash
   psql -U postgres
   CREATE DATABASE knova;
   \q
   ```

3. **Run Qdrant**
   ```bash
   docker run -d --name knova-qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your real values:
   ```bash
   copy .env.example .env
   ```
   You'll need to set: `DATABASE_URL` (your Postgres password), `JWT_SECRET_KEY`
   (generate with `python -c "import secrets; print(secrets.token_hex(32))"`),
   and `GROQ_API_KEY`.

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend**
   ```bash
   uvicorn backend.main:app --reload
   ```

7. **Start the frontend** (in a separate terminal)
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

8. **Open the app**
   - Frontend: http://localhost:8501
   - API docs: http://localhost:8000/docs

## Running Tests

Tests use a separate database to avoid touching your real data.

```bash
psql -U postgres
CREATE DATABASE knova_test;
\q
```

Create `.env.test` (same format as `.env`, pointing `DATABASE_URL` at `knova_test`
and using a separate Qdrant collection name), then:

```bash
pytest tests/unit/ -v
```

## Running an Evaluation

```bash
python scripts/run_evaluation.py <workspace_id> <your_user_id>
```
Get both IDs from `/docs` (`GET /workspaces/`, `GET /auth/me`). Results are
printed and saved to `data/evaluation/last_run_results.json`.

## Docker

A `Dockerfile` and `docker-compose.yml` are included for containerized
deployment. **Note**: during development, full-stack Docker builds proved
resource-intensive on some machines (particularly the PyTorch/sentence-transformers
dependencies). The manual setup above is currently the more reliable path;
Docker support is present but may need tuning (build resources, CPU-only
PyTorch wheels) for your specific environment.

```bash
docker-compose --env-file .env.docker up --build
docker-compose --env-file .env.docker exec backend alembic upgrade head
```

## Security Notes

- The `/auth/forgot-password` endpoint returns the reset token directly in
  the API response **only** when `ENVIRONMENT=development` — this is a
  development convenience since email sending isn't implemented yet. This
  must be changed before any production deployment (the token should be
  emailed, never returned in the response).
- Permissions (workspace roles) are enforced at the backend/service layer,
  not just hidden in the UI.

## Project Status

Core product complete: authentication, multi-user workspace permissions,
full multi-format document ingestion, hybrid RAG with reranking and query
rewriting, grounded generation with hallucination control, prompt injection
hardening, an evaluation system, and a complete frontend. See
`docs/progress.md` for the full development history and `docs/roadmap.md`
for remaining/future work (analytics dashboard, rate limiting, research mode,
observability, production-ready Docker setup).

