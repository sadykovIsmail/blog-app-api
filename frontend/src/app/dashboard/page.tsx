"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { postsApi } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import type { MyPost, PostStatus } from "@/lib/types";

// ─── Status badge ─────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: PostStatus }) {
  const cfg: Record<PostStatus, { label: string; className: string }> = {
    PUBLISHED: {
      label: "Published",
      className: "bg-green-900/50 text-green-300 border-green-800/50",
    },
    DRAFT: {
      label: "Draft",
      className: "bg-neutral-800 text-neutral-400 border-neutral-700",
    },
    SCHEDULED: {
      label: "Scheduled",
      className: "bg-yellow-900/50 text-yellow-300 border-yellow-800/50",
    },
    ARCHIVED: {
      label: "Archived",
      className: "bg-neutral-800/50 text-neutral-500 border-neutral-700/50",
    },
  };
  const { label, className } = cfg[status] ?? cfg.DRAFT;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  );
}

// ─── Post row ─────────────────────────────────────────────────────────────────

interface PostRowProps {
  post: MyPost;
  onDelete: (id: number) => void;
  deleting: boolean;
}

function PostRow({ post, onDelete, deleting }: PostRowProps) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

  return (
    <div className="group flex flex-col gap-3 rounded-xl border border-neutral-800 bg-neutral-900 p-4 transition-colors hover:border-neutral-700 sm:flex-row sm:items-center sm:gap-4">
      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="mb-1 flex flex-wrap items-center gap-2">
          <StatusBadge status={post.status} />
          {post.visibility === "UNLISTED" && (
            <span className="inline-flex items-center gap-1 rounded-full border border-neutral-700 bg-neutral-800 px-2 py-0.5 text-xs text-neutral-500">
              <svg width="10" height="10" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                  clipRule="evenodd"
                />
              </svg>
              Unlisted
            </span>
          )}
        </div>
        <h3 className="mb-0.5 line-clamp-1 font-medium text-neutral-100">
          {post.title}
        </h3>
        <p className="text-xs text-neutral-600">
          {post.published_at
            ? `Published ${formatDate(post.published_at)}`
            : `Created ${formatDate(post.created_at)}`}
          {" · "}
          {post.reading_time_minutes} min read
        </p>
      </div>

      {/* Actions */}
      <div className="flex shrink-0 items-center gap-2">
        {post.status === "PUBLISHED" && (
          <Link
            href={`/posts/${post.slug}`}
            className="rounded-lg border border-neutral-700 px-3 py-1.5 text-xs font-medium text-neutral-400 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
          >
            View
          </Link>
        )}

        {!confirmDelete ? (
          <button
            onClick={() => setConfirmDelete(true)}
            disabled={deleting}
            className="rounded-lg border border-red-900/60 px-3 py-1.5 text-xs font-medium text-red-400 hover:border-red-700 hover:bg-red-950/30 transition-colors disabled:opacity-50"
          >
            Delete
          </button>
        ) : (
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-neutral-500">Sure?</span>
            <button
              onClick={() => {
                setConfirmDelete(false);
                onDelete(post.id);
              }}
              disabled={deleting}
              className="rounded-lg bg-red-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              {deleting ? "Deleting…" : "Yes"}
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="rounded-lg border border-neutral-700 px-3 py-1.5 text-xs font-medium text-neutral-400 hover:text-neutral-100 transition-colors"
            >
              No
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Dashboard page ───────────────────────────────────────────────────────────

function DashboardContent() {
  const { user } = useAuth();
  const [posts, setPosts] = useState<MyPost[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const [statusFilter, setStatusFilter] = useState<PostStatus | "ALL">("ALL");

  const fetchPosts = useCallback(async (page: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await postsApi.list(page);
      setPosts(data.results);
      setTotalCount(data.count);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load posts.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPosts(currentPage);
  }, [currentPage, fetchPosts]);

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await postsApi.delete(id);
      setPosts((prev) => prev.filter((p) => p.id !== id));
      setTotalCount((c) => c - 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed.");
    } finally {
      setDeletingId(null);
    }
  };

  const filteredPosts =
    statusFilter === "ALL"
      ? posts
      : posts.filter((p) => p.status === statusFilter);

  const totalPages = Math.ceil(totalCount / 10);

  // ── Stats row ──────────────────────────────────────────────────────────────
  const published = posts.filter((p) => p.status === "PUBLISHED").length;
  const drafts = posts.filter((p) => p.status === "DRAFT").length;

  return (
    <div>
      {/* Page header */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-50">
            Dashboard
          </h1>
          <p className="mt-1 text-neutral-500">
            Welcome back
            {user?.handle ? `, @${user.handle}` : user?.username ? `, ${user.username}` : ""}!
          </p>
        </div>
        <Link
          href="/dashboard/new"
          className="inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-500 transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
              clipRule="evenodd"
            />
          </svg>
          New Post
        </Link>
      </div>

      {/* Quick stats */}
      {!isLoading && posts.length > 0 && (
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: "Total Posts", value: totalCount },
            { label: "Published", value: published },
            { label: "Drafts", value: drafts },
            {
              label: "Scheduled",
              value: posts.filter((p) => p.status === "SCHEDULED").length,
            },
          ].map(({ label, value }) => (
            <div
              key={label}
              className="rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-4"
            >
              <p className="text-2xl font-bold text-neutral-50">{value}</p>
              <p className="mt-0.5 text-xs text-neutral-500">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Filter tabs */}
      <div className="mb-5 flex gap-1 rounded-lg border border-neutral-800 bg-neutral-900 p-1">
        {(["ALL", "PUBLISHED", "DRAFT", "SCHEDULED", "ARCHIVED"] as const).map(
          (s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-neutral-700 text-neutral-100"
                  : "text-neutral-500 hover:text-neutral-300"
              }`}
            >
              {s === "ALL" ? "All" : s.charAt(0) + s.slice(1).toLowerCase()}
            </button>
          )
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Posts list */}
      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="h-20 animate-pulse rounded-xl border border-neutral-800 bg-neutral-900"
            />
          ))}
        </div>
      ) : filteredPosts.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-neutral-800 py-16 text-center">
          <svg
            width="40"
            height="40"
            viewBox="0 0 24 24"
            fill="none"
            className="mb-4 text-neutral-700"
          >
            <path
              d="M9 12h6M9 16h4M7 4H4a2 2 0 00-2 2v14a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2h-3M9 4a3 3 0 016 0"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
          <p className="font-medium text-neutral-400">No posts yet</p>
          <p className="mt-1 text-sm text-neutral-600">
            Create your first post to get started.
          </p>
          <Link
            href="/dashboard/new"
            className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 transition-colors"
          >
            Write a Post
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {filteredPosts.map((post) => (
            <PostRow
              key={post.id}
              post={post}
              onDelete={handleDelete}
              deleting={deletingId === post.id}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <p className="text-sm text-neutral-500">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1 || isLoading}
              className="rounded-lg border border-neutral-700 px-3 py-1.5 text-sm text-neutral-400 hover:border-neutral-600 hover:text-neutral-100 disabled:opacity-40 transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() =>
                setCurrentPage((p) => Math.min(totalPages, p + 1))
              }
              disabled={currentPage === totalPages || isLoading}
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

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
