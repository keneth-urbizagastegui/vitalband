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

// Páginas de Cliente
import Dashboard from "./pages/Dashboard";
import HistoryPage from "./pages/HistoryPage";
import AlertsPage from "./pages/AlertsPage";
import ProfilePage from "./pages/ProfilePage";

// --- PÁGINAS DE ADMIN (ACTUALIZADO) ---
import AdminPanel from "./pages/AdminPanel"; // El Dashboard de Admin
import AdminPatientsPage from "./pages/AdminPatientsPage"; // La tabla de pacientes
import AdminPatientCreatePage from "./pages/AdminPatientCreatePage"; // Formulario para crear paciente
import AdminPatientDetailPage from "./pages/AdminPatientDetailPage"; // El detalle de un paciente
import AdminDevicesPage from "./pages/AdminDevicesPage"; // La tabla de dispositivos
import AdminDeviceCreatePage from "./pages/AdminDeviceCreatePage"; // Formulario para crear dispositivo
import AdminSettingsPage from "./pages/AdminSettingsPage"; // La página de Umbrales Globales

export default function App() {
  return (
    <Routes>
      {/* --- Rutas Públicas --- */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />

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
          {/* --- RUTAS DE ADMIN (ACTUALIZADO) --- */}
          
          {/* /admin */}
          <Route index element={<AdminPanel />} />
          
          {/* /admin/patients */}
          <Route path="patients" element={<AdminPatientsPage />} />
          {/* /admin/patients/new */}
          <Route path="patients/new" element={<AdminPatientCreatePage />} />
          {/* /admin/patients/123 */}
          <Route path="patients/:id" element={<AdminPatientDetailPage />} />

          {/* /admin/devices */}
          <Route path="devices" element={<AdminDevicesPage />} />
          {/* /admin/devices/new */}
          <Route path="devices/new" element={<AdminDeviceCreatePage />} />
          
          {/* /admin/settings */}
          <Route path="settings" element={<AdminSettingsPage />} />
          
        </Route> {/* <-- Se cierra la ruta padre de /admin */}

      </Route>

      {/* --- Placeholders y 404 --- */}
      <Route path="/forgot" element={<div className="p-6">Página para Recuperar Contraseña (Pendiente)</div>} />
      <Route path="/signup" element={<div className="p-6">Página de Registro (Pendiente)</div>} />
      <Route path="*" element={<div className="p-6">404 - No encontrado</div>} />
    </Routes>
  );
}
