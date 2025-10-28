// frontend/src/pages/AdminPatientsPage.tsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listPatientsAdmin, deletePatientAdmin } from "../api/endpoints";
import type { PatientDetail } from "../api/endpoints";

// --- Helper de formato (Idealmente, mover a utils.ts) ---
const formatSimpleDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(`${dateString}T00:00:00`);
    return date.toLocaleDateString(navigator.language, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch (e) {
    return 'Fecha inválida';
  }
};

export default function AdminPatientsPage() {
  const [patients, setPatients] = useState<PatientDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Función para cargar los pacientes
  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listPatientsAdmin();
      setPatients(data);
    } catch (err: any) {
      console.error("Error fetching patients:", err);
      const msg = err?.response?.data?.message || err?.message || "No se pudieron cargar los pacientes.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Carga inicial
  useEffect(() => {
    fetchPatients();
  }, []);

  // Handler para el botón de borrar
  const handleDelete = async (patientId: number, patientName: string) => {
    // Pedir confirmación
    if (!window.confirm(`¿Estás seguro de que quieres borrar a ${patientName}? Esta acción no se puede deshacer.`)) {
      return;
    }
    
    try {
      await deletePatientAdmin(patientId);
      // Si tiene éxito, actualiza la lista en el estado (sin recargar)
      setPatients(prevPatients => prevPatients.filter(p => p.id !== patientId));
    } catch (err: any) {
      console.error("Error deleting patient:", err);
      const msg = err?.response?.data?.message || err?.message || "No se pudo borrar el paciente.";
      // Muestra el error, pero no detengas la UI
      alert(`Error: ${msg}`);
    }
  };

  // Handler para el botón de crear
  const handleCreate = () => {
    navigate("/admin/patients/new"); // Navega a la futura página de formulario
  };

  // --- Renderizado ---

  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando pacientes...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error al cargar pacientes: {error}
      </div>
    );
  }

  return (
    <main className="flex-1 p-6 space-y-6">
      {/* --- Cabecera con Título y Botón --- */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-semibold text-ink">
          Gestión de Pacientes
        </h1>
        <button
          onClick={handleCreate}
          className="px-5 py-2 bg-primary-600 text-white rounded-lg shadow-md hover:bg-primary-700 transition-colors"
        >
          + Registrar Paciente
        </button>
      </div>

      {/* --- Tabla de Pacientes --- */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        {patients.length > 0 ? (
          <table className="w-full text-left">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Nombre Completo</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Email</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Teléfono</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Nacimiento</th>
                <th className="px-4 py-3 text-sm font-semibold text-muted">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {patients.map(patient => (
                <tr key={patient.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm font-medium text-ink">{patient.full_name}</td>
                  <td className="px-4 py-3 text-sm text-muted">{patient.email || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-muted">{patient.phone || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-muted">{formatSimpleDate(patient.birthdate)}</td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex gap-2">
                      {/* Link para ver el detalle */}
                      <Link
                        to={`/admin/patients/${patient.id}`}
                        className="font-medium text-primary-600 hover:text-primary-800"
                      >
                        Ver Detalles
                      </Link>
                      <span className="text-slate-300">|</span>
                      {/* Botón para borrar */}
                      <button
                        onClick={() => handleDelete(patient.id, patient.full_name)}
                        className="font-medium text-red-600 hover:text-red-800"
                      >
                        Borrar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center text-muted py-10">
            No hay pacientes registrados.
          </div>
        )}
      </div>
    </main>
  );
}