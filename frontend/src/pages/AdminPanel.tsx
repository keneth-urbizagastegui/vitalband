// frontend/src/pages/AdminPanel.tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listPatientsAdmin, listDevicesAdmin } from "../api/endpoints";
// Opcional: Iconos para los botones
// import { LuPlusCircle } from "react-icons/lu";

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cargar las estadísticas (Total de pacientes y dispositivos)
  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const [patientsData, devicesData] = await Promise.all([
          listPatientsAdmin(),
          listDevicesAdmin(),
        ]);
        setStats({
          patientCount: patientsData.length,
          deviceCount: devicesData.length,
        });
      } catch (err: any) {
        console.error("Error fetching stats:", err);
        setError("No se pudieron cargar las estadísticas.");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
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
        {/* Puedes añadir más tarjetas si la API lo permite, ej: "Alertas Pendientes" */}
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
              {/* <LuPlusCircle className="h-5 w-5" /> */}
              <span className="font-medium">Registrar Nuevo Paciente</span>
            </Link>
            <Link
              to="/admin/devices/new"
              className="flex items-center gap-3 w-full px-4 py-3 bg-slate-700 text-white rounded-lg shadow-sm hover:bg-slate-800 transition-colors"
            >
              {/* <LuPlusCircle className="h-5 w-5" /> */}
              <span className="font-medium">Registrar Nuevo Dispositivo</span>
            </Link>
          </div>
        </div>

        {/* --- Columna 2: Alertas Pendientes (Placeholder) --- */}
        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold text-ink">Alertas Pendientes</h2>
          <div className="bg-white rounded-xl border shadow-sm p-4">
            <p className="text-sm text-muted italic p-4 text-center">
              (Próximamente: Lista de alertas pendientes)
            </p>
            {/* NOTA: Implementar esto requeriría una nueva API (ej. GET /admin/alerts/pending).
              Llamar a listAlertsForPatientAdmin(id) por cada paciente sería muy ineficiente.
              Por ahora, lo dejamos como placeholder.
            */}
          </div>
        </div>
      </div>
    </main>
  );
}