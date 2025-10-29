import axios from "axios";
import { jwtDecode } from "jwt-decode"; // <-- 1. Re-import the decoding function

// Define the storage keys
const TOKEN_KEY = "token";
const USER_KEY = "user";

// --- 2. Re-add the type for the decoded payload ---
type DecodedJwtPayload = {
  csrf?: string; // The CSRF claim added by Flask-JWT-Extended
  [key: string]: any; // Allow other fields
};

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
    console.log(`PASO 3 (HTTP): Token read from localStorage: ${token}`);

    // --- 3. RE-ADD THE CSRF DECODING AND HEADER LOGIC ---
    try {
      const decoded = jwtDecode<DecodedJwtPayload>(token);
      const csrfToken = decoded?.csrf; // Extract the value from the 'csrf' claim

      if (csrfToken) {
        // Add the X-CSRF-TOKEN header
        config.headers["X-CSRF-TOKEN"] = csrfToken;
        console.log(`PASO 3.1 (HTTP): Adding X-CSRF-TOKEN header: ${csrfToken}`);
      } else {
         console.warn("PASO 3.1 (HTTP): Could not find 'csrf' claim in the decoded token.");
      }
    } catch (e) {
      console.error("PASO 3.1 (HTTP): Error decoding JWT or extracting CSRF:", e);
    }
    // --- END RE-ADDITION ---
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
