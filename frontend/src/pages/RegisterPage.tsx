import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, FileLock2, ShieldCheck, Wand2 } from "lucide-react";
import { useState } from "react";
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

export function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [accepted, setAccepted] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!accepted) {
      setError("Please confirm account creation");
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        email: email.trim(),
        password,
      });

      navigate("/verify-email", {
        replace: true,
        state: { email: email.trim(), registered: true },
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-screen auth-screen--register">
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
              <span>Already have an account?</span>
              <Link to="/login">Sign in</Link>
            </div>
          </div>

          <div className="auth-copy">
            <motion.p className="section-eyebrow" {...appear(0.05)}>
              Create account
            </motion.p>

            <motion.h1 className="auth-title auth-title--large" {...appear(0.1)}>
              Create your private CryptoFile account
            </motion.h1>

            <motion.p className="auth-subtitle auth-subtitle--wide" {...appear(0.15)}>
              Get started with protected messaging, steganographic workflows, and
              secure file management in one product experience.
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
                disabled={loading}
                required
              />
            </label>

            <label className="auth-label">
              <span>Password</span>
              <input
                className="auth-input"
                type="password"
                placeholder="Create a strong password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
              />
            </label>

            <label className="auth-label">
              <span>Confirm password</span>
              <input
                className="auth-input"
                type="password"
                placeholder="Repeat your password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                required
              />
            </label>

            <label className="auth-check auth-check--block">
              <input
                type="checkbox"
                checked={accepted}
                onChange={(e) => setAccepted(e.target.checked)}
                disabled={loading}
              />
              <span>I agree to create a secure CryptoFile workspace account.</span>
            </label>

            {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}

            <button
              type="submit"
              className="button button--primary button--full"
              disabled={loading}
            >
              {loading ? "Creating Account..." : "Create Account"}
              {!loading && <ArrowRight size={16} />}
            </button>
          </motion.form>

          <motion.p className="auth-footer auth-footer--large" {...appear(0.25)}>
            Already have an account? <Link to="/login">Sign in</Link>
          </motion.p>
        </motion.section>

        <motion.aside className="auth-panel auth-panel--visual" {...appear(0.08)}>
          <div className="auth-visual">
            <div className="auth-visual__badge">
              <ShieldCheck size={16} />
              <span>Private workspace setup</span>
            </div>

            <h2 className="auth-visual__title">
              Start using secure messaging and file protection
            </h2>

            <p className="auth-visual__text">
              Create your account to access protected communication flows,
              steganography tools, and organized file handling from day one.
            </p>

            <div className="auth-feature-list">
              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <Wand2 size={18} />
                </div>
                <div>
                  <h3>Stego workflow</h3>
                  <p>Conceal sensitive payloads through a guided interface.</p>
                </div>
              </article>

              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <FileLock2 size={18} />
                </div>
                <div>
                  <h3>Protected files</h3>
                  <p>Keep communication and file operations in one workspace.</p>
                </div>
              </article>
            </div>

            <div className="auth-mini-preview auth-mini-preview--register">
              <div className="auth-mini-preview__header">
                <span className="auth-mini-preview__dot" />
                <span className="auth-mini-preview__dot" />
                <span className="auth-mini-preview__dot" />
              </div>

              <div className="auth-mini-preview__body auth-mini-preview__body--stack">
                <div className="auth-mini-preview__card">
                  <span>Protected files</span>
                  <strong>689</strong>
                </div>
                <div className="auth-mini-preview__card">
                  <span>Embedded payloads</span>
                  <strong>124</strong>
                </div>
                <div className="auth-mini-preview__card auth-mini-preview__card--accent">
                  Workspace ready for secure onboarding
                </div>
              </div>
            </div>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}