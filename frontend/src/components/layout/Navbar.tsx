import { useNavigate } from "react-router-dom";
import { useAuth } from "../../features/auth/context/AuthContext";

export function Navbar() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="topbar">
      <div>
        <p className="topbar__eyebrow">CryptoFile</p>
        <h2 className="topbar__title">
          Welcome {user?.email}
        </h2>
      </div>

      <button className="button button--secondary" onClick={handleLogout}>
        Logout
      </button>
    </header>
  );
}