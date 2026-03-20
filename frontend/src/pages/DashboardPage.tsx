import { useAuth } from "../features/auth/context/AuthContext";

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <p className="section-eyebrow">Dashboard</p>
        <h1 className="section-title">Welcome back, {user?.email}</h1>
        <p className="section-text">
          Manage your secure files, conversations, and steganographic workflows.
        </p>
      </div>

      {/* Stats */}
      <div className="dashboard__grid">
        <div className="card">
          <p className="card__label">Protected files</p>
          <h2 className="card__value">689</h2>
          <span className="card__meta">+18 this week</span>
        </div>

        <div className="card">
          <p className="card__label">Secure threads</p>
          <h2 className="card__value">372</h2>
          <span className="card__meta">Active conversations</span>
        </div>

        <div className="card">
          <p className="card__label">Embedded payloads</p>
          <h2 className="card__value">124</h2>
          <span className="card__meta">Across supported media</span>
        </div>
      </div>

      {/* Actions */}
      <div className="dashboard__actions">
        <h3 className="section-subtitle">Quick actions</h3>

        <div className="dashboard__grid">
          <button className="card card--action">
            Upload secure file
          </button>

          <button className="card card--action">
            Start secure chat
          </button>

          <button className="card card--action">
            Open Stego Lab
          </button>
        </div>
      </div>

      {/* Activity */}
      <div className="dashboard__activity">
        <h3 className="section-subtitle">Recent activity</h3>

        <div className="card">
          <p className="card__label">No recent activity yet</p>
          <span className="card__meta">
            Your secure operations will appear here
          </span>
        </div>
      </div>
    </div>
  );
}