import Link from "next/link";
import type { PublicPost } from "@/lib/types";

interface PostCardProps {
  post: PublicPost;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function excerpt(content: string, maxChars = 160): string {
  const plain = content.replace(/#+\s/g, "").replace(/\*+/g, "").trim();
  if (plain.length <= maxChars) return plain;
  return plain.slice(0, maxChars).trimEnd() + "…";
}

export default function PostCard({ post }: PostCardProps) {
  return (
    <article className="group relative flex flex-col gap-3 rounded-xl border border-neutral-800 bg-neutral-900 p-5 transition-all duration-200 hover:border-neutral-700 hover:bg-neutral-850">
      {/* Pinned badge */}
      {post.pinned && (
        <span className="inline-flex w-fit items-center gap-1 rounded-full bg-brand-900/60 px-2 py-0.5 text-xs font-medium text-brand-300">
          <svg
            width="10"
            height="10"
            viewBox="0 0 16 16"
            fill="currentColor"
          >
            <path d="M9.828.722a.5.5 0 01.354.146l4.95 4.95a.5.5 0 010 .707c-.48.48-1.072.588-1.503.588-.177 0-.335-.018-.46-.039l-3.134 3.134a5.927 5.927 0 01.16 1.013c.046.702-.032 1.687-.72 2.375a.5.5 0 01-.707 0l-2.829-2.828-3.182 3.182c-.195.195-1.219.902-1.414.707-.195-.195.512-1.22.707-1.414l3.182-3.182-2.828-2.829a.5.5 0 010-.707c.688-.688 1.673-.767 2.375-.72a5.922 5.922 0 011.013.16l3.134-3.133a2.772 2.772 0 01-.04-.461c0-.43.108-1.022.589-1.503a.5.5 0 01.353-.146z" />
          </svg>
          Pinned
        </span>
      )}

      {/* Title */}
      <Link href={`/posts/${post.slug}`} className="block">
        <h2 className="text-lg font-semibold leading-snug text-neutral-50 group-hover:text-brand-300 transition-colors line-clamp-2">
          {post.title}
        </h2>
      </Link>

      {/* Excerpt */}
      <p className="text-sm leading-relaxed text-neutral-400 line-clamp-3">
        {excerpt(post.content)}
      </p>

      {/* Tags */}
      {post.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {post.tags.map((tag) => (
            <span
              key={tag.id}
              className="rounded-full bg-neutral-800 px-2.5 py-0.5 text-xs font-medium text-neutral-300"
            >
              #{tag.slug}
            </span>
          ))}
        </div>
      )}

      {/* Meta row */}
      <div className="flex items-center gap-4 text-xs text-neutral-500">
        {post.author_handle && (
          <Link
            href={`/profile/${post.author_handle}`}
            className="font-medium text-neutral-400 hover:text-brand-400 transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            @{post.author_handle}
          </Link>
        )}

        <span>{formatDate(post.published_at ?? post.created_at)}</span>

        <span>{post.reading_time_minutes} min read</span>

        <div className="ml-auto flex items-center gap-3">
          {/* Reactions */}
          <span className="flex items-center gap-1">
            <svg
              width="13"
              height="13"
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

          {/* Views */}
          <span className="flex items-center gap-1">
            <svg
              width="13"
              height="13"
              viewBox="0 0 20 20"
              fill="currentColor"
              className="text-neutral-500"
            >
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path
                fillRule="evenodd"
                d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                clipRule="evenodd"
              />
            </svg>
            {post.view_count}
          </span>
        </div>
      </div>

      {/* Stretch link overlay */}
      <Link href={`/posts/${post.slug}`} className="absolute inset-0 rounded-xl" aria-hidden="true" tabIndex={-1} />
    </article>
  );
}
