import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AdminPanel from "./pages/AdminPanel"; 
import ProtectedRoute from "./routes/ProtectedRoute";
import RoleGuard from "./routes/RoleGuard";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />

      {/* Rutas protegidas */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/admin"
          element={
            <RoleGuard allow={["admin"]}>
              <AdminPanel />
            </RoleGuard>
          }
        />
      </Route>

      {/* placeholders opcionales */}
      <Route path="/forgot" element={<div className="p-6">Página para Recuperar Contraseña (Pendiente)</div>} />
      <Route path="/signup" element={<div className="p-6">Página de Registro (Pendiente)</div>} />
      <Route path="*" element={<div className="p-6">No encontrado</div>} />
    </Routes>
  );
}
