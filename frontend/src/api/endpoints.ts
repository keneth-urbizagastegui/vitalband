import http from "./http";

/* ===========================
   Tipos Compartidos (Expandidos)
   =========================== */

export type Role = "admin" | "client";

// Información básica del usuario (del token/login)
export type User = {
  id: number;
  email: string;
  role: Role;
  name?: string; // Si el backend lo devuelve en /login o /me
};

// Información detallada del Paciente (viene del backend PatientResponse)
export type PatientDetail = {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  full_name: string; // Generado por el backend
  email?: string | null;
  phone?: string | null;
  birthdate?: string | null; // Formato YYYY-MM-DD
  sex: "male" | "female" | "other" | "unknown";
  height_cm?: string | null; // Viene como string del backend (Decimal)
  weight_kg?: string | null; // Viene como string del backend (Decimal)
  created_at: string; // ISO 8601
};

// Información del Dispositivo (viene del backend DeviceResponse)
export type Device = {
  id: number;
  patient_id: number | null;
  model: string;
  serial: string;
  status: "new" | "active" | "lost" | "retired" | "service";
  registered_at: string; // ISO 8601
};

// Lectura Biométrica (viene del backend ReadingResponse)
export type Reading = {
  id: number; // ID es requerido según el schema de respuesta
  device_id: number; // ID es requerido según el schema de respuesta
  ts: string; // ISO 8601
  heart_rate_bpm: number | null;
  spo2_pct: number | null;
  temp_c?: string | null; // Viene como string (Decimal places=1)
  motion_level?: number | null;
};

// Telemetría del Dispositivo (viene del backend DeviceTelemetryResponse)
export type DeviceTelemetry = {
  id: number;
  device_id: number;
  ts: string; // ISO 8601
  battery_mv: number | null;
  battery_pct: number | null;
  charging: boolean | null;
  rssi_dbm?: number | null;
  board_temp_c?: string | null; // Viene como string (Decimal places=1)
};

// Alerta (viene del backend AlertResponse)
export type Alert = {
  id: number;
  patient_id: number;
  ts: string; // ISO 8601
  type: "tachycardia" | "bradycardia" | "fever" | "hypoxia" | "custom"; // Asegúrate que coincidan con el backend
  severity: "low" | "moderate" | "high" | "critical"; // Asegúrate que coincidan con el backend
  message: string | null;
  acknowledged_by: number | null; // User ID
  acknowledged_at: string | null; // ISO 8601
};

// Umbral (viene del backend ThresholdResponse)
export type Threshold = {
  id: number;
  patient_id: number | null; // Null si es global
  metric: "heart_rate" | "temperature" | "spo2";
  min_value: string | null; // Viene como string (Decimal)
  max_value: string | null; // Viene como string (Decimal)
  created_at: string; // ISO 8601
};

// Tipo para parámetros de rango de fechas
export type DateRangeParams = {
  from?: string; // ISO 8601 string
  to?: string; // ISO 8601 string
  limit?: number;
};

// Tipo genérico para respuestas de lista del backend
type ListResponse<T> = {
  items: T[];
  // Podrías añadir paginación aquí si el backend la implementa
  // total?: number;
  // page?: number;
  // per_page?: number;
};


/* ===========================
   Helpers de storage (Sin cambios)
   =========================== */

const TOKEN_KEY = "token";
const USER_KEY = "user";

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  try {
    return raw ? (JSON.parse(raw) as User) : null;
  } catch (e) {
    console.error("Error parsing stored user:", e);
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  // Podrías añadir una redirección aquí si es necesario
  // window.location.href = '/login';
}

/* ===========================
   AUTH API Calls
   =========================== */

// login (Modificado ligeramente para coincidir con backend)
export async function login(email: string, password: string): Promise<{ token: string; user: User }> {
  // El backend ahora devuelve { access_token, user } directamente
  const { data } = await http.post<{ access_token: string; user: User }>("/auth/login", { email, password });

  const token: string = data?.access_token;
  const user: User | null = data?.user;

  if (!token || !user || !user.id || !user.email || !user.role) {
    throw new Error("Respuesta de login inválida del servidor.");
  }

  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return { token, user };
}

