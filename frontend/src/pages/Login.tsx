import { useState } from "react";
import { login } from "../api/endpoints";

export default function Login() {
  const [email, setEmail] = useState("admin@vitalband.local");
  const [password, setPassword] = useState("Admin123!");
  const [err, setErr] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    try {
      const { access_token } = await login(email, password);
      localStorage.setItem("token", access_token);
      location.href = "/";
    } catch (e) {
      setErr("Credenciales inválidas");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <form onSubmit={onSubmit} className="bg-white border rounded-2xl p-6 w-full max-w-sm shadow-sm">
        <h1 className="text-xl font-semibold mb-4">Iniciar sesión</h1>
        <label className="text-sm">Email</label>
        <input className="w-full border rounded px-3 py-2 mt-1 mb-3" value={email} onChange={e=>setEmail(e.target.value)} />
        <label className="text-sm">Contraseña</label>
        <input className="w-full border rounded px-3 py-2 mt-1 mb-4" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="w-full bg-slate-900 text-white rounded-md py-2 hover:bg-black">Entrar</button>
        {err && <p className="text-sm text-red-600 mt-3">{err}</p>}
      </form>
    </div>
  );
}
