'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Heart, Bookmark, MessageCircle, Clock, Tag } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Post } from '@/lib/types';

interface Props {
  post: Post;
  onLike?: () => void;
  onBookmark?: () => void;
}

export default function PostCard({ post, onLike, onBookmark }: Props) {
  return (
    <article className="group rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md">
      {post.image && (
        <div className="relative h-48 w-full overflow-hidden rounded-t-2xl">
          <Image
            src={post.image}
            alt={post.title}
            fill
            className="object-cover transition group-hover:scale-105"
          />
        </div>
      )}
      <div className="p-5">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          {post.category_name && (
            <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700">
              {post.category_name}
            </span>
          )}
          {post.tags.slice(0, 3).map((tag) => (
            <span
              key={tag.id}
              className="flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
            >
              <Tag className="h-3 w-3" />
              {tag.name}
            </span>
          ))}
        </div>

        <Link href={`/posts/${post.slug}`}>
          <h2 className="mb-2 line-clamp-2 text-lg font-semibold text-gray-900 hover:text-blue-600">
            {post.title}
          </h2>
        </Link>

        <p className="mb-4 line-clamp-3 text-sm text-gray-600">
          {post.content.replace(/<[^>]*>/g, '').substring(0, 200)}
        </p>

        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-3">
            <span className="font-medium text-gray-700">{post.author_name}</span>
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {post.reading_time} min read
            </span>
            <span>{formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onLike}
              className={`flex items-center gap-1 transition ${
                post.is_liked ? 'text-red-500' : 'hover:text-red-500'
              }`}
            >
              <Heart className={`h-4 w-4 ${post.is_liked ? 'fill-current' : ''}`} />
              {post.likes_count}
            </button>
            <button
              onClick={onBookmark}
              className={`flex items-center gap-1 transition ${
                post.is_bookmarked ? 'text-yellow-500' : 'hover:text-yellow-500'
              }`}
            >
              <Bookmark className={`h-4 w-4 ${post.is_bookmarked ? 'fill-current' : ''}`} />
            </button>
            <Link
              href={`/posts/${post.slug}#comments`}
              className="flex items-center gap-1 hover:text-blue-500"
            >
              <MessageCircle className="h-4 w-4" />
              {post.comments_count}
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
}
