'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { publicApi } from '@/lib/api';
import { Post, Comment } from '@/lib/types';
import { useAuth } from '@/contexts/AuthContext';
import CommentSection from '@/components/CommentSection';
import { formatDistanceToNow } from 'date-fns';
import { Heart, Bookmark, Clock, Tag, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';

export default function PostDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([publicApi.getPost(slug), publicApi.getComments(slug)])
      .then(([postRes, commentsRes]) => {
        setPost(postRes.data);
        setComments(commentsRes.data);
      })
      .catch(() => toast.error('Post not found'))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleLike = async () => {
    if (!isAuthenticated) { toast('Please log in'); return; }
    if (!post) return;
    try {
      const res = await publicApi.likePost(slug);
      setPost((p) => p ? { ...p, is_liked: res.data.liked, likes_count: res.data.likes_count } : p);
    } catch { toast.error('Failed'); }
  };

  const handleBookmark = async () => {
    if (!isAuthenticated) { toast('Please log in'); return; }
    if (!post) return;
    try {
      const res = await publicApi.bookmarkPost(slug);
      setPost((p) => p ? { ...p, is_bookmarked: res.data.bookmarked } : p);
      toast.success(res.data.bookmarked ? 'Bookmarked!' : 'Removed from bookmarks');
    } catch { toast.error('Failed'); }
  };

  const handleAddComment = async (content: string, parentId?: number) => {
    try {
      const res = await publicApi.addComment(slug, { content, parent: parentId });
      if (!parentId) {
        setComments((prev) => [...prev, res.data]);
      } else {
        setComments((prev) =>
          prev.map((c) =>
            c.id === parentId
              ? { ...c, replies: [...c.replies, res.data] }
              : c,
          ),
        );
      }
      toast.success('Comment posted!');
    } catch { toast.error('Failed to post comment'); }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <div className="h-8 w-3/4 animate-pulse rounded-xl bg-gray-100" />
        <div className="h-64 animate-pulse rounded-2xl bg-gray-100" />
      </div>
    );
  }

  if (!post) {
    return (
      <div className="py-20 text-center">
        <p className="text-gray-400">Post not found.</p>
        <Link href="/" className="mt-3 inline-block text-sm text-blue-600 hover:underline">
          Back to feed
        </Link>
      </div>
    );
  }

  return (
    <article className="mx-auto max-w-3xl">
      <Link href="/" className="mb-6 inline-flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600">
        <ArrowLeft className="h-4 w-4" /> Back to feed
      </Link>

      {post.image && (
        <div className="relative mb-8 h-72 w-full overflow-hidden rounded-2xl">
          <Image src={post.image} alt={post.title} fill className="object-cover" />
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {post.category_name && (
          <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
            {post.category_name}
          </span>
        )}
        {post.tags.map((tag) => (
          <span
            key={tag.id}
            className="flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-1 text-xs text-gray-600"
          >
            <Tag className="h-3 w-3" /> {tag.name}
          </span>
        ))}
      </div>

      <h1 className="mb-4 text-3xl font-bold leading-tight text-gray-900">{post.title}</h1>

      <div className="mb-8 flex items-center justify-between border-b border-gray-100 pb-6">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <span className="font-medium text-gray-700">{post.author_name}</span>
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" /> {post.reading_time} min read
          </span>
          <span>{formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleLike}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition ${
              post.is_liked ? 'bg-red-50 text-red-500' : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-500'
            }`}
          >
            <Heart className={`h-4 w-4 ${post.is_liked ? 'fill-current' : ''}`} />
            {post.likes_count}
          </button>
          <button
            onClick={handleBookmark}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm transition ${
              post.is_bookmarked ? 'bg-yellow-50 text-yellow-500' : 'bg-gray-100 text-gray-600 hover:bg-yellow-50 hover:text-yellow-500'
            }`}
          >
            <Bookmark className={`h-4 w-4 ${post.is_bookmarked ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>

      <div className="prose prose-gray max-w-none">
        {post.content.split('\n').map((para, i) => (
          <p key={i} className="mb-4 leading-relaxed text-gray-700">
            {para}
          </p>
        ))}
      </div>

      <CommentSection
        comments={comments}
        onAddComment={handleAddComment}
      />
    </article>
  );
}
