import { useAuth } from "../context/AuthContext";

export default function AdminPanel() {
  const { user, logout } = useAuth();
  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold">Panel de Administración</h1>
      <p className="mt-2 text-slate-600">Admin: {user?.email}</p>
      <button onClick={logout} className="mt-4 px-4 py-2 rounded-lg bg-slate-900 text-white">
        Cerrar sesión
      </button>
    </main>
  );
}
