"""
contract.py — Builds, signs, and sends finalizeTask() to Monad Testnet via web3.py.

Prerequisites:
  - PRIVATE_KEY in .env must be the same key that deployed AgentTrust.sol (onlyOwner).
  - CONTRACT_ADDRESS in .env must be filled after Remix deploy.
  - Run seed.py once first to registerAgent before calling finalizeTask.

Standalone test:
    python contract.py
"""

from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

from config import RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS, CHAIN_ID, ABI


def _build_web3():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to Monad RPC at {RPC_URL}")
    return w3


def finalize_task(
    task_id:        int,
    agent_address:  str,
    consensus_score: int,
    skill:          str,
    outliers:       list | None = None,
    slash_bps:      int = 0,
) -> str:
    """
    Call AgentTrust.finalizeTask() on-chain.

    Returns the transaction hash as a hex string (0x...).
    Raises on RPC error, insufficient gas, or onlyOwner revert.
    """
    if not PRIVATE_KEY:
        raise ValueError("PRIVATE_KEY is not set in .env")
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS is not set in .env")

    outliers = outliers or []
    w3       = _build_web3()
    account  = w3.eth.account.from_key(PRIVATE_KEY)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=ABI,
    )

    # Encode & build unsigned transaction
    fn_call = contract.functions.finalizeTask(
        task_id,
        Web3.to_checksum_address(agent_address),
        consensus_score,
        skill,
        [Web3.to_checksum_address(o) for o in outliers],
        slash_bps,
    )
    gas_price = w3.eth.gas_price or w3.to_wei(500, "gwei")
    tx = fn_call.build_transaction({
        "from":     account.address,
        "nonce":    w3.eth.get_transaction_count(account.address),
        "gas":      800_000,                 # Monad uses more gas; 500k hit ceiling
        "gasPrice": int(gas_price * 2),      # 2× current to guarantee acceptance
        "chainId":  CHAIN_ID,
    })

    # Sign locally — private key never leaves this machine
    signed  = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    # Wait for Monad to include the tx (~1 s block time)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

    # Status 0 = reverted on-chain — surface the error clearly
    if receipt.status == 0:
        raise RuntimeError(
            f"Transaction mined but REVERTED on-chain.\n"
            f"Tx: https://testnet.monadexplorer.com/tx/{tx_hash.hex()}\n"
            f"Gas used: {receipt.gasUsed} / 500000"
        )

    return tx_hash.hex()


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    from config import AGENT_ADDRESS, CONSENSUS, SKILL, TASK_ID
    if not AGENT_ADDRESS:
        print("⚠️  Set AGENT_ADDRESS in config.py first")
    else:
        print(f"Sending finalizeTask(taskId={TASK_ID}) …")
        tx = finalize_task(TASK_ID, AGENT_ADDRESS, CONSENSUS, SKILL)
        print(f"✅  Tx hash: {tx}")
        print(f"🔗  https://testnet.monadexplorer.com/tx/{tx}")
