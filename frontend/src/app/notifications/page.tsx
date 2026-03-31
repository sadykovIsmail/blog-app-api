"use client";

import { useCallback, useEffect, useState } from "react";
import { notificationsApi } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import type { Notification, NotificationType } from "@/lib/types";

// ─── Notification icon ────────────────────────────────────────────────────────

function NotifIcon({ type }: { type: NotificationType }) {
  const cfg: Record<NotificationType, { icon: string; color: string }> = {
    follow: { icon: "👤", color: "bg-blue-900/40" },
    comment: { icon: "💬", color: "bg-green-900/40" },
    reply: { icon: "↩️", color: "bg-teal-900/40" },
    new_post: { icon: "📝", color: "bg-purple-900/40" },
    citation_dead: { icon: "🔗", color: "bg-red-900/40" },
    citation_drift: { icon: "📊", color: "bg-orange-900/40" },
  };
  const { icon, color } = cfg[type] ?? { icon: "🔔", color: "bg-neutral-800" };

  return (
    <div
      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-lg ${color}`}
      aria-hidden="true"
    >
      {icon}
    </div>
  );
}

// ─── Notification labels ──────────────────────────────────────────────────────

function notifLabel(type: NotificationType): string {
  const map: Record<NotificationType, string> = {
    follow: "Someone followed you",
    comment: "New comment on your post",
    reply: "Reply to your comment",
    new_post: "New post from someone you follow",
    citation_dead: "A citation in your post may be dead",
    citation_drift: "Content drift detected in a citation",
  };
  return map[type] ?? "New notification";
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d}d ago`;
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

// ─── Notification item ────────────────────────────────────────────────────────

function NotifItem({ notification }: { notification: Notification }) {
  return (
    <div
      className={`flex items-start gap-3 rounded-xl border px-4 py-4 transition-colors ${
        notification.is_read
          ? "border-neutral-800 bg-neutral-900"
          : "border-brand-900/40 bg-brand-950/20"
      }`}
    >
      <NotifIcon type={notification.notification_type} />

      <div className="min-w-0 flex-1">
        <div className="mb-0.5 flex items-center gap-2">
          <p className="text-sm font-medium text-neutral-200">
            {notifLabel(notification.notification_type)}
          </p>
          {!notification.is_read && (
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-brand-400" />
          )}
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs text-neutral-600">
          <span>{timeAgo(notification.created_at)}</span>
          {notification.post && (
            <span className="text-neutral-500">Post #{notification.post}</span>
          )}
          {notification.comment && (
            <span className="text-neutral-500">
              Comment #{notification.comment}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Notifications page ───────────────────────────────────────────────────────

function NotificationsContent() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingRead, setMarkingRead] = useState(false);
  const [filter, setFilter] = useState<"all" | "unread">("all");

  const fetchNotifications = useCallback(async (page: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await notificationsApi.list(page);
      setNotifications(data.results);
      setUnreadCount(data.unread_count);
      setTotalCount(data.count);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load notifications."
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications(currentPage);
  }, [currentPage, fetchNotifications]);

  const handleMarkAllRead = async () => {
    setMarkingRead(true);
    try {
      await notificationsApi.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to mark as read.");
    } finally {
      setMarkingRead(false);
    }
  };

  const filtered =
    filter === "unread"
      ? notifications.filter((n) => !n.is_read)
      : notifications;

  const totalPages = Math.ceil(totalCount / 10);

  return (
    <div className="mx-auto max-w-2xl">
      {/* Header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-50">
            Notifications
          </h1>
          {unreadCount > 0 && (
            <p className="mt-1 text-sm text-neutral-500">
              {unreadCount} unread notification{unreadCount !== 1 ? "s" : ""}
            </p>
          )}
        </div>

        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            disabled={markingRead}
            className="inline-flex items-center gap-2 rounded-lg border border-neutral-700 px-4 py-2 text-sm font-medium text-neutral-300 hover:border-neutral-600 hover:text-neutral-100 transition-colors disabled:opacity-60"
          >
            {markingRead && (
              <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            )}
            Mark all as read
          </button>
        )}
      </div>

      {/* Filter tabs */}
      <div className="mb-6 flex gap-1 rounded-lg border border-neutral-800 bg-neutral-900 p-1">
        {(["all", "unread"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`flex-1 rounded-md py-1.5 text-sm font-medium transition-colors capitalize ${
              filter === f
                ? "bg-neutral-700 text-neutral-100"
                : "text-neutral-500 hover:text-neutral-300"
            }`}
          >
            {f}
            {f === "unread" && unreadCount > 0 && (
              <span className="ml-1.5 rounded-full bg-brand-600 px-1.5 py-0.5 text-xs text-white">
                {unreadCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="flex gap-3 rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-4"
            >
              <div className="h-9 w-9 shrink-0 animate-pulse rounded-full bg-neutral-800" />
              <div className="flex-1">
                <div className="mb-2 h-4 w-48 animate-pulse rounded bg-neutral-800" />
                <div className="h-3 w-20 animate-pulse rounded bg-neutral-800" />
              </div>
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-neutral-800 py-16 text-center">
          <div className="mb-4 text-4xl">🔔</div>
          <p className="font-medium text-neutral-400">
            {filter === "unread" ? "No unread notifications" : "No notifications yet"}
          </p>
          <p className="mt-1 text-sm text-neutral-600">
            {filter === "unread"
              ? "You're all caught up!"
              : "Activity from your posts and followers will appear here."}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3 animate-fade-in">
          {filtered.map((n) => (
            <NotifItem key={n.id} notification={n} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && !isLoading && (
        <div className="mt-8 flex items-center justify-between border-t border-neutral-800 pt-4">
          <p className="text-sm text-neutral-500">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="rounded-lg border border-neutral-700 px-3 py-1.5 text-sm text-neutral-400 hover:border-neutral-600 hover:text-neutral-100 disabled:opacity-40 transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="rounded-lg border border-neutral-700 px-3 py-1.5 text-sm text-neutral-400 hover:border-neutral-600 hover:text-neutral-100 disabled:opacity-40 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsContent />
    </ProtectedRoute>
  );
}
