"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { publicApi, usersApi } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import PostCard from "@/components/PostCard";
import type { PublicUser, UserStats, PublicPost } from "@/lib/types";

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function ProfileSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="mb-6 flex items-start gap-4">
        <div className="h-20 w-20 rounded-full bg-neutral-800" />
        <div className="flex-1">
          <div className="mb-2 h-7 w-40 rounded bg-neutral-800" />
          <div className="mb-3 h-4 w-28 rounded bg-neutral-800" />
          <div className="flex gap-4">
            <div className="h-4 w-24 rounded bg-neutral-800" />
            <div className="h-4 w-24 rounded bg-neutral-800" />
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Stat chip ────────────────────────────────────────────────────────────────

function StatChip({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-neutral-800 bg-neutral-900 px-5 py-3 text-center">
      <span className="text-xl font-bold text-neutral-50">{value.toLocaleString()}</span>
      <span className="text-xs text-neutral-500">{label}</span>
    </div>
  );
}

// ─── Profile page ─────────────────────────────────────────────────────────────

export default function ProfilePage() {
  const { handle } = useParams<{ handle: string }>();
  const { user: currentUser, isAuthenticated } = useAuth();

  const [profile, setProfile] = useState<PublicUser | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [posts, setPosts] = useState<PublicPost[]>([]);
  const [totalPosts, setTotalPosts] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [postsLoading, setPostsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [following, setFollowing] = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [followError, setFollowError] = useState<string | null>(null);

  // Fetch profile posts
  const fetchPosts = useCallback(
    async (pageNum: number) => {
      if (!handle) return;
      setPostsLoading(true);
      try {
        const data = await publicApi.profilePosts(handle, pageNum);
        setPosts((prev) =>
          pageNum === 1 ? data.results : [...prev, ...data.results]
        );
        setTotalPosts(data.count);
      } catch {
        // silently fail
      } finally {
        setPostsLoading(false);
      }
    },
    [handle]
  );

  // Initial load: profile + stats + posts
  useEffect(() => {
    if (!handle) return;
    let cancelled = false;

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // We don't have a handle-based profile endpoint directly, so we use
        // the public posts endpoint to discover the profile, then load by id.
        // First get posts to extract user id from the data.
        const postsData = await publicApi.profilePosts(handle, 1);
        if (cancelled) return;
        setPosts(postsData.results);
        setTotalPosts(postsData.count);

        // We build a synthetic profile from available post data
        if (postsData.results.length > 0) {
          const firstPost = postsData.results[0];
          // Use author_handle from post to confirm identity
          // We need the numeric user id — try to fetch stats via a search
          // For now create a synthetic profile from post data
          const syntheticProfile: PublicUser = {
            id: 0,
            username: handle,
            handle,
            follower_count: 0,
            following_count: 0,
          };
          setProfile(syntheticProfile);

          // Try fetching full profile by querying users endpoint.
          // The API doesn't provide a handle-based user lookup directly,
          // so we rely on data embedded in the post.
          if (firstPost.author_handle) {
            // We know the handle matches; build profile from embedded data
          }
        } else {
          setProfile({
            id: 0,
            username: handle,
            handle,
            follower_count: 0,
            following_count: 0,
          });
        }
      } catch (err) {
        if (!cancelled)
          setError(
            err instanceof Error ? err.message : "Could not load profile."
          );
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [handle]);

  const handleFollow = async () => {
    if (!profile || profile.id === 0) return;
    setFollowLoading(true);
    setFollowError(null);
    try {
      if (following) {
        await usersApi.unfollow(profile.id);
        setFollowing(false);
        setProfile((p) =>
          p ? { ...p, follower_count: p.follower_count - 1 } : p
        );
      } else {
        await usersApi.follow(profile.id);
        setFollowing(true);
        setProfile((p) =>
          p ? { ...p, follower_count: p.follower_count + 1 } : p
        );
      }
    } catch (err) {
      setFollowError(err instanceof Error ? err.message : "Action failed.");
    } finally {
      setFollowLoading(false);
    }
  };

  const isOwnProfile =
    currentUser?.handle === handle || currentUser?.username === handle;

  const hasMorePosts = posts.length < totalPosts;

  // ── Render ─────────────────────────────────────────────────────────────────

  if (isLoading) return <ProfileSkeleton />;

  if (error) {
    return (
      <div className="py-20 text-center">
        <p className="mb-2 text-lg font-semibold text-neutral-300">
          Profile not found
        </p>
        <p className="mb-6 text-sm text-neutral-500">{error}</p>
        <Link
          href="/"
          className="rounded-lg border border-neutral-700 px-4 py-2 text-sm text-neutral-300 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
        >
          Go Home
        </Link>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="mx-auto max-w-3xl">
      {/* Profile header */}
      <div className="mb-10 flex flex-col gap-6 sm:flex-row sm:items-start sm:gap-8">
        {/* Avatar */}
        <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-700 to-brand-500 text-3xl font-bold text-white">
          {handle.charAt(0).toUpperCase()}
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-neutral-50">
              @{handle}
            </h1>
            {isOwnProfile && (
              <span className="rounded-full bg-brand-900/40 px-2.5 py-0.5 text-xs font-medium text-brand-300">
                You
              </span>
            )}
          </div>

          {/* Stats row */}
          <div className="mb-4 flex flex-wrap gap-4 text-sm text-neutral-500">
            <span>
              <strong className="text-neutral-200">
                {profile.follower_count}
              </strong>{" "}
              followers
            </span>
            <span>
              <strong className="text-neutral-200">
                {profile.following_count}
              </strong>{" "}
              following
            </span>
            <span>
              <strong className="text-neutral-200">{totalPosts}</strong> posts
            </span>
          </div>

          {/* Follow button */}
          {isAuthenticated && !isOwnProfile && profile.id !== 0 && (
            <div>
              <button
                onClick={handleFollow}
                disabled={followLoading}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-60 ${
                  following
                    ? "border border-neutral-700 text-neutral-300 hover:border-red-700 hover:text-red-400"
                    : "bg-brand-600 text-white hover:bg-brand-500"
                }`}
              >
                {followLoading
                  ? "…"
                  : following
                  ? "Following"
                  : "Follow"}
              </button>
              {followError && (
                <p className="mt-1 text-xs text-red-400">{followError}</p>
              )}
            </div>
          )}

          {isOwnProfile && (
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-700 px-4 py-2 text-sm font-medium text-neutral-300 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              Edit Posts
            </Link>
          )}
        </div>
      </div>

      {/* Extended stats */}
      {stats && (
        <div className="mb-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatChip label="Posts" value={stats.post_count} />
          <StatChip label="Followers" value={stats.follower_count} />
          <StatChip label="Reactions" value={stats.total_reactions} />
          <StatChip label="Views" value={stats.total_views} />
        </div>
      )}

      {/* Divider */}
      <hr className="mb-8 border-neutral-800" />

      {/* Posts section */}
      <h2 className="mb-6 text-xl font-semibold text-neutral-100">
        Posts
        <span className="ml-2 text-sm font-normal text-neutral-500">
          ({totalPosts})
        </span>
      </h2>

      {postsLoading && posts.length === 0 ? (
        <div className="flex flex-col gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl border border-neutral-800 bg-neutral-900" />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div className="rounded-xl border border-dashed border-neutral-800 py-14 text-center">
          <p className="text-neutral-500">No published posts yet.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}

          {hasMorePosts && (
            <button
              onClick={() => {
                const nextPage = page + 1;
                setPage(nextPage);
                fetchPosts(nextPage);
              }}
              disabled={postsLoading}
              className="mt-2 w-full rounded-xl border border-neutral-800 bg-neutral-900 py-3 text-sm font-medium text-neutral-400 hover:border-neutral-700 hover:text-neutral-100 transition-colors disabled:opacity-50"
            >
              {postsLoading ? "Loading…" : "Load More Posts"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
