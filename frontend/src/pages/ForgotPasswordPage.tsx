// frontend/src/pages/ForgotPasswordPage.tsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../api/endpoints"; // Importa tu función de API
import logo from "../assets/logo.png";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!email) {
      setError("Por favor, introduce tu correo electrónico.");
      return;
    }
    
    setLoading(true);

    try {
      // Llama a la API
      // El backend siempre devuelve 200 OK (incluso si el email no existe)
      // con un mensaje genérico.
      const response = await forgotPassword(email);
      
      // Muestra el mensaje de éxito del backend
      setSuccessMessage(response.message);

    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.message || "Ocurrió un error.";
      setError(msg);
    } finally {
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

      {/* Tarjeta de Recuperación */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-xl bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-primary-500/20 p-8">
          <div className="text-center mb-6">
            <h1 className="text-4xl font-semibold tracking-tight text-primary-700">
              Recuperar Contraseña
            </h1>
          </div>

          {/* Muestra el formulario O el mensaje de éxito */}
          {successMessage ? (
            <div className="text-center">
              <p className="text-lg text-ink">{successMessage}</p>
              <p className="text-muted mt-2">Por favor, revisa tu bandeja de entrada (y spam).</p>
              <Link
                to="/login"
                className="mt-6 inline-block w-full rounded-xl bg-white text-primary-700 border border-primary-500/40
                           py-3 hover:bg-primary-500/10 active:bg-primary-500/20
                           focus:outline-none focus:ring-2 focus:ring-primary-500/50 text-center font-medium"
              >
                Volver a Iniciar Sesión
              </Link>
            </div>
          ) : (
            <>
              <p className="text-primary-600 text-center mb-6">
                Introduce tu email y te enviaremos un enlace para restablecer tu contraseña.
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Email */}
                <div>
                  <label htmlFor="emailInput" className="block text-sm font-medium text-primary-700">Email</label>
                  <input
                    id="emailInput"
                    type="email"
                    className="mt-1 w-full rounded-xl border border-primary-500/30 bg-white px-4 py-3
                               placeholder-primary-500/60 text-ink focus:outline-none
                               focus:ring-2 focus:ring-primary-500/50"
                    placeholder="tu.email@ejemplo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
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
                  {loading ? "Enviando..." : "Enviar Enlace"}
                </button>

                {/* Link a Login */}
                <div className="text-sm text-center mt-4">
                  <Link to="/login" className="underline text-primary-700 hover:text-primary-900 font-medium">
                    Volver a Iniciar Sesión
                  </Link>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
