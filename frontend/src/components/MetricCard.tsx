import type { ReactNode } from "react";

export function MetricCard({ label, value, detail, icon }: { label: string; value: string | number; detail?: string; icon: ReactNode }) {
  return <article className="metric-card"><div className="metric-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong>{detail && <small>{detail}</small>}</div></article>;
}
