import { AlertTriangle, CheckCircle2, Factory, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MetricCard } from "../components/MetricCard";
import { RiskBadge } from "../components/RiskBadge";
import { api } from "../services/api";
import type { Alert, Machine } from "../types/api";

export function Dashboard() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    const load = () => Promise.all([api.machines(), api.alerts()])
      .then(([nextMachines, nextAlerts]) => { setMachines(nextMachines); setAlerts(nextAlerts); setError(""); })
      .catch((reason: Error) => setError(reason.message));
    load(); const timer = window.setInterval(load, 3000); return () => clearInterval(timer);
  }, []);
  const counts = useMemo(() => ({
    healthy: machines.filter((m) => ["HEALTHY", "LOW"].includes(m.risk_level)).length,
    warning: machines.filter((m) => m.risk_level === "MEDIUM").length,
    critical: machines.filter((m) => ["HIGH", "CRITICAL"].includes(m.risk_level)).length,
  }), [machines]);
  const fleetHealth = machines.length ? Math.round(100 * machines.filter((m) => !["HIGH", "CRITICAL"].includes(m.risk_level)).length / machines.length) : 0;

  return <div className="page">
    <header className="page-header"><div><p className="eyebrow">OPERATIONS / LIVE</p><h1>Fleet overview</h1><p>Real-time machine health and predictive risk signals.</p></div><div className="live-pill"><i /> Live telemetry</div></header>
    {error && <div className="error-banner">Backend unavailable: {error}. Start the API and simulator to populate live data.</div>}
    <section className="metrics-grid">
      <MetricCard label="Total machines" value={machines.length} detail="Monitored assets" icon={<Factory />} />
      <MetricCard label="Fleet health" value={`${fleetHealth}%`} detail={`${counts.healthy} normal`} icon={<CheckCircle2 />} />
      <MetricCard label="Needs attention" value={counts.warning} detail="Medium risk" icon={<AlertTriangle />} />
      <MetricCard label="High priority" value={counts.critical} detail="High or critical" icon={<ShieldAlert />} />
    </section>
    <section className="dashboard-grid">
      <article className="panel fleet-panel"><div className="panel-heading"><div><h2>Machine fleet</h2><p>Ranked by current failure probability</p></div><span>{machines.length} assets</span></div>
        <div className="table-wrap"><table><thead><tr><th>Machine</th><th>Status</th><th>Risk score</th><th>Temperature</th><th>Speed</th><th>Torque</th></tr></thead><tbody>
          {machines.map((machine) => <tr key={machine.machine_id}><td><Link to={`/machines/${machine.machine_id}`}><strong>{machine.machine_id}</strong><small>Type {machine.type}</small></Link></td><td><RiskBadge level={machine.risk_level} /></td><td><div className="risk-meter"><span style={{ width: `${machine.failure_probability * 100}%` }} /><em>{(machine.failure_probability * 100).toFixed(1)}%</em></div></td><td>{machine.process_temperature.toFixed(1)} K</td><td>{Math.round(machine.rotational_speed)} rpm</td><td>{machine.torque.toFixed(1)} Nm</td></tr>)}
          {!machines.length && <tr><td colSpan={6} className="empty">Waiting for telemetry…</td></tr>}
        </tbody></table></div>
      </article>
      <aside className="panel alerts-panel"><div className="panel-heading"><div><h2>Recent alerts</h2><p>State-transition events</p></div></div>
        <div className="alert-list">{alerts.slice(0, 6).map((alert) => <Link to={`/machines/${alert.machine_id}`} className="alert-item" key={alert.id}><AlertTriangle /><div><strong>{alert.machine_id}</strong><p>{alert.message}</p><small>{new Date(alert.timestamp).toLocaleTimeString()}</small></div><RiskBadge level={alert.severity} /></Link>)}{!alerts.length && <p className="empty">No high-risk transitions recorded.</p>}</div>
      </aside>
    </section>
    <section className="panel compact-chart"><div className="panel-heading"><div><h2>Fleet risk snapshot</h2><p>Latest model probability by asset</p></div></div><ResponsiveContainer width="100%" height={220}><AreaChart data={[...machines].reverse()}><defs><linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#36d6bf" stopOpacity={0.4}/><stop offset="100%" stopColor="#36d6bf" stopOpacity={0}/></linearGradient></defs><XAxis dataKey="machine_id" tick={{fill: "#70849a", fontSize: 11}} axisLine={false}/><YAxis domain={[0, 1]} tickFormatter={(v) => `${v * 100}%`} tick={{fill: "#70849a", fontSize: 11}} axisLine={false}/><Tooltip formatter={(value) => `${(Number(value) * 100).toFixed(1)}%`} /><Area type="monotone" dataKey="failure_probability" stroke="#36d6bf" fill="url(#riskFill)" strokeWidth={2}/></AreaChart></ResponsiveContainer></section>
  </div>;
}

