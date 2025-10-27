import http from "./http";

// AUTH
export async function login(email: string, password: string) {
  const { data } = await http.post("/auth/login", { email, password });
  return data as { access_token: string };
}

// PACIENTES
export async function listPatients() {
  const { data } = await http.get("/patients");
  return (data?.items ?? []) as Array<{ id: number; full_name: string; email?: string|null }>;
}

// MÉTRICAS
export async function getReadings24h(deviceId: number) {
  const { data } = await http.get(`/metrics/${deviceId}/last24h`);
  return (data?.items ?? []) as any[];
}

// TELEMETRÍA
export async function listTelemetry(deviceId: number, fromISO: string, toISO?: string) {
  const params: any = { from: fromISO };
  if (toISO) params.to = toISO;
  const { data } = await http.get(`/devices/${deviceId}/telemetry`, { params });
  return (data?.items ?? []) as any[];
}

// (Opcional) ALERTAS
export async function listAlerts(patientId: number) {
  const { data } = await http.get(`/admin/patients/${patientId}/alerts`);
  return (data?.items ?? []) as any[];
}
