import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  Folder,
  Shield,
  Sparkles,
} from "lucide-react";

export function Sidebar() {
  return (
    <aside className="sidebar-v2">
      <div className="sidebar-v2__logo">
        <div className="sidebar-v2__logo-icon">🔐</div>
        <span>CryptoFile</span>
      </div>

      <nav className="sidebar-v2__nav">
        <NavLink to="/dashboard" className="sidebar-v2__link">
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

        <NavLink to="/chat" className="sidebar-v2__link">
          <MessageSquare size={18} />
          Secure Chat
        </NavLink>

        <NavLink to="/files" className="sidebar-v2__link">
          <Folder size={18} />
          Vault Files
        </NavLink>

        <NavLink to="/stego" className="sidebar-v2__link">
          <Sparkles size={18} />
          Stego Lab
        </NavLink>

        <NavLink to="/security" className="sidebar-v2__link">
          <Shield size={18} />
          Security
        </NavLink>
      </nav>
    </aside>
  );
}