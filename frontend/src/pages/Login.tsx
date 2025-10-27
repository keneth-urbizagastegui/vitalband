import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import logo from "../assets/logo.png"; // logo blanco

type LocState = { from?: { pathname?: string } } | null;

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
    if (!email || !password) { setError("Completa email y contraseña."); return false; }
    const re = /\S+@\S+\.\S+/;
    if (!re.test(email)) { setError("Email inválido."); return false; }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;

    try {
      await login(email, password);
      const from = locState?.from?.pathname;
      if (from) return navigate(from, { replace: true });
      const raw = localStorage.getItem("user");
      const role = raw ? (JSON.parse(raw).role as "admin" | "user") : "user";
      navigate(role === "admin" ? "/admin" : "/dashboard", { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "No se pudo iniciar sesión.";
      setError(msg);
    }
  };

  return (
    <div className="relative min-h-screen flex">
      {/* Capa 1: imagen de fondo (desde public/) */}
      <img
        src="/bg-hero.png"
        alt=""
        className="absolute inset-0 -z-20 h-full w-full object-cover object-left"
        loading="eager"
        decoding="async"
      />

      {/* Capa 2: overlay con tu paleta para dar uniformidad/legibilidad */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary-700/60 via-primary-600/45 to-primary-500/35" />

      {/* Columna logo (logo blanco tal cual, sin filtros ni recortes) */}
      <div className="hidden md:flex w-1/3 items-start justify-center p-10">
        <img src={logo} alt="VitalBand" className="w-64 h-auto drop-shadow-xl" />
      </div>

      {/* Tarjeta blanca con textos celestes */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-xl bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-primary-500/20 p-8">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-semibold tracking-tight text-primary-700">
              Bienvenido a VITALBAND
            </h1>
            <p className="text-primary-600 mt-2">Accede a tus métricas de VitalBand</p>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Email */}
            <label className="block text-sm font-medium text-primary-700">Email</label>
            <input
              type="email"
              className="mt-1 w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3
                         placeholder-primary-500/60 text-ink focus:outline-none
                         focus:ring-2 focus:ring-primary-500/50"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />

            {/* Password */}
            <label className="block text-sm font-medium text-primary-700 mt-4">Contraseña</label>
            <div className="mt-1 relative">
              <input
                type={show ? "text" : "password"}
                className="w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3 pr-20
                           placeholder-primary-500/60 text-ink focus:outline-none
                           focus:ring-2 focus:ring-primary-500/50"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShow((s) => !s)}
                className="absolute inset-y-0 right-3 my-auto text-sm text-primary-700/80 hover:text-primary-700"
                aria-label={show ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {show ? "Ocultar" : "Mostrar"}
              </button>
            </div>

            {/* Recordarme + enlaces */}
            <div className="mt-4 flex items-center justify-between">
              <label className="inline-flex items-center gap-2 text-sm text-primary-700">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="rounded border-primary-500/40 text-primary-600 focus:ring-primary-500/50"
                />
                Recordarme
              </label>
              <div className="text-sm">
                <a href="/forgot" className="underline text-primary-700 hover:text-primary-900">¿Olvidaste tu contraseña?</a>
                <span className="mx-2 text-primary-500/60">·</span>
                <a href="/signup" className="underline text-primary-700 hover:text-primary-900">Únete</a>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="mt-4 rounded-lg bg-red-50 text-red-700 px-4 py-3 text-sm">
                {error}
              </div>
            )}

            {/* Botón */}
            <button
              type="submit"
              disabled={loading}
              className="mt-6 w-full rounded-xl bg-white text-primary-700 border border-primary-500/40
                         py-3 hover:bg-primary-500/10 active:bg-primary-500/20 disabled:opacity-60
                         focus:outline-none focus:ring-2 focus:ring-primary-500/50"
            >
              {loading ? "Entrando…" : "Log in"}
            </button>

            <p className="text-center text-xs text-primary-600 mt-4">
              Este servicio es informativo y no brinda diagnóstico médico.
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
