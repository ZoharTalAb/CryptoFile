import { motion } from "framer-motion";
import { ArrowRight, Lock, ShieldCheck } from "lucide-react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useMemo, useState } from "react";
import { authService } from "../features/auth/services/auth.service";

const appear = (delay = 0) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.65,
    delay,
    ease: "easeOut" as const,
  },
});

export function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = useMemo(() => searchParams.get("token") ?? "", [searchParams]);

  const [newPassword, setNewPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!token.trim()) {
      setError("Missing or invalid reset token.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await authService.confirmPasswordReset(
        token.trim(),
        newPassword
      );

      setSuccess(response.message || "Password reset successfully.");
      setNewPassword("");

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setSubmitting(false);
    }
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
              <span>Remembered your password?</span>
              <Link to="/login">Back to sign in</Link>
            </div>
          </div>

          <div className="auth-copy">
            <motion.p className="section-eyebrow" {...appear(0.05)}>
              Reset password
            </motion.p>

            <motion.h1 className="auth-title auth-title--large" {...appear(0.1)}>
              Create a new secure password
            </motion.h1>

            <motion.p className="auth-subtitle auth-subtitle--wide" {...appear(0.15)}>
              Choose a strong new password to restore access to your protected
              workspace.
            </motion.p>
          </div>

          <motion.form
            className="auth-form auth-form--premium"
            onSubmit={handleSubmit}
            {...appear(0.2)}
          >
            <label className="auth-label">
              <span>New password</span>
              <input
                className="auth-input"
                type="password"
                placeholder="Choose a strong new password"
                autoComplete="new-password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={submitting}
                required
              />
            </label>

            {!token ? (
              <div className="auth-alert auth-alert--error">
                Missing reset token. Please open the reset link directly from your email.
              </div>
            ) : null}

            {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}
            {success ? (
              <div className="auth-alert auth-alert--success">{success}</div>
            ) : null}

            <button
              type="submit"
              className="button button--primary button--full"
              disabled={submitting || !token}
            >
              {submitting ? "Updating..." : "Reset password"}
              {!submitting && <ArrowRight size={16} />}
            </button>
          </motion.form>
        </motion.section>

        <motion.aside className="auth-panel auth-panel--visual" {...appear(0.08)}>
          <div className="auth-visual">
            <div className="auth-visual__badge">
              <ShieldCheck size={16} />
              <span>Protected recovery flow</span>
            </div>

            <h2 className="auth-visual__title">
              Reset access without compromising your workspace
            </h2>

            <p className="auth-visual__text">
              CryptoFile now uses an email-based recovery flow, so only the owner
              of the mailbox can complete the password reset.
            </p>

            <div className="auth-feature-list">
              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <ShieldCheck size={18} />
                </div>
                <div>
                  <h3>Email verified recovery</h3>
                  <p>Only the mailbox owner can reach this reset step.</p>
                </div>
              </article>

              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <Lock size={18} />
                </div>
                <div>
                  <h3>Short-lived token</h3>
                  <p>Password reset tokens expire and cannot be reused.</p>
                </div>
              </article>
            </div>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}