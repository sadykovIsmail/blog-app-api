"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { postsApi, authApi } from "@/lib/api";
import ProtectedRoute from "@/components/ProtectedRoute";
import type { PostStatus, PostVisibility } from "@/lib/types";

// ─── Word count util ──────────────────────────────────────────────────────────

function wordCount(text: string): number {
  return text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
}

function readingTime(words: number): number {
  return Math.max(1, Math.round(words / 200));
}

// ─── New post form ────────────────────────────────────────────────────────────

function NewPostContent() {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<PostStatus>("DRAFT");
  const [visibility, setVisibility] = useState<PostVisibility>("PUBLIC");
  const [authorId, setAuthorId] = useState<number | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  // We need an author id for post creation.
  // The /auth/me/ returns user info; the author is the AuthorModel (not the user).
  // We call /auth/profile/ which gives id — we use the user id as a best-effort fallback.
  useEffect(() => {
    const fetchAuthorId = async () => {
      try {
        const me = await authApi.me();
        setAuthorId(me.id);
      } catch {
        // will fail at submit time
      }
    };
    fetchAuthorId();
  }, []);

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    if (!title.trim()) errors.title = "Title is required.";
    else if (title.trim().length < 3) errors.title = "Title must be at least 3 characters.";
    if (!content.trim()) errors.content = "Content is required.";
    else if (status === "PUBLISHED" && content.trim().length < 50)
      errors.content = "Published posts must have at least 50 characters of content.";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!validate()) return;
    if (!authorId) {
      setError("Could not determine your author profile. Please refresh and try again.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const post = await postsApi.create({
        title: title.trim(),
        content: content.trim(),
        status,
        visibility,
        author: authorId,
      });
      router.push(
        status === "PUBLISHED" ? `/posts/${post.slug}` : "/dashboard"
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create post.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const words = wordCount(content);
  const rt = readingTime(words);

  return (
    <div className="mx-auto max-w-3xl">
      {/* Header */}
      <div className="mb-8 flex items-center gap-4">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
              clipRule="evenodd"
            />
          </svg>
          Dashboard
        </Link>
        <span className="text-neutral-700">/</span>
        <h1 className="text-xl font-semibold text-neutral-100">New Post</h1>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mb-6 flex items-start gap-2 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
          <svg
            width="16"
            height="16"
            viewBox="0 0 20 20"
            fill="currentColor"
            className="mt-0.5 shrink-0"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        {/* Title */}
        <div>
          <label
            htmlFor="title"
            className="mb-2 block text-sm font-medium text-neutral-300"
          >
            Title <span className="text-red-400">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isSubmitting}
            placeholder="Your post title…"
            className={`w-full rounded-lg border bg-neutral-900 px-4 py-3 text-lg text-neutral-100 placeholder-neutral-600 transition-colors focus:outline-none focus:ring-1 disabled:opacity-60 ${
              fieldErrors.title
                ? "border-red-600 focus:border-red-500 focus:ring-red-500/30"
                : "border-neutral-800 focus:border-brand-500 focus:ring-brand-500/30"
            }`}
          />
          {fieldErrors.title && (
            <p className="mt-1 text-xs text-red-400">{fieldErrors.title}</p>
          )}
          {title && (
            <p className="mt-1 text-xs text-neutral-600">
              {title.length}/200 characters
            </p>
          )}
        </div>

        {/* Content */}
        <div>
          <div className="mb-2 flex items-center justify-between">
            <label
              htmlFor="content"
              className="text-sm font-medium text-neutral-300"
            >
              Content <span className="text-red-400">*</span>
            </label>
            <span className="text-xs text-neutral-600">
              {words} words · {rt} min read
            </span>
          </div>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            disabled={isSubmitting}
            rows={18}
            placeholder="Write your post here. Markdown is supported in the display."
            className={`w-full resize-y rounded-lg border bg-neutral-900 px-4 py-3 font-mono text-sm leading-relaxed text-neutral-100 placeholder-neutral-600 transition-colors focus:outline-none focus:ring-1 disabled:opacity-60 ${
              fieldErrors.content
                ? "border-red-600 focus:border-red-500 focus:ring-red-500/30"
                : "border-neutral-800 focus:border-brand-500 focus:ring-brand-500/30"
            }`}
          />
          {fieldErrors.content && (
            <p className="mt-1 text-xs text-red-400">{fieldErrors.content}</p>
          )}
          <p className="mt-1 text-xs text-neutral-600">
            {content.length}/50000 characters
          </p>
        </div>

        {/* Settings row */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {/* Status */}
          <div>
            <label
              htmlFor="status"
              className="mb-2 block text-sm font-medium text-neutral-300"
            >
              Status
            </label>
            <select
              id="status"
              value={status}
              onChange={(e) => setStatus(e.target.value as PostStatus)}
              disabled={isSubmitting}
              className="w-full rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-2.5 text-sm text-neutral-100 transition-colors focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30 disabled:opacity-60"
            >
              <option value="DRAFT">Draft — save privately</option>
              <option value="PUBLISHED">Published — go live now</option>
            </select>
            {status === "PUBLISHED" && (
              <p className="mt-1 text-xs text-green-400">
                This post will be publicly visible immediately.
              </p>
            )}
          </div>

          {/* Visibility */}
          <div>
            <label
              htmlFor="visibility"
              className="mb-2 block text-sm font-medium text-neutral-300"
            >
              Visibility
            </label>
            <select
              id="visibility"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as PostVisibility)}
              disabled={isSubmitting}
              className="w-full rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-2.5 text-sm text-neutral-100 transition-colors focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30 disabled:opacity-60"
            >
              <option value="PUBLIC">Public — anyone can find it</option>
              <option value="UNLISTED">Unlisted — only via direct link</option>
            </select>
          </div>
        </div>

        {/* Preview card */}
        {title && content && (
          <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-neutral-600">
              Preview
            </p>
            <h3 className="text-lg font-semibold text-neutral-100">{title}</h3>
            <p className="mt-1 line-clamp-2 text-sm text-neutral-400">
              {content.slice(0, 200)}
              {content.length > 200 ? "…" : ""}
            </p>
            <div className="mt-2 flex gap-3 text-xs text-neutral-600">
              <span>{words} words</span>
              <span>{rt} min read</span>
              <span className="capitalize">{status.toLowerCase()}</span>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between border-t border-neutral-800 pt-4">
          <Link
            href="/dashboard"
            className="rounded-lg border border-neutral-700 px-4 py-2.5 text-sm font-medium text-neutral-400 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
          >
            Cancel
          </Link>

          <div className="flex items-center gap-3">
            {status === "PUBLISHED" && (
              <button
                type="button"
                onClick={() => {
                  setStatus("DRAFT");
                }}
                className="text-sm text-neutral-500 hover:text-neutral-300 transition-colors"
              >
                Save as draft instead
              </button>
            )}
            <button
              type="submit"
              disabled={isSubmitting || !title.trim() || !content.trim()}
              className="flex items-center gap-2 rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-500 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting && (
                <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              )}
              {isSubmitting
                ? status === "PUBLISHED"
                  ? "Publishing…"
                  : "Saving…"
                : status === "PUBLISHED"
                ? "Publish Post"
                : "Save Draft"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

export default function NewPostPage() {
  return (
    <ProtectedRoute>
      <NewPostContent />
    </ProtectedRoute>
  );
}
