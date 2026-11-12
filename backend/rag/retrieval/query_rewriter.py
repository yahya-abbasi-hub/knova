from backend.rag.generation.llm_provider import get_llm_provider

REWRITE_SYSTEM_PROMPT = """You rewrite user questions to be clearer and more \
complete for a document search system. Do not answer the question. Do not add \
information that wasn't implied by the original question. If the question is \
already clear and complete, return it unchanged.

Return ONLY the rewritten question, nothing else — no explanation, no quotes."""


def rewrite_query(question: str) -> str:
    """
    Expands/clarifies a user's question using the LLM before retrieval.
    Falls back to the original question if rewriting fails for any reason —
    retrieval should never be blocked by this being unavailable.
    """
    try:
        provider = get_llm_provider()
        rewritten = provider.generate(REWRITE_SYSTEM_PROMPT, question)
        rewritten = rewritten.strip()
        return rewritten if rewritten else question
    except Exception:
        return question