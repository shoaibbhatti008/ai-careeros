import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import type { User } from "@/types";
import { clearTokens, hasAccessToken } from "@/lib/api";
import {
  getCurrentUser,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  type LoginCredentials,
  type RegisterData,
} from "@/lib/auth";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const me = await getCurrentUser();
      setUser(me);
    } catch {
      clearTokens();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    async function bootstrap() {
      if (hasAccessToken()) {
        await refreshUser();
      }
      setIsLoading(false);
    }
    bootstrap();
  }, [refreshUser]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const { user: me } = await apiLogin(credentials);
    setUser(me);
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    const { user: me } = await apiRegister(data);
    setUser(me);
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}