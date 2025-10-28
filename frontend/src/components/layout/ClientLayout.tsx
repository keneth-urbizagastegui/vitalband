// frontend/src/components/layout/ClientLayout.tsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { logout } from "../../api/endpoints"; // Importa tu función logout
// Opcional: Importa iconos si los tienes (ej. react-icons)
// import { LuLayoutDashboard, LuBell, LuHistory, LuUserCircle } from "react-icons/lu";

// --- Componente de Link de Navegación (NavLink) ---
// Usamos NavLink de react-router-dom porque nos da una clase 'active'
// que podemos usar para resaltar la página actual.

type NavItemProps = {
  to: string;
  children: React.ReactNode;
  // icon?: React.ReactNode; // Descomenta si usas iconos
};

function NavItem({ to, children /*, icon*/ }: NavItemProps) {
  const activeClass = "bg-primary-700 text-white";
  const inactiveClass = "text-primary-100 hover:bg-primary-600 hover:text-white";

  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 transition-all ${
          isActive ? activeClass : inactiveClass
        }`
      }
    >
      {/* {icon} */}
      <span className="font-medium">{children}</span>
    </NavLink>
  );
}

// --- Componente de Layout Principal ---

export default function ClientLayout() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout(); // Limpia el localStorage
    navigate("/login", { replace: true }); // Redirige al login
  };

  const userName = user?.name || user?.email?.split("@")[0] || "Usuario";

  return (
    <div className="grid min-h-screen w-full lg:grid-cols-[280px_1fr]">
      {/* --- Sidebar (Barra Lateral) --- */}
      <div className="hidden border-r bg-primary-800 text-white lg:block">
        <div className="flex h-full max-h-screen flex-col gap-2">
          <div className="flex h-[60px] items-center border-b border-primary-700 px-6">
            <h1 className="text-xl font-bold text-white">App de Salud</h1>
            {/*  */}
          </div>
          <nav className="flex-1 overflow-auto px-4 py-4">
            <ul className="space-y-2">
              {/* Aquí van los links a tus páginas */}
              <li>
                <NavItem to="/dashboard">Dashboard</NavItem> {/* Asume que la ruta es /dashboard */}
              </li>
              <li>
                <NavItem to="/history">Historial</NavItem> {/* Asume que la ruta es /history */}
              </li>
              <li>
                <NavItem to="/alerts">Alertas</NavItem> {/* Asume que la ruta es /alerts */}
              </li>
              <li>
                <NavItem to="/profile">Mi Perfil</NavItem> {/* Asume que la ruta es /profile */}
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* --- Contenido Principal (Incluye Topbar) --- */}
      <div className="flex flex-col">
        {/* --- Topbar (Barra Superior) --- */}
        <header className="flex h-[60px] items-center justify-end gap-4 border-b bg-white px-6">
          <span className="text-sm text-muted">Hola, <span className="font-semibold text-ink">{userName}</span></span>
          <button
            onClick={handleLogout}
            className="rounded-md px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* --- Área de Contenido de la Página --- */}
        {/* React Router renderizará la página activa (Dashboard, Alerts, etc.) aquí */}
        <div className="flex-1 overflow-y-auto bg-slate-50">
          <Outlet />
        </div>
        
      </div>
    </div>
  );
}