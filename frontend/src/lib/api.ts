/**
 * api.ts — Typed fetch wrapper with auth header injection and auto token refresh.
 *
 * All API calls go through `apiFetch`. On 401, it silently refreshes the access
 * token and retries once before giving up.
 */

import {
  getAccessToken,
  refreshAccessToken,
  setAccessToken,
} from "./auth";
import type {
  TokenPair,
  RegisterPayload,
  LoginPayload,
  User,
  MeResponse,
  PublicPost,
  MyPost,
  CreatePostPayload,
  UpdatePostPayload,
  PaginatedResponse,
  OgData,
  NotificationListResponse,
  HealthResponse,
  PublicUser,
  UserStats,
  Comment,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

interface FetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  /**
   * Skip the Authorization header even if an access token is present.
   * Useful for public endpoints where sending a stale token would cause 401.
   */
  skipAuth?: boolean;
}

async function apiFetch<T>(
  path: string,
  options: FetchOptions = {}
): Promise<T> {
  const { body, skipAuth = false, ...rest } = options;

  const buildHeaders = (token: string | null): HeadersInit => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token && !skipAuth) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  };

  const doRequest = (token: string | null): Promise<Response> =>
    fetch(`${BASE}${path}`, {
      ...rest,
      headers: {
        ...buildHeaders(token),
        ...(rest.headers ?? {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

  let token = getAccessToken();
  let res = await doRequest(token);

  // Auto-refresh on 401
  if (res.status === 401 && !skipAuth) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      setAccessToken(newToken);
      res = await doRequest(newToken);
    }
  }

  if (!res.ok) {
    let message = `${res.status} ${res.statusText}`;
    try {
      const err = (await res.json()) as Record<string, unknown>;
      if (typeof err.detail === "string") message = err.detail;
      else {
        const first = Object.values(err)[0];
        if (Array.isArray(first) && typeof first[0] === "string") {
          message = first[0];
        }
      }
    } catch {
      // ignore JSON parse failure
    }
    throw new Error(message);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

// ─── Auth endpoints ───────────────────────────────────────────────────────────

export const authApi = {
  login(payload: LoginPayload): Promise<TokenPair> {
    return apiFetch<TokenPair>("/api/v1/token/", {
      method: "POST",
      body: payload,
      skipAuth: true,
    });
  },

  register(payload: RegisterPayload): Promise<User> {
    return apiFetch<User>("/api/v1/auth/register/", {
      method: "POST",
      body: payload,
      skipAuth: true,
    });
  },

  me(): Promise<MeResponse> {
    return apiFetch<MeResponse>("/api/v1/auth/me/");
  },
};

// ─── Public feed ──────────────────────────────────────────────────────────────

export interface FeedParams {
  page?: number;
  search?: string;
  tag?: string;
  ordering?: string;
}

export const publicApi = {
  feed(params: FeedParams = {}): Promise<PaginatedResponse<PublicPost>> {
    const qs = new URLSearchParams();
    if (params.page) qs.set("page", String(params.page));
    if (params.search) qs.set("search", params.search);
    if (params.tag) qs.set("tag", params.tag);
    if (params.ordering) qs.set("ordering", params.ordering);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return apiFetch<PaginatedResponse<PublicPost>>(`/api/v1/public/posts/${query}`, {
      skipAuth: true,
    });
  },

  trending(): Promise<PublicPost[]> {
    return apiFetch<PublicPost[]>("/api/v1/public/posts/trending/", {
      skipAuth: true,
    });
  },

  postOg(slug: string): Promise<OgData> {
    return apiFetch<OgData>(`/api/v1/public/posts/${slug}/og/`, {
      skipAuth: true,
    });
  },

  profilePosts(
    handle: string,
    page = 1
  ): Promise<PaginatedResponse<PublicPost>> {
    return apiFetch<PaginatedResponse<PublicPost>>(
      `/api/v1/public/profiles/${handle}/posts/?page=${page}`,
      { skipAuth: true }
    );
  },

  health(): Promise<HealthResponse> {
    return apiFetch<HealthResponse>("/api/v1/health/", { skipAuth: true });
  },
};

// ─── My posts (authenticated) ─────────────────────────────────────────────────

export const postsApi = {
  list(page = 1): Promise<PaginatedResponse<MyPost>> {
    return apiFetch<PaginatedResponse<MyPost>>(`/api/v1/posts/?page=${page}`);
  },

  create(payload: CreatePostPayload): Promise<MyPost> {
    return apiFetch<MyPost>("/api/v1/posts/", {
      method: "POST",
      body: payload,
    });
  },

  update(id: number, payload: UpdatePostPayload): Promise<MyPost> {
    return apiFetch<MyPost>(`/api/v1/posts/${id}/`, {
      method: "PATCH",
      body: payload,
    });
  },

  delete(id: number): Promise<void> {
    return apiFetch<void>(`/api/v1/posts/${id}/`, { method: "DELETE" });
  },
};

// ─── Notifications ────────────────────────────────────────────────────────────

export const notificationsApi = {
  list(page = 1): Promise<NotificationListResponse> {
    return apiFetch<NotificationListResponse>(
      `/api/v1/notifications/?page=${page}`
    );
  },

  markAllRead(): Promise<void> {
    return apiFetch<void>("/api/v1/notifications/mark-read/", {
      method: "PATCH",
    });
  },
};

// ─── Users ────────────────────────────────────────────────────────────────────

export const usersApi = {
  publicProfile(id: number): Promise<PublicUser> {
    return apiFetch<PublicUser>(`/api/v1/users/${id}/`, { skipAuth: true });
  },

  stats(id: number): Promise<UserStats> {
    return apiFetch<UserStats>(`/api/v1/users/${id}/stats/`);
  },

  follow(id: number): Promise<{ detail: string }> {
    return apiFetch<{ detail: string }>(`/api/v1/users/${id}/follow/`, {
      method: "POST",
    });
  },

  unfollow(id: number): Promise<void> {
    return apiFetch<void>(`/api/v1/users/${id}/unfollow/`, {
      method: "DELETE",
    });
  },
};

// ─── Comments ─────────────────────────────────────────────────────────────────

export const commentsApi = {
  list(postId: number): Promise<PaginatedResponse<Comment>> {
    return apiFetch<PaginatedResponse<Comment>>(
      `/api/v1/posts/${postId}/comments/`
    );
  },

  create(postId: number, body: string): Promise<Comment> {
    return apiFetch<Comment>(`/api/v1/posts/${postId}/comments/`, {
      method: "POST",
      body: { body },
    });
  },
};
