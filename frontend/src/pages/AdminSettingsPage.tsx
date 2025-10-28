// frontend/src/pages/AdminSettingsPage.tsx
import { useEffect, useState } from "react";
import { getGlobalThresholdsAdmin, setGlobalThresholdAdmin } from "../api/endpoints";
import type { ThresholdUpdateData } from "../api/endpoints";

// Define the shape of our form state
type ThresholdsState = {
  heart_rate: ThresholdUpdateData;
  temperature: ThresholdUpdateData;
  spo2: ThresholdUpdateData;
};

// Define metrics to ensure we render all forms
const METRICS: (keyof ThresholdsState)[] = ["heart_rate", "temperature", "spo2"];

export default function AdminSettingsPage() {
  // Form state
  const [thresholds, setThresholds] = useState<ThresholdsState>({
    heart_rate: { min_value: null, max_value: null },
    temperature: { min_value: null, max_value: null },
    spo2: { min_value: null, max_value: null },
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Separate saving state for each form
  const [saving, setSaving] = useState<Record<string, boolean>>({
    heart_rate: false,
    temperature: false,
    spo2: false,
  });

  // Load initial global thresholds
  useEffect(() => {
    const fetchThresholds = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getGlobalThresholdsAdmin();
        
        // Transform the array response into our state object
        const newThresholdsState = { ...thresholds };
        data.forEach(t => {
          if (t.metric in newThresholdsState) {
            newThresholdsState[t.metric as keyof ThresholdsState] = {
              min_value: t.min_value,
              max_value: t.max_value,
            };
          }
        });
        setThresholds(newThresholdsState);

      } catch (err: any) {
        console.error("Error fetching thresholds:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar los umbrales.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    fetchThresholds();
    // We only want to run this on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle changes to any input
  const handleChange = (metric: keyof ThresholdsState, field: 'min_value' | 'max_value', value: string) => {
    setThresholds(prev => ({
      ...prev,
      [metric]: {
        ...prev[metric],
        [field]: value === '' ? null : value // Convert empty string to null
      }
    }));
  };

  // Handle saving for a specific metric
  const handleSave = async (e: React.FormEvent<HTMLFormElement>, metric: keyof ThresholdsState) => {
    e.preventDefault();
    setSaving(prev => ({ ...prev, [metric]: true }));
    setError(null);
    
    try {
      const payload = thresholds[metric];
      await setGlobalThresholdAdmin(metric, payload);
      // Optional: show a success message
    } catch (err: any) {
      console.error(`Error saving ${metric}:`, err);
      const msg = err?.response?.data?.message || err?.message || `No se pudo guardar ${metric}.`;
      setError(msg);
    } finally {
      setSaving(prev => ({ ...prev, [metric]: false }));
    }
  };

  // Helper to format metric names
  const formatMetricName = (metric: string) => {
    switch (metric) {
      case 'heart_rate': return 'Ritmo Cardíaco (bpm)';
      case 'temperature': return 'Temperatura (°C)';
      case 'spo2': return 'Saturación de Oxígeno (SpO₂) (%)';
      default: return metric;
    }
  };

  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando configuración...</div>;
  }

  return (
    <main className="flex-1 p-6 space-y-6">
      <h1 className="text-3xl font-semibold text-ink">
        Configuración de Umbrales Globales
      </h1>
      <p className="text-muted max-w-2xl">
        Estos valores se aplicarán a todos los pacientes que no tengan umbrales personalizados.
        Dejar un campo en blanco (o en 0) lo desactiva.
      </p>

      {error && (
        <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
      )}

      {/* Forms container */}
      <div className="max-w-xl space-y-6">
        {METRICS.map(metric => (
          <form key={metric} onSubmit={(e) => handleSave(e, metric)} className="bg-white rounded-xl border shadow-sm p-6">
            <h2 className="text-xl font-semibold text-ink">
              {formatMetricName(metric)}
            </h2>
            
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Min Value Input */}
              <div>
                <label htmlFor={`${metric}_min`} className="block text-sm font-medium text-muted">Valor Mínimo</label>
                <input
                  type="number"
                  step="0.1"
                  id={`${metric}_min`}
                  name="min_value"
                  value={thresholds[metric]?.min_value || ''}
                  onChange={(e) => handleChange(metric, 'min_value', e.target.value)}
                  placeholder="Ej: 50"
                  className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm"
                />
              </div>
              {/* Max Value Input */}
              <div>
                <label htmlFor={`${metric}_max`} className="block text-sm font-medium text-muted">Valor Máximo</label>
                <input
                  type="number"
                  step="0.1"
                  id={`${metric}_max`}
                  name="max_value"
                  value={thresholds[metric]?.max_value || ''}
                  onChange={(e) => handleChange(metric, 'max_value', e.target.value)}
                  placeholder="Ej: 120"
                  className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm"
                />
              </div>
            </div>

            {/* Save Button */}
            <div className="mt-6 pt-4 border-t flex justify-end">
              <button
                type="submit"
                disabled={saving[metric]}
                className="px-5 py-2 bg-primary-600 text-white rounded-lg shadow-sm hover:bg-primary-700 disabled:bg-slate-400"
              >
                {saving[metric] ? "Guardando..." : "Guardar Cambios"}
              </button>
            </div>
          </form>
        ))}
      </div>
    </main>
  );
}
