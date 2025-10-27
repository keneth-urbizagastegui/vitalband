import http from "./http";

/* ===========================
   Tipos compartidos
   =========================== */

export type Role = "admin" | "user";

export type User = {
  id: number;
  email: string;
  role: Role;
};

export type Patient = {
  id: number;
  full_name: string;
  email?: string | null;
};

export type Reading = {
  ts: string;     // ISO timestamp
  hr: number;     // heart rate
  spo2: number;   // oxygen saturation
  temp?: number;  // opcional
};

/* ===========================
   Helpers de storage
   =========================== */

const TOKEN_KEY = "token";
const USER_KEY = "user";

export function getStoredUser(): User | null {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? (JSON.parse(raw) as User) : null;
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/* ===========================
   AUTH
   =========================== */

/**
 * Inicia sesión:
 * - POST /auth/login { email, password }
 * - Espera { access_token, user? }
 * - Si no viene user, hace GET /auth/me
 * - Persiste token y user en localStorage
 */
export async function login(email: string, password: string): Promise<{ token: string; user: User }> {
  const { data } = await http.post("/auth/login", { email, password });

  const token: string = data?.access_token;
  if (!token) throw new Error("No se recibió access_token.");

  localStorage.setItem(TOKEN_KEY, token);

  let user: User | undefined = data?.user;
  if (!user) {
    const me = await http.get("/auth/me"); // requiere JWT
    user = me.data as User;
  }

  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return { token, user };
}

/* ===========================
   PACIENTES
   =========================== */

export async function listPatients(): Promise<Patient[]> {
  const { data } = await http.get("/patients");
  return (data?.items ?? []) as Patient[];
}

/* ===========================
   MÉTRICAS
   =========================== */

export async function getReadings24h(deviceId: number): Promise<Reading[]> {
  const { data } = await http.get(`/metrics/${deviceId}/last24h`);
  return (data?.items ?? []) as Reading[];
}

/* ===========================
   TELEMETRÍA
   =========================== */

export async function listTelemetry(
  deviceId: number,
  fromISO: string,
  toISO?: string
): Promise<any[]> {
  const params: Record<string, string> = { from: fromISO };
  if (toISO) params.to = toISO;
  const { data } = await http.get(`/devices/${deviceId}/telemetry`, { params });
  return (data?.items ?? []) as any[];
}

/* ===========================
   ALERTAS (ADMIN)
   =========================== */

export async function listAlerts(patientId: number): Promise<any[]> {
  const { data } = await http.get(`/admin/patients/${patientId}/alerts`);
  return (data?.items ?? []) as any[];
}
