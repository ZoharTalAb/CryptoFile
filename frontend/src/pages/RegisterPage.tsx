import { Link } from "react-router-dom";

export function RegisterPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="section-eyebrow">Create account</p>
        <h1 className="auth-title">Join CryptoFile</h1>
        <p className="auth-subtitle">
          Create your secure account and start using protected communication.
        </p>

        <form className="auth-form">
          <label className="auth-label">
            Email
            <input className="auth-input" type="email" placeholder="you@example.com" />
          </label>

          <label className="auth-label">
            Password
            <input className="auth-input" type="password" placeholder="Create a strong password" />
          </label>

          <button type="submit" className="button button--primary button--full">
            Create Account
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}