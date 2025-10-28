// frontend/src/pages/ProfilePage.tsx
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { getMyProfile, getMyDevices } from "../api/endpoints";
import type { PatientDetail, Device } from "../api/endpoints";

// --- Helpers de Formato (puedes moverlos a un archivo utils.ts) ---

// Formatea YYYY-MM-DD a un formato local (ej: 15/10/1990)
const formatSimpleDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'No especificado';
  try {
    // Añade 'T00:00:00' para asegurar que se interprete como fecha local
    // y no se desplace por la zona horaria (UTC)
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

// Traduce los valores 'sex'
const formatSex = (sex: PatientDetail['sex']): string => {
  const translations: Record<PatientDetail['sex'], string> = {
    male: "Masculino",
    female: "Femenino",
    other: "Otro",
    unknown: "No especificado",
  };
  return translations[sex] || 'No especificado';
};

// Traduce los estados del dispositivo
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

// --- Componente de Item de Detalle (reutilizable) ---
type DetailItemProps = {
  label: string;
  value: string | number | null | undefined;
  unit?: string;
};

// Un pequeño componente para mostrar un par "Etiqueta: Valor"
function DetailItem({ label, value, unit }: DetailItemProps) {
  const displayValue = value ?? 'No especificado';
  return (
    <div className="py-2 sm:py-3">
      <dt className="text-sm font-medium text-muted">{label}</dt>
      <dd className="mt-1 text-base font-semibold text-ink">
        {displayValue}
        {value && unit && <span className="ml-1 text-sm font-normal text-muted">{unit}</span>}
      </dd>
    </div>
  );
}

// --- Componente Principal de la Página ---

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<PatientDetail | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfileData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Llama a ambas APIs en paralelo
        const [profileData, devicesData] = await Promise.all([
          getMyProfile(),
          getMyDevices(), // Esta API ya devuelve un array (data.items ?? [])
        ]);
        
        setProfile(profileData);
        setDevices(devicesData);

      } catch (err: any) {
        console.error("Error fetching profile data:", err);
        const msg = err?.response?.data?.message || err?.message || "No se pudo cargar el perfil.";
        setError(msg);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchProfileData();
    } else {
      setLoading(false);
    }
  }, [user]); // Recarga si el usuario cambia

  // --- Renderizado ---

  if (loading) {
    return <div className="p-6 text-center text-muted">Cargando perfil...</div>;
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg bg-red-50 text-red-700 text-sm">
        Error al cargar perfil: {error}
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="p-6 text-center text-muted">
        No se encontró la información del perfil.
      </div>
    );
  }

  return (
    <main className="flex-1 p-6 space-y-6 bg-slate-50">
      <h1 className="text-3xl font-semibold text-primary-700">
        Mi Perfil
      </h1>

      {/* Tarjeta de Información Personal */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <h2 className="text-xl font-semibold text-ink">Información Personal</h2>
        <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6">
          <DetailItem label="Nombre Completo" value={profile.full_name} />
          <DetailItem label="Email" value={profile.email} />
          <DetailItem label="Fecha de Nacimiento" value={formatSimpleDate(profile.birthdate)} />
          <DetailItem label="Sexo" value={formatSex(profile.sex)} />
          <DetailItem label="Teléfono" value={profile.phone} />
        </dl>
      </div>

      {/* Tarjeta de Información Física */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <h2 className="text-xl font-semibold text-ink">Métricas Físicas</h2>
        <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6">
          <DetailItem label="Altura" value={profile.height_cm} unit="cm" />
          <DetailItem label="Peso" value={profile.weight_kg} unit="kg" />
        </dl>
      </div>

      {/* Tarjeta de Dispositivo(s) Asignado(s) */}
      <div className="bg-white rounded-xl border shadow-sm p-6">
        <h2 className="text-xl font-semibold text-ink">Mi Dispositivo</h2>
        {devices.length > 0 ? (
          // Mapea por si el paciente tuviera más de uno
          devices.map(device => (
            <dl key={device.id} className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 border-t pt-4 first:border-t-0 first:pt-0">
              <DetailItem label="Modelo" value={device.model} />
              <DetailItem label="Número de Serie" value={device.serial} />
              <DetailItem label="Estado" value={formatDeviceStatus(device.status)} />
              <DetailItem label="Registrado el" value={formatSimpleDate(device.registered_at.split('T')[0])} />
            </dl>
          ))
        ) : (
          <p className="mt-4 text-muted">No tienes ningún dispositivo asignado.</p>
        )}
      </div>
    </main>
  );
}