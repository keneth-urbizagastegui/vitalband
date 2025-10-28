// frontend/src/components/layout/AdminLayout.tsx
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { logout } from "../../api/endpoints"; // Importa tu función logout
// Opcional: Importa iconos si los tienes (ej. react-icons)
// import { LuLayoutDashboard, LuUsers, LuHardDrive, LuSettings } from "react-icons/lu";

// --- Componente de Link de Navegación (NavLink) ---
// Específico para el Admin Layout, con colores 'slate'
type NavItemProps = {
  to: string;
  // 'end' es importante para que la ruta padre no se quede activa
  // (ej. que "/admin" no se quede activo cuando estás en "/admin/patients")
  end?: boolean; 
  children: React.ReactNode;
  // icon?: React.ReactNode; 
};

function NavItem({ to, end = false, children /*, icon*/ }: NavItemProps) {
  const activeClass = "bg-slate-700 text-white";
  const inactiveClass = "text-slate-300 hover:bg-slate-700 hover:text-white";

  return (
    <NavLink
      to={to}
      end={end} // 'end' le dice a NavLink que no coincida con rutas anidadas
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

export default function AdminLayout() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout(); // Limpia el localStorage
    navigate("/login", { replace: true }); // Redirige al login
  };

  const userName = user?.name || user?.email?.split("@")[0] || "Admin";

  return (
    <div className="grid min-h-screen w-full lg:grid-cols-[280px_1fr]">
      {/* --- Sidebar (Barra Lateral) --- */}
      <div className="hidden border-r bg-slate-800 text-white lg:block">
        <div className="flex h-full max-h-screen flex-col gap-2">
          <div className="flex h-[60px] items-center border-b border-slate-700 px-6">
            <h1 className="text-xl font-bold text-white">Panel Admin</h1>
            {/*  */}
          </div>
          <nav className="flex-1 overflow-auto px-4 py-4">
            <ul className="space-y-2">
              {/* Aquí van los links a las páginas de Admin */}
              <li>
                {/* 'end={true}' es crucial aquí para la ruta index */}
                <NavItem to="/admin" end={true}>
                  Dashboard
                </NavItem>
              </li>
              <li>
                <NavItem to="/admin/patients">
                  Pacientes
                </NavItem>
              </li>
              <li>
                <NavItem to="/admin/devices">
                  Dispositivos
                </NavItem>
              </li>
              <li>
                <NavItem to="/admin/settings">
                  Configuración
                </NavItem>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* --- Contenido Principal (Incluye Topbar) --- */}
      <div className="flex flex-col">
        {/* --- Topbar (Barra Superior) --- */}
        <header className="flex h-[60px] items-center justify-end gap-4 border-b bg-white px-6">
          <span className="text-sm text-muted">Hola, <span className="font-semibold text-ink">{userName} (Admin)</span></span>
          <button
            onClick={handleLogout}
            className="rounded-md px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            Cerrar Sesión
          </button>
        </header>

        {/* --- Área de Contenido de la Página --- */}
        {/* React Router renderizará la página activa (AdminPanel, etc.) aquí */}
        <div className="flex-1 overflow-y-auto bg-slate-50">
          <Outlet />
        </div>
        
      </div>
    </div>
  );
}