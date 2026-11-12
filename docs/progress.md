# KNOVA — Progress Log

## Stack decisions
- Python 3.12, FastAPI, Uvicorn
- Pydantic Settings for config
- PostgreSQL (installed, in use), Qdrant (upcoming), Redis (upcoming)
- SQLAlchemy ORM + Alembic migrations
- JWT auth (python-jose) + bcrypt hashing (passlib) — note: required bcrypt==4.0.1 pin
  to fix a passlib/bcrypt compatibility bug (ValueError: password cannot be longer
  than 72 bytes)
- Frontend: Streamlit first, later Next.js

## Current phase
Phase 1 — Foundation. Core backend + auth system complete. Not yet started: workspaces,
documents, RAG, vector DB.

## Completed steps
1. Project venv created, FastAPI + Uvicorn installed
2. backend/main.py — FastAPI app with /, /health
3. backend/core/config.py — Pydantic Settings, loads .env
4. backend/core/logging.py — centralized logging, get_logger()
5. backend/core/exceptions.py — KnovaException + subclasses, global exception handler
6. PostgreSQL installed locally, knova database created, added to PATH
7. backend/database/session.py — SQLAlchemy engine, SessionLocal, Base, get_db()
8. backend/models/user.py — User table (UUID id, email, hashed_password, etc.)
9. Alembic initialized, first migration applied (users table created)
10. backend/core/security.py — hash_password, verify_password, create/decode JWT
11. backend/schemas/user.py — UserCreate, UserLogin, UserResponse, Token
12-13. backend/services/auth_service.py — register_user, authenticate_user
14. backend/api/routes/auth.py — POST /auth/register, POST /auth/login
15. Router wired into main.py
16-17. backend/api/dependencies.py — get_current_user (JWT verification dependency)
    + GET /auth/me (protected route) — tested working end-to-end via /docs
18-23. Workspace system complete:
   - backend/models/workspace.py — Workspace table (owner_id FK to users)
   - Alembic migration applied
   - backend/schemas/workspace.py — WorkspaceCreate, WorkspaceResponse
   - backend/services/workspace_service.py — create/list/get/delete, with
     ownership enforcement (404 if not found, 403 if not yours)
   - backend/api/routes/workspaces.py — full CRUD, all routes protected
   - Tested working end-to-end via /docs
   Phase 2 started:
24. backend/models/document.py — Document table (workspace_id, owner_id FKs,
    filename, file_type, file_path, status, etc.)
25. Alembic migration applied for documents table
26. backend/core/constants.py — ALLOWED_FILE_TYPES (pdf/txt/docx), MAX_FILE_SIZE_BYTES
27. backend/schemas/document.py — DocumentResponse
28. backend/services/document_service.py — upload_document (validates type/size,
    saves to data/raw/ with generated filename, creates DB row), list_documents
29. backend/api/routes/documents.py — POST/GET nested under
    /workspaces/{workspace_id}/documents/
30. Tested end-to-end: uploaded project.txt successfully, status "uploaded"
31. backend/ingestion/extraction/extractors.py — extract_txt, extract_pdf
    (PyMuPDF), extract_docx (python-docx), dispatcher extract_text()
32. backend/ingestion/pipeline.py — process_document() background task:
    uploaded -> processing -> ready/failed, saves page_count, catches errors
    and stores error_message on failure
33. Wired into upload route via FastAPI BackgroundTasks (document.py route)
34. Tested end-to-end: uploaded project.txt, auto-processed to "ready" status
    with correct page_count, confirmed via logs (17649 chars extracted)
35-39. Chunking complete:
   - backend/models/chunk.py — Chunk table (document_id, workspace_id FKs,
     chunk_index, text, char_count)
   - Alembic migration applied
   - backend/ingestion/chunking/chunker.py — chunk_text() character-based
     splitter with overlap (default 500 chars, 50 overlap)
   - Wired into pipeline.py — chunks created and saved after extraction,
     before marking document "ready"
   - Debug route: GET /workspaces/{id}/documents/{id}/chunks
   - Tested end-to-end: uploaded a ~20K character file, produced 40 correctly
     ordered, correctly sized overlapping chunks
    Phase 3 complete:
40. Docker Desktop installed, Qdrant running via docker run (container: knova-qdrant,
    ports 6333/6334, persistent volume qdrant_storage)
