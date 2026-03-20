import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function AppShell() {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-shell__content">
        <Navbar />
        <main className="app-shell__main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}