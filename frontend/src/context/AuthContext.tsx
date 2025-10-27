import { createContext, useContext, useMemo, useState, useEffect } from "react";
import type { User } from "../api/endpoints";
import { login as apiLogin, logout as apiLogout, getStoredUser } from "../api/endpoints";

type AuthState = {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthCtx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // hidrata estado desde localStorage al cargar
  useEffect(() => {
    setUser(getStoredUser());
    setLoading(false);
  }, []);

  const doLogin = async (email: string, password: string) => {
    setLoading(true);
    try {
      const { user } = await apiLogin(email, password);
      setUser(user);
    } finally {
      setLoading(false);
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
