import http from "./http";

export const api = {
  login: (email: string, password: string) =>
    http.post("/auth/login", { email, password }).then(r => r.data),

  listPatients: () =>
    http.get("/patients").then(r => r.data.items),

  last24hMetrics: (deviceId: number) =>
    http.get(`/metrics/${deviceId}/last24h`).then(r => r.data.items),
};
