// frontend/src/pages/AdminPanel.tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
// Importamos las APIs necesarias
import {
  listPatientsAdmin,
  listDevicesAdmin,
  listPendingAlertsAdmin
} from "../api/endpoints";
import type { Alert } from "../api/endpoints"; // Importamos el tipo Alert

// --- Sub-componente: Tarjeta de Estadística ---
type StatCardProps = {
  title: string;
  value: number | string;
  loading: boolean;
};

function StatCard({ title, value, loading }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl border border-primary-500/20 shadow-sm p-5">
      <div className="text-sm font-medium text-muted">{title}</div>
      <div className="mt-2 text-3xl font-semibold tracking-tight text-ink">
        {loading ? "..." : value}
      </div>
    </div>
  );
}

// --- Componente Principal ---
export default function AdminPanel() {
  const [stats, setStats] = useState({ patientCount: 0, deviceCount: 0 });
  const [pendingAlerts, setPendingAlerts] = useState<Alert[]>([]); // Estado para alertas
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar las estadísticas Y las alertas pendientes
  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Pedimos todo en paralelo
        const [patientsData, devicesData, alertsData] = await Promise.all([
          listPatientsAdmin(),
          listDevicesAdmin(),
          listPendingAlertsAdmin({ limit: 10 }) // Pedimos las 10 más nuevas
        ]);
        
        setStats({
          patientCount: patientsData.length,
          deviceCount: devicesData.length,
        });
        setPendingAlerts(alertsData); // Guardamos las alertas

      } catch (err: any) {
        console.error("Error fetching dashboard data:", err);
        setError("No se pudieron cargar los datos del dashboard.");
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm m-6">
        Error al cargar el dashboard: {error}
      </div>
    );
  }

  return (
    <main className="flex-1 p-6 space-y-6">
      <h1 className="text-3xl font-semibold text-ink">
        Dashboard de Administración
      </h1>

      {/* --- Tarjetas de Estadísticas --- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <StatCard
          title="Total de Pacientes"
          value={stats.patientCount}
          loading={loading}
        />
        <StatCard
          title="Total de Dispositivos"
          value={stats.deviceCount}
          loading={loading}
        />
        {/* Tarjeta de Alertas Pendientes */}
        <StatCard
          title="Alertas Pendientes"
          value={pendingAlerts.length} // Mostramos el conteo
          loading={loading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* --- Columna 1: Accesos Rápidos --- */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold text-ink">Accesos Rápidos</h2>
          <div className="bg-white rounded-xl border shadow-sm p-4 space-y-3">
            <Link
              to="/admin/patients/new"
              className="flex items-center gap-3 w-full px-4 py-3 bg-primary-600 text-white rounded-lg shadow-sm hover:bg-primary-700 transition-colors"
            >
              <span className="font-medium">Registrar Nuevo Paciente</span>
            </Link>
            <Link
              to="/admin/devices/new"
              className="flex items-center gap-3 w-full px-4 py-3 bg-slate-700 text-white rounded-lg shadow-sm hover:bg-slate-800 transition-colors"
            >
              <span className="font-medium">Registrar Nuevo Dispositivo</span>
            </Link>
          </div>
        </div>

        {/* --- Columna 2: Alertas Pendientes (Implementada) --- */}
        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold text-ink">Alertas Pendientes</h2>
          <div className="bg-white rounded-xl border shadow-sm p-4">
            {loading ? (
              <p className="text-sm text-muted p-4 text-center">Cargando alertas...</p>
            ) : pendingAlerts.length > 0 ? (
              <ul className="divide-y divide-slate-200">
                {/* Mostramos la lista de alertas */}
                {pendingAlerts.map(alert => (
                  <li key={alert.id} className="py-3 px-2 hover:bg-slate-50">
                    <div className="flex justify-between items-center">
                      <div className="font-medium text-ink">
                        {alert.type} 
                        <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${
                          alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                          alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>{alert.severity}</span>
                      </div>
                      <Link
                        to={`/admin/patients/${alert.patient_id}?tab=alerts`} // Link directo a la pestaña de alertas del paciente
                        className="text-sm font-medium text-primary-600 hover:text-primary-800"
                      >
                        Revisar
                      </Link>
                    </div>
                    <p className="text-sm text-muted mt-1">{alert.message || 'Sin mensaje.'}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted italic p-4 text-center">
                No hay alertas pendientes por revisar.
              </p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}