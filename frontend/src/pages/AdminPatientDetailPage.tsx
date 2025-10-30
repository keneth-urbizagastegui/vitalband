// frontend/src/pages/AdminPatientDetailPage.tsx
import { useEffect, useState} from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  getPatientDetailAdmin,
  updatePatientAdmin,
  listAlertsForPatientAdmin,
  acknowledgeAlertAdmin,
  getPatientThresholdsAdmin,
  setPatientThresholdAdmin // <-- Importamos esta
} from "../api/endpoints";
import type { PatientDetail, Alert, Threshold, PatientUpdateData, ThresholdUpdateData } from "../api/endpoints";

// --- Helpers de Formato (puedes moverlos a utils.ts) ---

const formatSimpleDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  const date = new Date(`${dateString}T00:00:00`);
  return date.toLocaleDateString(navigator.language, { day: '2-digit', month: '2-digit', year: 'numeric' });
};

const formatDateTime = (isoString: string | null | undefined): string => {
  if (!isoString) return '--:--';
  const date = new Date(isoString);
  return date.toLocaleString(navigator.language, { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const formatSex = (sex: PatientDetail['sex']): string => {
  const translations: Record<PatientDetail['sex'], string> = { male: "Masculino", female: "Femenino", other: "Otro", unknown: "No especificado" };
  return translations[sex] || 'N/A';
};

// --- Componente de Item de Detalle (reutilizable) ---
type DetailItemProps = { label: string; value: string | number | null | undefined };
function DetailItem({ label, value }: DetailItemProps) {
  return (
    <div>
      <dt className="text-sm font-medium text-muted">{label}</dt>
      <dd className="mt-1 text-base text-ink">{value ?? 'N/A'}</dd>
    </div>
  );
}

// ===================================================================
// --- PESTAÑA 1: PERFIL DEL PACIENTE (CON EDICIÓN) ---
// (REEMPLAZA ESTE COMPONENTE COMPLETO)
// ===================================================================
type ProfileTabProps = {
  patient: PatientDetail;
  onUpdate: (updatedPatient: PatientDetail) => void; // Función para actualizar el estado en el padre
};

function PatientProfileTab({ patient, onUpdate }: ProfileTabProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Estado del formulario
  const [formData, setFormData] = useState<PatientUpdateData>({
    first_name: patient.first_name,
    last_name: patient.last_name,
    email: patient.email,
    phone: patient.phone,
    birthdate: patient.birthdate,
    sex: patient.sex,
    height_cm: patient.height_cm,
    weight_kg: patient.weight_kg,
  });

  // Actualiza el formulario si el 'patient' prop cambia (ej. al guardar)
  useEffect(() => {
    setFormData({
      first_name: patient.first_name,
      last_name: patient.last_name,
      email: patient.email,
      phone: patient.phone,
      birthdate: patient.birthdate,
      sex: patient.sex,
      height_cm: patient.height_cm,
      weight_kg: patient.weight_kg,
    });
  }, [patient]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value === '' ? null : value }));
  };

  const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const updatedPatient = await updatePatientAdmin(patient.id, formData);
      onUpdate(updatedPatient); // Actualiza el estado del padre
      setIsEditing(false);
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "Error al guardar.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="bg-white rounded-xl border shadow-sm p-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-ink">Información Personal</h2>
        {!isEditing && (
          <button type="button" onClick={() => setIsEditing(true)} className="px-4 py-1.5 text-sm font-medium bg-slate-100 text-slate-700 rounded-md hover:bg-slate-200">Editar</button>
        )}
      </div>

      {error && <div className="my-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>}
      
      <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Mostramos inputs o texto plano dependiendo de 'isEditing' */}
        {isEditing ? (
          <>
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-muted">Nombre</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="text" name="first_name" id="first_name" value={formData.first_name || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-muted">Apellido</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="text" name="last_name" id="last_name" value={formData.last_name || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-muted">Email</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="email" name="email" id="email" value={formData.email || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-muted">Teléfono</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="tel" name="phone" id="phone" value={formData.phone || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="birthdate" className="block text-sm font-medium text-muted">Fecha de Nacimiento</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="date" name="birthdate" id="birthdate" value={formData.birthdate || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="sex" className="block text-sm font-medium text-muted">Sexo</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <select name="sex" id="sex" value={formData.sex || 'unknown'} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white">
                <option value="unknown">No especificado</option>
                <option value="male">Masculino</option>
                <option value="female">Femenino</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div>
              <label htmlFor="height_cm" className="block text-sm font-medium text-muted">Altura (cm)</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="number" name="height_cm" id="height_cm" value={formData.height_cm || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
            <div>
              <label htmlFor="weight_kg" className="block text-sm font-medium text-muted">Peso (kg)</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input type="number" name="weight_kg" id="weight_kg" value={formData.weight_kg || ''} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white" />
            </div>
          </>
        ) : (
          <>
            <DetailItem label="Nombre Completo" value={patient.full_name} />
            <DetailItem label="Email" value={patient.email} />
            <DetailItem label="Teléfono" value={patient.phone} />
            <DetailItem label="Fecha de Nacimiento" value={formatSimpleDate(patient.birthdate)} />
            <DetailItem label="Sexo" value={formatSex(patient.sex)} />
            <DetailItem label="Altura" value={`${patient.height_cm || 'N/A'} cm`} />
            <DetailItem label="Peso" value={`${patient.weight_kg || 'N/A'} kg`} />
          </>
        )}
      </dl>

      {isEditing && (
        <div className="mt-6 flex gap-4">
          <button type="submit" disabled={loading} className="px-5 py-2 bg-primary-600 text-white rounded-lg shadow-sm hover:bg-primary-700 disabled:bg-slate-400">
            {loading ? "Guardando..." : "Guardar Cambios"}
          </button>
          <button type="button" onClick={() => setIsEditing(false)} className="px-4 py-1.5 text-sm font-medium bg-slate-100 text-slate-700 rounded-md hover:bg-slate-200">
            Cancelar
          </button>
        </div>
      )}
    </form>
  );
}

// ===================================================================
// --- PESTAÑA 2: ALERTAS DEL PACIENTE ---
// ===================================================================
type AlertsTabProps = { patientId: number };

function PatientAlertsTab({ patientId }: AlertsTabProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Carga inicial de alertas
  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await listAlertsForPatientAdmin(patientId, { limit: 50 });
        setAlerts(data.sort((a, b) => new Date(b.ts).getTime() - new Date(a.ts).getTime()));
      } catch (err: any) {
        setError("No se pudieron cargar las alertas.");
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [patientId]);

  // Handler para "Reconocer" (Acknowledge) una alerta
  const handleAcknowledge = async (alertId: number) => {
    try {
      const updatedAlert = await acknowledgeAlertAdmin(alertId);
      // Actualiza la lista localmente
      setAlerts(prev => prev.map(a => (a.id === alertId ? updatedAlert : a)));
    } catch (err) {
      alert("Error al reconocer la alerta.");
    }
  };
  
  if (loading) return <div className="p-6 text-center text-muted">Cargando alertas...</div>;
  if (error) return <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>;

  return (
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
      {alerts.length > 0 ? (
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 text-sm font-semibold text-muted">Fecha y Hora</th>
              <th className="px-4 py-3 text-sm font-semibold text-muted">Tipo</th>
              <th className="px-4 py-3 text-sm font-semibold text-muted">Severidad</th>
              <th className="px-4 py-3 text-sm font-semibold text-muted">Mensaje</th>
              <th className="px-4 py-3 text-sm font-semibold text-muted">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {alerts.map(alert => (
              <tr key={alert.id} className={!alert.acknowledged_at ? "bg-yellow-50" : "hover:bg-slate-50"}>
                <td className="px-4 py-3 text-sm text-ink">{formatDateTime(alert.ts)}</td>
                <td className="px-4 py-3 text-sm text-ink">{alert.type}</td>
                <td className="px-4 py-3 text-sm text-ink">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>{alert.severity}</span>
                </td>
                <td className="px-4 py-3 text-sm text-muted">{alert.message || 'N/A'}</td>
                <td className="px-4 py-3 text-sm">
                  {alert.acknowledged_at ? (
                    <span className="text-green-600 font-medium">Revisado</span>
                  ) : (
                    <button 
                      onClick={() => handleAcknowledge(alert.id)}
                      className="font-medium text-primary-600 hover:text-primary-800"
                    >
                      Reconocer
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="text-center text-muted py-10">No hay alertas para este paciente.</div>
      )}
    </div>
  );
}

// ===================================================================
// --- PESTAÑA 3: UMBRALES (EDITABLE) ---
// (REEMPLAZA ESTE COMPONENTE COMPLETO)
// ===================================================================
type ThresholdsTabProps = { patientId: number };

function PatientThresholdsTab({ patientId }: ThresholdsTabProps) {
  const [thresholds, setThresholds] = useState<Record<string, ThresholdUpdateData>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carga inicial de umbrales
  useEffect(() => {
    const fetchThresholds = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPatientThresholdsAdmin(patientId);
        // Transforma el array en un objeto para el formulario
        const thresholdMap: Record<string, ThresholdUpdateData> = {
          heart_rate: {},
          temperature: {},
          spo2: {},
        };
        data.forEach(t => {
          thresholdMap[t.metric] = { min_value: t.min_value, max_value: t.max_value };
        });
        setThresholds(thresholdMap);
      } catch (err) {
        setError("No se pudieron cargar los umbrales.");
      } finally {
        setLoading(false);
      }
    };
    fetchThresholds();
  }, [patientId]);
  
  const handleChange = (metric: string, field: 'min_value' | 'max_value', value: string) => {
    setThresholds(prev => ({
      ...prev,
      [metric]: {
        ...prev[metric],
        [field]: value === '' ? null : value
      }
    }));
  };

  const handleSave = async (metric: string) => {
    setSaving(true);
    setError(null);
    try {
      const payload = thresholds[metric];
      await setPatientThresholdAdmin(patientId, metric, payload);
      // Opcional: mostrar un mensaje de "Guardado"
    } catch (err: any) {
      setError(`Error al guardar ${metric}: ${err?.response?.data?.message || err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6 text-center text-muted">Cargando umbrales...</div>;
  if (error) return <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>;

  return (
    <div className="bg-white rounded-xl border shadow-sm p-6 space-y-6">
      <h2 className="text-xl font-semibold text-ink">Umbrales Personalizados</h2>
      <p className="text-sm text-muted">
        Define umbrales específicos para este paciente. Si se dejan en blanco, se usarán los umbrales globales del sistema.
      </p>

      {/* Repetimos este bloque para cada métrica */}
      {Object.keys(thresholds).map(metric => (
        <form key={metric} onSubmit={(e) => { e.preventDefault(); handleSave(metric); }} className="p-4 border rounded-lg bg-slate-50">
          <h3 className="text-lg font-medium text-ink capitalize">{metric.replace('_', ' ')}</h3>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <label htmlFor={`${metric}_min`} className="block text-sm font-medium text-muted">Valor Mínimo</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input
                type="number"
                id={`${metric}_min`}
                value={thresholds[metric]?.min_value || ''}
                onChange={(e) => handleChange(metric, 'min_value', e.target.value)}
                placeholder="Global"
                className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white"
              />
            </div>
            <div>
              <label htmlFor={`${metric}_max`} className="block text-sm font-medium text-muted">Valor Máximo</label>
              {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
              <input
                type="number"
                id={`${metric}_max`}
                value={thresholds[metric]?.max_value || ''}
                onChange={(e) => handleChange(metric, 'max_value', e.target.value)}
                placeholder="Global"
                className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white"
              />
            </div>
          </div>
          <button type="submit" disabled={saving} className="mt-4 px-4 py-1.5 text-sm bg-primary-600 text-white rounded-md shadow-sm hover:bg-primary-700 disabled:bg-slate-400">
            {saving ? "Guardando..." : "Guardar Umbral"}
          </button>
        </form>
      ))}
    </div>
  );
}


// ===================================================================
// --- COMPONENTE PRINCIPAL DE LA PÁGINA ---
// ===================================================================
type TabKey = 'profile' | 'alerts' | 'thresholds';

export default function AdminPatientDetailPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('profile');
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const patientId = Number(id);

  // Carga inicial del detalle del paciente
  useEffect(() => {
    if (!patientId) {
      setError("ID de paciente inválido.");
      setLoading(false);
      return;
    }

    const fetchPatient = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getPatientDetailAdmin(patientId);
        setPatient(data);
      } catch (err: any) {
        const msg = err?.response?.data?.message || err?.message || "No se pudo cargar el paciente.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    
    fetchPatient();
  }, [patientId]);

  // Botón de Pestaña (Tab)
  const TabButton = ({ tabKey, label }: { tabKey: TabKey; label: string }) => (
    <button
      onClick={() => setActiveTab(tabKey)}
      className={`px-4 py-2 font-medium text-sm rounded-md ${
        activeTab === tabKey
          ? 'bg-primary-600 text-white'
          : 'text-muted hover:bg-slate-100'
      }`}
    >
      {label}
    </button>
  );
  
  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando paciente...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error: {error}
      </div>
    );
  }

  if (!patient) {
    return <div className="p-6 text-center text-muted">Paciente no encontrado.</div>;
  }

  return (
    <main className="flex-1 p-6 space-y-6">
      {/* --- Cabecera con Nombre y Botón de Volver --- */}
      <div className="flex justify-between items-center">
        <div>
          <button onClick={() => navigate(-1)} className="text-sm text-primary-600 hover:underline">
            &larr; Volver a Pacientes
          </button>
          <h1 className="text-3xl font-semibold text-ink mt-1">
            {patient.full_name}
          </h1>
        </div>
      </div>
      
      {/* --- Navegación de Pestañas (Tabs) --- */}
      <div className="flex gap-2 p-2 bg-white rounded-lg border shadow-sm w-fit">
        <TabButton tabKey="profile" label="Perfil" />
        <TabButton tabKey="alerts" label="Alertas" />
        <TabButton tabKey="thresholds" label="Umbrales" />
      </div>

      {/* --- Contenido de la Pestaña Activa --- */}
      <div className="mt-6">
        {activeTab === 'profile' && (
          <PatientProfileTab patient={patient} onUpdate={setPatient} />
        )}
        {activeTab === 'alerts' && (
          <PatientAlertsTab patientId={patient.id} />
        )}
        {activeTab === 'thresholds' && (
          <PatientThresholdsTab patientId={patient.id} />
        )}
      </div>
    </main>
  );
}