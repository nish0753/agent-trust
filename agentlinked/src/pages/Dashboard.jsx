import AgentCard      from "../components/AgentCard";
import SkillsSection  from "../components/SkillsSection";
import TaskFeed       from "../components/TaskFeed";
import Leaderboard    from "../components/Leaderboard";
import { useContractEvents } from "../hooks/useContractEvents";
import { AGENT_ADDRESS }     from "../config";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { profile, skills, events, isLoading, error } =
    useContractEvents(AGENT_ADDRESS);

  return (
    <div className="app" id="app-root">
      <header className="app-header" id="app-header">
        <div className="header-inner">
          <Link to="/" className="logo" id="logo" style={{ textDecoration: "none" }}>
            <span className="logo-hex">◆</span>
            <span className="logo-text">AgentLinked</span>
          </Link>
          <nav className="header-right">
            <span className="monad-badge" id="network-badge">
              <span className="live-dot" />
              LIVE · MONAD
            </span>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="config-warn" id="config-warn">
            ⚠️ {error}
          </div>
        )}

        <section className="profile-section" id="profile-section">
          <AgentCard profile={profile} isLoading={isLoading} />
        </section>

        <section className="mid-grid" id="mid-grid">
          <div id="skills-col">
            <SkillsSection skills={skills} isLoading={isLoading} />
          </div>
          <div id="feed-col">
            <TaskFeed events={events} isLoading={isLoading} />
          </div>
        </section>

        <section className="lb-section" id="lb-section">
          <Leaderboard realProfile={profile} realAddress={AGENT_ADDRESS} />
        </section>
      </main>

      <footer className="app-footer" id="app-footer">
        <span>agentlinked · monad blitz bangalore · forged on monad testnet</span>
      </footer>
    </div>
  );
}
