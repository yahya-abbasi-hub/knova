import time
import json
import uuid

from backend.database.session import SessionLocal
from backend.services import chat_service
from backend.core.logging import get_logger

logger = get_logger(__name__)


def run_evaluation(workspace_id: str, owner_id: str, eval_set_path: str) -> list[dict]:
    """
    Runs every question in an evaluation dataset through the real chat
    pipeline, and records the results (answer, sources, timing, grounded
    status) for scoring.
    """
    with open(eval_set_path, "r") as f:
        eval_cases = json.load(f)

    db = SessionLocal()
    results = []

    try:
        for case in eval_cases:
            question = case["question"]
            start_time = time.time()

            try:
                response = chat_service.ask_question(
                    db, uuid.UUID(owner_id), uuid.UUID(workspace_id), question
                )
                elapsed = time.time() - start_time

                results.append({
                    "question": question,
                    "answer": response.answer,
                    "grounded": response.grounded,
                    "sources": [s.document_name for s in response.sources],
                    "latency_seconds": round(elapsed, 2),
                    "expected_answer_contains": case.get("expected_answer_contains", []),
                    "should_be_grounded": case.get("should_be_grounded", True),
                    "error": None,
                })
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Eval case failed for question '{question}': {e}")
                results.append({
                    "question": question,
                    "answer": None,
                    "grounded": None,
                    "sources": [],
                    "latency_seconds": round(elapsed, 2),
                    "expected_answer_contains": case.get("expected_answer_contains", []),
                    "should_be_grounded": case.get("should_be_grounded", True),
                    "error": str(e),
                })

        return results
    finally:
        db.close()