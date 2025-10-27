import { useState } from "react";
import { useNavigate, useLocation} from "react-router-dom";
import type { Location } from "react-router-dom"; 
import { useAuth } from "../context/AuthContext";
import logo from "../assets/logo.png";

type LocState = { from?: Location } | null;

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const locState = (location.state as LocState) || null;

  const validate = () => {
    if (!email || !password) {
      setError("Completa email y contraseña.");
      return false;
    }
    const re = /\S+@\S+\.\S+/;
    if (!re.test(email)) {
      setError("Email inválido.");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;

    try {
      // Nota: el "remember" aquí es visual; si quisieras sessionStorage cuando NO recuerde,
      // puedes duplicar lógica en api/endpoints.ts
      await login(email, password);

      // si venía de una ruta protegida, vuelve allí
      const from = (locState?.from as any)?.pathname as string | undefined;
      if (from) return navigate(from, { replace: true });

      // según el rol
      const raw = localStorage.getItem("user");
      const role = raw ? (JSON.parse(raw).role as "admin" | "user") : "user";
      if (role === "admin") navigate("/admin", { replace: true });
      else navigate("/dashboard", { replace: true });
    } catch (err: any) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        "No se pudo iniciar sesión. Revisa tus credenciales.";
      setError(msg);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Columna izquierda con logo (oculta en pantallas chicas) */}
      <div className="hidden md:flex w-1/3 items-start justify-center p-8">
        <img src={logo} alt="VitalBand" className="w-64 h-64 object-contain" />
      </div>

      {/* Columna principal */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="max-w-xl text-center mb-8">
          <h1 className="text-4xl font-semibold tracking-tight">Bienvenido a VITALBAND</h1>
          <p className="text-slate-500 mt-2">Accede a tus métricas de VitalBand</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="w-full max-w-xl bg-white rounded-2xl shadow p-6 border border-slate-200"
        >
          {/* Email */}
          <label className="block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-slate-400"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />

          {/* Password */}
          <label className="block text-sm font-medium text-slate-700 mt-4">Contraseña</label>
          <div className="mt-1 relative">
            <input
              type={show ? "text" : "password"}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 pr-16 focus:outline-none focus:ring-2 focus:ring-slate-400"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShow((s) => !s)}
              className="absolute inset-y-0 right-3 my-auto text-sm text-slate-500"
              aria-label={show ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {show ? "Ocultar" : "Mostrar"}
            </button>
          </div>

          {/* Recordarme + enlaces */}
          <div className="mt-4 flex items-center justify-between">
            <label className="inline-flex items-center gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="rounded"
              />
              Recordarme
            </label>
            <div className="text-sm">
              <a href="/forgot" className="underline">¿Olvidaste tu contraseña?</a>
              <span className="mx-2">·</span>
              <a href="/signup" className="underline">Únete</a>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="mt-4 rounded-lg bg-red-50 text-red-700 px-4 py-3 text-sm">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-xl bg-slate-900 text-white py-3 hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Entrando…" : "Log in"}
          </button>

          <p className="text-center text-xs text-slate-400 mt-4">
            Este servicio es informativo y no brinda diagnóstico médico.
          </p>
        </form>
      </div>
    </div>
  );
}
