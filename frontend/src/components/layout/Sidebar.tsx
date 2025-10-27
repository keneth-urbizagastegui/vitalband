import { NavLink } from "react-router-dom";

const Item = ({ to, children }: { to: string; children: React.ReactNode }) => (
  <NavLink
    to={to}
    className={({isActive}) =>
      `block px-3 py-2 rounded-md text-sm hover:bg-slate-100 ${isActive ? "bg-slate-200 font-medium" : ""}`
    }
  >
    {children}
  </NavLink>
);

export default function Sidebar() {
  return (
    <aside className="w-56 border-r bg-white h-[calc(100vh-3.5rem)] sticky top-14">
      <nav className="p-3 space-y-1">
        <Item to="/">Dashboard</Item>
        <Item to="/history">Historial</Item>
        <Item to="/alerts">Alertas</Item>
        <Item to="/admin">Admin</Item>
      </nav>
    </aside>
  );
}
