import { AGENT_ADDRESS } from "../config";

/**
 * Leaderboard — ranked by reputation.
 * Real agent reads from chain; 3 demo agents are hardcoded.
 * Re-sorts when the live agent's score changes.
 */

const HARDCODED_AGENTS = [
  { name: "DataAgent-Beta",    address: "0x71Be63f3384f5fb98995Ec79E646EBFa4F7d8e4D", score: 91, skill: "Data Analysis", tasks: 12 },
  { name: "ReasonAgent-Gamma", address: "0x90F79bf6EB2c4f870365E785982E1f101E93b906", score: 88, skill: "Reasoning",     tasks: 9  },
  { name: "PlanAgent-Delta",   address: "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65", score: 79, skill: "Planning",      tasks: 7  },
];

const RANK_STYLES = [
  { bg: "rgba(201,162,70,0.08)",  border: "rgba(201,162,70,0.2)",   badge: "#c9a246", label: "01" },
  { bg: "rgba(168,154,134,0.06)", border: "rgba(168,154,134,0.15)", badge: "#a89a86", label: "02" },
  { bg: "rgba(107,94,78,0.06)",   border: "rgba(107,94,78,0.15)",   badge: "#8a7e6e", label: "03" },
  { bg: "rgba(61,52,43,0.06)",    border: "rgba(61,52,43,0.15)",    badge: "#6b5e4e", label: "04" },
];

function truncate(addr) {
  if (!addr) return "—";
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

export default function Leaderboard({ realProfile, realAddress }) {
  const realScore = Number(realProfile?.rep) || 0;
  const realName  = realProfile?.name || "CodeAgent-Alpha";
  const realTasks = Number(realProfile?.tasksDone) || 0;

  const realEntry = {
    name:    realName,
    address: realAddress || AGENT_ADDRESS,
    score:   realScore,
    skill:   "Code Generation",
    tasks:   realTasks,
    isReal:  true,
  };

  const all = [realEntry, ...HARDCODED_AGENTS]
    .sort((a, b) => b.score - a.score);

  return (
    <div className="lb-card glass-card" id="leaderboard">
      <div className="card-title">
        <span className="card-title-dot" style={{ background: "#c9a246" }} />
        Leaderboard
      </div>

      <div className="lb-header-row">
        <span className="lb-col-rank">#</span>
        <span className="lb-col-agent">AGENT</span>
        <span className="lb-col-tasks">TASKS</span>
        <span className="lb-col-skill">DOMAIN</span>
        <span className="lb-col-score">SCORE</span>
      </div>

      <div className="lb-list">
        {all.map((agent, i) => {
          const rs = RANK_STYLES[i] || RANK_STYLES[3];
          return (
            <div
              key={agent.address || i}
              className={`lb-row ${agent.isReal ? "lb-row-real" : ""}`}
              style={{
                background:   rs.bg,
                borderColor:  rs.border,
              }}
              id={agent.isReal ? "lb-real-agent" : undefined}
            >
              <span className="lb-rank" style={{ color: rs.badge }}>{rs.label}</span>
              <div className="lb-agent">
                <span className="lb-name">
                  {agent.name}
                  {agent.isReal && <span className="lb-live-tag">LIVE</span>}
                </span>
                <span className="lb-addr">{truncate(agent.address)}</span>
              </div>
              <span className="lb-tasks-count">{agent.tasks}</span>
              <div className="lb-right">
                <span className="lb-skill">{agent.skill}</span>
                <span className="lb-score" style={{ color: rs.badge }}>
                  {agent.score}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="lb-footer">
        <span className="lb-footer-dot" />
        reading from monad testnet · updates on finalizetask()
      </div>
    </div>
  );
}
