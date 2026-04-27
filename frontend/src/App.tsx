import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { PublicShell } from "./components/layout/PublicShell";
import About from "./pages/About";
import Companies from "./pages/Companies";
import CompanyDetail from "./pages/CompanyDetail";
import Copilot from "./pages/Copilot";
import Dashboard from "./pages/Dashboard";
import Home from "./pages/Home";
import Upload from "./pages/Upload";

export default function App() {
  return (
    <Routes>
      <Route element={<PublicShell />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
      </Route>
      <Route element={<AppShell />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="upload" element={<Upload />} />
        <Route path="companies" element={<Companies />} />
        <Route path="companies/:id" element={<CompanyDetail />} />
        <Route path="copilot" element={<Copilot />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
