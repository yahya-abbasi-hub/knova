from sentence_transformers import SentenceTransformer

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

_model = None  # loaded once, reused for every embedding call


def get_embedding_model() -> SentenceTransformer:
    """
    Loads the embedding model once (lazily, on first use) and reuses it.
    Loading the model is slow (a few seconds), so we never want to reload
    it for every single chunk or request.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """Turns a single piece of text into a vector (list of floats)."""
    model = get_embedding_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turns multiple texts into vectors in one batch call — much faster
    than calling embed_text() in a loop, since the model processes them together."""
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()