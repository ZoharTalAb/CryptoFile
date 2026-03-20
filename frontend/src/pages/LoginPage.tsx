import { Link } from "react-router-dom";

export function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="section-eyebrow">Welcome back</p>
        <h1 className="auth-title">Sign in to CryptoFile</h1>
        <p className="auth-subtitle">
          Access your secure workspace, conversations, and files.
        </p>

        <form className="auth-form">
          <label className="auth-label">
            Email
            <input className="auth-input" type="email" placeholder="you@example.com" />
          </label>

          <label className="auth-label">
            Password
            <input className="auth-input" type="password" placeholder="Enter your password" />
          </label>

          <button type="submit" className="button button--primary button--full">
            Sign In
          </button>
        </form>

        <p className="auth-footer">
          Don&apos;t have an account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}