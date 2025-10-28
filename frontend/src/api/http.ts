import axios from "axios";

// Define las claves aquí o impórtalas si las centralizas en otro lugar
const TOKEN_KEY = "token";
const USER_KEY = "user";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // ej: http://localhost:5000/api/v1
  timeout: 15000,
});

// === Request: adjunta JWT si existe ===
http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    // --- LÍNEA AÑADIDA PARA EL PASO 3 ---
    console.log(`PASO 3 (HTTP): Token leído de localStorage y a punto de enviar: ${token}`);
    // --- FIN DE LÍNEA AÑADIDA ---
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// === Response: normaliza errores y maneja 401 ===
http.interceptors.response.use(
  (r) => r,
  async (error) => {
    const originalRequest = error.config; // Guarda la configuración original

    // Verifica si es un error 401 y no es un reintento (si tuvieras lógica de refresh)
    if (error?.response?.status === 401 && !originalRequest._retry) {
      // originalRequest._retry = true; // Marca como reintento si implementas refresh

      // --- Lógica de Refresh Token (Comentada - requiere backend) ---
      // try {
      //   const { data } = await axios.post(`${import.meta.env.VITE_API_URL}/auth/refresh`, {}, { withCredentials: true });
      //   localStorage.setItem(TOKEN_KEY, data.access_token);
      //   // Actualiza el header de la petición original y reinténtala
      //   originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
      //   return http(originalRequest);
      // } catch (refreshError) {
      //   // Si el refresh falla, procede a desloguear
      //   console.error("Refresh token failed:", refreshError);
      //   // (Continúa con la lógica de abajo)
      // }
      // --- Fin Lógica Refresh ---

      // --- Lógica de Deslogueo por 401 (sin refresh o si refresh falla) ---
      console.error("Error 401: No autorizado o token expirado. Deslogueando...");

      // Replica la lógica de logout() de endpoints.ts
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);

      // Redirige a la página de login (si no estamos ya ahí)
      if (window.location.pathname !== '/login') {
          // Guarda la ruta actual para redirigir después del login (opcional)
          const currentPath = window.location.pathname + window.location.search;
          // Usa replace para evitar que el usuario vuelva atrás a la página protegida
          window.location.replace(`/login?from=${encodeURIComponent(currentPath)}`);
      }
      // --- Fin Lógica Deslogueo ---
    }

    // Para otros errores o si ya se manejó el 401, rechaza la promesa
    return Promise.reject(error);
  }
);

export default http;