// NUEVO: Registro
export async function register(userData: { name: string; email: string; password: string; confirm_password?: string }): Promise<{ message: string; user: User; access_token?: string }> {
  // El backend devuelve { message, user, access_token? }
  const { data } = await http.post("/auth/register", userData);
  // Si hay token, loguear al usuario
  if (data?.access_token && data?.user) {
      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  }
  return data;
}

// NUEVO: Olvidó Contraseña
export async function forgotPassword(email: string): Promise<{ message: string }> {
  const { data } = await http.post("/auth/forgot-password", { email });
  return data; // Devuelve { message: "..." }
}

// NUEVO: Resetear Contraseña
export async function resetPassword(token: string, new_password: string, confirm_new_password?: string): Promise<{ message: string }> {
  const payload = { token, new_password, confirm_new_password };
  const { data } = await http.post("/auth/reset-password", payload);
  return data; // Devuelve { message: "..." }
}

// NUEVO: Obtener info del usuario actual (si se necesita refrescar)
export async function getMe(): Promise<User> {
   const { data } = await http.get<User>("/auth/me");
   // Actualiza el usuario en localStorage si es necesario
   localStorage.setItem(USER_KEY, JSON.stringify(data));
   return data;
}


/* ===========================
   CLIENT API Calls (/me/*)
   =========================== */

// NUEVO: Obtener perfil del paciente logueado
export async function getMyProfile(): Promise<PatientDetail> {
  const { data } = await http.get<PatientDetail>("/me/profile");
  return data;
}

// NUEVO: Obtener dispositivos del paciente logueado
export async function getMyDevices(): Promise<Device[]> {
  const { data } = await http.get<ListResponse<Device>>("/me/devices");
  return data?.items ?? [];
}

// NUEVO: Obtener última lectura para el dashboard
export async function getMyLatestReadings(): Promise<{ latest_reading: Reading | null; device_status: string | null }> {
  const { data } = await http.get<{ latest_reading: Reading | null; device_status: string | null }>("/me/readings/latest");
  return data;
}

// NUEVO: Obtener historial de lecturas con filtros
export async function getMyReadingsHistory(params?: DateRangeParams): Promise<Reading[]> {
  const { data } = await http.get<ListResponse<Reading>>("/me/readings", { params });
  return data?.items ?? [];
}

// NUEVO: Obtener alertas del paciente logueado
export async function getMyAlerts(params?: { limit?: number; acknowledged?: boolean }): Promise<Alert[]> {
  const { data } = await http.get<ListResponse<Alert>>("/me/alerts", { params });
  return data?.items ?? [];
}


/* ===========================
   ADMIN API Calls (/admin/*)
   =========================== */

// --- Admin: Pacientes ---

// listPatients ahora apunta a la ruta admin
export async function listPatientsAdmin(params?: { /* filtros? */ }): Promise<PatientDetail[]> {
  const { data } = await http.get<ListResponse<PatientDetail>>("/admin/patients", { params });
  return data?.items ?? [];
}

export async function getPatientDetailAdmin(patientId: number): Promise<PatientDetail> {
  const { data } = await http.get<PatientDetail>(`/admin/patients/${patientId}`);
  return data;
}

// Define un tipo para la creación (excluye campos generados como id, full_name, created_at)
export type PatientCreateData = Omit<PatientDetail, 'id' | 'full_name' | 'created_at'>;
export async function createPatientAdmin(patientData: PatientCreateData): Promise<PatientDetail> {
  const { data } = await http.post<PatientDetail>("/admin/patients", patientData);
  return data;
}

// Define un tipo para la actualización (todos los campos opcionales)
export type PatientUpdateData = Partial<Omit<PatientDetail, 'id' | 'user_id' | 'full_name' | 'created_at'>>;
export async function updatePatientAdmin(patientId: number, patientData: PatientUpdateData): Promise<PatientDetail> {
  const { data } = await http.put<PatientDetail>(`/admin/patients/${patientId}`, patientData);
  return data;
}

export async function deletePatientAdmin(patientId: number): Promise<void> {
  await http.delete(`/admin/patients/${patientId}`);
}

