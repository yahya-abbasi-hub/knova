from sqlalchemy.orm import Session

from backend.models.document import Document
from backend.models.chunk import Chunk
from backend.ingestion.extraction.extractors import extract_text
from backend.ingestion.chunking.chunker import chunk_text
from backend.rag.embeddings.embedder import embed_texts
from backend.rag.retrieval.vector_store import ensure_collection_exists, upsert_chunk_vector
from backend.core.logging import get_logger
from backend.core.security_checks import scan_for_injection_attempts

logger = get_logger(__name__)


def process_document(document_id, db_session_factory):
    db: Session = db_session_factory()

    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            logger.error(f"process_document: document {document_id} not found")
            return

        document.status = "processing"
        db.commit()

        # 1. Extract text
        text, page_count = extract_text(document.file_path, document.file_type)
        document.page_count = page_count
        # Security: log any suspicious injection-like patterns (doesn't block)
        scan_for_injection_attempts(text, document.id, document.filename)

        # 2. Chunk the extracted text
        chunk_texts = chunk_text(text, chunk_size=500, overlap=50)

        if not chunk_texts:
            raise ValueError("No text could be extracted from this document")

        # 3. Save chunk rows to PostgreSQL first, so each has a real id
        chunks = []
        for index, chunk_content in enumerate(chunk_texts):
            chunk = Chunk(
                document_id=document.id,
                workspace_id=document.workspace_id,
                chunk_index=index,
                text=chunk_content,
                char_count=len(chunk_content),
            )
            db.add(chunk)
            chunks.append(chunk)

        db.flush()  # assigns real IDs to each chunk without fully committing yet

        # 4. Embed all chunks in one batch call (efficient)
        vectors = embed_texts([c.text for c in chunks])

        # 5. Store each vector in Qdrant
        ensure_collection_exists(vector_size=len(vectors[0]))
        for chunk, vector in zip(chunks, vectors):
            upsert_chunk_vector(
                chunk_id=chunk.id,
                vector=vector,
                document_id=document.id,
                workspace_id=document.workspace_id,
                chunk_index=chunk.chunk_index,
            )

        document.status = "ready"
        document.error_message = None
        db.commit()

        logger.info(
            f"Document {document_id} processed successfully "
            f"({page_count} pages, {len(chunks)} chunks embedded and stored)"
        )

    except Exception as e:
        logger.error(f"Document {document_id} processing failed: {e}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "failed"
            document.error_message = str(e)
            db.commit()

    finally:
        db.close()