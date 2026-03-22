import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Lock, MessageSquareMore, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
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

export function LoginPage() {
  const navigate = useNavigate();
  const { user, loading, refreshSession } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && user) {
      navigate("/dashboard", { replace: true });
    }
  }, [loading, user, navigate]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      const response = await authService.login({
        email: email.trim(),
        password,
      });

      authService.saveToken(response.access_token);
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
              Welcome back
            </motion.p>

            <motion.h1 className="auth-title auth-title--large" {...appear(0.1)}>
              Sign in to your secure workspace
            </motion.h1>

            <motion.p className="auth-subtitle auth-subtitle--wide" {...appear(0.15)}>
              Access protected conversations, steganography tools, and secure file
              management from one modern workspace.
            </motion.p>
          </div>

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
                <input type="checkbox" disabled />
                <span>Remember me</span>
              </label>

              <button type="button" className="auth-text-button" disabled>
                Forgot password?
              </button>
            </div>

            {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}

            <button
              type="submit"
              className="button button--primary button--full"
              disabled={submitting}
            >
              {submitting ? "Signing In..." : "Sign In"}
              {!submitting && <ArrowRight size={16} />}
            </button>
          </motion.form>

          <motion.p className="auth-footer auth-footer--large" {...appear(0.25)}>
            Don&apos;t have an account? <Link to="/register">Create one</Link>
          </motion.p>
        </motion.section>

        <motion.aside className="auth-panel auth-panel--visual" {...appear(0.08)}>
          <div className="auth-visual">
            <div className="auth-visual__badge">
              <ShieldCheck size={16} />
              <span>Protected access</span>
            </div>

            <h2 className="auth-visual__title">
              Continue your secure communication flow
            </h2>

            <p className="auth-visual__text">
              Sign in to reach your private workspace, manage protected assets,
              and continue secure delivery without friction.
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
                    Protected session ready
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