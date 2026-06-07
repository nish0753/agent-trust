# AgentLinked + TaskHub
### Decentralized AI Agent Reputation · Monad Blitz Bangalore

Two independent apps sharing one Solidity contract on **Monad Testnet** as their only integration point.

| Piece | Stack | What it does |
|-------|-------|--------------|
| **AgentTrust.sol** | Solidity 0.8.20 | On-chain reputation ledger |
| **TaskHub** | Python + Streamlit + Groq | Runs an AI agent, scores it, writes result on-chain |
| **AgentLinked** | React + Vite + ethers v6 | LinkedIn-style profile, reads from chain in real-time |

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node 18+
- Testnet MON (from Monad faucet)
- Groq API key (free at [console.groq.com](https://console.groq.com))
- MetaMask connected to Monad Testnet (chain ID 10143)

---

### Step 1 — Deploy the contract

1. Open [Remix IDE](https://remix.ethereum.org)
2. Paste `contracts/AgentTrust.sol`
3. Compile with Solidity 0.8.20
4. Connect MetaMask → Monad Testnet
5. Deploy `AgentTrust`
6. **Copy the deployed contract address**

---

### Step 2 — Configure TaskHub

```bash
cd taskhub
cp .env.example .env
```

Edit `.env`:
```
RPC_URL=https://testnet-rpc.monad.xyz
PRIVATE_KEY=0x<your-metamask-private-key>
CONTRACT_ADDRESS=0x<deployed-contract-address>
GROQ_API_KEY=gsk_<your-key-from-console.groq.com>
```

Edit `config.py`:
```python
AGENT_ADDRESS = "0x<same-metamask-address-as-private-key>"
```

---

### Step 3 — Install Python deps & seed historical data

```bash
cd taskhub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed.py          # registers agent + 3 historical tasks
```

---

### Step 4 — Run TaskHub

```bash
source venv/bin/activate
streamlit run app.py
# → http://localhost:8501
```

Click **▶ Run Agent** to:
1. Stream Groq (Llama 3.3 70B) solution token-by-token
2. Reveal verifier scores with animation
3. Commit consensus score to Monad Testnet

---

### Step 5 — Configure AgentLinked

Edit `agentlinked/src/config.js`:
```js
export const CONTRACT_ADDRESS = "0x<deployed-contract-address>";
export const AGENT_ADDRESS    = "0x<agent-wallet-address>";
```

---

### Step 6 — Run AgentLinked

```bash
cd agentlinked
npm install
npm run dev
# → http://localhost:5173
```

The profile updates via HTTP polling + WebSocket — data refreshes automatically when TaskHub commits a task.

---

## Architecture

```
TaskHub (Streamlit)          AgentLinked (React)
    │                               │
    │  finalizeTask()               │  getAgentProfile() (HTTP)
    │  (web3.py)                    │  ReputationUpdated (WebSocket)
    └──────────► AgentTrust.sol ◄───┘
                  (Monad Testnet)
```

## File Structure

```
agent-trust/
├── contracts/AgentTrust.sol
├── taskhub/
│   ├── app.py          ← Streamlit UI
│   ├── agent.py        ← Groq streaming (Llama 3.3 70B)
│   ├── verifier.py     ← 3 independent AI verifiers (Llama 3.3 70B)
│   ├── contract.py     ← web3.py tx signing
│   ├── config.py       ← constants + ABI
│   ├── seed.py         ← pre-seed historical data
│   ├── diagnose.py     ← diagnostic tool
│   └── requirements.txt
└── agentlinked/
    └── src/
        ├── App.jsx                 ← Router
        ├── main.jsx                ← BrowserRouter wrapper
        ├── config.js
        ├── index.css               ← Forge design system tokens
        ├── pages/
        │   ├── Landing.jsx         ← Marketing site
        │   ├── landing.css         ← Scoped landing styles
        │   └── Dashboard.jsx       ← Main app
        ├── hooks/useContractEvents.js
        └── components/
            ├── AgentCard.jsx
            ├── SkillsSection.jsx
            ├── TaskFeed.jsx
            └── Leaderboard.jsx
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Blockchain | Monad Testnet (EVM, chain ID 10143) |
| Smart Contract | Solidity 0.8.20 |
| AI Agent & Verifier | Groq API (Llama 3.3 70B, free tier) |
| Backend | Python 3.13, web3.py, Streamlit |
| Frontend | React 19, Vite, React Router, ethers v6 |
| Design System | "Forge" (Warm obsidian, ember accents, Syne + JetBrains Mono) |

---

Built for Monad Blitz Bangalore Hackathon
