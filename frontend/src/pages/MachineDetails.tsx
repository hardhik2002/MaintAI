import { ArrowLeft, Gauge, Thermometer, Timer, Wrench } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Area, AreaChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { RiskBadge } from "../components/RiskBadge";
import { api } from "../services/api";
import type { Prediction } from "../types/api";

export function MachineDetails() {
  const { id = "" } = useParams(); const [current, setCurrent] = useState<Prediction>(); const [history, setHistory] = useState<Prediction[]>([]);
  useEffect(() => { const load = () => Promise.all([api.machine(id), api.history(id)]).then(([machine, points]) => { setCurrent(machine); setHistory(points); }); load(); const timer = setInterval(load, 3000); return () => clearInterval(timer); }, [id]);
  if (!current) return <div className="page"><p>Loading machine telemetry…</p></div>;
  const chartData = history.map((point) => ({...point, time: new Date(point.timestamp).toLocaleTimeString(), probability: point.failure_probability * 100}));
  return <div className="page"><Link className="back-link" to="/"><ArrowLeft /> Back to fleet</Link>
    <header className="machine-hero"><div><p className="eyebrow">ASSET / TYPE {current.type}</p><h1>{current.machine_id}</h1><p>Updated {new Date(current.timestamp).toLocaleString()}</p></div><div className="hero-risk"><RiskBadge level={current.risk_level}/><strong>{(current.failure_probability * 100).toFixed(1)}%</strong><span>calibrated failure probability</span></div></header>
    <section className="sensor-grid"><div><Thermometer/><span>Process temperature</span><strong>{current.process_temperature.toFixed(1)} K</strong></div><div><Gauge/><span>Rotational speed</span><strong>{Math.round(current.rotational_speed)} rpm</strong></div><div><Timer/><span>Torque</span><strong>{current.torque.toFixed(1)} Nm</strong></div><div><Wrench/><span>Tool wear</span><strong>{current.tool_wear.toFixed(0)} min</strong></div></section>
    <section className="details-grid"><article className="panel"><div className="panel-heading"><div><h2>Risk trajectory</h2><p>Model probability over recent telemetry</p></div></div><ResponsiveContainer width="100%" height={280}><AreaChart data={chartData}><CartesianGrid stroke="#17283a" vertical={false}/><XAxis dataKey="time" minTickGap={30}/><YAxis domain={[0,100]} tickFormatter={(v) => `${v}%`}/><Tooltip/><Area type="monotone" dataKey="probability" stroke="#36d6bf" fill="#36d6bf22" strokeWidth={2}/></AreaChart></ResponsiveContainer></article>
      <article className="panel"><div className="panel-heading"><div><h2>Prediction factors</h2><p>Local perturbation influence, not causal claims</p></div></div><div className="factor-list">{current.top_contributing_features.map((item) => <div key={item.feature}><span>{item.feature.replaceAll("_", " ")}</span><strong className={item.contribution >= 0 ? "up" : "down"}>{item.direction} risk · {Math.abs(item.contribution * 100).toFixed(1)} pp</strong></div>)}</div>{current.warnings.map((warning) => <p className="warning" key={warning}>{warning}</p>)}</article>
    </section>
    <section className="panel"><div className="panel-heading"><div><h2>Operating telemetry</h2><p>Temperatures, torque, and speed over time</p></div></div><ResponsiveContainer width="100%" height={300}><LineChart data={chartData}><CartesianGrid stroke="#17283a" vertical={false}/><XAxis dataKey="time" minTickGap={30}/><YAxis yAxisId="left"/><YAxis yAxisId="right" orientation="right"/><Tooltip/><Legend/><Line yAxisId="left" type="monotone" dataKey="air_temperature" stroke="#7c9cff" dot={false}/><Line yAxisId="left" type="monotone" dataKey="process_temperature" stroke="#ffb34d" dot={false}/><Line yAxisId="right" type="monotone" dataKey="rotational_speed" stroke="#36d6bf" dot={false}/><Line yAxisId="left" type="monotone" dataKey="torque" stroke="#ff6577" dot={false}/></LineChart></ResponsiveContainer></section>
  </div>;
}

