import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Assistant from "./pages/Assistant";
import Dashboard from "./pages/Dashboard";
import Jobs from "./pages/Jobs";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Register from "./pages/Register";
import Resumes from "./pages/Resumes";
import Security from "./pages/Security";

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/resumes" element={<Resumes />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/security" element={<Security />} />
        </Route>
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}