// --- Admin: Dispositivos ---

export async function listDevicesAdmin(params?: { /* filtros? page? per_page? */ }): Promise<Device[]> {
  const { data } = await http.get<ListResponse<Device>>("/admin/devices", { params });
  return data?.items ?? [];
}

export async function getDeviceDetailAdmin(deviceId: number): Promise<Device> {
  const { data } = await http.get<Device>(`/admin/devices/${deviceId}`);
  return data;
}

export type DeviceCreateData = { serial: string; model: string; status?: string; patient_id?: number | null };
export async function createDeviceAdmin(deviceData: DeviceCreateData): Promise<Device> {
  const { data } = await http.post<Device>("/admin/devices", deviceData);
  return data;
}

export type DeviceUpdateData = Partial<Pick<Device, 'model' | 'status'>>;
export async function updateDeviceAdmin(deviceId: number, deviceData: DeviceUpdateData): Promise<Device> {
  const { data } = await http.put<Device>(`/admin/devices/${deviceId}`, deviceData);
  return data;
}

export async function assignDeviceAdmin(deviceId: number, patientId: number | null): Promise<Device> {
  const { data } = await http.post<Device>(`/admin/devices/${deviceId}/assign`, { patient_id: patientId });
  return data;
}

export async function deleteDeviceAdmin(deviceId: number): Promise<void> {
  await http.delete(`/admin/devices/${deviceId}`);
}

// --- Admin: Alertas ---

// listAlerts renombrado para claridad
export async function listAlertsForPatientAdmin(patientId: number, params?: { limit?: number }): Promise<Alert[]> {
  const { data } = await http.get<ListResponse<Alert>>(`/admin/patients/${patientId}/alerts`, { params });
  return data?.items ?? [];
}

export async function getAlertDetailAdmin(alertId: number): Promise<Alert> {
  const { data } = await http.get<Alert>(`/admin/alerts/${alertId}`);
  return data;
}

export async function acknowledgeAlertAdmin(alertId: number, notes?: string): Promise<Alert> {
  const payload = notes ? { notes } : {};
  const { data } = await http.post<Alert>(`/admin/alerts/${alertId}/acknowledge`, payload);
  return data;
}

// --- Admin: Umbrales ---

export async function getGlobalThresholdsAdmin(): Promise<Threshold[]> {
   const { data } = await http.get<ListResponse<Threshold>>("/admin/thresholds/global");
   return data?.items ?? [];
}

export type ThresholdUpdateData = { min_value?: number | string | null; max_value?: number | string | null };
export async function setGlobalThresholdAdmin(metric: string, thresholdData: ThresholdUpdateData): Promise<Threshold> {
  const { data } = await http.put<Threshold>(`/admin/thresholds/global/${metric}`, thresholdData);
  return data;
}

export async function getPatientThresholdsAdmin(patientId: number): Promise<Threshold[]> {
   const { data } = await http.get<ListResponse<Threshold>>(`/admin/patients/${patientId}/thresholds`);
   return data?.items ?? [];
}

export async function setPatientThresholdAdmin(patientId: number, metric: string, thresholdData: ThresholdUpdateData): Promise<Threshold> {
  const { data } = await http.put<Threshold>(`/admin/patients/${patientId}/thresholds/${metric}`, thresholdData);
  return data;
}


/* ===========================
   TELEMETRÍA (Lectura puede ser para Admin o Cliente)
   =========================== */

export async function listDeviceTelemetry(deviceId: number, params?: DateRangeParams): Promise<DeviceTelemetry[]> {
  const { data } = await http.get<ListResponse<DeviceTelemetry>>(`/devices/${deviceId}/telemetry`, { params });
  return data?.items ?? [];
}
// NOTA: POST /devices/<id>/telemetry (escritura) probablemente no se llama desde el frontend React.

/* ===========================
   CHATBOT API Calls
   =========================== */

// NUEVO: Enviar consulta al chatbot
export async function queryChatbot(message: string): Promise<{ reply: string }> {
  const { data } = await http.post<{ reply: string }>("/chatbot/query", { message });
  return data;
}