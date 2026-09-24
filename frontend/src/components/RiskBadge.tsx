import type { RiskLevel } from "../types/api";

export function RiskBadge({ level }: { level: RiskLevel }) {
  return <span className={`risk-badge risk-${level.toLowerCase()}`}><i />{level}</span>;
}

