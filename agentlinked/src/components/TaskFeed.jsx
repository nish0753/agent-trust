/**
 * TaskFeed — live event history from ReputationUpdated events.
 * Events arrive via useContractEvents hook — no page refresh needed.
 */

const SKILL_COLORS = {
  "Code Generation": "#e8501d",
  "Reasoning":       "#c9a246",
  "Planning":        "#5a9e6e",
};

function timeAgo(ts) {
  const secs = Math.floor((Date.now() - ts) / 1000);
  if (secs < 60)  return `${secs}s ago`;
  if (secs < 3600) return `${Math.floor(secs / 60)}m ago`;
  return `${Math.floor(secs / 3600)}h ago`;
}

function truncateHash(hash) {
  if (!hash) return "—";
  return `${hash.slice(0, 8)}…${hash.slice(-6)}`;
}

function EventRow({ event }) {
  const color = SKILL_COLORS[event.skill] || "#a89a86";
  return (
    <div className="feed-row" id={`task-${event.taskId}`}>
      <div className="feed-left">
        <div className="feed-icon" style={{ borderColor: color, color }}>
          ◆
        </div>
        <div className="feed-line" />
      </div>
      <div className="feed-content">
        <div className="feed-top">
          <span className="feed-task">TASK #{event.taskId}</span>
          <span className="feed-skill" style={{
            background: `${color}15`,
            color,
            borderColor: `${color}30`
          }}>
            {event.skill}
          </span>
        </div>
        <div className="feed-score">
          score committed: <strong style={{ color }}>{event.score}</strong> / 100
        </div>
        <div className="feed-meta">
          <a
            href={`https://testnet.monadexplorer.com/tx/${event.txHash}`}
            target="_blank"
            rel="noreferrer"
            className="feed-hash"
          >
            {truncateHash(event.txHash)}
          </a>
          <span className="feed-time">{timeAgo(event.ts)}</span>
        </div>
      </div>
    </div>
  );
}

export default function TaskFeed({ events, isLoading }) {
  return (
    <div className="feed-card glass-card" id="task-feed">
      <div className="card-title">
        <span className="card-title-dot pulsing" style={{ background: "#5a9e6e" }} />
        Event Log
        {events.length > 0 && (
          <span className="feed-count">{events.length}</span>
        )}
      </div>

      {isLoading ? (
        <div className="skeleton-rows">
          {[1, 2, 3].map(i => <div key={i} className="skeleton-event" />)}
        </div>
      ) : events.length === 0 ? (
        <div className="feed-empty">
          <span>◆</span>
          <p>Listening for on-chain events…</p>
          <small>run taskhub to populate the feed</small>
        </div>
      ) : (
        <div className="feed-list">
          {events.map((ev, i) => (
            <EventRow key={`${ev.taskId}-${i}`} event={ev} />
          ))}
        </div>
      )}
    </div>
  );
}
