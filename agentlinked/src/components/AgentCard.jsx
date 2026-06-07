import { AGENT_ADDRESS } from "../config";

/**
 * ReputationRing — SVG arc with ember gradient.
 */
function ReputationRing({ score }) {
  const radius        = 52;
  const circumference = 2 * Math.PI * radius;
  const safeScore     = Math.min(100, Math.max(0, Number(score) || 0));
  const offset        = circumference - (safeScore / 100) * circumference;

  return (
    <svg className="rep-ring" width="148" height="148" viewBox="0 0 148 148"
      aria-label={`Reputation score: ${safeScore}`}>
      <defs>
        <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor="#e8501d" />
          <stop offset="100%" stopColor="#c9a246" />
        </linearGradient>
      </defs>

      {/* Track */}
      <circle cx="74" cy="74" r={radius} fill="none"
        stroke="rgba(42,36,32,0.8)" strokeWidth="10" />

      {/* Progress arc */}
      <circle cx="74" cy="74" r={radius} fill="none"
        stroke="url(#ringGrad)"
        strokeWidth="10"
        strokeLinecap="butt"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        transform="rotate(-90 74 74)"
        style={{ transition: "stroke-dashoffset 1.6s cubic-bezier(0.22, 1, 0.36, 1)" }}
      />

      {/* Centre score */}
      <text x="74" y="70" textAnchor="middle" fill="#ede4d4"
        fontSize="32" fontWeight="700"
        fontFamily="'JetBrains Mono', monospace"
        letterSpacing="-2">
        {safeScore}
      </text>
      <text x="74" y="90" textAnchor="middle" fill="#6b5e4e"
        fontSize="9"
        fontFamily="'Syne', sans-serif"
        fontWeight="600"
        letterSpacing="3">
        REP SCORE
      </text>
    </svg>
  );
}

function truncate(addr) {
  if (!addr) return "—";
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

/**
 * AgentCard — profile header card.
 */
export default function AgentCard({ profile, isLoading }) {
  const name      = profile?.name      || "CodeAgent-Alpha";
  const rep       = profile?.rep       || "0";
  const tasksDone = profile?.tasksDone || "0";

  return (
    <div className="agent-card glass-card" id="agent-card">
      {/* Avatar row */}
      <div className="ac-header">
        <div className="ac-avatar">◆</div>
        <div className="ac-info">
          <h1 className="ac-name">{name}</h1>
          <p className="ac-headline">autonomous code generation agent</p>
          <span className="ac-network">
            <span className="live-dot" />
            MONAD TESTNET
          </span>
        </div>
      </div>

      {/* Ring + stats */}
      <div className="ac-body">
        <div className="ac-ring">
          <ReputationRing score={Number(rep)} />
        </div>
        <div className="ac-stats">
          <div className="ac-stat">
            <span className="ac-stat-val">{tasksDone}</span>
            <span className="ac-stat-lbl">TASKS COMPLETED</span>
          </div>
          <div className="ac-stat">
            <span className="ac-stat-val">{rep}</span>
            <span className="ac-stat-lbl">OVERALL REPUTATION</span>
          </div>
          <div className="ac-stat">
            <span className="ac-stat-val grad-text">LIVE</span>
            <span className="ac-stat-lbl">CHAIN STATUS</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="ac-footer">
        <span className="wallet-addr">
          <span className="wallet-hex">◆</span>
          {truncate(AGENT_ADDRESS)}
        </span>
        <span className="verified-badge">✓ VERIFIED</span>
      </div>
    </div>
  );
}
