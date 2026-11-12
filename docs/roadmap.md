# KNOVA — Full Roadmap

This is the complete build plan, broken into phases. Check items off as completed.
Pair this with docs/progress.md (which tracks what's actually done + gotchas).

---

## PHASE 1 — Foundation (current phase)
- [x] FastAPI app skeleton (main.py)
- [x] Config system (core/config.py)
- [x] Logging (core/logging.py)
- [x] Custom exceptions (core/exceptions.py)
- [x] PostgreSQL installed + connected
- [x] Database session layer (database/session.py)
- [x] User model + Alembic migrations
- [x] Auth: password hashing, JWT (core/security.py)
- [x] Auth: register/login routes + schemas
- [x] Protected route pattern (dependencies.py, /auth/me)
- [x] Workspace model (models/workspace.py) ← IN PROGRESS
- [x] Workspace migration (alembic revision --autogenerate)
- [x] Workspace schemas (schemas/workspace.py)
- [x] Workspace service (services/workspace_service.py)
- [x] Workspace routes: create, list mine, get one, delete
      (api/routes/workspaces.py — all protected via get_current_user)
- [x] Enforce ownership: a user can only see/edit their own workspaces

## PHASE 2 — Document Upload & Processing
- [x] Document model (models/document.py) — belongs to workspace + user,
      stores filename, file_type, status, page_count, etc.
- [x] Document migration
- [x] File upload route (api/routes/documents.py) — accepts PDF/DOCX/TXT first,
      expand to CSV/XLSX/PPTX/images later
- [x] File validation (core/exceptions.py ValidationError for bad types/size)
- [x] Save uploaded file to disk (data/raw/) with a safe generated filename
- [x] Text extraction:
      - PDF → PyMuPDF
      - DOCX → python-docx
      - TXT → plain read
      (ingestion/extraction/ folder, one extractor per file type)
- [x] Document status tracking (uploaded → processing → ready/failed)
- [x] Background processing (so upload doesn't block the HTTP response) —
      start simple with FastAPI BackgroundTasks, upgrade to Celery/Redis later
      if needed

## PHASE 3 — Chunking & Embeddings
- [x] Chunking strategy (ingestion/chunking/) — split extracted text into
      overlapping chunks (e.g. 500 tokens, 50 token overlap) while preserving
      page/section metadata
- [x] Choose + integrate embedding model (BGE via sentence-transformers,
      local, free — avoids API costs while learning)
- [x] rag/embeddings/ — wrapper service to turn text chunks into vectors
- [x] Install + run Qdrant (Docker container, simplest route)
- [x] rag/retrieval/ — Qdrant client wrapper: upsert vectors with metadata
      (document_id, workspace_id, user_id, page, chunk_id)
- [x] Wire ingestion pipeline end-to-end: upload → extract → chunk → embed →
      store in Qdrant → mark document "ready"

## PHASE 4 — Basic RAG Q&A (first real "chat with docs")
- [x] Chat schemas (ask a question, get an answer + sources)
- [x] Vector similarity search against Qdrant, scoped to workspace_id
- [x] LLM provider abstraction (rag/generation/ or core/llm_provider.py) —
      interface so we can swap OpenAI/Groq/Gemini later without rewriting
      everything else
- [x] Prompt template: inject retrieved chunks as context, instruct LLM to
      answer ONLY from context, say "not enough information" if context is weak
- [x] Citations: return source document + page alongside the answer
- [x] POST /chat/ask route — this is the first real "RAG" milestone

## PHASE 5 — Hybrid Search & Reranking (upgrade retrieval quality)
- [x] BM25 keyword search alongside vector search
- [x] Combine vector + keyword results (hybrid retrieval)
- [x] Integrate a reranker (BGE reranker or cross-encoder) to reorder
      candidates by relevance before sending to the LLM
- [x] Query rewriting/expansion (have the LLM reformulate vague questions
      before retrieval)

## PHASE 6 — Prompt Injection Protection & Hallucination Control
- [x] Clearly separate system prompt / retrieved content / user input in
      every LLM call (never concatenate untrusted text into instructions)
- [x] Add a grounding-confidence check before generating an answer
- [x] Explicit "insufficient evidence" response path (skip LLM call entirely
      if retrieval returns nothing relevant)
- [x] Basic tests simulating prompt injection attempts inside documents

## PHASE 7 — Multi-user & Permissions
- [x] Workspace roles (owner/admin/member/viewer) — extend workspace model
- [ ] Enforce permission checks at the service layer (not just frontend)
- [ ] Organization model (optional, if going multi-tenant B2B)

## PHASE 8 — Evaluation System
- [x] Build a small evaluation dataset (sample questions + expected answers
      from your own test documents)
- [ ] Retrieval metrics: precision, recall, hit rate
- [ ] Generation metrics: faithfulness, answer relevance, citation accuracy
- [ ] Script to run evals automatically (scripts/evaluate.py)

## PHASE 9 — Analytics Dashboard
- [ ] Track queries, latency, token usage, failures (simple DB table first)
- [ ] Analytics routes (api/routes/analytics.py)
- [ ] Admin-only extended analytics

## PHASE 10 — Advanced Features
- [ ] Research mode (break complex questions into sub-tasks)
- [ ] Multi-document comparison mode
- [ ] Observability (Langfuse integration)

## PHASE 11 — Frontend
- [ ] Streamlit app (frontend/streamlit_app.py) — login, dashboard, upload,
      chat, search — wired to the FastAPI backend via HTTP calls
- [ ] (Later, separate effort) Next.js frontend, reusing the same API

## PHASE 12 — Deployment
- [ ] Dockerfile for backend
- [ ] docker-compose.yml (backend + Postgres + Qdrant + Redis together)
- [ ] Environment-specific configs (dev vs production)
- [ ] Basic CI (GitHub Actions running pytest on push)

---

## How to resume in a new chat
1. Paste the contents of docs/progress.md (what's done + gotchas)
2. Paste the contents of this file (docs/roadmap.md), or just say which
   phase/step you're on
3. Say: "Continue from [step name]"