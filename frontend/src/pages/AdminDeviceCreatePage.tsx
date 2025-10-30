// frontend/src/pages/AdminDeviceCreatePage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDeviceAdmin } from "../api/endpoints";
import type { DeviceCreateData } from "../api/endpoints"; // Usamos el tipo de la API

// Estado inicial del formulario
const initialState: DeviceCreateData = {
  serial: "",
  model: "",
  status: "new", // Por defecto, un dispositivo se registra como "Nuevo"
  patient_id: null,
};

export default function AdminDeviceCreatePage() {
  const [formData, setFormData] = useState<DeviceCreateData>(initialState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // --- Validación simple ---
    if (!formData.serial || !formData.model) {
      setError("El Número de Serie y el Modelo son obligatorios.");
      setLoading(false);
      return;
    }

    try {
      // --- Llamar a la API ---
      // El 'status' y 'patient_id' (null) ya están en el estado
      await createDeviceAdmin(formData);

      // --- Éxito ---
      setLoading(false);
      // Redirige a la lista de dispositivos
      navigate("/admin/devices"); 

    } catch (err: any) {
      console.error("Error creating device:", err);
      const msg = err?.response?.data?.message || err?.message || "No se pudo crear el dispositivo.";
      setError(msg);
      setLoading(false);
    }
  };

  return (
    <main className="flex-1 p-6 space-y-6">
      {/* --- Cabecera con Título y Botón de Volver --- */}
      <div>
        <button onClick={() => navigate(-1)} className="text-sm text-primary-600 hover:underline">
          &larr; Volver a Dispositivos
        </button>
        <h1 className="text-3xl font-semibold text-ink mt-1">
          Registrar Nuevo Dispositivo
        </h1>
      </div>

      {/* --- Formulario --- */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border shadow-sm p-6 max-w-lg">
        
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
        )}

        <div className="space-y-4">
          <div>
            <label htmlFor="serial" className="block text-sm font-medium text-muted">Número de Serie <span className="text-red-500">*</span></label>
            {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
            <input
              type="text"
              name="serial"
              id="serial"
              value={formData.serial}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white"
              placeholder="Ej: ABC-12345678"
            />
          </div>
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-muted">Modelo <span className="text-red-500">*</span></label>
            {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
            <input
              type="text"
              name="model"
              id="model"
              value={formData.model}
              onChange={handleChange}
              required
              className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white"
              placeholder="Ej: HealthBand v3"
            />
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-muted">Estado Inicial</label>
            {/* MODIFICACIÓN: Añadido bg-white y cambiado border-slate-400 */}
            <select
              name="status"
              id="status"
              value={formData.status}
              onChange={handleChange}
              className="mt-1 block w-full rounded-md border-slate-400 shadow-sm sm:text-sm bg-white"
            >
              <option value="new">Nuevo</option>
              <option value="active">Activo</option>
              <option value="service">En Servicio</option>
              <option value="lost">Perdido</option>
              <option value="retired">Retirado</option>
            </select>
          </div>
        </div>

        {/* Botón de Envío */}
        <div className="mt-8 pt-6 border-t flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-primary-600 text-white rounded-lg shadow-md hover:bg-primary-700 disabled:bg-slate-400"
          >
            {loading ? "Registrando..." : "Registrar Dispositivo"}
          </button>
        </div>
      </form>
    </main>
  );
}