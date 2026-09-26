import type { Alert, Machine, ModelMetrics, Prediction } from "../types/api";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8001";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  machines: () => request<Machine[]>("/api/v1/machines"),
  machine: (id: string) => request<Prediction>(`/api/v1/machines/${id}`),
  history: (id: string) => request<Prediction[]>(`/api/v1/machines/${id}/history?limit=120`),
  alerts: () => request<Alert[]>("/api/v1/alerts"),
  metrics: () => request<ModelMetrics>("/api/v1/model/metrics"),
};

