"""
agent.py — Calls Groq API (free) with streaming, yields tokens one-by-one.

Using model: llama-3.3-70b-versatile (excellent at code generation, free tier)

Get your free GROQ_API_KEY at: https://console.groq.com → API Keys

Standalone test:
    python3 agent.py
"""

import os
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


def run_agent(problem: str):
    """
    Stream Groq's solution for `problem`.
    Yields text chunks (str) — wire directly into a Streamlit st.empty() loop.
    """
    client = _get_client()
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are CodeAgent-Alpha. Solve the problem with clean Python code "
                    "and brief inline comments. Return only the code — no markdown fences."
                ),
            },
            {"role": "user", "content": problem},
        ],
        max_tokens=1024,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    from config import PROBLEM
    print("── CodeAgent-Alpha (Groq) streaming solution ──\n")
    for token in run_agent(PROBLEM):
        print(token, end="", flush=True)
    print("\n\n── Done ──")