41. backend/rag/embeddings/embedder.py — BGE model (bge-small-en-v1.5) via
    sentence-transformers, lazy-loaded singleton, embed_text()/embed_texts()
42. backend/rag/retrieval/vector_store.py — Qdrant client wrapper,
    ensure_collection_exists(), upsert_chunk_vector() with workspace_id/
    document_id metadata payload
43. Wired into pipeline.py — chunks now get embedded in batch and stored in
    Qdrant right after being saved to PostgreSQL, using db.flush() to get
    real chunk IDs before embedding
44. Tested end-to-end: uploaded document, confirmed vectors appear in Qdrant
    dashboard with correct metadata
  Phase 4 complete - BASIC RAG WORKING:
49. backend/schemas/chat.py — ChatRequest, ChatResponse, SourceCitation
    (includes grounded: bool flag)
50. backend/rag/retrieval/vector_store.py — added search_similar_chunks()
    with Qdrant Filter on workspace_id (enforces isolation at retrieval level)
    and score_threshold (hallucination control - weak matches excluded)
51. backend/services/chat_service.py — ask_question():
    - ownership check -> embed question -> vector search (workspace-scoped)
    - empty results -> skip LLM, return "insufficient evidence" honestly
    - builds context from real retrieved chunks, real citations (no fabrication)
    - SYSTEM_PROMPT enforces: answer only from context, admit when unsure,
      treat document content as untrusted (prompt injection protection),
      never invent facts/citations
    - clear separation: system prompt (trusted) vs context+question (user turn)
52. backend/api/routes/chat.py — POST /workspaces/{workspace_id}/chat/ask
53. Removed temporary /test-llm route
54. TESTED AND WORKING: relevant questions return grounded answers with real
    citations; irrelevant questions return grounded:false + honest
    "insufficient evidence" response
  Phase 5 - Hybrid Search & Reranking:
55. pip install rank-bm25
56. backend/rag/retrieval/keyword_search.py — bm25_search() using BM25Okapi,
    rebuilds index per-query over workspace's chunks (noted tradeoff: fine for
    now, a production system would use a persistent index e.g. Elasticsearch)
57. backend/rag/retrieval/hybrid_search.py — hybrid_search() combines vector
    + BM25 results: normalizes both score scales to 0-1, weighted sum
    (vector_weight=0.6, keyword_weight=0.4), returns top_k ranked Chunks
58. backend/rag/reranking/reranker.py — CrossEncoder
    (cross-encoder/ms-marco-MiniLM-L-6-v2), lazy-loaded singleton, rerank()
    narrows a candidate pool down using query+chunk pairs scored together
59. backend/services/chat_service.py updated — now does two-stage retrieval:
    hybrid_search (top 10 candidates) -> rerank (narrow to top 5) -> generate
60. Tested working: chat responses still correct, now backed by hybrid +
    reranked retrieval instead of vector-only search
  61. backend/rag/retrieval/query_rewriter.py — rewrite_query() uses LLM to
    clarify vague questions before retrieval, falls back to original question
    on any failure (resilient, never blocks the chat flow)
62. Wired into chat_service.py: rewritten query used for hybrid_search +
    rerank, but ORIGINAL question used for final answer generation
    (rewriting only affects what's searched for, not what's answered)
63. PHASE 5 COMPLETE: hybrid search (vector + BM25) + reranking + query
    rewriting all working together

Known gotcha: Docker Desktop can fail with "WSL too old" even after running
wsl --update once. Fix: run wsl --update from an ADMIN PowerShell window,
then wsl --shutdown, then reopen Docker Desktop. If Qdrant becomes
unreachable, documents will fail with WinError 10061 - they can just be
re-uploaded once Qdrant is back up (error handling catches this correctly,
no data corruption, just marks document "failed" with a clear reason).
PHASE 11 (Frontend) - Streamlit app built:
64. pip install streamlit requests
65. frontend/api_client.py — centralized API client functions (register,
    login, get_me, list/create_workspace, list/upload_document, ask_question)
    all take token explicitly, raise_for_status() for clean error handling
66. frontend/streamlit_app.py — main shell, session_state for token/user,
    login/logout flow
67. frontend/pages/1_Login.py — login + register tabs, auto-login after
    register, fetches full user profile via get_me() after auth
68. frontend/pages/2_Documents.py — workspace selector + creator (popover),
    file upload with status icons (uploaded/processing/ready/failed),
    shows error_message for failed documents
