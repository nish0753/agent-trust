"""
verifier.py — Three AI verifiers independently score the agent's solution.

Each verifier uses Groq (Llama 3.3 70B) with a different evaluation focus:
  V1_Correctness — Does the code solve the problem correctly?
  V2_Efficiency  — Is the algorithm time/space efficient?
  V3_Quality     — Is the code clean, readable, and well-structured?

Returns a dict of scores (0-100) and a weighted consensus.
"""

import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in .env")
        _client = Groq(api_key=api_key)
    return _client


VERIFIER_PROMPTS = {
    "V1_Correctness": (
        "You are a strict code correctness verifier. "
        "Evaluate whether the solution correctly solves the given problem. "
        "Consider: edge cases, off-by-one errors, return types, and logical soundness. "
        "Respond ONLY with a JSON object: {\"score\": <0-100>, \"reason\": \"<one sentence>\"}"
    ),
    "V2_Efficiency": (
        "You are an algorithm efficiency verifier. "
        "Evaluate the time and space complexity of the solution. "
        "A brute-force O(n²) approach scores ~40-60. An optimal O(n) hash-map approach scores 80-95. "
        "Respond ONLY with a JSON object: {\"score\": <0-100>, \"reason\": \"<one sentence>\"}"
    ),
    "V3_Quality": (
        "You are a code quality verifier. "
        "Evaluate readability, naming conventions, comments, structure, and Pythonic style. "
        "Respond ONLY with a JSON object: {\"score\": <0-100>, \"reason\": \"<one sentence>\"}"
    ),
}


def _parse_score(text: str) -> tuple[int, str]:
    """Extract score and reason from LLM response, with fallback parsing."""
    # Try JSON parse first
    try:
        obj = json.loads(text.strip())
        return int(obj["score"]), obj.get("reason", "")
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: find first number in response
    match = re.search(r'"score"\s*:\s*(\d+)', text)
    if match:
        return int(match.group(1)), ""

    # Last resort: find any number between 0-100
    nums = [int(n) for n in re.findall(r'\b(\d+)\b', text) if 0 <= int(n) <= 100]
    if nums:
        return nums[0], ""

    return 50, "Could not parse verifier response"


def evaluate_solution(problem: str, solution: str) -> dict:
    """
    Run 3 independent verifiers on the solution.

    Returns:
        {
            "scores": {"V1_Correctness": 85, "V2_Efficiency": 72, "V3_Quality": 80},
            "reasons": {"V1_Correctness": "...", ...},
            "consensus": 79,   # weighted average
        }
    """
    client = _get_client()
    scores = {}
    reasons = {}

    for name, system_prompt in VERIFIER_PROMPTS.items():
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"PROBLEM:\n{problem}\n\n"
                            f"SOLUTION:\n{solution}"
                        ),
                    },
                ],
                max_tokens=150,
                temperature=0.3,   # low temp for consistent scoring
            )
            raw = resp.choices[0].message.content or ""
            score, reason = _parse_score(raw)
            scores[name] = max(0, min(100, score))
            reasons[name] = reason
        except Exception as e:
            # If a verifier fails, give a neutral 50
            scores[name] = 50
            reasons[name] = f"Verifier error: {e}"

    # Weighted consensus: correctness 50%, efficiency 25%, quality 25%
    consensus = int(
        scores["V1_Correctness"] * 0.50 +
        scores["V2_Efficiency"]  * 0.25 +
        scores["V3_Quality"]     * 0.25
    )

    return {
        "scores": scores,
        "reasons": reasons,
        "consensus": consensus,
    }


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_problem = "Write a Python function that finds two numbers in a list that add up to a target and returns their indices."
    test_solution = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    print("Evaluating solution...\n")
    result = evaluate_solution(test_problem, test_solution)
    for name, score in result["scores"].items():
        print(f"  {name}: {score}/100  — {result['reasons'][name]}")
    print(f"\n  Consensus: {result['consensus']}/100")
