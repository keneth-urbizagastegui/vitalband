export default function Topbar() {
  const logout = () => { localStorage.removeItem("token"); location.href="/login"; };
  return (
    <header className="h-14 border-b bg-white/80 backdrop-blur sticky top-0 z-40">
      <div className="mx-auto max-w-7xl h-full px-4 flex items-center justify-between">
        <div className="font-semibold">VitalBand</div>
        <button onClick={logout} className="px-3 py-1.5 text-sm rounded-md border hover:bg-slate-50">
          Salir
        </button>
      </div>
    </header>
  );
}
