import { motion } from "framer-motion";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Copy,
  Lock,
  MessageSquareMore,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { authService } from "../features/auth/services/auth.service";
import { useAuth } from "../features/auth/context/AuthContext";

const appear = (delay = 0) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.65,
    delay,
    ease: "easeOut" as const,
  },
});

type LoginMode = "login" | "request-reset" | "confirm-reset";

type LocationState = {
  registered?: boolean;
  email?: string;
};

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, loading, refreshSession } = useAuth();

  const state = (location.state as LocationState | null) ?? null;

  const [mode, setMode] = useState<LoginMode>("login");

  const [email, setEmail] = useState(state?.email ?? "");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);

  const [resetToken, setResetToken] = useState("");
  const [resetPassword, setResetPassword] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const resetTokenPreview = useMemo(() => {
    return resetToken.trim();
  }, [resetToken]);

  useEffect(() => {
    if (!loading && user) {
      navigate("/dashboard", { replace: true });
    }
  }, [loading, user, navigate]);

  useEffect(() => {
    if (state?.registered) {
      setSuccess("Account created successfully. You can sign in now.");
    }
  }, [state]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      const response = await authService.login({
        email: email.trim(),
        password,
      });

      authService.saveToken(response.access_token, rememberMe);
      await refreshSession();
      navigate("/dashboard", { replace: true });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRequestReset(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      const response = await authService.requestPasswordReset(email.trim());

      setResetToken(response.reset_token ?? "");
      setSuccess(
        response.reset_token
          ? "Reset token issued. Paste it below and choose a new password."
          : "If the account exists, a reset token was issued."
      );
      setMode("confirm-reset");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleConfirmReset(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      const response = await authService.confirmPasswordReset(
        resetToken.trim(),
        resetPassword
      );

      setSuccess(response.message || "Password reset successfully.");
      setPassword("");
      setResetPassword("");
      setResetToken("");
      setMode("login");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleCopyToken() {
    if (!resetTokenPreview) return;

    try {
      await navigator.clipboard.writeText(resetTokenPreview);
      setSuccess("Reset token copied to clipboard.");
    } catch {
      setError("Could not copy reset token.");
    }
  }

  function goToLoginMode() {
    setMode("login");
    setError("");
    setSuccess("");
  }

  if (loading) {
    return (
      <div className="auth-screen auth-screen--login">
        <div className="auth-screen__backdrop" />
        <div className="auth-screen__grid" />
        <div className="auth-loading">
          <div className="auth-loading__dot" />
          <p>Checking secure session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-screen auth-screen--login">
      <div className="auth-screen__backdrop" />
      <div className="auth-screen__grid" />

      <div className="auth-layout">
        <motion.section className="auth-panel auth-panel--content" {...appear(0)}>
          <div className="auth-panel__top">
            <Link to="/" className="auth-brand">
              <span className="brand-mark">C</span>
              <span>CryptoFile</span>
            </Link>

            <div className="auth-switch">
              <span>New here?</span>
              <Link to="/register">Create account</Link>
            </div>
          </div>

          <div className="auth-copy">
            <motion.p className="section-eyebrow" {...appear(0.05)}>
              {mode === "login"
                ? "Welcome back"
                : mode === "request-reset"
                ? "Forgot password"
                : "Reset password"}
            </motion.p>

            <motion.h1 className="auth-title auth-title--large" {...appear(0.1)}>
              {mode === "login"
                ? "Sign in to your secure workspace"
                : mode === "request-reset"
                ? "Request a password reset token"
                : "Set a new password"}
            </motion.h1>

            <motion.p className="auth-subtitle auth-subtitle--wide" {...appear(0.15)}>
              {mode === "login"
                ? "Access protected conversations, steganography tools, and secure file management from one modern workspace."
                : mode === "request-reset"
                ? "Enter your account email and CryptoFile will issue a reset token through the current backend flow."
                : "Paste the reset token and choose a new password to recover access to your workspace."}
            </motion.p>
          </div>

          {mode === "login" ? (
            <motion.form
              className="auth-form auth-form--premium"
              onSubmit={handleSubmit}
              {...appear(0.2)}
            >
              <label className="auth-label">
                <span>Email</span>
                <input
                  className="auth-input"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={submitting}
                  required
                />
              </label>

              <label className="auth-label">
                <span>Password</span>
                <input
                  className="auth-input"
                  type="password"
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={submitting}
                  required
                />
              </label>

              <div className="auth-form__meta">
                <label className="auth-check">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    disabled={submitting}
                  />
                  <span>Remember me</span>
                </label>

                <button
                  type="button"
                  className="auth-text-button"
                  onClick={() => {
                    setMode("request-reset");
                    setError("");
                    setSuccess("");
                  }}
                  disabled={submitting}
                >
                  Forgot password?
                </button>
              </div>

              {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}
              {success ? (
                <div className="auth-alert auth-alert--success">{success}</div>
              ) : null}

              <button
                type="submit"
                className="button button--primary button--full"
                disabled={submitting}
              >
                {submitting ? "Signing In..." : "Sign In"}
                {!submitting && <ArrowRight size={16} />}
              </button>
            </motion.form>
          ) : null}

          {mode === "request-reset" ? (
            <motion.form
              className="auth-form auth-form--premium"
              onSubmit={handleRequestReset}
              {...appear(0.2)}
            >
              <label className="auth-label">
                <span>Account email</span>
                <input
                  className="auth-input"
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={submitting}
                  required
                />
              </label>

              {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}
              {success ? (
                <div className="auth-alert auth-alert--success">{success}</div>
              ) : null}

              <div className="auth-reset-actions">
                <button
                  type="submit"
                  className="button button--primary"
                  disabled={submitting}
                >
                  {submitting ? "Requesting..." : "Issue reset token"}
                </button>

                <button
                  type="button"
                  className="button button--secondary"
                  onClick={goToLoginMode}
                  disabled={submitting}
                >
                  Back to sign in
                </button>
              </div>
            </motion.form>
          ) : null}

          {mode === "confirm-reset" ? (
            <motion.form
              className="auth-form auth-form--premium"
              onSubmit={handleConfirmReset}
              {...appear(0.2)}
            >
              <label className="auth-label">
                <span>Reset token</span>
                <input
                  className="auth-input"
                  type="text"
                  placeholder="Paste reset token"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  disabled={submitting}
                  required
                />
              </label>

              {resetTokenPreview ? (
                <div className="auth-reset-token-card">
                  <div>
                    <strong>Issued reset token</strong>
                    <p>{resetTokenPreview}</p>
                  </div>

                  <button
                    type="button"
                    className="button button--secondary"
                    onClick={handleCopyToken}
                  >
                    <Copy size={16} />
                    Copy
                  </button>
                </div>
              ) : null}

              <label className="auth-label">
                <span>New password</span>
                <input
                  className="auth-input"
                  type="password"
                  placeholder="Choose a strong new password"
                  autoComplete="new-password"
                  value={resetPassword}
                  onChange={(e) => setResetPassword(e.target.value)}
                  disabled={submitting}
                  required
                />
              </label>

              {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}
              {success ? (
                <div className="auth-alert auth-alert--success">{success}</div>
              ) : null}

              <div className="auth-reset-actions">
                <button
                  type="submit"
                  className="button button--primary"
                  disabled={submitting}
                >
                  {submitting ? "Resetting..." : "Confirm password reset"}
                </button>

                <button
                  type="button"
                  className="button button--secondary"
                  onClick={() => {
                    setMode("request-reset");
                    setError("");
                    setSuccess("");
                  }}
                  disabled={submitting}
                >
                  Back
                </button>
              </div>
            </motion.form>
          ) : null}

          <motion.p className="auth-footer auth-footer--large" {...appear(0.25)}>
            Don&apos;t have an account? <Link to="/register">Create account</Link>
          </motion.p>
        </motion.section>

        <motion.aside className="auth-panel auth-panel--visual" {...appear(0.08)}>
          <div className="auth-visual">
            <div className="auth-visual__badge">
              <ShieldCheck size={16} />
              <span>
                {mode === "login"
                  ? "Protected workspace access"
                  : "Credential recovery flow"}
              </span>
            </div>

            <h2 className="auth-visual__title">
              {mode === "login"
                ? "Protected messaging and file workflows in one workspace"
                : "Recover access without leaving the secure flow"}
            </h2>

            <p className="auth-visual__text">
              {mode === "login"
                ? "Sign in to continue secure conversations, steganography workflows, and protected file handling from one polished product surface."
                : "CryptoFile already exposes password reset endpoints in the backend flow, so this screen now gives you a usable recovery path instead of a dead button."}
            </p>

            <div className="auth-feature-list">
              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <MessageSquareMore size={18} />
                </div>
                <div>
                  <h3>Secure chat</h3>
                  <p>Protected conversations connected to file delivery.</p>
                </div>
              </article>

              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <Lock size={18} />
                </div>
                <div>
                  <h3>Controlled access</h3>
                  <p>Security-first entry into your private environment.</p>
                </div>
              </article>
            </div>

            <div className="auth-mini-preview">
              <div className="auth-mini-preview__header">
                <span className="auth-mini-preview__dot" />
                <span className="auth-mini-preview__dot" />
                <span className="auth-mini-preview__dot" />
              </div>

              <div className="auth-mini-preview__body">
                <div className="auth-mini-preview__sidebar">
                  <div className="auth-mini-preview__sidebar-item auth-mini-preview__sidebar-item--active">
                    Dashboard
                  </div>
                  <div className="auth-mini-preview__sidebar-item">Secure Chat</div>
                  <div className="auth-mini-preview__sidebar-item">File Vault</div>
                </div>

                <div className="auth-mini-preview__content">
                  <div className="auth-mini-preview__stat">
                    <span>Secure threads</span>
                    <strong>372</strong>
                  </div>
                  <div className="auth-mini-preview__message">
                    {mode === "login"
                      ? "Protected session ready"
                      : "Password recovery flow active"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}