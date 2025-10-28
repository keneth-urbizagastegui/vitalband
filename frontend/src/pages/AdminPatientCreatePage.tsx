// frontend/src/pages/AdminPatientCreatePage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register, createPatientAdmin } from "../api/endpoints";
import type { PatientCreateData } from "../api/endpoints";

// Define un tipo para el estado del formulario (combinando user + patient)
type CreateFormState = {
  // Datos del Usuario
  email: string;
  password: string;
  // Datos del Paciente
  first_name: string;
  last_name: string;
  phone: string;
  birthdate: string;
  sex: "male" | "female" | "other" | "unknown";
  height_cm: string;
  weight_kg: string;
};

// Estado inicial del formulario
const initialState: CreateFormState = {
  email: "",
  password: "",
  first_name: "",
  last_name: "",
  phone: "",
  birthdate: "",
  sex: "unknown",
  height_cm: "",
  weight_kg: "",
};

export default function AdminPatientCreatePage() {
  const [formData, setFormData] = useState<CreateFormState>(initialState);
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
    if (!formData.email || !formData.password || !formData.first_name || !formData.last_name) {
      setError("Email, Contraseña, Nombre y Apellido son obligatorios.");
      setLoading(false);
      return;
    }

    try {
      // --- Paso 1: Registrar el Usuario ---
      // El 'name' para el registro puede ser el nombre completo
      const newUserData = {
        name: `${formData.first_name} ${formData.last_name}`,
        email: formData.email,
        password: formData.password
      };
      const registerResponse = await register(newUserData);
      
      if (!registerResponse.user || !registerResponse.user.id) {
        throw new Error("La respuesta del registro no devolvió un ID de usuario.");
      }
      
      const newUserId = registerResponse.user.id;

      // --- Paso 2: Crear el Perfil del Paciente ---
      // Prepara los datos del paciente, vinculando el newUserId
      const patientData: PatientCreateData = {
        user_id: newUserId,
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email, // El email de contacto puede ser el mismo
        phone: formData.phone || null,
        birthdate: formData.birthdate || null,
        sex: formData.sex,
        height_cm: formData.height_cm || null,
        weight_kg: formData.weight_kg || null,
      };
      
      await createPatientAdmin(patientData);

      // --- Éxito ---
      setLoading(false);
      // Redirige a la lista de pacientes
      navigate("/admin/patients"); 

    } catch (err: any) {
      console.error("Error creating patient:", err);
      // Deshace el usuario si el perfil del paciente falla؟ (Lógica avanzada)
      // Por ahora, solo muestra el error
      const msg = err?.response?.data?.message || err?.message || "No se pudo crear el paciente.";
      setError(msg);
      setLoading(false);
    }
  };

  return (
    <main className="flex-1 p-6 space-y-6">
      {/* --- Cabecera con Título y Botón de Volver --- */}
      <div>
        <button onClick={() => navigate(-1)} className="text-sm text-primary-600 hover:underline">
          &larr; Volver a Pacientes
        </button>
        <h1 className="text-3xl font-semibold text-ink mt-1">
          Registrar Nuevo Paciente
        </h1>
      </div>

      {/* --- Formulario --- */}
      <form onSubmit={handleSubmit} className="bg-white rounded-xl border shadow-sm p-6 max-w-3xl">
        
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
        )}

        {/* Sección de Cuenta de Usuario */}
        <div className="space-y-4 pb-6 border-b">
          <h2 className="text-lg font-semibold text-ink">Datos de Acceso (Usuario)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-muted">Email (Login) <span className="text-red-500">*</span></label>
              <input type="email" name="email" id="email" value={formData.email} onChange={handleChange} required className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-muted">Contraseña <span className="text-red-500">*</span></label>
              <input type="password" name="password" id="password" value={formData.password} onChange={handleChange} required className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
          </div>
        </div>

        {/* Sección de Perfil de Paciente */}
        <div className="space-y-4 pt-6">
          <h2 className="text-lg font-semibold text-ink">Datos Personales (Paciente)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="first_name" className="block text-sm font-medium text-muted">Nombre <span className="text-red-500">*</span></label>
              <input type="text" name="first_name" id="first_name" value={formData.first_name} onChange={handleChange} required className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="last_name" className="block text-sm font-medium text-muted">Apellido <span className="text-red-500">*</span></label>
              <input type="text" name="last_name" id="last_name" value={formData.last_name} onChange={handleChange} required className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-muted">Teléfono</label>
              <input type="tel" name="phone" id="phone" value={formData.phone} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="birthdate" className="block text-sm font-medium text-muted">Fecha de Nacimiento</label>
              <input type="date" name="birthdate" id="birthdate" value={formData.birthdate} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="sex" className="block text-sm font-medium text-muted">Sexo</label>
              <select name="sex" id="sex" value={formData.sex} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm">
                <option value="unknown">No especificado</option>
                <option value="male">Masculino</option>
                <option value="female">Femenino</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div>
              <label htmlFor="height_cm" className="block text-sm font-medium text-muted">Altura (cm)</label>
              <input type="number" name="height_cm" id="height_cm" value={formData.height_cm} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
            <div>
              <label htmlFor="weight_kg" className="block text-sm font-medium text-muted">Peso (kg)</label>
              <input type="number" name="weight_kg" id="weight_kg" value={formData.weight_kg} onChange={handleChange} className="mt-1 block w-full rounded-md border-slate-300 shadow-sm sm:text-sm" />
            </div>
          </div>
        </div>

        {/* Botón de Envío */}
        <div className="mt-8 pt-6 border-t flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-primary-600 text-white rounded-lg shadow-md hover:bg-primary-700 disabled:bg-slate-400"
          >
            {loading ? "Creando Paciente..." : "Crear Paciente"}
          </button>
        </div>
      </form>
    </main>
  );
}
