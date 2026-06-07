/**
 * config.js — Shared ABI, addresses, and RPC endpoints for AgentLinked.
 *
 * After deploying AgentTrust.sol:
 *   1. Paste the contract address into CONTRACT_ADDRESS.
 *   2. Paste the agent wallet address into AGENT_ADDRESS.
 *   3. Confirm WSS_RPC_URL matches Monad Testnet WebSocket endpoint.
 */

export const CONTRACT_ADDRESS = "0x3F06C938C3EbaFF7b7cC6361945e64fbac115cB2";  // AgentTrust.sol on Monad Testnet
export const AGENT_ADDRESS    = "0x2772BE0a1B620bD5Dde86E92D118D7d3cB1eae92";  // deployer wallet

// Monad Testnet endpoints
export const HTTP_RPC_URL = "https://testnet-rpc.monad.xyz";
export const WSS_RPC_URL  = "wss://testnet-rpc.monad.xyz";  // update if different

export const ABI = [
  { inputs: [], stateMutability: "nonpayable", type: "constructor" },
  {
    anonymous: false,
    inputs: [
      { indexed: true,  internalType: "address", name: "agent", type: "address" },
      { indexed: false, internalType: "string",  name: "name",  type: "string"  }
    ],
    name: "AgentRegistered", type: "event"
  },
  {
    anonymous: false,
    inputs: [
      { indexed: true,  internalType: "address", name: "agent",    type: "address" },
      { indexed: false, internalType: "uint256", name: "newScore", type: "uint256" },
      { indexed: false, internalType: "string",  name: "skill",    type: "string"  },
      { indexed: false, internalType: "uint256", name: "taskId",   type: "uint256" }
    ],
    name: "ReputationUpdated", type: "event"
  },
  {
    anonymous: false,
    inputs: [
      { indexed: true,  internalType: "address", name: "verifier", type: "address" },
      { indexed: false, internalType: "uint256", name: "amount",   type: "uint256" }
    ],
    name: "VerifierSlashed", type: "event"
  },
  {
    inputs: [
      { internalType: "address", name: "agent", type: "address" },
      { internalType: "string",  name: "name",  type: "string"  }
    ],
    name: "registerAgent", outputs: [],
    stateMutability: "nonpayable", type: "function"
  },
  { inputs: [], name: "stakeAsVerifier", outputs: [], stateMutability: "payable", type: "function" },
  {
    inputs: [
      { internalType: "uint256",   name: "taskId",         type: "uint256"   },
      { internalType: "address",   name: "agent",          type: "address"   },
      { internalType: "uint256",   name: "consensusScore", type: "uint256"   },
      { internalType: "string",    name: "skill",          type: "string"    },
      { internalType: "address[]", name: "outliers",       type: "address[]" },
      { internalType: "uint256",   name: "slashBps",       type: "uint256"   }
    ],
    name: "finalizeTask", outputs: [],
    stateMutability: "nonpayable", type: "function"
  },
  {
    inputs: [{ internalType: "address", name: "agent", type: "address" }],
    name: "getAgentProfile",
    outputs: [
      { internalType: "string",  name: "", type: "string"  },
      { internalType: "uint256", name: "", type: "uint256" },
      { internalType: "uint256", name: "", type: "uint256" }
    ],
    stateMutability: "view", type: "function"
  },
  {
    inputs: [
      { internalType: "address", name: "agent", type: "address" },
      { internalType: "string",  name: "skill", type: "string"  }
    ],
    name: "getSkillScore",
    outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
    stateMutability: "view", type: "function"
  },
  {
    inputs: [],
    name: "owner",
    outputs: [{ internalType: "address", name: "", type: "address" }],
    stateMutability: "view", type: "function"
  }
];
