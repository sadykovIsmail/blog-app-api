"use client";

/**
 * auth.ts — Token management
 *
 * Strategy:
 *  - Access token: held in module-level memory (cleared on page refresh → re-login or silent refresh)
 *  - Refresh token: persisted in localStorage so the user stays logged in across refreshes
 */

import type { TokenPair } from "./types";

const REFRESH_KEY = "blog_refresh_token";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Module-level memory store for the access token
let _accessToken: string | null = null;

// ─── Accessors ────────────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  return _accessToken;
}

export function setAccessToken(token: string): void {
  _accessToken = token;
}

export function clearAccessToken(): void {
  _accessToken = null;
}

// ─── Refresh token (localStorage) ─────────────────────────────────────────────

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setRefreshToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(REFRESH_KEY, token);
  }
}

export function clearRefreshToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(REFRESH_KEY);
  }
}

// ─── Session helpers ───────────────────────────────────────────────────────────

export function storeTokenPair(pair: TokenPair): void {
  setAccessToken(pair.access);
  setRefreshToken(pair.refresh);
}

export function clearSession(): void {
  clearAccessToken();
  clearRefreshToken();
}

export function isLoggedIn(): boolean {
  return _accessToken !== null || getRefreshToken() !== null;
}

// ─── Token refresh ────────────────────────────────────────────────────────────

/**
 * Attempt a silent token refresh using the stored refresh token.
 * Returns the new access token on success, null on failure.
 */
export async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  try {
    const res = await fetch(`${API_URL}/api/v1/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) {
      clearSession();
      return null;
    }

    const data = (await res.json()) as { access: string };
    setAccessToken(data.access);
    return data.access;
  } catch {
    clearSession();
    return null;
  }
}
