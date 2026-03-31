"use client";

import PostCard from "./PostCard";
import type { PublicPost } from "@/lib/types";

interface PostListProps {
  posts: PublicPost[];
  isLoading: boolean;
  totalCount: number;
  currentPage: number;
  onPageChange: (page: number) => void;
  pageSize?: number;
}

function PostSkeleton() {
  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
      <div className="mb-3 h-5 w-3/4 animate-pulse rounded bg-neutral-800" />
      <div className="mb-2 h-4 w-full animate-pulse rounded bg-neutral-800" />
      <div className="mb-4 h-4 w-2/3 animate-pulse rounded bg-neutral-800" />
      <div className="flex gap-2">
        <div className="h-5 w-16 animate-pulse rounded-full bg-neutral-800" />
        <div className="h-5 w-12 animate-pulse rounded-full bg-neutral-800" />
      </div>
      <div className="mt-4 flex gap-3">
        <div className="h-3.5 w-20 animate-pulse rounded bg-neutral-800" />
        <div className="h-3.5 w-16 animate-pulse rounded bg-neutral-800" />
      </div>
    </div>
  );
}

export default function PostList({
  posts,
  isLoading,
  totalCount,
  currentPage,
  onPageChange,
  pageSize = 10,
}: PostListProps) {
  const totalPages = Math.ceil(totalCount / pageSize);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <PostSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!isLoading && posts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-neutral-800 bg-neutral-900 py-16 text-center">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          className="mb-4 text-neutral-600"
        >
          <path
            d="M9 12h6M9 16h4M7 4H4a2 2 0 00-2 2v14a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2h-3"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <path
            d="M9 4a3 3 0 016 0"
            stroke="currentColor"
            strokeWidth="1.5"
          />
        </svg>
        <p className="text-lg font-medium text-neutral-400">No posts found</p>
        <p className="mt-1 text-sm text-neutral-600">
          Try adjusting your search or filters.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 animate-fade-in">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-neutral-800 pt-4">
          <p className="text-sm text-neutral-500">
            Showing {(currentPage - 1) * pageSize + 1}–
            {Math.min(currentPage * pageSize, totalCount)} of {totalCount}
          </p>

          <div className="flex items-center gap-1">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="flex h-8 w-8 items-center justify-center rounded-md border border-neutral-700 text-neutral-400 transition-colors hover:border-neutral-600 hover:text-neutral-100 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </button>

            {/* Page numbers — show at most 5 */}
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter(
                (p) =>
                  p === 1 ||
                  p === totalPages ||
                  Math.abs(p - currentPage) <= 1
              )
              .reduce<(number | "…")[]>((acc, p, idx, arr) => {
                if (idx > 0 && p - (arr[idx - 1] as number) > 1) {
                  acc.push("…");
                }
                acc.push(p);
                return acc;
              }, [])
              .map((p, idx) =>
                p === "…" ? (
                  <span
                    key={`ellipsis-${idx}`}
                    className="flex h-8 w-8 items-center justify-center text-sm text-neutral-600"
                  >
                    …
                  </span>
                ) : (
                  <button
                    key={p}
                    onClick={() => onPageChange(p as number)}
                    className={`flex h-8 w-8 items-center justify-center rounded-md text-sm font-medium transition-colors ${
                      p === currentPage
                        ? "bg-brand-600 text-white"
                        : "border border-neutral-700 text-neutral-400 hover:border-neutral-600 hover:text-neutral-100"
                    }`}
                  >
                    {p}
                  </button>
                )
              )}

            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="flex h-8 w-8 items-center justify-center rounded-md border border-neutral-700 text-neutral-400 transition-colors hover:border-neutral-600 hover:text-neutral-100 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
