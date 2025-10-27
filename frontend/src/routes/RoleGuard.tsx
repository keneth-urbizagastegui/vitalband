import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import type { Role } from "../api/endpoints";

export default function RoleGuard({ allow, children }: { allow: Role[]; children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="p-6">Cargando…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!allow.includes(user.role)) return <Navigate to="/dashboard" replace />;

  return <>{children}</>;
}
