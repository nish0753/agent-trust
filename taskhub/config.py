"""
config.py — All constants and environment variables for TaskHub.

After deploying AgentTrust.sol on Monad Testnet:
  1. Copy the contract address into CONTRACT_ADDRESS below.
  2. Copy the agent wallet address into AGENT_ADDRESS below.
  3. Fill in taskhub/.env  (see .env.example).
  4. Increment TASK_ID before each demo run to avoid duplicate IDs on-chain.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Problem given to the agent ──────────────────────────────────────────────
PROBLEM = """Write a Python function that finds two numbers in a list that add up \
to a target value and returns their indices."""

# ── Identity ─────────────────────────────────────────────────────────────────
AGENT_NAME    = "CodeAgent-Alpha"
AGENT_ADDRESS = "0x2772BE0a1B620bD5Dde86E92D118D7d3cB1eae92"   # deployer wallet
SKILL         = "Code Generation"
TASK_ID       = 100           # starting offset — app.py auto-increments from chain state

# ── Environment variables ────────────────────────────────────────────────────
RPC_URL          = os.getenv("RPC_URL",          "https://testnet-rpc.monad.xyz")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY",      "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

CHAIN_ID = 10143            # Monad Testnet — verify at chainlist.org

# ── Contract ABI (generated from AgentTrust.sol) ─────────────────────────────
ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "internalType": "address", "name": "agent", "type": "address"},
            {"indexed": False, "internalType": "string",  "name": "name",  "type": "string"}
        ],
        "name": "AgentRegistered", "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "internalType": "address",  "name": "agent",    "type": "address"},
            {"indexed": False, "internalType": "uint256",  "name": "newScore", "type": "uint256"},
            {"indexed": False, "internalType": "string",   "name": "skill",    "type": "string"},
            {"indexed": False, "internalType": "uint256",  "name": "taskId",   "type": "uint256"}
        ],
        "name": "ReputationUpdated", "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True,  "internalType": "address", "name": "verifier", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount",   "type": "uint256"}
        ],
        "name": "VerifierSlashed", "type": "event"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "agent", "type": "address"},
            {"internalType": "string",  "name": "name",  "type": "string"}
        ],
        "name": "registerAgent", "outputs": [],
        "stateMutability": "nonpayable", "type": "function"
    },
    {
        "inputs": [], "name": "stakeAsVerifier", "outputs": [],
        "stateMutability": "payable", "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256",   "name": "taskId",         "type": "uint256"},
            {"internalType": "address",   "name": "agent",          "type": "address"},
            {"internalType": "uint256",   "name": "consensusScore", "type": "uint256"},
            {"internalType": "string",    "name": "skill",          "type": "string"},
            {"internalType": "address[]", "name": "outliers",       "type": "address[]"},
            {"internalType": "uint256",   "name": "slashBps",       "type": "uint256"}
        ],
        "name": "finalizeTask", "outputs": [],
        "stateMutability": "nonpayable", "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "getAgentProfile",
        "outputs": [
            {"internalType": "string",  "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view", "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "agent", "type": "address"},
            {"internalType": "string",  "name": "skill", "type": "string"}
        ],
        "name": "getSkillScore",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view", "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view", "type": "function"
    }
]
