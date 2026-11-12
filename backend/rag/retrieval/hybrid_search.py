import uuid

from sqlalchemy.orm import Session

from backend.models.chunk import Chunk
from backend.rag.embeddings.embedder import embed_text
from backend.rag.retrieval.vector_store import search_similar_chunks
from backend.rag.retrieval.keyword_search import bm25_search


def _normalize_scores(scores: list[float]) -> list[float]:
    """Scales a list of scores to the 0-1 range, so vector scores and BM25
    scores (which use completely different scales) can be fairly combined."""
    if not scores:
        return []
    min_s, max_s = min(scores), max(scores)
    if max_s == min_s:
        return [1.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]


def hybrid_search(
    db: Session,
    workspace_id: uuid.UUID,
    query: str,
    top_k: int = 10,
    vector_weight: float = 0.6,
    keyword_weight: float = 0.4,
) -> list[Chunk]:
    """
    Combines vector search and BM25 keyword search into one ranked list.
    Returns plain Chunk objects, ordered by combined relevance score.
    """
    # 1. Vector search
    query_vector = embed_text(query)
    vector_results = search_similar_chunks(query_vector, workspace_id, top_k=top_k)
    vector_chunk_ids = [point.id for point in vector_results]
    vector_scores_raw = [point.score for point in vector_results]
    vector_scores_norm = _normalize_scores(vector_scores_raw)

    # 2. Keyword (BM25) search
    bm25_results = bm25_search(db, workspace_id, query, top_k=top_k)
    bm25_chunk_ids = [str(chunk.id) for chunk, _ in bm25_results]
    bm25_scores_raw = [score for _, score in bm25_results]
    bm25_scores_norm = _normalize_scores(bm25_scores_raw)

    # 3. Combine into one dict: chunk_id -> combined_score
    combined_scores: dict[str, float] = {}

    for chunk_id, score in zip(vector_chunk_ids, vector_scores_norm):
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * vector_weight

    for chunk_id, score in zip(bm25_chunk_ids, bm25_scores_norm):
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * keyword_weight

    # 4. Sort by combined score, take top_k
    ranked_ids = sorted(combined_scores, key=combined_scores.get, reverse=True)[:top_k]

    # 5. Fetch full Chunk objects, preserving rank order
    chunks = db.query(Chunk).filter(Chunk.id.in_([uuid.UUID(cid) for cid in ranked_ids])).all()
    chunks_by_id = {str(c.id): c for c in chunks}
    ordered_chunks = [chunks_by_id[cid] for cid in ranked_ids if cid in chunks_by_id]

    return ordered_chunks