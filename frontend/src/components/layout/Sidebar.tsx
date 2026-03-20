import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/chat", label: "Secure Chat" },
  { to: "/files", label: "My Files" },
  { to: "/stego", label: "Stego Lab" },
  { to: "/security", label: "Security" },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__logo">C</div>
        <div>
          <h1 className="sidebar__title">CryptoFile</h1>
          <p className="sidebar__subtitle">Private by design</p>
        </div>
      </div>

      <nav className="sidebar__nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive
                ? "sidebar__link sidebar__link--active"
                : "sidebar__link"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}