import { useState } from "react";
import {
  Activity,
  KeyRound,
  LogOut,
  Server,
  ShieldCheck,
  Wifi,
  X,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../features/auth/context/AuthContext";
import { authService } from "../features/auth/services/auth.service";
import { api } from "../lib/api";

type ApiErrorLike = {
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
      message?: unknown;
    };
  };
  message?: string;
};

function getApiErrorMessage(error: unknown): string {
  const apiError = error as ApiErrorLike;
  const status = apiError.response?.status;
  const detail = apiError.response?.data?.detail;
  const message = apiError.response?.data?.message;

  if (typeof detail === "string") {
    const lowerDetail = detail.toLowerCase();

    if (lowerDetail.includes("invalid current password")) {
      return "The current password you entered is incorrect. Please try again.";
    }

    if (lowerDetail.includes("already used")) {
      return "For security reasons, your new password cannot be one you used recently.";
    }

    if (lowerDetail.includes("password")) {
      return detail;
    }

    return detail;
  }

  if (typeof message === "string") {
    return message;
  }

  if (status === 401) {
    return "The current password you entered is incorrect. Please try again.";
  }

  if (status === 400) {
    return "The new password does not meet the security requirements. Please choose a stronger password.";
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return "Something went wrong while updating your password. Please try again.";
}

export function SecurityPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const email = user?.email ?? "Unknown user";

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showReloginModal, setShowReloginModal] = useState(false);

  async function handleChangePassword() {
    setError(null);

    if (!currentPassword.trim()) {
      setError("Please enter your current password.");
      return;
    }

    if (!newPassword.trim()) {
      setError("Please enter a new password.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Your new password must contain at least 8 characters.");
      return;
    }

    if (currentPassword === newPassword) {
      setError("Your new password must be different from your current password.");
      return;
    }

    setLoading(true);

    try {
      const token = authService.getToken();

      if (!token) {
        throw new Error("You are not authenticated");
      }

      await api.post(
        "/auth/change-password",
        {
          current_password: currentPassword,
          new_password: newPassword,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setCurrentPassword("");
      setNewPassword("");
      setShowReloginModal(true);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  function handleLogoutCurrentSession() {
    logout();
    navigate("/login");
  }

  function handleReloginRedirect() {
    logout();
    navigate("/login");
  }

  return (
    <>
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
                disabled={loading || showReloginModal}
              />

              <input
                type="password"
                placeholder="New password"
                className="auth-input"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading || showReloginModal}
              />

              <button
                type="button"
                className="button button--primary"
                onClick={handleChangePassword}
                disabled={loading || showReloginModal}
              >
                {loading ? "Updating..." : "Update password"}
              </button>

              {error ? (
                <div className="auth-alert auth-alert--error security-v1__password-error">
                  {error}
                </div>
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

      {showReloginModal ? (
        <div className="security-modal__overlay" role="dialog" aria-modal="true">
          <div className="security-modal">
            <button
              type="button"
              className="security-modal__close"
              onClick={handleReloginRedirect}
              aria-label="Close and go to login"
            >
              <X size={18} />
            </button>

            <div className="security-modal__icon">
              <ShieldCheck size={22} />
            </div>

            <p className="security-modal__eyebrow">Security updated</p>

            <h2 className="security-modal__title">
              Password changed successfully
            </h2>

            <p className="security-modal__text">
              Your secure session has been invalidated because the password was updated.
            </p>

            <div className="security-modal__status">
              <span className="security-modal__status-dot" />
              Session invalidated
            </div>

            <p className="security-modal__subtext">
              Please sign in again to continue using your protected workspace with the new credentials.
            </p>

            <div className="security-modal__actions">
              <button
                type="button"
                className="button button--primary"
                onClick={handleReloginRedirect}
              >
                Go to login
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}