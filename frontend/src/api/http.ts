import axios from "axios";

// Define the storage keys
const TOKEN_KEY = "token";
const USER_KEY = "user";

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 15000,
});

// === Request Interceptor: Attach JWT and X-CSRF-TOKEN if they exist ===
http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    // Attach the Bearer token
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


// === Response Interceptor: Normalize errors and handle 401 ===
http.interceptors.response.use(
  (r) => r,
  async (error) => {
    const originalRequest = error.config;
    if (error?.response?.status === 401 && !originalRequest._retry) {
      console.error("Error 401: Unauthorized. Logging out...");
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      if (window.location.pathname !== '/login') {
          const currentPath = window.location.pathname + window.location.search;
          window.location.replace(`/login?from=${encodeURIComponent(currentPath)}`);
      }
    }
    return Promise.reject(error);
  }
);

export default http;
