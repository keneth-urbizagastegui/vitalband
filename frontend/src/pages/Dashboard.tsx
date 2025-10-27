import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function Dashboard() {
  const [userName, setUserName] = useState("Usuario");

  useEffect(() => {
    const raw = localStorage.getItem("user");
    if (raw) {
      const user = JSON.parse(raw);
      setUserName(user?.email?.split("@")[0] || "Usuario");
    }
  }, []);

  return (
    <div className="min-h-screen flex bg-slate-50 text-ink">
      {/* Sidebar */}
      <Sidebar />

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col">
        {/* Topbar */}
        <Topbar userName={userName} />

        {/* Sección principal */}
        <main className="flex-1 p-8 space-y-8">
          <h1 className="text-2xl font-semibold text-primary-700">
            Panel de métricas
          </h1>

          {/* Tarjetas o gráficos aquí */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-md border border-primary-500/10">
              <h2 className="text-primary-700 font-medium">Ritmo cardíaco</h2>
              <p className="text-3xl mt-3 font-semibold text-primary-600">78 bpm</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-primary-500/10">
              <h2 className="text-primary-700 font-medium">SpO₂</h2>
              <p className="text-3xl mt-3 font-semibold text-primary-600">96%</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-primary-500/10">
              <h2 className="text-primary-700 font-medium">Temperatura</h2>
              <p className="text-3xl mt-3 font-semibold text-primary-600">36.8 °C</p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
