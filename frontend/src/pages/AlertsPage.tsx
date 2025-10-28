// frontend/src/pages/AlertsPage.tsx
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getMyAlerts } from "../api/endpoints";
import type { Alert, Role } from "../api/endpoints"; // Importamos 'Alert'

// --- Helpers de formato (puedes moverlos a un archivo utils.ts) ---

// Helper para formatear la fecha y hora
const formatDateTime = (isoString: string | null | undefined): string => {
  if (!isoString) return '--:--';
  try {
    const date = new Date(isoString);
    return date.toLocaleString(navigator.language, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (e) {
    return 'Fecha inválida';
  }
};

// Helper para traducir el tipo de alerta
const getAlertTitle = (type: Alert['type']): string => {
  const titles: Record<Alert['type'], string> = {
    tachycardia: "Taquicardia (Ritmo Rápido)",
    bradycardia: "Bradicardia (Ritmo Lento)",
    fever: "Fiebre (Temperatura Alta)",
    hypoxia: "Hipoxia (Oxígeno Bajo)",
    custom: "Alerta Personalizada",
  };
  return titles[type] || "Alerta Desconocida";
};

// Helper para obtener el color de severidad (usando clases de Tailwind)
const getSeverityClass = (severity: Alert['severity']): string => {
  const classes: Record<Alert['severity'], string> = {
    low: "bg-yellow-100 text-yellow-800", // Baja
    moderate: "bg-orange-100 text-orange-800", // Moderada
    high: "bg-red-100 text-red-800", // Alta
    critical: "bg-red-200 text-red-900 font-bold", // Crítica
  };
  return classes[severity] || "bg-gray-100 text-gray-800";
};

// --- Componente Principal de la Página ---

export default function AlertsPage() {
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // NOTA: Podrías añadir un estado para los filtros, ej:
  // const [filter, setFilter] = useState<'all' | 'pending'>('all');

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      setError(null);
      
      // Prepara los parámetros para la API
      const params = {
        limit: 50, // Traer las últimas 50
        // Si tuvieras el filtro, lo aplicarías aquí:
        // acknowledged: filter === 'pending' ? false : undefined,
      };

      try {
        const data = await getMyAlerts(params);
        // Ordena las alertas, la más reciente primero
        setAlerts(data.sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime()));
      } catch (err: any) {
        console.error("Error fetching alerts:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar las alertas.";
        setError(msg);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchAlerts();
    } else {
      setLoading(false);
    }
  }, [user]); // Vuelve a cargar si el usuario cambia (o si el filtro cambiara)

  // --- Renderizado ---

  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando alertas...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error al cargar alertas: {error}
      </div>
    );
  }

  return (
    <main className="flex-1 p-6 space-y-6 bg-slate-50">
      <h1 className="text-3xl font-semibold text-primary-700">
        Mis Alertas
      </h1>
      <p className="text-muted">
        Aquí puedes ver un historial de todas las alertas de salud generadas por tu dispositivo.
      </p>

      {/* Aquí podrías poner los botones de filtro "Todas" | "Pendientes" */}

      {/* Lista de Alertas */}
      <div className="space-y-4">
        {alerts.length > 0 ? (
          alerts.map(alert => (
            <AlertItem key={alert.id} alert={alert} />
          ))
        ) : (
          <div className="text-center text-muted py-10 bg-white rounded-xl border p-4">
            No tienes ninguna alerta registrada.
          </div>
        )}
      </div>
    </main>
  );
}

// --- Componente de Item de Alerta (en el mismo archivo por simplicidad) ---

// Este componente solo recibe una alerta y la muestra
function AlertItem({ alert }: { alert: Alert }) {
  const title = getAlertTitle(alert.type);
  const severityClass = getSeverityClass(alert.severity);
  const isAcknowledged = !!alert.acknowledged_at; // Verifica si la alerta fue vista por un admin

  return (
    // Tarjeta de Alerta
    <div className={`flex items-start gap-4 p-4 rounded-xl border shadow-sm ${isAcknowledged ? 'bg-white' : 'bg-yellow-50 border-yellow-300'}`}>
      
      {/* Icono de severidad (simple) */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${severityClass}`}>
        <span className="text-xl font-bold">!</span>
      </div>

      {/* Contenido de la Alerta */}
      <div className="flex-1">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-ink">{title}</h3>
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${severityClass}`}>
            {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
          </span>
        </div>
        
        <p className="text-sm text-muted mt-1">
          {formatDateTime(alert.ts)}
        </p>
        
        {alert.message && (
          <p className="text-sm text-ink mt-2">
            {alert.message}
          </p>
        )}
      </div>

      {/* Estado: Visto (Acknowledged) o Pendiente */}
      <div className="text-right">
        {isAcknowledged ? (
          <span className="text-xs font-medium text-green-600">Visto por Admin</span>
        ) : (
          <span className="text-xs font-medium text-yellow-700">Pendiente</span>
        )}
      </div>
    </div>
  );
}