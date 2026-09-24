export type RiskLevel = "HEALTHY" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Machine {
  machine_id: string;
  type: string;
  timestamp: string;
  risk_level: RiskLevel;
  failure_probability: number;
  air_temperature: number;
  process_temperature: number;
  rotational_speed: number;
  torque: number;
  tool_wear: number;
}

export interface Prediction extends Machine {
  record_id: number;
  failure_prediction: boolean;
  predicted_failure_modes: string[];
  top_contributing_features: Array<{ feature: string; value: string | number; contribution: number; direction: string }>;
  warnings: string[];
  model_version: string;
  inference_ms: number;
}

export interface Alert {
  id: number; timestamp: string; machine_id: string; severity: RiskLevel;
  risk_score: number; message: string; acknowledged: boolean;
}

export interface ModelMetrics {
  model_version: string;
  algorithm: string;
  decision_threshold: number;
  test_metrics: Record<string, number | number[][]>;
  model_comparison: Record<string, Record<string, number>>;
  feature_importance: Array<{ feature: string; importance: number; std: number }>;
}

