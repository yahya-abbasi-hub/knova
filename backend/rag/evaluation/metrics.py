def score_keyword_match(answer: str, expected_keywords: list[str]) -> float:
    """
    Simple, cheap check: what fraction of expected keywords/phrases actually
    appear in the generated answer? Not a perfect measure of correctness,
    but a fast, deterministic first signal that doesn't require another LLM
    call to compute.
    """
    if not expected_keywords:
        return 1.0  # nothing expected, nothing to check

    answer_lower = (answer or "").lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return found / len(expected_keywords)


def score_grounding_correctness(actual_grounded: bool, expected_grounded: bool) -> bool:
    """Did the system correctly decide whether it had enough evidence to answer?"""
    return actual_grounded == expected_grounded


def summarize_results(results: list[dict]) -> dict:
    """
    Computes overall metrics across an entire evaluation run:
    - keyword match rate (average across all cases)
    - grounding accuracy (did grounded/not-grounded decisions match expectations)
    - average latency
    - failure rate
    """
    total = len(results)
    if total == 0:
        return {}

    keyword_scores = []
    grounding_correct = 0
    total_latency = 0.0
    failures = 0

    for r in results:
        if r["error"]:
            failures += 1
            continue

        keyword_scores.append(
            score_keyword_match(r["answer"], r["expected_answer_contains"])
        )

        if score_grounding_correctness(r["grounded"], r["should_be_grounded"]):
            grounding_correct += 1

        total_latency += r["latency_seconds"]

    successful = total - failures

    return {
        "total_cases": total,
        "failures": failures,
        "failure_rate": round(failures / total, 3),
        "avg_keyword_match_score": round(sum(keyword_scores) / len(keyword_scores), 3) if keyword_scores else 0,
        "grounding_accuracy": round(grounding_correct / successful, 3) if successful else 0,
        "avg_latency_seconds": round(total_latency / successful, 2) if successful else 0,
    }