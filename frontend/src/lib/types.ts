// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  handle?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

// ─── User ─────────────────────────────────────────────────────────────────────

export interface User {
  id: number;
  username: string;
  email: string;
  handle: string | null;
}

export interface PublicUser {
  id: number;
  username: string;
  handle: string | null;
  follower_count: number;
  following_count: number;
}

export interface UserStats {
  post_count: number;
  follower_count: number;
  following_count: number;
  total_reactions: number;
  total_views: number;
}

export interface MeResponse {
  id: number;
  username: string;
  email: string;
  handle: string | null;
  post_count?: number;
  follower_count?: number;
  following_count?: number;
}

// ─── Tags ─────────────────────────────────────────────────────────────────────

export interface Tag {
  id: number;
  name: string;
  slug: string;
}

// ─── Posts ────────────────────────────────────────────────────────────────────

export type PostStatus = "DRAFT" | "SCHEDULED" | "PUBLISHED" | "ARCHIVED";
export type PostVisibility = "PUBLIC" | "UNLISTED";

export interface PublicPost {
  id: number;
  title: string;
  slug: string;
  content: string;
  author_handle: string | null;
  status: PostStatus;
  visibility: PostVisibility;
  published_at: string | null;
  created_at: string;
  reaction_count: number;
  tags: Tag[];
  reading_time_minutes: number;
  pinned: boolean;
  view_count: number;
  co_author_handles: string[];
}

export interface MyPost {
  id: number;
  title: string;
  content: string;
  author: number;
  author_name: string;
  status: PostStatus;
  visibility: PostVisibility;
  slug: string;
  published_at: string | null;
  scheduled_for: string | null;
  created_at: string;
  updated_at: string;
  image: string | null;
  user: number;
  reading_time_minutes: number;
}

export interface CreatePostPayload {
  title: string;
  content: string;
  status: PostStatus;
  visibility: PostVisibility;
  author: number;
}

export interface UpdatePostPayload {
  title?: string;
  content?: string;
  status?: PostStatus;
  visibility?: PostVisibility;
  reason_for_change?: string;
}

// ─── OpenGraph ────────────────────────────────────────────────────────────────

export interface OgData {
  title: string;
  description: string;
  url: string;
  image: string | null;
  author: string | null;
  published_at: string | null;
  tags: string[];
}

// ─── Pagination ───────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ─── Notifications ────────────────────────────────────────────────────────────

export type NotificationType =
  | "follow"
  | "comment"
  | "reply"
  | "new_post"
  | "citation_dead"
  | "citation_drift";

export interface Notification {
  id: number;
  notification_type: NotificationType;
  actor: number | null;
  post: number | null;
  comment: number | null;
  is_read: boolean;
  created_at: string;
}

export interface NotificationListResponse extends PaginatedResponse<Notification> {
  unread_count: number;
}

// ─── Comments ─────────────────────────────────────────────────────────────────

export interface Comment {
  id: number;
  post: number;
  user: string;
  parent: number | null;
  body: string;
  created_at: string;
  updated_at: string;
}

// ─── Health ───────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  database: string;
  cache: string;
}

// ─── API Errors ───────────────────────────────────────────────────────────────

export interface ApiError {
  detail?: string;
  non_field_errors?: string[];
  [key: string]: string | string[] | undefined;
}

export function extractApiError(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  return "An unexpected error occurred.";
}
