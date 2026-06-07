"""
Full diagnostic — verifies AGENT_ADDRESS, checks all on-chain state,
sends a FRESH finalizeTask, and reports the receipt.
"""
from dotenv import load_dotenv
load_dotenv()

from web3 import Web3
import os

RPC_URL          = os.getenv("RPC_URL")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

from config import AGENT_ADDRESS, ABI, CHAIN_ID, AGENT_NAME

w3      = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# ── 1. Verify AGENT_ADDRESS matches PRIVATE_KEY ──────────────────────────────
derived_address = account.address
print("=== Address Verification ===")
print(f"  PRIVATE_KEY derives → {derived_address}")
print(f"  AGENT_ADDRESS set   → {AGENT_ADDRESS}")
print(f"  Match?                {derived_address.lower() == AGENT_ADDRESS.lower()}")
if derived_address.lower() != AGENT_ADDRESS.lower():
    print("  ❌  MISMATCH! AGENT_ADDRESS does not belong to this PRIVATE_KEY!")
    print(f"     Fix config.py line 22 → AGENT_ADDRESS = \"{derived_address}\"")
print()

# ── 2. Check contract state ──────────────────────────────────────────────────
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI
)

owner = contract.functions.owner().call()
agent_cs = Web3.to_checksum_address(AGENT_ADDRESS)
name, rep, tasks = contract.functions.getAgentProfile(agent_cs).call()

print("=== On-Chain State ===")
print(f"  Contract owner : {owner}")
print(f"  Our sender     : {account.address}")
print(f"  Owner match    : {owner.lower() == account.address.lower()}")
print(f"  Agent name     : '{name}'")
print(f"  Registered     : {bool(name)}")
print(f"  Tasks done     : {tasks}")
print(f"  Overall rep    : {rep}")
print()

# ── 3. Current gas price ─────────────────────────────────────────────────────
gas_price = w3.eth.gas_price
print("=== Gas Info ===")
print(f"  Current gas price : {gas_price} wei = {gas_price / 10**9:.2f} gwei")
print(f"  We will use       : {int(gas_price * 2)} wei = {int(gas_price * 2) / 10**9:.2f} gwei (2×)")
print()

# ── 4. Simulate ──────────────────────────────────────────────────────────────
TEST_TASK_ID = 999  # unlikely to collide
print(f"=== Simulating finalizeTask(taskId={TEST_TASK_ID}) ===")
try:
    contract.functions.finalizeTask(
        TEST_TASK_ID, agent_cs, 80, "Code Generation", [], 0
    ).call({"from": account.address})
    print("  ✅ Simulation PASSED")
except Exception as e:
    print(f"  ❌ Simulation REVERTED: {e}")
    exit(1)
print()

# ── 5. Send real transaction ─────────────────────────────────────────────────
print(f"=== Sending REAL finalizeTask(taskId={TEST_TASK_ID}) ===")
fn_call = contract.functions.finalizeTask(
    TEST_TASK_ID, agent_cs, 80, "Code Generation", [], 0
)

nonce = w3.eth.get_transaction_count(account.address)
tx = fn_call.build_transaction({
    "from":     account.address,
    "nonce":    nonce,
    "gas":      500_000,
    "gasPrice": int(gas_price * 2),
    "chainId":  CHAIN_ID,
})

print(f"  Nonce    : {nonce}")
print(f"  Gas      : 500000")
print(f"  GasPrice : {tx['gasPrice']} wei")
print(f"  ChainId  : {CHAIN_ID}")
print(f"  To       : {tx['to']}")
print(f"  Signing ...")

signed  = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"  Sent     : {tx_hash.hex()}")
print(f"  Waiting for receipt ...")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
print()
print("=== Receipt ===")
print(f"  Status   : {receipt.status}  {'✅ SUCCESS' if receipt.status == 1 else '❌ REVERTED'}")
print(f"  Gas used : {receipt.gasUsed} / 500000")
print(f"  Block    : {receipt.blockNumber}")
print(f"  Tx hash  : {receipt.transactionHash.hex()}")
print(f"  Explorer : https://testnet.monadexplorer.com/tx/{receipt.transactionHash.hex()}")

if receipt.status == 1:
    # Verify task count increased
    _, _, tasks_after = contract.functions.getAgentProfile(agent_cs).call()
    print(f"\n  Tasks before: {tasks} → after: {tasks_after}")
    print("  🎉  Transaction is VALID on-chain!")