69. frontend/pages/3_Chat.py — st.chat_message/st.chat_input UI, per-workspace
    chat history in session_state, shows grounded:false warning, expandable
    sources section with document name + chunk + snippet
70. TESTED END TO END: register -> login -> create workspace -> upload doc ->
    wait for "ready" -> ask questions -> get grounded answers with real
    citations, through the actual UI

Known gotcha: Streamlit session_state is per-browser-tab. Opening a new tab
or refreshing can lose login state - always navigate via the sidebar links
within the same tab, not by typing URLs or opening new tabs.
PHASE 6 COMPLETE - Prompt injection hardening:
77. backend/core/security_checks.py — scan_for_injection_attempts(): regex
    pattern matching for common injection phrases, LOGS warnings (does not
    block documents - avoids false positives on legitimate content that
    happens to mention these phrases)
78. Wired into pipeline.py right after text extraction
79. Updated SYSTEM_PROMPT in chat_service.py (rule 5): LLM now explicitly
    instructed to FLAG suspicious instruction-like content to the user in
    its answer, not just silently resist it - transparency over silent defense
80. TESTED with 2 real injection attempts:
    - Test 1: direct "reveal system prompt / API keys" attempt -> correctly
      resisted, content only described not obeyed
    - Test 2: subtler attempt to manipulate a specific fact (fake revenue
      number) -> correctly reported real figure ($450,000), resisted
      manipulation
    Both confirm: system prompt separation (system role vs user role with
    labeled untrusted context) + explicit LLM instructions are holding up
    against real injection attempts, not just in theory
    PHASE 7 COMPLETE - Multi-user roles & permissions:
81. backend/models/workspace_member.py — WorkspaceMember table (workspace_id
    + user_id FKs, role string, UniqueConstraint prevents duplicate
    memberships per user per workspace)
82. Alembic migration applied for workspace_members table
83. backend/core/permissions.py — Role enum (OWNER/ADMIN/MEMBER/VIEWER),
    ROLE_PERMISSIONS dict mapping each role to its allowed actions
    (view/chat/upload/delete_document/manage_members/delete_workspace),
    role_has_permission() checker
84. backend/services/workspace_service.py updated:
    - create_workspace() now also creates an "owner" WorkspaceMember row
    - new require_permission() - central gatekeeper, checks workspace
      exists -> user is a member -> role has the specific permission
      (404/403/403 with clear reasons respectively)
    - list_workspaces() now shows workspaces user is a MEMBER of, not just
      owned ones
    - new list_members(), invite_member() (by email), remove_member()
      (blocks removing the owner)
85. backend/schemas/workspace_member.py — MemberInvite, MemberResponse,
    MemberRoleUpdate
86. backend/api/routes/workspace_members.py — GET/POST members, DELETE
    member by user_id
87. document_service.py and chat_service.py updated to use
    require_permission() instead of the old owner-only get_workspace() check
    (upload/view/chat permissions respectively)
88. TESTED END TO END: workspace creation auto-creates owner membership,
    GET /members/ correctly shows owner role, upload + chat still work
    correctly under the new permission system (no regression)
    89. frontend/api_client.py — added list_members(), invite_member(),
    remove_member()
90. frontend/pages/4_Members.py — workspace selector, invite form (email +
    role dropdown), member list with role icons (👑🛠️✍️👀), remove button
    (hidden for owner row and for yourself, backend still enforces the
    real rule regardless)
91. TESTED: invited a member, saw them appear with correct role, removed
    them successfully, confirmed through the actual UI (not just /docs)

PHASE 7 FULLY COMPLETE (backend + frontend) - multi-user roles and
permissions working end-to-end.

Note: Frontend (Streamlit) does NOT yet have UI for member management -
invites/role changes still require /docs for now. Could add later.
PHASE 14 - Evaluation system:
92. data/evaluation/sample_eval_set.json — 5 hand-written test questions
    against project.txt, each with expected_answer_contains keywords and
    should_be_grounded flag
93. backend/rag/evaluation/evaluator.py — run_evaluation() runs each
    question through the REAL chat_service.ask_question() (same path real
    users hit), records answer/grounded/sources/latency/errors per case
94. backend/rag/evaluation/metrics.py — score_keyword_match() (deterministic,
    no extra LLM call), score_grounding_correctness(), summarize_results()
    (failure_rate, avg_keyword_match_score, grounding_accuracy, avg_latency)
