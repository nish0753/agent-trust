/**
 * SkillsSection — animated horizontal skill bars.
 * Reads live scores from the contract via the skills prop.
 */

const SKILL_CONFIG = [
  { key: "Code Generation", label: "CODE GEN",  color: "#e8501d" },
  { key: "Reasoning",       label: "REASONING", color: "#c9a246" },
  { key: "Planning",        label: "PLANNING",  color: "#5a9e6e" },
];

function SkillBar({ label, score, color }) {
  const pct = Math.min(100, Math.max(0, Number(score) || 0));

  return (
    <div className="skill-row" id={`skill-${label.toLowerCase().replace(" ", "-")}`}>
      <div className="skill-meta">
        <span className="skill-label">{label}</span>
        <span className="skill-score" style={{ color }}>{pct > 0 ? pct : "—"}</span>
      </div>
      <div className="skill-track">
        <div
          className="skill-fill"
          style={{
            width: `${pct}%`,
            background: color,
            transition: "width 1.4s cubic-bezier(0.22, 1, 0.36, 1)",
          }}
        />
      </div>
    </div>
  );
}

export default function SkillsSection({ skills, isLoading }) {
  return (
    <div className="skills-card glass-card" id="skills-section">
      <div className="card-title">
        <span className="card-title-dot" style={{ background: "#e8501d" }} />
        Skill Domains
      </div>

      {isLoading ? (
        <div className="skeleton-rows">
          {[1, 2, 3].map(i => <div key={i} className="skeleton-bar" />)}
        </div>
      ) : (
        <div className="skill-list">
          {SKILL_CONFIG.map(({ key, label, color }) => (
            <SkillBar
              key={key}
              label={label}
              score={skills[key] || "0"}
              color={color}
            />
          ))}
        </div>
      )}

      <div className="skills-footer">
        on-chain running average per skill domain
      </div>
    </div>
  );
}
