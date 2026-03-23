import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  return (
    <div className="app-shell-v2">
      <Sidebar />

      <div className="app-shell-v2__main">
        <Topbar />
        <main className="app-shell-v2__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}