from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from backend.models.chunk import Chunk


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + lowercase tokenizer. Good enough for BM25."""
    return text.lower().split()


def bm25_search(db: Session, workspace_id, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
    """
    Keyword search over all chunks in a workspace using BM25.
    Returns a list of (Chunk, score) tuples, highest score first.

    Note: this recomputes BM25 over the workspace's chunks on every call.
    That's fine for learning and small/medium workspaces. A production system
    would maintain a persistent BM25 index (e.g. via Elasticsearch/OpenSearch)
    instead of rebuilding it per query — a known tradeoff, noted for later.
    """
    chunks = db.query(Chunk).filter(Chunk.workspace_id == workspace_id).all()

    if not chunks:
        return []

    tokenized_corpus = [_tokenize(chunk.text) for chunk in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return scored_chunks[:top_k]