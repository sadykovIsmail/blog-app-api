"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { publicApi, commentsApi } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import type { PublicPost, OgData, Comment } from "@/lib/types";

// ─── Loading skeleton ────────────────────────────────────────────────────────

function PostSkeleton() {
  return (
    <div className="mx-auto max-w-3xl animate-pulse">
      <div className="mb-6 h-4 w-24 rounded bg-neutral-800" />
      <div className="mb-4 h-10 w-full rounded bg-neutral-800" />
      <div className="mb-2 h-10 w-3/4 rounded bg-neutral-800" />
      <div className="mb-8 flex gap-4">
        <div className="h-4 w-20 rounded bg-neutral-800" />
        <div className="h-4 w-20 rounded bg-neutral-800" />
        <div className="h-4 w-20 rounded bg-neutral-800" />
      </div>
      <div className="flex flex-col gap-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="h-4 rounded bg-neutral-800"
            style={{ width: `${70 + Math.random() * 30}%` }}
          />
        ))}
      </div>
    </div>
  );
}

// ─── Comment item ─────────────────────────────────────────────────────────────

function CommentItem({ comment }: { comment: Comment }) {
  const timeAgo = (iso: string): string => {
    const diff = Date.now() - new Date(iso).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "just now";
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  };

  return (
    <div className="flex gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-neutral-800 text-sm font-semibold text-neutral-400">
        {comment.user.charAt(0).toUpperCase()}
      </div>
      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-center gap-2">
          <span className="text-sm font-medium text-neutral-200">
            {comment.user}
          </span>
          <span className="text-xs text-neutral-600">
            {timeAgo(comment.created_at)}
          </span>
        </div>
        <p className="text-sm leading-relaxed text-neutral-400">{comment.body}</p>
      </div>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function PostDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [post, setPost] = useState<PublicPost | null>(null);
  const [og, setOg] = useState<OgData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [comments, setComments] = useState<Comment[]>([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [commentBody, setCommentBody] = useState("");
  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [commentError, setCommentError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    let cancelled = false;

    const load = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch OG data (which has post metadata including content)
        const [ogData, feed] = await Promise.all([
          publicApi.postOg(slug),
          publicApi.feed({ search: undefined }),
        ]);
        if (cancelled) return;

        setOg(ogData);

        // Find full post in feed by slug via a targeted search or just use OG data
        // We fetch the public feed and filter — for a production app you'd have GET /public/posts/{slug}/
        // For now, fetch first page and look for it
        const match = feed.results.find((p) => p.slug === slug);
        if (match) {
          setPost(match);
        } else {
          // The post might be on a page beyond the first; fetch with search
          const byTitle = await publicApi.feed({ search: ogData.title });
          const found = byTitle.results.find((p) => p.slug === slug);
          if (found) setPost(found);
          else {
            // Build a synthetic post from OG data
            setPost({
              id: 0,
              title: ogData.title,
              slug,
              content: ogData.description,
              author_handle: ogData.author,
              status: "PUBLISHED",
              visibility: "PUBLIC",
              published_at: ogData.published_at,
              created_at: ogData.published_at ?? new Date().toISOString(),
              reaction_count: 0,
              tags: ogData.tags.map((t, i) => ({ id: i, name: t, slug: t })),
              reading_time_minutes: 1,
              pinned: false,
              view_count: 0,
              co_author_handles: [],
            });
          }
        }
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Post not found.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [slug]);

  // Load comments once we have the post id
  const loadComments = useCallback(async (postId: number) => {
    if (postId === 0) return;
    setCommentsLoading(true);
    try {
      const data = await commentsApi.list(postId);
      setComments(data.results);
    } catch {
      // non-critical
    } finally {
      setCommentsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (post && post.id !== 0) loadComments(post.id);
  }, [post, loadComments]);

  const handleCommentSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!post || post.id === 0 || !commentBody.trim()) return;
    setCommentSubmitting(true);
    setCommentError(null);
    try {
      const newComment = await commentsApi.create(post.id, commentBody.trim());
      setComments((prev) => [newComment, ...prev]);
      setCommentBody("");
    } catch (err) {
      setCommentError(
        err instanceof Error ? err.message : "Failed to post comment."
      );
    } finally {
      setCommentSubmitting(false);
    }
  };

  const formatDate = (iso: string | null): string => {
    if (!iso) return "";
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  if (isLoading) return <PostSkeleton />;

  if (error) {
    return (
      <div className="mx-auto max-w-3xl text-center py-20">
        <p className="mb-2 text-lg font-semibold text-neutral-300">
          Could not load post
        </p>
        <p className="mb-6 text-sm text-neutral-500">{error}</p>
        <button
          onClick={() => router.back()}
          className="rounded-lg border border-neutral-700 px-4 py-2 text-sm text-neutral-300 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (!post) return null;

  return (
    <div className="mx-auto max-w-3xl">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="mb-8 inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
      >
        <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
          <path
            fillRule="evenodd"
            d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
            clipRule="evenodd"
          />
        </svg>
        Back
      </button>

      {/* Header */}
      <header className="mb-8">
        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {post.tags.map((tag) => (
              <span
                key={tag.id}
                className="rounded-full bg-brand-900/40 px-2.5 py-0.5 text-xs font-medium text-brand-300"
              >
                #{tag.slug}
              </span>
            ))}
          </div>
        )}

        {/* Title */}
        <h1 className="mb-4 text-3xl font-bold leading-tight tracking-tight text-neutral-50 sm:text-4xl">
          {post.title}
        </h1>

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-500">
          {post.author_handle && (
            <Link
              href={`/profile/${post.author_handle}`}
              className="flex items-center gap-2 font-medium text-neutral-300 hover:text-brand-400 transition-colors"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-neutral-800 text-xs font-semibold">
                {post.author_handle.charAt(0).toUpperCase()}
              </div>
              @{post.author_handle}
            </Link>
          )}

          {post.published_at && (
            <span>{formatDate(post.published_at)}</span>
          )}

          <span>{post.reading_time_minutes} min read</span>

          <span className="flex items-center gap-1">
            <svg
              width="14"
              height="14"
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
            {post.reaction_count} reactions
          </span>

          <span className="flex items-center gap-1">
            <svg
              width="14"
              height="14"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path
                fillRule="evenodd"
                d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                clipRule="evenodd"
              />
            </svg>
            {post.view_count} views
          </span>
        </div>

        {/* Co-authors */}
        {post.co_author_handles.length > 0 && (
          <div className="mt-3 flex items-center gap-2 text-sm text-neutral-500">
            <span>Co-authors:</span>
            {post.co_author_handles.map((h) => (
              <Link
                key={h}
                href={`/profile/${h}`}
                className="text-neutral-400 hover:text-brand-400 transition-colors"
              >
                @{h}
              </Link>
            ))}
          </div>
        )}
      </header>

      {/* Divider */}
      <hr className="mb-8 border-neutral-800" />

      {/* Content */}
      <div className="article-prose mb-12 whitespace-pre-wrap">{post.content}</div>

      {/* ── Comments section ── */}
      <section className="border-t border-neutral-800 pt-10">
        <h2 className="mb-6 text-xl font-semibold text-neutral-100">
          Comments
          {comments.length > 0 && (
            <span className="ml-2 text-sm font-normal text-neutral-500">
              ({comments.length})
            </span>
          )}
        </h2>

        {/* Comment form */}
        {isAuthenticated ? (
          <form
            onSubmit={handleCommentSubmit}
            className="mb-8 flex flex-col gap-3"
          >
            <textarea
              value={commentBody}
              onChange={(e) => setCommentBody(e.target.value)}
              placeholder="Share your thoughts…"
              rows={3}
              disabled={commentSubmitting}
              className="w-full resize-none rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2.5 text-sm text-neutral-100 placeholder-neutral-600 transition-colors focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30 disabled:opacity-60"
            />
            {commentError && (
              <p className="text-xs text-red-400">{commentError}</p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={commentSubmitting || !commentBody.trim()}
                className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
              >
                {commentSubmitting && (
                  <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                )}
                Post Comment
              </button>
            </div>
          </form>
        ) : (
          <div className="mb-8 rounded-lg border border-neutral-800 bg-neutral-900 px-4 py-5 text-center">
            <p className="text-sm text-neutral-400">
              <Link
                href="/login"
                className="font-medium text-brand-400 hover:text-brand-300"
              >
                Sign in
              </Link>{" "}
              to join the conversation.
            </p>
          </div>
        )}

        {/* Comment list */}
        {commentsLoading ? (
          <div className="flex flex-col gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <div className="h-8 w-8 shrink-0 animate-pulse rounded-full bg-neutral-800" />
                <div className="flex-1">
                  <div className="mb-2 h-3 w-24 animate-pulse rounded bg-neutral-800" />
                  <div className="h-4 w-full animate-pulse rounded bg-neutral-800" />
                </div>
              </div>
            ))}
          </div>
        ) : comments.length === 0 ? (
          <p className="text-sm text-neutral-600">
            No comments yet. Be the first!
          </p>
        ) : (
          <div className="flex flex-col gap-6">
            {comments.map((c) => (
              <CommentItem key={c.id} comment={c} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
