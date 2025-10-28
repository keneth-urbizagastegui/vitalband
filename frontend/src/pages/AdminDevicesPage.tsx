// frontend/src/pages/AdminDevicesPage.tsx
import { useEffect, useState, useMemo} from "react";
import { useNavigate } from "react-router-dom";
import {
  listDevicesAdmin,
  listPatientsAdmin,
  deleteDeviceAdmin,
  assignDeviceAdmin,
} from "../api/endpoints";
import type { Device, PatientDetail } from "../api/endpoints";

// --- Helper de formato (Idealmente, mover a utils.ts) ---
const formatDeviceStatus = (status: Device['status']): string => {
  const translations: Record<Device['status'], string> = {
    new: "Nuevo",
    active: "Activo",
    lost: "Perdido",
    retired: "Retirado",
    service: "En servicio",
  };
  return translations[status] || status;
};

// ===================================================================
// --- Componente del Modal de Asignación ---
// (Lo ponemos en el mismo archivo por simplicidad)
// ===================================================================
type AssignModalProps = {
  device: Device;
  patients: PatientDetail[];
  onClose: () => void;
  onSave: (deviceId: number, patientId: number | null) => Promise<void>;
};

function AssignDeviceModal({ device, patients, onClose, onSave }: AssignModalProps) {
  // El ID del paciente seleccionado. Puede ser string (del select) o null
  const [selectedPatientId, setSelectedPatientId] = useState<string>(
    device.patient_id?.toString() || ""
  );
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSaving(true);
    
    // Convierte el ID a número, o a null si está vacío ("")
    const newPatientId = selectedPatientId ? parseInt(selectedPatientId, 10) : null;

    try {
      await onSave(device.id, newPatientId);
    } catch (err) {
      // El error se maneja en el componente padre
    } finally {
      setIsSaving(false);
    }
  };

  return (
    // Fondo oscuro
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      {/* Panel del Modal */}
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        <form onSubmit={handleSubmit}>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-ink">Asignar Dispositivo</h2>
            <p className="mt-1 text-sm text-muted">
              Asignar dispositivo (Serial: {device.serial})
            </p>

            <div className="mt-4">
              <label htmlFor="patient" className="block text-sm font-medium text-muted">
                Seleccionar Paciente
              </label>
              <select
                id="patient"
                value={selectedPatientId}
                onChange={(e) => setSelectedPatientId(e.target.value)}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm"
              >
                {/* Opción para des-asignar */}
                <option value="">-- No Asignado --</option>
                
                {/* Lista de pacientes */}
                {patients.map(p => (
                  <option key={p.id} value={p.id.toString()}>
                    {p.full_name} (ID: {p.id})
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Footer con botones */}
          <div className="flex justify-end gap-3 bg-slate-50 p-4 rounded-b-xl">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:bg-slate-400"
            >
              {isSaving ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}


// ===================================================================
// --- Componente Principal de la Página ---
// ===================================================================

export default function AdminDevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [patients, setPatients] = useState<PatientDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Estado para el modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);

  const navigate = useNavigate();

  // Carga inicial de dispositivos Y pacientes
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [devicesData, patientsData] = await Promise.all([
          listDevicesAdmin(),
          listPatientsAdmin(),
        ]);
        setDevices(devicesData);
        setPatients(patientsData);
      } catch (err: any) {
        console.error("Error fetching data:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar los datos.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Creamos un "mapa" (diccionario) de Pacientes para buscar nombres por ID
  // useMemo evita que este mapa se recalcule en cada render, solo si 'patients' cambia
  const patientMap = useMemo(() => {
    const map = new Map<number, PatientDetail>();
    for (const patient of patients) {
      map.set(patient.id, patient);
    }
    return map;
  }, [patients]);

  // --- Handlers de Acciones ---

  const handleDelete = async (deviceId: number, deviceSerial: string) => {
    if (!window.confirm(`¿Estás seguro de que quieres borrar el dispositivo ${deviceSerial}?`)) {
      return;
    }
    try {
      await deleteDeviceAdmin(deviceId);
      setDevices(prev => prev.filter(d => d.id !== deviceId));
    } catch (err: any) {
      alert(`Error al borrar dispositivo: ${err?.response?.data?.message || err.message}`);
    }
  };

  const handleCreate = () => {
    navigate("/admin/devices/new"); // Navega al formulario de creación
  };

  // Abre el modal
  const handleOpenAssignModal = (device: Device) => {
    setSelectedDevice(device);
    setIsModalOpen(true);
  };

  // Cierra el modal
  const handleCloseModal = () => {
    setSelectedDevice(null);
    setIsModalOpen(false);
  };

  // Se ejecuta al guardar desde el modal
  const handleSaveAssignment = async (deviceId: number, patientId: number | null) => {
    try {
      const updatedDevice = await assignDeviceAdmin(deviceId, patientId);
      // Actualiza la lista de dispositivos localmente
      setDevices(prev => prev.map(d => (d.id === deviceId ? updatedDevice : d)));
      handleCloseModal(); // Cierra el modal si tiene éxito
    } catch (err: any) {
      alert(`Error al asignar: ${err?.response?.data?.message || err.message}`);
      // No cierra el modal si hay error
      throw err; // Propaga el error para que el modal sepa que no debe cerrarse
    }
  };

  // --- Renderizado ---

  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando dispositivos...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error al cargar: {error}
      </div>
    );
  }

  return (
    <main className="flex-1 p-6 space-y-6">
      {/* --- Cabecera con Título y Botón --- */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold text-ink">
          Gestión de Dispositivos
        </h1>
        <button
          onClick={handleCreate}
          className="px-5 py-2 bg-primary-600 text-white rounded-lg shadow-md hover:bg-primary-700 transition-colors"
        >
          + Registrar Dispositivo
        </button>
      </div>

      {/* --- Tabla de Dispositivos --- */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        {devices.length > 0 ? (
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Serial</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Modelo</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Estado</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Paciente Asignado</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {devices.map(device => {
                const assignedPatient = device.patient_id ? patientMap.get(device.patient_id) : null;
                return (
                  <tr key={device.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-mono text-ink">{device.serial}</td>
                    <td className="px-4 py-3 text-sm text-muted">{device.model}</td>
                    <td className="px-4 py-3 text-sm text-muted">{formatDeviceStatus(device.status)}</td>
                    <td className="px-4 py-3 text-sm font-medium text-ink">
                      {assignedPatient ? assignedPatient.full_name : <span className="text-slate-400">-- No Asignado --</span>}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleOpenAssignModal(device)}
                          className="font-medium text-primary-600 hover:text-primary-800"
                        >
                          Asignar
                        </button>
                        <span className="text-slate-300">|</span>
                        <button
                          onClick={() => handleDelete(device.id, device.serial)}
                          className="font-medium text-red-600 hover:text-red-800"
                        >
                          Borrar
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="text-center text-muted py-10">
            No hay dispositivos registrados.
          </div>
        )}
      </div>

      {/* --- Renderizado del Modal --- */}
      {isModalOpen && selectedDevice && (
        <AssignDeviceModal
          device={selectedDevice}
          patients={patients}
          onClose={handleCloseModal}
          onSave={handleSaveAssignment}
        />
      )}
    </main>
  );
}