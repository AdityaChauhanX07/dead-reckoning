import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parents[2]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))

from backend.persona.agent import ask_harold

DATASET_PATH = ROOT / "data" / "evaluations" / "harold_eval_dataset.json"
RESULTS_PATH = ROOT / "data" / "evaluations" / "eval_results.json"

KEY_PHRASE_THRESHOLD = 3


def extract_key_phrases(text: str) -> list[str]:
    """Pull out meaningful multi-word phrases from the expected output."""
    # Quoted phrases first, then noun-ish chunks of 3+ words
    quoted = re.findall(r'"([^"]{6,})"', text)
    sentences = re.split(r"[.;—]", text)
    chunks = []
    for sentence in sentences:
        words = sentence.strip().split()
        # sliding window: grab 3-word phrases
        for i in range(len(words) - 2):
            phrase = " ".join(words[i : i + 3]).strip("(),").lower()
            if len(phrase) > 10:
                chunks.append(phrase)
    return quoted + chunks


def score_response(actual: str, expected: str) -> tuple[bool, int, list[str]]:
    actual_lower = actual.lower()
    key_phrases = extract_key_phrases(expected)
    matched = [p for p in key_phrases if p.lower() in actual_lower]
    passed = len(matched) >= KEY_PHRASE_THRESHOLD
    return passed, len(matched), matched[:5]  # return up to 5 sample matches


async def run_evals() -> None:
    dataset = json.loads(DATASET_PATH.read_text())
    results = []
    passed_count = 0

    for i, case in enumerate(dataset, start=1):
        question = case["input"]
        expected = case["expected_output"]

        print(f"[{i:02d}/{len(dataset)}] {question[:70]}...")
        try:
            actual = await ask_harold(question)
            passed, match_count, sample_matches = score_response(actual, expected)
        except Exception as exc:
            actual = f"ERROR: {exc}"
            passed, match_count, sample_matches = False, 0, []

        status = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1
        print(f"       {status}  ({match_count} key phrases matched)\n")

        results.append(
            {
                "index": i,
                "input": question,
                "expected_output": expected,
                "actual_output": actual,
                "passed": passed,
                "key_phrases_matched": match_count,
                "sample_matched_phrases": sample_matches,
            }
        )

    total = len(dataset)
    print(f"{'='*50}")
    print(f"Score: {passed_count}/{total} passed")
    print(f"{'='*50}\n")

    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "score": f"{passed_count}/{total}",
        "passed": passed_count,
        "total": total,
        "cases": results,
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(output, indent=2))
    print(f"Results saved to {RESULTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(run_evals())
