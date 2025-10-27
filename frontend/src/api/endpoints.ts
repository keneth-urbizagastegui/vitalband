import http from "./http";

/* ===========================
   Tipos compartidos
   =========================== */

export type Role = "admin" | "client"; 

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
  id?: number; 
  device_id?: number; 
  ts: string;     
  heart_rate_bpm: number | null; 
  spo2_pct: number | null;       
  temp_c?: number | string | null; 
  motion_level?: number | null;   
};

/* ===========================
   Helpers de storage
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
}

/* ===========================
   AUTH
   =========================== */

/**
 * Inicia sesión contra Flask backend:
 * - POST /login { email, password }
 * - Devuelve { access_token }
 * - Decodifica el JWT para extraer el rol
 * - Persiste token y user en localStorage
 */

export async function login(email: string, password: string): Promise<{ token: string; user: User }> {
  const { data } = await http.post("/auth/login", { email, password });

  const token: string = data?.access_token;
  if (!token) {
    throw new Error("No se recibió access_token.");
  }
  localStorage.setItem(TOKEN_KEY, token); 

  let user: User | null = data?.user ?? null; 

  if (!user) {
    try {
      const meResponse = await http.get("/auth/me"); 
      user = meResponse.data as User;
    } catch (meError) {
      console.error("Error fetching user data from /auth/me:", meError);
      localStorage.removeItem(TOKEN_KEY);
      throw new Error("Login exitoso pero no se pudo obtener la información del usuario.");
    }
  }

  if (!user || typeof user !== 'object' || !user.id || !user.email || !user.role) {
     localStorage.removeItem(TOKEN_KEY); // Limpia el token si el usuario no es válido
     throw new Error("La información del usuario recibida no es válida.");
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
  const { data } = await http.get(`/readings/${deviceId}/last24h`); 
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
