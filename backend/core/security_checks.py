import re

from backend.core.logging import get_logger

logger = get_logger(__name__)

# Patterns commonly seen in prompt injection attempts.
# This is NOT meant to block anything - just to flag/log suspicious content
# for visibility. Blocking legitimate documents that happen to mention these
# phrases (e.g. a security training doc) would be worse than just logging.
SUSPICIOUS_PATTERNS = [
    r"ignore (all |previous |above )?instructions",
    r"system (prompt|message)",
    r"you are now in (unrestricted|admin|developer) mode",
    r"reveal (your |the )?(system prompt|api key|secret)",
    r"disregard (all |previous )?(rules|instructions|guidelines)",
    r"do not (mention|tell|reveal) this (to the user|instruction)",
]

_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS]


def scan_for_injection_attempts(text: str, document_id, filename: str) -> list[str]:
    """
    Scans extracted text for known prompt-injection patterns.
    Returns a list of matched pattern descriptions (empty list = nothing found).
    This is purely for logging/visibility - it does NOT block the document
    from being processed. The LLM's own instructions (system prompt
    separation) remain the actual defense; this is just an audit trail.
    """
    matches = []
    for pattern in _compiled_patterns:
        if pattern.search(text):
            matches.append(pattern.pattern)

    if matches:
        logger.warning(
            f"Possible prompt injection pattern(s) detected in document "
            f"{document_id} ('{filename}'): {matches}"
        )

    return matches