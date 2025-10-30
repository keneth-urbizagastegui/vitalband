// frontend/src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
// Importa las nuevas funciones de API
import { getMyLatestReadings, getMyReadingsHistory } from "../api/endpoints";
// Mantén los tipos (asegúrate que estén actualizados en endpoints.ts)
import type { Reading, User } from "../api/endpoints";
// Importa componentes UI y de Layout
// Asumiendo que AppLayout ya incluye Sidebar y Topbar
// import AppLayout from "../components/layout/AppLayout";
import StatCard from "../components/ui/StatCard";
import LineChartCard from "../components/LineChartCard";

// Helper para formatear la hora (ej: "14:30") - Sin cambios
const formatTime = (isoString: string | null | undefined): string => {
  if (!isoString) return '--:--';
  try {
    const date = new Date(isoString);
    // Formato 24h
    return date.toLocaleTimeString(navigator.language, {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch (e) {
    console.error("Error formatting time:", e);
    return 'Invalid Date';
  }
};

// Helper para obtener fecha de hace 24h en ISO
const get24HoursAgoISO = (): string => {
  const date = new Date();
  date.setHours(date.getHours() - 24);
  return date.toISOString();
};

export default function Dashboard() {
  const { user } = useAuth();
  // Estado simplificado
  const [latestData, setLatestData] = useState<{ reading: Reading | null; deviceStatus: string | null }>({ reading: null, deviceStatus: null });
  const [historyData, setHistoryData] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Obtener nombre (más robusto)
  const userName = user?.name || user?.email?.split("@")[0] || "Usuario";

  // Cargar datos (última lectura e historial 24h)
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Llama a ambas APIs en paralelo para eficiencia
        const [latest, history] = await Promise.all([
          getMyLatestReadings(),
          getMyReadingsHistory({ from: get24HoursAgoISO() }) // Pide historial de 24h
        ]);

        setLatestData({ reading: latest.latest_reading, deviceStatus: latest.device_status });
        // Ordena el historial para el gráfico (más antiguo primero)
        setHistoryData(history.sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()));

      } catch (err: any) {
        console.error("Error fetching dashboard data:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar los datos del panel.";
        setError(msg);
        setLatestData({ reading: null, deviceStatus: null });
        setHistoryData([]);
      } finally {
        setLoading(false);
      }
    };

    // Solo carga datos si el usuario está definido (evita llamadas innecesarias)
    if (user) {
       fetchData();
    } else {
       // Si no hay usuario (raro si está protegido, pero por si acaso)
       setLoading(false);
    }
  }, [user]); // Recarga si el usuario cambia

  // Prepara datos para el gráfico (HR vs Tiempo)
  const chartData = historyData.map(r => ({
    time: formatTime(r.ts), // Formatea la hora para el eje X
    hr: r.heart_rate_bpm,
    // puedes añadir spo2, temp si quieres mostrarlos en el tooltip
    temp: r.temp_c ? parseFloat(r.temp_c) : null,
    spo2: r.spo2_pct,
  }));

  // Renderizado condicional mientras carga o si hay error
  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando panel...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error al cargar el panel: {error}
      </div>
    );
  }

  // --- Estructura Principal del Dashboard ---
  // Nota: Asume que AppLayout ya provee Sidebar y Topbar
  return (
      <main className="flex-1 p-6 space-y-6 bg-slate-50"> {/* Fondo gris claro como base */}
        <h1 className="text-3xl font-semibold text-primary-700"> {/* Título más grande, color primario */}
          ¡Hola, {userName}!
        </h1>
        <p className="text-muted"> {/* Usa color muted */}
           Aquí tienes un resumen de tus métricas recientes.
           <span className="ml-2 text-xs">Última actualización: {formatTime(latestData.reading?.ts)}</span>
        </p>

        {/* Grid para las tarjetas de estadísticas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {/* Tarjetas de Métricas Recientes */}
          <StatCard
            label="Ritmo Cardíaco"
            value={latestData.reading?.heart_rate_bpm ?? '--'}
            unit="bpm"
            // Puedes añadir iconos aquí si creas un componente StatCard más avanzado
          />
          <StatCard
            label="SpO₂"
            value={latestData.reading?.spo2_pct ?? '--'}
            unit="%"
          />
          <StatCard
            label="Temperatura"
            value={latestData.reading?.temp_c ? parseFloat(latestData.reading.temp_c) : '--'}
            unit={latestData.reading?.temp_c ? "°C" : undefined}
          />
          {/* Tarjeta de Estado del Dispositivo */}
          <StatCard
             label="Estado Pulsera"
             value={latestData.deviceStatus ? latestData.deviceStatus.charAt(0).toUpperCase() + latestData.deviceStatus.slice(1) : 'Desconocido'} // Capitaliza 'active' -> 'Active'
             // Podrías cambiar el color de fondo o icono según el estado
          />
        </div>

        {/* Gráfico (usando el componente LineChartCard actualizado) */}
        {historyData.length > 0 ? (
          <LineChartCard // Asegúrate que LineChartCard use estilos consistentes (bordes, sombra)
            title="Ritmo Cardíaco (Últimas 24h)"
            data={chartData}
            xKey="time"
            yKey="hr"
            height={300}
          />
        ) : (
          <div className="text-center text-muted py-10 bg-white rounded-xl border p-4"> {/* Mensaje dentro de una tarjeta */}
            No hay datos históricos disponibles para mostrar en el gráfico.
          </div>
        )}

        {/* Puedes añadir más gráficos aquí para SpO2 y Temperatura si lo deseas */}
        {historyData.length > 0 && (
          <LineChartCard
            title="Saturación de Oxígeno (Últimas 24h)"
            data={chartData}
            xKey="time"
            yKey="spo2"
            height={250} // Un poco más bajo quizás
          />
        )}

        {historyData.length > 0 && (
          <LineChartCard
            title="Temperatura Corporal (Últimas 24h)"
            data={chartData}
            xKey="time"
            yKey="temp"
            height={250} 
          />
        )}
      </main>
  );
}

