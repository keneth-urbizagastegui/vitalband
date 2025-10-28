import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute() {
  const { user } = useAuth();

  // Si no hay usuario (no logueado), redirige a /login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Si hay usuario, renderiza el contenido de la ruta (el "Outlet")
  // En nuestro caso, el Outlet será el ClientLayout
  return <Outlet />;
}