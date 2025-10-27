import axios from "axios";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // ej: http://localhost:5000/api/v1
  timeout: 15000,
});

// === Request: adjunta JWT si existe ===
http.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // << nombre unificado
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// === Response: normaliza errores (opcional refresh) ===
http.interceptors.response.use(
  (r) => r,
  async (error) => {
    // Si tu backend expone /auth/refresh, puedes reintentar aquí.
    // if (error?.response?.status === 401 && !error.config.__isRetry) {
    //   try {
    //     const { data } = await axios.post(
    //       `${import.meta.env.VITE_API_URL}/auth/refresh`,
    //       {},
    //       { withCredentials: true }
    //     );
    //     localStorage.setItem("token", data.access_token);
    //     const cfg = { ...error.config, __isRetry: true };
    //     cfg.headers.Authorization = `Bearer ${data.access_token}`;
    //     return http(cfg);
    //   } catch (_) {}
    // }
    return Promise.reject(error);
  }
);

export default http;
