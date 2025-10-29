// frontend/src/App.tsx
import { Routes, Route, Navigate } from "react-router-dom";

// Guards
import ProtectedRoute from "./routes/ProtectedRoute";
import RoleGuard from "./routes/RoleGuard";

// Layouts
import ClientLayout from "./components/layout/ClientLayout";
import AdminLayout from "./components/layout/AdminLayout";

// Páginas Públicas
import Login from "./pages/Login";
// --- 1. AÑADE LAS IMPORTACIONES DE LAS PÁGINAS PÚBLICAS ---
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";

// Páginas de Cliente
import Dashboard from "./pages/Dashboard";
import HistoryPage from "./pages/HistoryPage";
import AlertsPage from "./pages/AlertsPage";
import ProfilePage from "./pages/ProfilePage";

// --- PÁGINAS DE ADMIN (COMPLETAS) ---
import AdminPanel from "./pages/AdminPanel";
import AdminPatientsPage from "./pages/AdminPatientsPage";
import AdminPatientCreatePage from "./pages/AdminPatientCreatePage";
import AdminPatientDetailPage from "./pages/AdminPatientDetailPage";
import AdminDevicesPage from "./pages/AdminDevicesPage";
import AdminDeviceCreatePage from "./pages/AdminDeviceCreatePage";
import AdminSettingsPage from "./pages/AdminSettingsPage";

export default function App() {
  return (
    <Routes>
      {/* --- Rutas Públicas --- */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />

      {/* --- 2. REEMPLAZA LOS PLACEHOLDERS --- */}
      <Route path="/signup" element={<RegisterPage />} />
      <Route path="/forgot" element={<ForgotPasswordPage />} />
      {/* --- FIN MODIFICACIÓN --- */}


      {/* --- Rutas Protegidas (Requieren Login) --- */}
      <Route element={<ProtectedRoute />}>
        
        {/* 1. Portal del Cliente (con Layout) */}
        <Route element={<ClientLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        {/* 2. Portal de Admin (con Layout) */}
        <Route
          path="/admin"
          element={
            <RoleGuard allow={["admin"]}>
              <AdminLayout />
            </RoleGuard>
          }
        >
          {/* Rutas de Admin */}
          <Route index element={<AdminPanel />} />
          <Route path="patients" element={<AdminPatientsPage />} />
          <Route path="patients/new" element={<AdminPatientCreatePage />} />
          <Route path="patients/:id" element={<AdminPatientDetailPage />} />
          <Route path="devices" element={<AdminDevicesPage />} />
          <Route path="devices/new" element={<AdminDeviceCreatePage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
        </Route>

      </Route>

      {/* --- 404 --- */}
      {/* Mueve esta ruta al final para que capture todo lo demás */}
      <Route path="*" element={<div className="p-6">404 - No encontrado</div>} />
    </Routes>
  );
}
