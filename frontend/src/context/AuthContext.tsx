import { createContext, useContext, useMemo, useState, useEffect } from "react";
import type { User } from "../api/endpoints";
import { login as apiLogin, logout as apiLogout, getStoredUser } from "../api/endpoints";

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
};

const AuthCtx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setUser(getStoredUser());
    setLoading(false);
  }, []);

  // Modifica doLogin para que devuelva el usuario
  const doLogin = async (email: string, password: string): Promise<User> => {
    setLoading(true);
    try {
      // apiLogin ya devuelve { token, user }
      const { user: loggedInUser } = await apiLogin(email, password);
      setUser(loggedInUser);
      setLoading(false); // Mover setLoading(false) aquí
      return loggedInUser; // Devuelve el usuario
    } catch (error) {
      setLoading(false); // Asegúrate de parar la carga en caso de error
      throw error; // Relanza el error para que Login.tsx lo maneje
    }
  };

  const doLogout = () => {
    apiLogout();
    setUser(null);
  };

  const value = useMemo<AuthState>(
    () => ({ user, loading, login: doLogin, logout: doLogout }),
    [user, loading]
  );

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