// --- Actualizaciones Sugeridas para StatCard y LineChartCard ---

// En StatCard.tsx: aplica clases de Tailwind para consistencia
/*
export default function StatCard({ label, value, unit }: ...) {
  return (
    <div className="bg-white rounded-xl border border-primary-500/20 shadow-sm p-4 hover:shadow-md transition-shadow"> // Estilo similar a Login card
      <div className="text-sm font-medium text-muted">{label}</div> // Color muted
      <div className="mt-1 text-3xl font-semibold tracking-tight text-ink"> // Color ink, más grande
        {value}
        {unit && <span className="text-slate-400 text-lg ml-1 font-normal">{unit}</span>} // Unidad más pequeña/ligera
      </div>
    </div>
  );
}
*/

// En LineChartCard.tsx: aplica clases de Tailwind
/*
export default function LineChartCard({ title, data, xKey, yKey, height = 260 }: Props) {
  return (
    // Usa clases de Tailwind en lugar de style
    <div className="bg-white border border-primary-500/20 rounded-xl shadow-sm p-4 mt-4 hover:shadow-md transition-shadow">
      <h3 className="m-0 mb-3 text-lg font-semibold text-primary-700">{title}</h3> // Título con color primario
      <div style={{ width: "100%", height }}> // Mantiene style para tamaño dinámico
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}> // Ajusta márgenes
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" /> // Color grid más suave
            <XAxis dataKey={xKey} tick={{ fontSize: 12, fill: '#6b7280' }} /> // Eje X color muted
            <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} /> // Eje Y color muted
            <Tooltip wrapperClassName="!text-sm !border-slate-300 !shadow-lg !rounded-md" /> // Estilo Tooltip
            <Line type="monotone" dataKey={yKey} stroke="#007D85" strokeWidth={2} dot={false} activeDot={{ r: 6 }} /> // Color línea (primary-600), grosor
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
*/