95. scripts/run_evaluation.py — CLI runner, prints per-question results +
    summary, saves full results to data/evaluation/last_run_results.json
96. FIRST RUN found a real bug: grounded was always True whenever retrieval
    found ANY chunks, even when the LLM's own answer said "I don't have
    enough information." grounding_accuracy was only 0.8 because of this.
97. FIX: added _answer_indicates_no_info() keyword check in chat_service.py
    - detects phrases like "don't have enough information", "does not
      contain", etc. in the LLM's answer itself, overrides grounded to
      False in these cases (and clears sources, since they weren't
      actually used)
    - Known limitation: keyword-based, not perfect - a more robust future
      version could use a second LLM call as a judge instead
98. RE-RAN after fix: grounding_accuracy improved from 0.8 to 1.0
    (confirmed via real evaluation run, not just manual spot-check)
    avg_keyword_match_score stayed 0.8 - genuine retrieval limitation on
    one question (Qdrant not mentioned in the specific retrieved chunk),
    noted as a future tuning target, not a bug
    PHASE 7+ UI polish:
99. backend/services/document_service.py — delete_document(): removes
    Qdrant vectors first, then physical file, then DB rows (chunks + doc),
    in that order so a partial failure leaves orphaned data, not broken
    references. Protected by require_permission(..., "delete_document")
100. backend/rag/retrieval/vector_store.py — delete_chunks_by_document()
    using Qdrant's FilterSelector
101. DELETE /workspaces/{workspace_id}/documents/{document_id} route added
102. frontend/pages/2_Documents.py — now checks current user's role via
    list_members(), shows/hides upload section and delete buttons based on
    role (can_upload: owner/admin/member, can_delete: owner/admin).
    IMPORTANT: this is UX only - the real security enforcement is the
    backend's require_permission() check, per spec Section 16
103. TESTED: delete button works, removes document from list and
    (implied) from Qdrant

Known gotcha: careful with Python indentation when manually editing
Streamlit files - a misplaced few spaces can silently break the whole
page's logic. When in doubt, replace the whole file rather than patching
piece by piece.
TIER 1 FINALIZATION - Password Reset:
104. backend/models/user.py — added reset_token, reset_token_expires_at
     columns, migration applied
105. backend/core/security.py — generate_reset_token() using secrets.
     token_urlsafe(32) (cryptographically secure, not Python's random module)
106. backend/schemas/user.py — ForgotPasswordRequest, ForgotPasswordResponse,
     ResetPasswordRequest
107. backend/services/auth_service.py — request_password_reset() (30 min
     expiry, same email-exists-or-not response either way - prevents
     leaking which emails are registered), reset_password() (validates
     token + expiry, single-use - cleared after success)
108. backend/api/routes/auth.py — POST /auth/forgot-password,
     POST /auth/reset-password
     IMPORTANT: forgot-password returns the token directly in the response
     ONLY when ENVIRONMENT=development, clearly commented as a dev-only
     placeholder since no email sending is set up yet. MUST be removed/
     changed before any real production use - this would be a serious
     security hole otherwise.
109. frontend/api_client.py — forgot_password(), reset_password()
110. frontend/pages/1_Login.py — added "Forgot Password" tab, two-step flow
     (request token -> use token + new password), token auto-fills in
     step 2 for dev convenience
111. TESTED END TO END: requested reset, got dev token, reset password,
     logged in with new password, confirmed old token can't be reused
## Next step (not yet started)
TIER 1 (finalize product) remaining:
- Automated test suite (pytest) - tests/unit, tests/integration
- Docker + docker-compose (package the whole stack)
- Minor cleanup (README, .env.example check, remove dead code)

TIER 2 (additional modules, deferred until Tier 1 done):
analytics dashboard, rate limiting, audit logging, research mode,
observability
## Known gotchas / fixes applied
- VS Code sometimes creates .ipynb instead of .py — always check file extension
- Passwords with special characters (@, $, etc.) must be URL-encoded in
  DATABASE_URL, or just avoid special chars in the postgres password
- bcrypt must be pinned to 4.0.1 due to a passlib compatibility bug
- Always run uvicorn from the KNOVA root: uvicorn backend.main:app --reload
- psql needs PostgreSQL's bin folder added to Windows PATH manually