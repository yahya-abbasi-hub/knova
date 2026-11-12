def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits text into overlapping chunks.

    chunk_size: target number of characters per chunk
    overlap: number of characters repeated at the start of the next chunk,
             so context isn't lost at chunk boundaries
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap  # step forward, but re-include the overlap region

    return chunks