import { useNavigate } from "react-router-dom";

export function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("cryptofile_token");
    navigate("/login");
  }

  return (
    <header className="topbar">
      <div>
        <p className="topbar__eyebrow">CryptoFile</p>
        <h2 className="topbar__title">Secure Workspace</h2>
      </div>

      <button className="button button--secondary" onClick={handleLogout}>
        Logout
      </button>
    </header>
  );
}