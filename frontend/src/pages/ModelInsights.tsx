import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../services/api";
import type { ModelMetrics } from "../types/api";

export function ModelInsights() {
  const [data, setData] = useState<ModelMetrics>(); useEffect(() => { api.metrics().then(setData); }, []);
  if (!data) return <div className="page"><p>Loading measured model results…</p></div>;
  const metric = (key: string) => Number(data.test_metrics[key] ?? 0);
  const comparison = Object.entries(data.model_comparison).map(([name, values]) => ({ name: name.replaceAll("_", " "), pr_auc: values.pr_auc }));
  return <div className="page"><header className="page-header"><div><p className="eyebrow">MODEL / EVALUATION</p><h1>Model insights</h1><p>Measured on the untouched AI4I test split—never fabricated.</p></div><span className="version-pill">{data.model_version}</span></header>
    <section className="metrics-grid model-metrics">{[["Algorithm", data.algorithm.replaceAll("_", " ")],["PR-AUC", metric("pr_auc").toFixed(3)],["Recall", metric("recall").toFixed(3)],["Precision", metric("precision").toFixed(3)],["F1 score", metric("f1").toFixed(3)],["Threshold", data.decision_threshold.toFixed(3)]].map(([label,value]) => <article className="stat" key={label}><span>{label}</span><strong>{value}</strong></article>)}</section>
    <section className="details-grid"><article className="panel"><div className="panel-heading"><div><h2>Candidate comparison</h2><p>Mean 5-fold cross-validation PR-AUC</p></div></div><ResponsiveContainer width="100%" height={300}><BarChart data={comparison} layout="vertical"><CartesianGrid stroke="#17283a" horizontal={false}/><XAxis type="number" domain={[0,1]}/><YAxis dataKey="name" type="category" width={130}/><Tooltip/><Bar dataKey="pr_auc" fill="#36d6bf" radius={[0,5,5,0]}/></BarChart></ResponsiveContainer></article>
      <article className="panel"><div className="panel-heading"><div><h2>Permutation importance</h2><p>Test-set PR-AUC decrease after shuffling</p></div></div><ResponsiveContainer width="100%" height={300}><BarChart data={data.feature_importance} layout="vertical"><CartesianGrid stroke="#17283a" horizontal={false}/><XAxis type="number"/><YAxis dataKey="feature" type="category" width={130}/><Tooltip/><Bar dataKey="importance" fill="#7c9cff" radius={[0,5,5,0]}/></BarChart></ResponsiveContainer></article></section>
    <article className="panel methodology"><h2>Evaluation contract</h2><p>The subtype labels are excluded because they directly encode the main failure target. Candidate algorithms are compared using stratified cross-validation on the training partition, sigmoid calibration is fitted on a separate validation partition, the maintenance threshold is selected there using F2 with a minimum precision constraint, and all displayed headline metrics come from the untouched 20% test set.</p><p>This synthetic dataset is useful for demonstrating engineering practice, but these results do not establish performance on real industrial equipment.</p></article>
  </div>;
}

