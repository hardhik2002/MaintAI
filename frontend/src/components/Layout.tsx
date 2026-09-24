import { Activity, BarChart3, Gauge, Radio } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark"><Activity /></span><div><strong>MaintAI</strong><small>Intelligent Maintenance</small></div></div>
        <nav>
          <NavLink to="/" end><Gauge /> Fleet Overview</NavLink>
          <NavLink to="/insights"><BarChart3 /> Model Insights</NavLink>
        </nav>
        <div className="system-status"><Radio /><div><strong>Simulation live</strong><small>Polling every 3 seconds</small></div></div>
      </aside>
      <main><Outlet /></main>
    </div>
  );
}

