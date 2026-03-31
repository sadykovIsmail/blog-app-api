"use client";

import { useCallback, useEffect, useState } from "react";
import { publicApi } from "@/lib/api";
import type { PublicPost } from "@/lib/types";
import PostList from "@/components/PostList";
import SearchBar from "@/components/SearchBar";
import Link from "next/link";

// ─── Trending Sidebar ─────────────────────────────────────────────────────────

function TrendingSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-1.5">
          <div className="h-4 w-full animate-pulse rounded bg-neutral-800" />
          <div className="h-3 w-2/3 animate-pulse rounded bg-neutral-800" />
        </div>
      ))}
    </div>
  );
}

function TrendingPost({ post, rank }: { post: PublicPost; rank: number }) {
  return (
    <Link
      href={`/posts/${post.slug}`}
      className="group flex gap-3 rounded-lg p-2 transition-colors hover:bg-neutral-800"
    >
      <span className="mt-0.5 min-w-[1.5rem] text-center text-sm font-bold text-neutral-600">
        {rank}
      </span>
      <div className="min-w-0">
        <p className="line-clamp-2 text-sm font-medium text-neutral-300 group-hover:text-brand-300 transition-colors">
          {post.title}
        </p>
        <div className="mt-1 flex items-center gap-2 text-xs text-neutral-600">
          {post.author_handle && <span>@{post.author_handle}</span>}
          <span className="flex items-center gap-0.5">
            <svg
              width="10"
              height="10"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="text-rose-400"
            >
              <path
                fillRule="evenodd"
                d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                clipRule="evenodd"
              />
            </svg>
            {post.reaction_count}
          </span>
        </div>
      </div>
    </Link>
  );
}

// ─── Tag filter chips ─────────────────────────────────────────────────────────

const POPULAR_TAGS = [
  "javascript",
  "python",
  "webdev",
  "ai",
  "career",
  "tutorial",
  "ux",
  "devops",
];

// ─── Main page ────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [posts, setPosts] = useState<PublicPost[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState("");

  const [trending, setTrending] = useState<PublicPost[]>([]);
  const [trendingLoading, setTrendingLoading] = useState(true);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setCurrentPage(1);
    }, 350);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTag]);

  // Fetch feed
  useEffect(() => {
    let cancelled = false;
    const fetchFeed = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await publicApi.feed({
          page: currentPage,
          search: search || undefined,
          tag: activeTag || undefined,
          ordering: "-published_at",
        });
        if (!cancelled) {
          setPosts(data.results);
          setTotalCount(data.count);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load posts.");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    fetchFeed();
    return () => {
      cancelled = true;
    };
  }, [currentPage, search, activeTag]);

  // Fetch trending
  useEffect(() => {
    let cancelled = false;
    const fetchTrending = async () => {
      setTrendingLoading(true);
      try {
        const data = await publicApi.trending();
        if (!cancelled) setTrending(data.slice(0, 6));
      } catch {
        // silently fail for trending sidebar
      } finally {
        if (!cancelled) setTrendingLoading(false);
      }
    };
    fetchTrending();
    return () => {
      cancelled = true;
    };
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  return (
    <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:gap-10">
      {/* ── Main feed ── */}
      <div className="min-w-0 flex-1">
        {/* Hero */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-neutral-50 sm:text-4xl">
            Latest Posts
          </h1>
          <p className="mt-2 text-neutral-400">
            Discover ideas, tutorials, and stories from writers worldwide.
          </p>
        </div>

        {/* Filters row */}
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex-1">
            <SearchBar
              value={searchInput}
              onChange={setSearchInput}
              placeholder="Search posts by title or content…"
            />
          </div>
        </div>

        {/* Tag chips */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTag(null)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              activeTag === null
                ? "bg-brand-600 text-white"
                : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-neutral-100"
            }`}
          >
            All
          </button>
          {POPULAR_TAGS.map((tag) => (
            <button
              key={tag}
              onClick={() => setActiveTag(activeTag === tag ? null : tag)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                activeTag === tag
                  ? "bg-brand-600 text-white"
                  : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700 hover:text-neutral-100"
              }`}
            >
              #{tag}
            </button>
          ))}
        </div>

        {/* Active filters summary */}
        {(search || activeTag) && (
          <div className="mb-4 flex items-center gap-2 text-sm text-neutral-500">
            <span>Filtering by:</span>
            {search && (
              <span className="rounded-full bg-neutral-800 px-2 py-0.5 text-neutral-300">
                &quot;{search}&quot;
              </span>
            )}
            {activeTag && (
              <span className="rounded-full bg-neutral-800 px-2 py-0.5 text-neutral-300">
                #{activeTag}
              </span>
            )}
            <button
              onClick={() => {
                setSearchInput("");
                setSearch("");
                setActiveTag(null);
              }}
              className="ml-1 text-xs text-neutral-600 underline hover:text-neutral-400"
            >
              Clear all
            </button>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-4 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Post list */}
        <PostList
          posts={posts}
          isLoading={isLoading}
          totalCount={totalCount}
          currentPage={currentPage}
          onPageChange={handlePageChange}
        />
      </div>

      {/* ── Sidebar ── */}
      <aside className="w-full shrink-0 lg:w-72 xl:w-80">
        <div className="sticky top-20 flex flex-col gap-6">
          {/* Trending */}
          <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
            <div className="mb-4 flex items-center gap-2">
              <svg
                width="16"
                height="16"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="text-orange-400"
              >
                <path
                  fillRule="evenodd"
                  d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z"
                  clipRule="evenodd"
                />
              </svg>
              <h2 className="text-sm font-semibold text-neutral-200">
                Trending
              </h2>
            </div>
            {trendingLoading ? (
              <TrendingSkeleton />
            ) : trending.length === 0 ? (
              <p className="text-sm text-neutral-600">No trending posts yet.</p>
            ) : (
              <div className="flex flex-col gap-1">
                {trending.map((post, i) => (
                  <TrendingPost key={post.id} post={post} rank={i + 1} />
                ))}
              </div>
            )}
          </div>

          {/* Write CTA */}
          <div className="rounded-xl border border-brand-900/40 bg-gradient-to-br from-brand-950/60 to-neutral-900 p-5 text-center">
            <h3 className="mb-1 font-semibold text-neutral-100">
              Share your ideas
            </h3>
            <p className="mb-4 text-sm text-neutral-400">
              Join thousands of writers and publish your first post today.
            </p>
            <Link
              href="/register"
              className="inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </aside>
    </div>
  );
}
