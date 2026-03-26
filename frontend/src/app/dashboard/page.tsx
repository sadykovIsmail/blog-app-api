'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { postsApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Post } from '@/lib/types';
import { formatDistanceToNow } from 'date-fns';
import {
  PenSquare, Trash2, Eye, EyeOff, Heart, MessageCircle, Plus,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [filter, setFilter] = useState<'all' | 'published' | 'draft'>('all');
  const [loading, setLoading] = useState(true);

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filter !== 'all') params.status = filter;
      const res = await postsApi.list(params);
      setPosts(res.data.results || res.data);
    } catch {
      toast.error('Failed to load posts');
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.push('/login');
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) fetchPosts();
  }, [isAuthenticated, fetchPosts]);

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this post?')) return;
    try {
      await postsApi.delete(id);
      setPosts((prev) => prev.filter((p) => p.id !== id));
      toast.success('Post deleted');
    } catch { toast.error('Failed to delete'); }
  };

  const handleTogglePublish = async (post: Post) => {
    try {
      const res = post.status === 'published'
        ? await postsApi.unpublish(post.id)
        : await postsApi.publish(post.id);
      setPosts((prev) => prev.map((p) => (p.id === post.id ? res.data : p)));
      toast.success(post.status === 'published' ? 'Post unpublished' : 'Post published!');
    } catch { toast.error('Failed'); }
  };

  if (isLoading) return null;

  const stats = {
    total: posts.length,
    published: posts.filter((p) => p.status === 'published').length,
    drafts: posts.filter((p) => p.status === 'draft').length,
    likes: posts.reduce((sum, p) => sum + p.likes_count, 0),
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Dashboard</h1>
        <Link
          href="/posts/new"
          className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" /> New Post
        </Link>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Total Posts', value: stats.total, color: 'blue' },
          { label: 'Published', value: stats.published, color: 'green' },
          { label: 'Drafts', value: stats.drafts, color: 'yellow' },
          { label: 'Total Likes', value: stats.likes, color: 'red' },
        ].map(({ label, value, color }) => (
          <div key={label} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className={`text-3xl font-bold text-${color}-600`}>{value}</div>
            <div className="mt-1 text-sm text-gray-500">{label}</div>
          </div>
        ))}
      </div>

      <div className="mb-4 flex gap-2">
        {(['all', 'published', 'draft'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-lg px-4 py-1.5 text-sm font-medium capitalize transition ${
              filter === f ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {posts.map((post) => (
            <div
              key={post.id}
              className="flex items-center gap-4 rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      post.status === 'published'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {post.status}
                  </span>
                  <h3 className="truncate text-sm font-semibold text-gray-900">{post.title}</h3>
                </div>
                <div className="mt-1 flex items-center gap-4 text-xs text-gray-400">
                  <span>{formatDistanceToNow(new Date(post.created_at), { addSuffix: true })}</span>
                  <span className="flex items-center gap-1">
                    <Heart className="h-3 w-3" /> {post.likes_count}
                  </span>
                  <span className="flex items-center gap-1">
                    <MessageCircle className="h-3 w-3" /> {post.comments_count}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleTogglePublish(post)}
                  title={post.status === 'published' ? 'Unpublish' : 'Publish'}
                  className={`rounded-lg p-1.5 transition ${
                    post.status === 'published'
                      ? 'text-green-600 hover:bg-green-50'
                      : 'text-gray-400 hover:bg-gray-100'
                  }`}
                >
                  {post.status === 'published' ? (
                    <Eye className="h-4 w-4" />
                  ) : (
                    <EyeOff className="h-4 w-4" />
                  )}
                </button>
                <Link
                  href={`/posts/edit/${post.id}`}
                  className="rounded-lg p-1.5 text-blue-500 hover:bg-blue-50"
                >
                  <PenSquare className="h-4 w-4" />
                </Link>
                <button
                  onClick={() => handleDelete(post.id)}
                  className="rounded-lg p-1.5 text-red-400 hover:bg-red-50"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}

          {posts.length === 0 && (
            <div className="py-16 text-center">
              <p className="text-gray-400">No posts yet.</p>
              <Link href="/posts/new" className="mt-3 inline-block text-sm text-blue-600 hover:underline">
                Create your first post
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
