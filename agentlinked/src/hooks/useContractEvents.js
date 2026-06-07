import { useEffect, useState, useRef } from "react";
import { ethers } from "ethers";
import { ABI, CONTRACT_ADDRESS, HTTP_RPC_URL, WSS_RPC_URL } from "../config";

/**
 * useContractEvents — Fetches AgentTrust data with HTTP polling + WebSocket live updates.
 *
 * Strategy:
 *   1. Initial load via HTTP (JsonRpcProvider) — always works.
 *   2. Try WebSocket for live updates — if it fails, fall back to polling every 10s.
 *   3. On each ReputationUpdated event (or poll), re-fetch getAgentProfile + getSkillScore.
 *
 * Returns: { profile, skills, events, isLoading, error }
 */
export function useContractEvents(agentAddress) {
  const [profile,   setProfile]   = useState(null);
  const [skills,    setSkills]    = useState({});
  const [events,    setEvents]    = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error,     setError]     = useState(null);

  const wsProviderRef  = useRef(null);
  const wsContractRef  = useRef(null);
  const pollTimerRef   = useRef(null);

  useEffect(() => {
    if (!agentAddress || !CONTRACT_ADDRESS) {
      setIsLoading(false);
      setError("CONTRACT_ADDRESS or AGENT_ADDRESS not set in config.js");
      return;
    }

    let mounted = true;

    async function setup() {
      try {
        // ── 1. HTTP provider for initial + guaranteed data fetch ─────────
        const httpProvider = new ethers.JsonRpcProvider(HTTP_RPC_URL);
        const httpContract = new ethers.Contract(CONTRACT_ADDRESS, ABI, httpProvider);

        // Initial data fetch
        await fetchAll(httpContract, agentAddress, setProfile, setSkills, setEvents, mounted);
        if (mounted) setIsLoading(false);

        // ── 2. Try WebSocket for live updates ───────────────────────────
        let wsConnected = false;
        try {
          const wsProvider = new ethers.WebSocketProvider(WSS_RPC_URL);
          const wsContract = new ethers.Contract(CONTRACT_ADDRESS, ABI, wsProvider);

          wsProviderRef.current = wsProvider;
          wsContractRef.current = wsContract;

          // Subscribe to ReputationUpdated
          const onReputation = async (agent, newScore, skill, taskId, eventLog) => {
            if (!mounted) return;
            if (agent.toLowerCase() !== agentAddress.toLowerCase()) return;

            // Re-fetch all state from HTTP (more reliable)
            await fetchAll(httpContract, agentAddress, setProfile, setSkills, setEvents, mounted);

            if (mounted) {
              setEvents(prev => [
                {
                  taskId:   taskId.toString(),
                  skill,
                  score:    newScore.toString(),
                  txHash:   eventLog?.log?.transactionHash || "",
                  blockNum: eventLog?.log?.blockNumber?.toString() || "",
                  ts:       Date.now(),
                },
                ...prev,
              ]);
            }
          };

          wsContract.on("ReputationUpdated", onReputation);
          wsConnected = true;
          console.log("[AgentLinked] WebSocket connected — live updates active");
        } catch (wsErr) {
          console.warn("[AgentLinked] WebSocket failed, using HTTP polling:", wsErr.message);
        }

        // ── 3. HTTP polling — keeps leaderboard fresh after each finalizeTask
        pollTimerRef.current = setInterval(async () => {
          if (mounted) {
            await fetchAll(httpContract, agentAddress, setProfile, setSkills, setEvents, mounted);
          }
        }, wsConnected ? 15_000 : 5_000);  // 5s polling = leaderboard updates within seconds

      } catch (err) {
        if (mounted) {
          setError(err.message);
          setIsLoading(false);
        }
      }
    }

    setup();

    return () => {
      mounted = false;
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      if (wsContractRef.current) wsContractRef.current.removeAllListeners();
      if (wsProviderRef.current) wsProviderRef.current.destroy();
    };
  }, [agentAddress]);

  return { profile, skills, events, isLoading, error };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const SKILL_NAMES = ["Code Generation", "Reasoning", "Planning"];

async function fetchAll(contract, agentAddress, setProfile, setSkills, setEvents, mounted) {
  try {
    const [name, rep, tasksDone] = await contract.getAgentProfile(agentAddress);
    if (mounted) {
      setProfile({
        name,
        rep:       rep.toString(),
        tasksDone: tasksDone.toString(),
      });
    }

    const scores = {};
    for (const skill of SKILL_NAMES) {
      const s = await contract.getSkillScore(agentAddress, skill);
      scores[skill] = s.toString();
    }
    if (mounted) setSkills(scores);

    // Fetch recent task history for the feed
    try {
      const totalTasks = await contract.taskHistory.length;
      // This won't work because taskHistory is a public array accessed by index.
      // We'll let events handle the feed instead.
    } catch {
      // taskHistory indexing not supported here — events handle the feed
    }
  } catch (err) {
    console.warn("[AgentLinked] fetchAll error:", err.message);
  }
}
