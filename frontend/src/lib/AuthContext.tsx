"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  storeTokenPair,
  clearSession,
  getRefreshToken,
  refreshAccessToken,
} from "./auth";
import { authApi } from "./api";
import type { LoginPayload, MeResponse, RegisterPayload } from "./types";

// ─── Context shape ────────────────────────────────────────────────────────────

interface AuthContextValue {
  user: MeResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<MeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    try {
      const me = await authApi.me();
      setUser(me);
    } catch {
      setUser(null);
    }
  }, []);

  // On mount: try to restore the session via the stored refresh token
  useEffect(() => {
    const restore = async () => {
      setIsLoading(true);
      const refresh = getRefreshToken();
      if (!refresh) {
        setIsLoading(false);
        return;
      }
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        await fetchMe();
      }
      setIsLoading(false);
    };
    restore();
  }, [fetchMe]);

  const login = useCallback(
    async (payload: LoginPayload) => {
      const tokens = await authApi.login(payload);
      storeTokenPair(tokens);
      await fetchMe();
    },
    [fetchMe]
  );

  const register = useCallback(async (payload: RegisterPayload) => {
    await authApi.register(payload);
    // Registration doesn't auto-log in — caller should redirect to /login
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    await fetchMe();
  }, [fetchMe]);

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: user !== null,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
}
