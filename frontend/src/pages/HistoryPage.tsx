// frontend/src/pages/HistoryPage.tsx
import { useEffect, useState, useCallback} from "react";
import { useAuth } from "../context/AuthContext";
import { getMyReadingsHistory } from "../api/endpoints";
import type { Reading } from "../api/endpoints";
import LineChartCard from "../components/LineChartCard"; // Asume que el componente está aquí

// --- Helpers de formato (puedes moverlos a un archivo utils.ts) ---

// Helper para formatear la hora (ej: "14:30") - (Reutilizado del Dashboard)
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
    return 'Invalid Date';
  }
};

// NUEVO: Helper para formatear una fecha a YYYY-MM-DD (para el input <input type="date">)
const formatDateForInput = (date: Date): string => {
  return date.toISOString().split('T')[0];
};

// --- Componente Principal de la Página ---

// Configura las fechas por defecto (ej: última semana)
const getInitialDateRange = () => {
  const to = new Date();
  const from = new Date();
  from.setDate(to.getDate() - 7); // 7 días atrás
  return {
    from: formatDateForInput(from), // YYYY-MM-DD
    to: formatDateForInput(to),     // YYYY-MM-DD
  };
};

export default function HistoryPage() {
  const { user } = useAuth();
  const [historyData, setHistoryData] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(true); // Carga al inicio
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState(getInitialDateRange());

  // Usamos useCallback para que la función fetchHistory no cambie en cada render
  // a menos que cambie el rango de fechas (lo cual no pasará por sí solo)
  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Importante: Convertir las fechas del input a formato ISO 8601
      // El input da "YYYY-MM-DD", lo cual se interpreta como medianoche (00:00) UTC.
      // Para asegurar que incluimos todo el día 'to', ajustamos la hora.
      
      const fromDate = new Date(dateRange.from);
      fromDate.setHours(0, 0, 0, 0); // Inicio del día 'from'
      
      const toDate = new Date(dateRange.to);
      toDate.setHours(23, 59, 59, 999); // Final del día 'to'

      const params = {
        from: fromDate.toISOString(),
        to: toDate.toISOString(),
        limit: 1000 // Aumentamos el límite para rangos de fecha largos
      };
      
      const data = await getMyReadingsHistory(params);
      // Ordena el historial para el gráfico (más antiguo primero)
      setHistoryData(data.sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()));

    } catch (err: any) {
      console.error("Error fetching history data:", err);
      const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar los datos históricos.";
      setError(msg);
      setHistoryData([]);
    } finally {
      setLoading(false);
    }
  }, [dateRange]); // Depende del rango de fechas

  // Carga inicial de datos (la última semana) cuando el usuario entra
  useEffect(() => {
    if (user) {
      fetchHistory();
    }
  }, [user, fetchHistory]); // Ejecuta cuando el usuario cambia o la función fetch se actualiza

  // Handler para el formulario
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Evita que la página se recargue
    fetchHistory(); // Llama a la API con las fechas del estado
  };

  // Handler para cambiar las fechas
  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDateRange(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  // Prepara datos para los gráficos
  const chartData = historyData.map(r => ({
    time: formatTime(r.ts), // Formatea la hora para el eje X
    hr: r.heart_rate_bpm,
    temp: r.temp_c ? parseFloat(r.temp_c) : null,
    spo2: r.spo2_pct,
  }));

  return (
    <main className="flex-1 p-6 space-y-6 bg-slate-50">
      <h1 className="text-3xl font-semibold text-primary-700">
        Historial de Métricas
      </h1>
      <p className="text-muted">
        Selecciona un rango de fechas para explorar tus lecturas pasadas.
      </p>

      {/* Formulario de Filtro de Fechas */}
      <form onSubmit={handleSubmit} className="p-4 bg-white rounded-xl border shadow-sm flex items-center gap-4">
        <div className="flex-1">
          <label htmlFor="from" className="block text-sm font-medium text-muted">Desde</label>
          <input
            type="date"
            id="from"
            name="from"
            value={dateRange.from}
            onChange={handleDateChange}
            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
        <div className="flex-1">
          <label htmlFor="to" className="block text-sm font-medium text-muted">Hasta</label>
          <input
            type="date"
            id="to"
            name="to"
            value={dateRange.to}
            onChange={handleDateChange}
            className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 mt-6 bg-primary-600 text-white rounded-md shadow-sm hover:bg-primary-700 disabled:bg-slate-400"
        >
          {loading ? "Cargando..." : "Filtrar"}
        </button>
      </form>

      {/* Sección de Gráficos */}
      {loading && (
        <div className="p-6 text-center text-muted">Cargando gráficos...</div>
      )}

      {error && (
        <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
          Error: {error}
        </div>
      )}

      {!loading && !error && historyData.length === 0 && (
         <div className="text-center text-muted py-10 bg-white rounded-xl border p-4">
            No se encontraron datos para el rango de fechas seleccionado.
         </div>
      )}

      {!loading && !error && historyData.length > 0 && (
        <div className="space-y-6">
          <LineChartCard
            title="Ritmo Cardíaco"
            data={chartData}
            xKey="time"
            yKey="hr"
            height={300}
          />
          <LineChartCard
            title="Saturación de Oxígeno (SpO₂)"
            data={chartData}
            xKey="time"
            yKey="spo2"
            height={300}
          />
          <LineChartCard
            title="Temperatura Corporal"
            data={chartData}
            xKey="time"
            yKey="temp"
            height={300}
          />
        </div>
      )}
    </main>
  );
}