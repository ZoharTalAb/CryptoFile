import { createContext, useContext, useEffect, useState } from "react";
import { authService } from "../services/auth.service";

type User = {
  id: number;
  email: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = authService.getToken();

    if (!token) {
      setLoading(false);
      return;
    }

    authService
      .getCurrentUser()
      .then((user) => {
        setUser(user);
      })
      .catch(() => {
        authService.clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  function logout() {
    authService.clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}