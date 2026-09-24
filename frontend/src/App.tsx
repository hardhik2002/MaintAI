import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { MachineDetails } from "./pages/MachineDetails";
import { ModelInsights } from "./pages/ModelInsights";

export default function App() { return <Routes><Route element={<Layout />}><Route path="/" element={<Dashboard />} /><Route path="/machines/:id" element={<MachineDetails />} /><Route path="/insights" element={<ModelInsights />} /></Route></Routes>; }

