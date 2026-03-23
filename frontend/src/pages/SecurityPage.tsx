import { useState } from "react";
import {
  Activity,
  KeyRound,
  LogOut,
  Server,
  ShieldCheck,
  Wifi,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/context/AuthContext";
import { authService } from "../features/auth/services/auth.service";

export function SecurityPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const email = user?.email ?? "Unknown user";

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleChangePassword() {
    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      const token = authService.getToken();

      if (!token) {
        throw new Error("You are not authenticated");
      }

      const res = await fetch("http://localhost:8000/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to change password");
      }

      setMessage("Password changed successfully");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "Something went wrong";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function handleLogoutCurrentSession() {
    logout();
    navigate("/login");
  }

  return (
    <div className="security-v1">
      <section className="security-v1__hero">
        <div>
          <p className="security-v1__eyebrow">Security</p>
          <h1 className="security-v1__title security-v2__title">
            Control your
            <span> secure environment</span>
          </h1>
          <p className="security-v1__text">
            Manage your account protection, credentials, and system-level
            encryption state.
          </p>
        </div>

        <div className="security-v1__status">
          <ShieldCheck size={16} />
          All systems secure
        </div>
      </section>

      <section className="security-v1__grid">
        <div className="security-v1__card">
          <div className="security-v1__card-header">
            <ShieldCheck size={18} />
            <h2>Account security</h2>
          </div>

          <div className="security-v1__card-content">
            <div className="security-v1__row">
              <span>Email</span>
              <strong>{email}</strong>
            </div>

            <div className="security-v1__row">
              <span>Session</span>
              <strong>Active</strong>
            </div>

            <button
              type="button"
              className="button button--secondary"
              onClick={handleLogoutCurrentSession}
            >
              <LogOut size={16} />
              Logout current session
            </button>

            <p className="security-v1__muted" style={{ marginTop: 12 }}>
              Global logout across all devices is not connected yet in the backend API.
            </p>
          </div>
        </div>

        <div className="security-v1__card">
          <div className="security-v1__card-header">
            <KeyRound size={18} />
            <h2>Change password</h2>
          </div>

          <div className="security-v1__card-content">
            <input
              type="password"
              placeholder="Current password"
              className="auth-input"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />

            <input
              type="password"
              placeholder="New password"
              className="auth-input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />

            <button
              type="button"
              className="button button--primary"
              onClick={handleChangePassword}
              disabled={loading}
            >
              {loading ? "Updating..." : "Update password"}
            </button>

            {message ? (
              <p style={{ color: "#22c55e", marginTop: 8 }}>{message}</p>
            ) : null}

            {error ? (
              <p style={{ color: "#ef4444", marginTop: 8 }}>{error}</p>
            ) : null}
          </div>
        </div>

        <div className="security-v1__card security-v1__card--wide">
          <div className="security-v1__card-header">
            <Activity size={18} />
            <h2>System status</h2>
          </div>

          <div className="security-v2__status-grid">
            <div className="security-v2__status-card">
              <Server size={16} />
              <div>
                <strong>API</strong>
                <span>Operational</span>
              </div>
            </div>

            <div className="security-v2__status-card">
              <Wifi size={16} />
              <div>
                <strong>WebSocket</strong>
                <span>Connected</span>
              </div>
            </div>

            <div className="security-v2__status-card">
              <ShieldCheck size={16} />
              <div>
                <strong>Encryption</strong>
                <span>Active</span>
              </div>
            </div>
          </div>
        </div>

        <div className="security-v1__card security-v1__card--wide">
          <div className="security-v1__card-header">
            <ShieldCheck size={18} />
            <h2>Security notes</h2>
          </div>

          <p className="security-v1__muted">
            CryptoFile ensures that sensitive data is encrypted before
            transmission and securely stored. Future updates can add
            multi-device session revocation once a dedicated backend endpoint is exposed.
          </p>
        </div>
      </section>
    </div>
  );
}