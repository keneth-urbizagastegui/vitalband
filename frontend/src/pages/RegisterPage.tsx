// frontend/src/pages/RegisterPage.tsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { register } from "../api/endpoints"; // Importa tu función de API
import logo from "../assets/logo.png";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Validaciones simples
  const validate = () => {
    if (!name || !email || !password || !confirmPassword) {
      setError("Todos los campos son obligatorios.");
      return false;
    }
    const re = /\S+@\S+\.\S+/;
    if (!re.test(email)) {
      setError("Email inválido.");
      return false;
    }
    if (password.length < 8) {
        setError("La contraseña debe tener al menos 8 caracteres.");
        return false;
    }
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return false;
    }
    return true;
  };

const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!validate()) return;

    setLoading(true);

    try {
      // Llama a la API de registro
      const response = await register({
        name: name,
        email: email,
        password: password,
        confirm_password: confirmPassword
      });

      // --- MODIFICACIÓN ---
      // Guardamos manualmente el token y el usuario, ya que la API (endpoints.ts) ya no lo hace.
      if (response.access_token && response.user) {
        localStorage.setItem("token", response.access_token);
        localStorage.setItem("user", JSON.stringify(response.user));
      } else {
        throw new Error("El registro no devolvió un token o un usuario.");
      }
      // --- FIN MODIFICACIÓN ---


      // Si tiene éxito, redirige al dashboard.
      // ProtectedRoute verá el token en localStorage y permitirá el acceso.
      // Usamos window.location.href para forzar un re-load completo
      // y asegurar que el AuthContext lea el nuevo usuario de localStorage.
      window.location.href = "/dashboard";

    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "No se pudo completar el registro.";
      setError(msg);
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex">
      {/* Fondo (igual que en Login) */}
      <img
        src="/bg-hero.png"
        alt=""
        className="absolute inset-0 -z-20 h-full w-full object-cover object-left"
        loading="eager"
        decoding="async"
      />
      <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary-700/60 via-primary-600/45 to-primary-500/35" />

      {/* Columna logo (igual que en Login) */}
      <div className="hidden md:flex w-1/3 items-start justify-center p-10">
        <img src={logo} alt="VitalBand" className="w-64 h-auto drop-shadow-xl" />
      </div>

      {/* Tarjeta de Registro */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-xl bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-primary-500/20 p-8">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-semibold tracking-tight text-primary-700">
              Crear Cuenta
            </h1>
            <p className="text-primary-600 mt-2">Únete a VitalBand para monitorizar tu salud.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Nombre */}
            <div>
              <label htmlFor="nameInput" className="block text-sm font-medium text-primary-700">Nombre Completo</label>
              <input
                id="nameInput"
                type="text"
                className="mt-1 w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3
                           placeholder-primary-500/60 text-ink focus:outline-none
                           focus:ring-2 focus:ring-primary-500/50"
                placeholder="Ej: Ana Pérez"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="emailInput" className="block text-sm font-medium text-primary-700">Email</label>
              <input
                id="emailInput"
                type="email"
                className="mt-1 w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3
                           placeholder-primary-500/60 text-ink focus:outline-none
                           focus:ring-2 focus:ring-primary-500/50"
                placeholder="ana.perez@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="passwordInput" className="block text-sm font-medium text-primary-700">Contraseña</label>
              <div className="mt-1 relative">
                <input
                  id="passwordInput"
                  type={showPass ? "text" : "password"}
                  className="w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3 pr-20
                             placeholder-primary-500/60 text-ink focus:outline-none
                             focus:ring-2 focus:ring-primary-500/50"
                  placeholder="Mínimo 8 caracteres"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass((s) => !s)}
                  className="absolute inset-y-0 right-3 my-auto text-sm text-primary-700/80 hover:text-primary-700"
                  aria-label={showPass ? "Ocultar" : "Mostrar"}
                >
                  {showPass ? "Ocultar" : "Mostrar"}
                </button>
              </div>
            </div>

            {/* Confirmar Password */}
            <div>
              <label htmlFor="confirmPasswordInput" className="block text-sm font-medium text-primary-700">Confirmar Contraseña</label>
              <input
                id="confirmPasswordInput"
                type={showPass ? "text" : "password"}
                className="mt-1 w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3
                           placeholder-primary-500/60 text-ink focus:outline-none
                           focus:ring-2 focus:ring-primary-500/50"
                placeholder="Repite tu contraseña"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
              />
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
              {loading ? "Registrando..." : "Crear Cuenta"}
            </button>

            {/* Link a Login */}
            <div className="text-sm text-center mt-4">
              <span className="text-primary-700">¿Ya tienes cuenta? </span>
              <Link to="/login" className="underline text-primary-700 hover:text-primary-900 font-medium">
                Inicia Sesión
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
