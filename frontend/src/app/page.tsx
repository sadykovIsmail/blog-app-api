'use client';

import { useEffect, useState, useCallback } from 'react';
import { publicApi, categoriesApi, tagsApi } from '@/lib/api';
import { Post, Category, Tag, PaginatedResponse } from '@/lib/types';
import PostCard from '@/components/PostCard';
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import toast from 'react-hot-toast';

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [posts, setPosts] = useState<PaginatedResponse<Post> | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchPosts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page };
      if (search) params.search = search;
      if (selectedCategory) params.category = selectedCategory;
      if (selectedTag) params.tags = selectedTag;
      const res = await publicApi.listPosts(params);
      setPosts(res.data);
    } catch {
      toast.error('Failed to load posts');
    } finally {
      setLoading(false);
    }
  }, [page, search, selectedCategory, selectedTag]);

  useEffect(() => {
    publicApi.listPosts().then((r) => setPosts(r.data));
    categoriesApi.list().then((r) => setCategories(r.data.results || r.data));
    tagsApi.list().then((r) => setTags(r.data.results || r.data));
  }, []);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const handleLike = async (post: Post) => {
    if (!isAuthenticated) { toast('Please log in to like posts'); return; }
    try {
      const res = await publicApi.likePost(post.slug);
      setPosts((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.map((p) =>
                p.id === post.id
                  ? { ...p, is_liked: res.data.liked, likes_count: res.data.likes_count }
                  : p,
              ),
            }
          : prev,
      );
    } catch { toast.error('Failed'); }
  };

  const handleBookmark = async (post: Post) => {
    if (!isAuthenticated) { toast('Please log in to bookmark posts'); return; }
    try {
      const res = await publicApi.bookmarkPost(post.slug);
      setPosts((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.map((p) =>
                p.id === post.id ? { ...p, is_bookmarked: res.data.bookmarked } : p,
              ),
            }
          : prev,
      );
    } catch { toast.error('Failed'); }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchPosts();
  };

  return (
    <div className="flex gap-8">
      <aside className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-6">
          <div>
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Categories
            </h3>
            <ul className="space-y-1">
              <li>
                <button
                  onClick={() => { setSelectedCategory(''); setPage(1); }}
                  className={`w-full rounded-lg px-3 py-1.5 text-left text-sm transition ${!selectedCategory ? 'bg-blue-50 font-medium text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  All
                </button>
              </li>
              {categories.map((cat) => (
                <li key={cat.id}>
                  <button
                    onClick={() => { setSelectedCategory(String(cat.id)); setPage(1); }}
                    className={`w-full rounded-lg px-3 py-1.5 text-left text-sm transition ${selectedCategory === String(cat.id) ? 'bg-blue-50 font-medium text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`}
                  >
                    {cat.name}
                    <span className="ml-1 text-xs text-gray-400">({cat.post_count})</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
              Tags
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {tags.map((tag) => (
                <button
                  key={tag.id}
                  onClick={() => {
                    setSelectedTag(selectedTag === tag.slug ? '' : tag.slug);
                    setPage(1);
                  }}
                  className={`rounded-full px-2.5 py-1 text-xs transition ${selectedTag === tag.slug ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  #{tag.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </aside>

      <div className="min-w-0 flex-1">
        <form onSubmit={handleSearch} className="mb-6 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search posts..."
              className="w-full rounded-xl border border-gray-200 py-2.5 pl-10 pr-4 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>
          <button
            type="submit"
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Filter className="h-4 w-4" />
            Filter
          </button>
        </form>

        {loading ? (
          <div className="grid gap-6 sm:grid-cols-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-64 animate-pulse rounded-2xl bg-gray-100" />
            ))}
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-500">
              {posts?.count ?? 0} posts found
            </div>
            <div className="grid gap-6 sm:grid-cols-2">
              {posts?.results.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onLike={() => handleLike(post)}
                  onBookmark={() => handleBookmark(post)}
                />
              ))}
            </div>

            {posts && (posts.previous || posts.next) && (
              <div className="mt-8 flex items-center justify-center gap-4">
                <button
                  disabled={!posts.previous}
                  onClick={() => setPage((p) => p - 1)}
                  className="flex items-center gap-1 rounded-lg border px-4 py-2 text-sm disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" /> Previous
                </button>
                <span className="text-sm text-gray-500">Page {page}</span>
                <button
                  disabled={!posts.next}
                  onClick={() => setPage((p) => p + 1)}
                  className="flex items-center gap-1 rounded-lg border px-4 py-2 text-sm disabled:opacity-40"
                >
                  Next <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            )}

            {posts?.results.length === 0 && (
              <div className="py-16 text-center">
                <p className="text-gray-400">No posts found. Try different filters.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
