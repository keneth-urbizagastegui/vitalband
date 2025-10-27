// frontend/src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getReadings24h } from "../api/endpoints";
import type { Reading } from "../api/endpoints"; // Asegúrate que Reading esté exportado o defínelo aquí
import Sidebar from "../components/layout/Sidebar"; // Asumiendo que moviste Sidebar/Topbar a /layout
import Topbar from "../components/layout/Topbar";
import StatCard from "../components/ui/StatCard";
import LineChartCard from "../components/LineChartCard"; // Asegúrate que la ruta sea correcta

// Si Reading no está exportado en endpoints.ts, defínelo aquí:
// type Reading = {
//   ts: string;
//   heart_rate_bpm: number | null;
//   spo2_pct: number | null;
//   temp_c: number | string | null; // Puede venir como string desde el DTO
//   motion_level?: number | null;
//   // Añade otros campos si los necesitas
// };

// Helper para formatear la hora (ej: "14:30")
const formatTime = (isoString: string): string => {
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString(navigator.language, { // Usa el idioma del navegador
      hour: '2-digit',
      minute: '2-digit',
      hour12: false // Formato 24h
    });
  } catch (e) {
    return 'Invalid Date';
  }
};

export default function Dashboard() {
  const { user } = useAuth();
  const [userName, setUserName] = useState("Usuario");
  const [readings, setReadings] = useState<Reading[]>([]);
  const [latestReading, setLatestReading] = useState<Reading | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Obtener nombre de usuario
  useEffect(() => {
    if (user?.email) {
      setUserName(user.email.split("@")[0] || "Usuario");
    }
    // Si tuvieras el nombre completo en el objeto user, sería mejor usar eso
    // setUserName(user?.name || user?.email?.split("@")[0] || "Usuario");
  }, [user]);

  // Cargar datos de lecturas
  useEffect(() => {
    const fetchReadings = async () => {
      setLoading(true);
      setError(null);
      try {
        // --- USAREMOS deviceId = 1 por ahora ---
        const deviceId = 1; // TODO: Obtener el deviceId real del usuario logueado
        // --- ---
        if (!deviceId) {
          throw new Error("No se pudo determinar el dispositivo del usuario.");
        }

        const data = await getReadings24h(deviceId);

        // Ordenar por fecha (más reciente primero) si no vienen ordenados
        const sortedData = [...data].sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime());

        setReadings(sortedData);
        setLatestReading(sortedData.length > 0 ? sortedData[0] : null);

      } catch (err: any) {
        console.error("Error fetching readings:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar las métricas.";
        setError(msg);
        setReadings([]);
        setLatestReading(null);
      } finally {
        setLoading(false);
      }
    };

    fetchReadings();
  }, []); // Se ejecuta solo una vez al montar

  // Prepara datos para el gráfico (HR vs Tiempo)
  // Recharts necesita los datos ordenados del más antiguo al más reciente
  const chartData = readings
    .map(r => ({
      time: formatTime(r.ts), // Formatea la hora para el eje X
      hr: r.heart_rate_bpm,
      // puedes añadir spo2, temp si quieres mostrarlos en el tooltip del gráfico
    }))
    .reverse(); // Invierte para que el tiempo avance de izquierda a derecha

  return (
    <div className="min-h-screen flex bg-slate-50 text-ink">
      {/* Sidebar (Asegúrate que la ruta sea correcta) */}
      <Sidebar />

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col">
        {/* Topbar (Asegúrate que la ruta sea correcta) */}
        <Topbar /> {/* Quitamos userName si Topbar no lo necesita o lo obtiene de otro lado */}

        {/* Sección principal */}
        <main className="flex-1 p-6 md:p-8 space-y-6">
          <h1 className="text-2xl font-semibold text-primary-700">
            Panel de Métricas - ¡Hola, {userName}!
          </h1>

          {loading && <div className="text-muted">Cargando métricas...</div>}

          {error && (
            <div className="rounded-lg bg-red-50 text-red-700 px-4 py-3 text-sm">
              Error: {error}
            </div>
          )}

          {!loading && !error && (
            <>
              {/* Tarjetas con las últimas métricas */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                <StatCard
                  label="Ritmo Cardíaco (actual)"
                  value={latestReading?.heart_rate_bpm ?? '--'}
                  unit="bpm"
                />
                <StatCard
                  label="SpO₂ (actual)"
                  value={latestReading?.spo2_pct ?? '--'}
                  unit="%"
                />
                <StatCard
                  label="Temperatura (actual)"
                  // Asegúrate que temp_c sea numérico para mostrar °C, si no, solo el valor
                  value={latestReading?.temp_c ? parseFloat(String(latestReading.temp_c)) : '--'}
                  unit={latestReading?.temp_c ? "°C" : undefined}
                />
              </div>

              {/* Gráfico de Ritmo Cardíaco */}
              {readings.length > 0 ? (
                <LineChartCard
                  title="Ritmo Cardíaco (Últimas 24h)"
                  data={chartData}
                  xKey="time" // Usamos la hora formateada
                  yKey="hr" // La clave debe coincidir con la de chartData
                  height={300} // Ajusta la altura si es necesario
                />
              ) : (
                !loading && <div className="text-muted text-center py-10">No hay datos históricos disponibles para mostrar.</div>
              )}

              {/* Puedes añadir más gráficos aquí (SpO2, Temperatura) si lo deseas */}
              {/* Ejemplo:
                <LineChartCard
                  title="Saturación de Oxígeno (Últimas 24h)"
                  data={chartData.map(d => ({ time: d.time, spo2: readings.find(r => formatTime(r.ts) === d.time)?.spo2_pct }))}
                  xKey="time"
                  yKey="spo2"
                  height={300}
                />
                */}
            </>
          )}
        </main>
      </div>
    </div>
  );
}