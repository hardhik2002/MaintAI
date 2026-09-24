import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";

const Dashboard = lazy(() =>
  import("./pages/Dashboard").then((module) => ({ default: module.Dashboard })),
);
const MachineDetails = lazy(() =>
  import("./pages/MachineDetails").then((module) => ({ default: module.MachineDetails })),
);
const ModelInsights = lazy(() =>
  import("./pages/ModelInsights").then((module) => ({ default: module.ModelInsights })),
);

export default function App() {
  return (
    <Suspense fallback={<div className="page">Loading MaintAI…</div>}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/machines/:id" element={<MachineDetails />} />
          <Route path="/insights" element={<ModelInsights />} />
        </Route>
      </Routes>
    </Suspense>
  );
}

