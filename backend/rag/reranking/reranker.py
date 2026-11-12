from sentence_transformers import CrossEncoder

from backend.core.logging import get_logger

logger = get_logger(__name__)

_reranker_model = None


def get_reranker() -> CrossEncoder:
    global _reranker_model
    if _reranker_model is None:
        logger.info("Loading reranker model: cross-encoder/ms-marco-MiniLM-L-6-v2")
        _reranker_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker_model


def rerank(query: str, chunks: list, top_k: int = 5) -> list:
    """
    Takes a list of candidate Chunk objects and reorders them by how
    relevant each one actually is to the query, using a cross-encoder.
    Returns the top_k most relevant chunks.
    """
    if not chunks:
        return []

    model = get_reranker()
    pairs = [(query, chunk.text) for chunk in chunks]
    scores = model.predict(pairs)

    scored_chunks = list(zip(chunks, scores))
    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    return [chunk for chunk, score in scored_chunks[:top_k]]