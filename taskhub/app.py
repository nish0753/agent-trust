"""
app.py — TaskHub Streamlit UI.

Run:
    cd taskhub && source venv/bin/activate && streamlit run app.py

Flow:
  1. Agent generates a solution (Groq streaming)
  2. Three AI verifiers independently score the solution
  3. Weighted consensus is computed
  4. Result is committed on-chain via finalizeTask()
"""

import time
import streamlit as st

# ── Page config must be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="TaskHub — AI Agent Evaluation",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Imports after page config ─────────────────────────────────────────────────
import os
from config import (
    PROBLEM, AGENT_NAME, AGENT_ADDRESS,
    SKILL, CONTRACT_ADDRESS,
)
from agent    import run_agent
from verifier import evaluate_solution
from contract import finalize_task

# ── Auto-increment TASK_ID from chain state ──────────────────────────────────
def get_next_task_id() -> int:
    """Read current tasksDone from chain and return next task ID."""
    try:
        from web3 import Web3
        from config import RPC_URL, ABI
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI,
        )
        _, _, tasks_done = contract.getAgentProfile(
            Web3.to_checksum_address(AGENT_ADDRESS)
        ).call()
        return tasks_done + 1
    except Exception:
        return int(time.time()) % 100000   # fallback: use timestamp

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.taskhub-header {
    text-align: center;
    padding: 1.6rem 0 1rem;
}
.taskhub-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #e8501d;
    letter-spacing: -1.5px;
    margin-bottom: 0.25rem;
}
.taskhub-sub {
    color: #6b5e4e;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 1px;
}
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(232,80,29,0.08);
    border: 1px solid rgba(232,80,29,0.2);
    border-radius: 3px;
    padding: 7px 20px;
    color: #e8501d;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 0.9rem;
}
.problem-box {
    background: rgba(22,19,16,0.9);
    border: 1px solid rgba(42,36,32,0.8);
    border-radius: 3px;
    padding: 1.25rem 1.5rem;
    color: #a89a86;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    line-height: 1.7;
}
.tx-box {
    background: rgba(90,158,110,0.06);
    border: 1px solid rgba(90,158,110,0.2);
    border-radius: 3px;
    padding: 1rem 1.25rem;
    color: #5a9e6e;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}
.verifier-reason {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6b5e4e;
    margin-top: 2px;
}
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #6b5e4e;
    margin-bottom: 0.5rem;
}
hr { border-color: rgba(42,36,32,0.5) !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="taskhub-header">
  <div class="taskhub-title">◆ TaskHub</div>
  <div class="taskhub-sub">decentralised ai agent evaluation · monad testnet</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

task_id = get_next_task_id()

with left:
    st.markdown('<div class="section-label">Problem Statement</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="problem-box">{PROBLEM}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="agent-badge">◆ &nbsp; {AGENT_NAME}</div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown('<div class="section-label">Session Info</div>', unsafe_allow_html=True)
    st.metric("Task ID",      f"#{task_id}")
    st.metric("Skill Domain", SKILL)
    st.metric("Network",      "Monad Testnet")

st.markdown("<br>", unsafe_allow_html=True)

# ── Run Agent button ──────────────────────────────────────────────────────────
run_btn = st.button("▶  Run Agent", type="primary", use_container_width=True)

if run_btn:
    # Guard: check config is filled
    if not AGENT_ADDRESS:
        st.error("⚠️  Set AGENT_ADDRESS in config.py first, then run seed.py.")
        st.stop()
    if not CONTRACT_ADDRESS:
        st.error("⚠️  Set CONTRACT_ADDRESS in .env first.")
        st.stop()
    if not os.getenv("GROQ_API_KEY"):
        st.error("⚠️  GROQ_API_KEY is missing from .env — get a free key at console.groq.com")
        st.stop()

    # ── Step 1: Stream solution ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Agent Solution</div>', unsafe_allow_html=True)
    code_area = st.empty()
    full_solution = ""

    try:
        for token in run_agent(PROBLEM):
            full_solution += token
            code_area.code(full_solution, language="python")
    except Exception as e:
        st.error(f"Groq API error: {e}")
        st.stop()

    st.success("✅  Solution generated by CodeAgent-Alpha")

    # ── Step 2: AI Verifier evaluation (3 independent verifiers) ──────────────
    st.markdown("---")
    st.markdown('<div class="section-label">AI Verifier Evaluation</div>', unsafe_allow_html=True)

    with st.spinner("Running 3 independent AI verifiers on the solution …"):
        result = evaluate_solution(PROBLEM, full_solution)

    verifier_scores = result["scores"]
    reasons         = result["reasons"]
    consensus       = result["consensus"]

    # Staggered reveal of verifier scores
    score_cols = st.columns(3)
    placeholders = [c.empty() for c in score_cols]

    time.sleep(0.4)
    for i, (verifier, score) in enumerate(verifier_scores.items()):
        placeholders[i].metric(
            label=verifier,
            value=f"{score} / 100",
            delta=f"{score - 70:+d} vs baseline",
        )
        # Show verifier reasoning
        score_cols[i].markdown(
            f'<div class="verifier-reason">{reasons[verifier]}</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.4)

    # ── Step 3: Consensus score ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">Weighted Consensus</div>', unsafe_allow_html=True)
    st.metric(
        label="50% correctness · 25% efficiency · 25% quality",
        value=f"{consensus} / 100",
        delta=f"{consensus - 70:+d} vs baseline",
    )

    # ── Step 4: Write to chain ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-label">On-Chain Commit</div>', unsafe_allow_html=True)

    with st.spinner("Broadcasting finalizeTask() to Monad Testnet …"):
        try:
            tx_hash = finalize_task(task_id, AGENT_ADDRESS, consensus, SKILL)
        except Exception as e:
            st.error(f"Transaction failed: {e}")
            st.stop()

    explorer_url = f"https://testnet.monadexplorer.com/tx/{tx_hash}"
    st.markdown(
        f'<div class="tx-box">✅ &nbsp; Reputation committed on-chain<br>'
        f'<b>Consensus:</b> {consensus}/100<br>'
        f'<b>Tx:</b> <code>{tx_hash}</code><br>'
        f'<a href="{explorer_url}" target="_blank" '
        f'style="color:#e8501d">◆ View on Monad Explorer</a></div>',
        unsafe_allow_html=True,
    )

    st.info("🔄  AgentLinked dashboard will auto-update within ~10 seconds")
