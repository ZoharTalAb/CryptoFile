import { motion } from "framer-motion";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, MailCheck, RefreshCw, ShieldCheck } from "lucide-react";
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

type LocationState = {
  email?: string;
  registered?: boolean;
};

function normalizeCode(value: string) {
  return value.replace(/\D/g, "").slice(0, 6);
}

export function VerifyEmailPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state as LocationState | null) ?? null;

  const [email, setEmail] = useState(state?.email ?? "");
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(
    state?.registered
      ? "Account created. We sent a verification code to your email."
      : ""
  );

  async function handleVerify(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalizedEmail = email.trim();
    const normalizedCode = normalizeCode(code);

    setError("");
    setSuccess("");

    if (!normalizedEmail) {
      setError("Email is required.");
      return;
    }

    if (normalizedCode.length !== 6) {
      setError("Please enter the 6-digit verification code.");
      return;
    }

    setLoading(true);

    try {
      await authService.verifyEmail({
        email: normalizedEmail,
        code: normalizedCode,
      });

      navigate("/login", {
        replace: true,
        state: {
          email: normalizedEmail,
          registered: true,
        },
      });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Could not verify email. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    const normalizedEmail = email.trim();

    setError("");
    setSuccess("");

    if (!normalizedEmail) {
      setError("Email is required before requesting a new code.");
      return;
    }

    setResending(true);

    try {
      const response = await authService.resendVerificationCode(normalizedEmail);
      setSuccess(response.message || "A new verification code has been sent.");
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Could not send a new code.";
      setError(message);
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="auth-screen auth-screen--verify-email">
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
              <span>Already verified?</span>
              <Link to="/login">Sign in</Link>
            </div>
          </div>

          <div className="auth-copy">
            <motion.p className="section-eyebrow" {...appear(0.05)}>
              Verify email
            </motion.p>

            <motion.h1 className="auth-title auth-title--large" {...appear(0.1)}>
              Enter your verification code
            </motion.h1>

            <motion.p className="auth-subtitle auth-subtitle--wide" {...appear(0.15)}>
              We sent a 6-digit code to your email. Verify your account before
              accessing your secure workspace.
            </motion.p>
          </div>

          <motion.form
            className="auth-form auth-form--premium"
            onSubmit={handleVerify}
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
                disabled={loading || resending}
                required
              />
            </label>

            <label className="auth-label">
              <span>Verification code</span>
              <input
                className="auth-input"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                placeholder="123456"
                autoComplete="one-time-code"
                value={code}
                onChange={(e) => setCode(normalizeCode(e.target.value))}
                disabled={loading || resending}
                required
              />
            </label>

            {error ? <div className="auth-alert auth-alert--error">{error}</div> : null}
            {success ? (
              <div className="auth-alert auth-alert--success">{success}</div>
            ) : null}

            <button
              type="submit"
              className="button button--primary button--full"
              disabled={loading || resending}
            >
              {loading ? "Verifying..." : "Verify account"}
              {!loading && <ArrowRight size={16} />}
            </button>

            <button
              type="button"
              className="button button--secondary button--full"
              disabled={loading || resending}
              onClick={() => void handleResend()}
            >
              <RefreshCw size={16} />
              {resending ? "Sending new code..." : "Resend code"}
            </button>
          </motion.form>
        </motion.section>

        <motion.aside className="auth-panel auth-panel--visual" {...appear(0.08)}>
          <div className="auth-visual">
            <div className="auth-visual__badge">
              <MailCheck size={16} />
              <span>Email verification required</span>
            </div>

            <h2 className="auth-visual__title">
              One more step before opening your secure workspace
            </h2>

            <p className="auth-visual__text">
              Email verification helps ensure that only the real account owner can
              activate a CryptoFile workspace.
            </p>

            <div className="auth-feature-list">
              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <ShieldCheck size={18} />
                </div>
                <div>
                  <h3>Account protection</h3>
                  <p>Unverified accounts cannot sign in until the code is confirmed.</p>
                </div>
              </article>

              <article className="auth-feature-card">
                <div className="auth-feature-card__icon">
                  <MailCheck size={18} />
                </div>
                <div>
                  <h3>Code-based flow</h3>
                  <p>Users receive a short verification code directly by email.</p>
                </div>
              </article>
            </div>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}
