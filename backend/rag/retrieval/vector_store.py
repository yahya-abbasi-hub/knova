import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import FilterSelector
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

_client = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _client


def ensure_collection_exists(vector_size: int = 384):
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]

    if settings.QDRANT_COLLECTION_NAME not in existing:
        logger.info(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION_NAME}")
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def upsert_chunk_vector(
    chunk_id: uuid.UUID,
    vector: list[float],
    document_id: uuid.UUID,
    workspace_id: uuid.UUID,
    chunk_index: int,
):
    client = get_qdrant_client()
    client.upsert(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(chunk_id),
                vector=vector,
                payload={
                    "document_id": str(document_id),
                    "workspace_id": str(workspace_id),
                    "chunk_index": chunk_index,
                },
            )
        ],
    )


def search_similar_chunks(
    query_vector: list[float],
    workspace_id,
    top_k: int = 5,
    score_threshold: float = 0.3,
):
    client = get_qdrant_client()

    results = client.query_points(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="workspace_id",
                    match=MatchValue(value=str(workspace_id)),
                )
            ]
        ),
        limit=top_k,
        score_threshold=score_threshold,
    )
    return results.points

def delete_chunks_by_document(document_id):
    """Removes all vectors belonging to one document from Qdrant."""
    client = get_qdrant_client()
    client.delete(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=str(document_id)),
                    )
                ]
            )
        ),
    )