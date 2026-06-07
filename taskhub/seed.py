"""
seed.py — One-time script to:
  1. registerAgent(AGENT_ADDRESS, "CodeAgent-Alpha") on-chain
  2. Seed 3 historical tasks so AgentLinked isn't empty on demo day.

Run ONCE after deploying the contract and filling .env + config.py:
    cd taskhub && python seed.py

Tasks seeded:
  #100  Code Generation  score=82
  #101  Reasoning        score=75
  #102  Code Generation  score=88
→ Results in Code Generation avg ~85, Reasoning avg 75 on AgentLinked.
"""

import sys
import time
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

from config import (
    RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS,
    CHAIN_ID, ABI, AGENT_ADDRESS, AGENT_NAME,
)

# ── Historical tasks to pre-seed ─────────────────────────────────────────────
SEED_TASKS = [
    {"task_id": 100, "score": 82, "skill": "Code Generation"},
    {"task_id": 101, "score": 75, "skill": "Reasoning"},
    {"task_id": 102, "score": 88, "skill": "Code Generation"},
]


def _check_config():
    errors = []
    if not AGENT_ADDRESS:
        errors.append("AGENT_ADDRESS is empty in config.py")
    if not PRIVATE_KEY:
        errors.append("PRIVATE_KEY is missing from .env")
    if not CONTRACT_ADDRESS:
        errors.append("CONTRACT_ADDRESS is missing from .env")
    if errors:
        for e in errors:
            print(f"❌  {e}")
        sys.exit(1)


def _send_tx(w3: Web3, account, contract, fn_call) -> str:
    gas_price = w3.eth.gas_price or w3.to_wei(500, "gwei")
    tx = fn_call.build_transaction({
        "from":     account.address,
        "nonce":    w3.eth.get_transaction_count(account.address),
        "gas":      300_000,
        "gasPrice": int(gas_price * 2),
        "chainId":  CHAIN_ID,
    })
    signed  = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    return tx_hash.hex()


def main():
    _check_config()

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print(f"❌  Cannot connect to {RPC_URL}")
        sys.exit(1)

    account  = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=ABI,
    )
    agent_cs = Web3.to_checksum_address(AGENT_ADDRESS)

    # ── Register agent ────────────────────────────────────────────────────────
    print(f"Registering {AGENT_NAME} at {agent_cs} …")
    try:
        tx = _send_tx(w3, account, contract,
                      contract.functions.registerAgent(agent_cs, AGENT_NAME))
        print(f"✅  Registered  → {tx}")
    except Exception as e:
        # If already registered the tx will revert — that's fine, continue.
        print(f"⚠️   registerAgent reverted (possibly already registered): {e}")

    time.sleep(1)

    # ── Seed historical tasks ─────────────────────────────────────────────────
    for task in SEED_TASKS:
        print(f"\nSeeding Task #{task['task_id']}  skill={task['skill']}  score={task['score']} …")
        try:
            tx = _send_tx(
                w3, account, contract,
                contract.functions.finalizeTask(
                    task["task_id"],
                    agent_cs,
                    task["score"],
                    task["skill"],
                    [],   # no outliers
                    0,    # no slashing
                ),
            )
            print(f"✅  Task {task['task_id']} committed → {tx}")
        except Exception as e:
            print(f"❌  Task {task['task_id']} failed: {e}")
        time.sleep(1)

    print(f"""
🎉  Seed complete!
   Code Generation avg : ~85
   Reasoning avg       : 75
   AgentLinked should now show non-empty skill bars and task feed.
""")


if __name__ == "__main__":
    main()
