import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.rag.evaluation.evaluator import run_evaluation
from backend.rag.evaluation.metrics import summarize_results


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/run_evaluation.py <workspace_id> <owner_id>")
        sys.exit(1)

    workspace_id = sys.argv[1]
    owner_id = sys.argv[2]
    eval_set_path = "data/evaluation/sample_eval_set.json"

    print(f"Running evaluation on workspace {workspace_id}...")
    results = run_evaluation(workspace_id, owner_id, eval_set_path)

    print("\n--- Individual Results ---")
    for r in results:
        status = "❌ ERROR" if r["error"] else ("✅" if r["grounded"] == r["should_be_grounded"] else "⚠️")
        print(f"{status} Q: {r['question']}")
        if r["error"]:
            print(f"   Error: {r['error']}")
        else:
            print(f"   Answer: {r['answer'][:100]}...")
            print(f"   Grounded: {r['grounded']} (expected: {r['should_be_grounded']})")
            print(f"   Latency: {r['latency_seconds']}s")

    summary = summarize_results(results)
    print("\n--- Summary ---")
    print(json.dumps(summary, indent=2))

    # Save full results to a file for later review
    output_path = "data/evaluation/last_run_results.json"
    with open(output_path, "w") as f:
        json.dump({"results": results, "summary": summary}, f, indent=2)
    print(f"\nFull results saved to {output_path}")


if __name__ == "__main__":
    main()