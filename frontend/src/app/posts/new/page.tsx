'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { postsApi, authorsApi, categoriesApi, tagsApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Author, Category, Tag } from '@/lib/types';
import toast from 'react-hot-toast';
import { Save, Send } from 'lucide-react';

export default function NewPostPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [authors, setAuthors] = useState<Author[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [form, setForm] = useState({
    title: '',
    content: '',
    author: '',
    category: '',
    tag_ids: [] as number[],
    status: 'draft',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.push('/login');
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      authorsApi.list().then((r) => setAuthors(r.data.results || r.data));
      categoriesApi.list().then((r) => setCategories(r.data.results || r.data));
      tagsApi.list().then((r) => setTags(r.data.results || r.data));
    }
  }, [isAuthenticated]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => setForm({ ...form, [e.target.name]: e.target.value });

  const toggleTag = (id: number) => {
    setForm((prev) => ({
      ...prev,
      tag_ids: prev.tag_ids.includes(id)
        ? prev.tag_ids.filter((t) => t !== id)
        : [...prev.tag_ids, id],
    }));
  };

  const handleSubmit = async (status: 'draft' | 'published') => {
    if (!form.title || !form.content || !form.author) {
      toast.error('Title, content, and author are required');
      return;
    }
    setSubmitting(true);
    try {
      const payload: Record<string, unknown> = {
        title: form.title,
        content: form.content,
        author: Number(form.author),
        status,
        tag_ids: form.tag_ids,
      };
      if (form.category) payload.category = Number(form.category);
      const res = await postsApi.create(payload);
      toast.success(status === 'published' ? 'Post published!' : 'Draft saved!');
      router.push(status === 'published' ? `/posts/${res.data.slug}` : '/dashboard');
    } catch {
      toast.error('Failed to save post');
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) return null;

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">New Post</h1>

      <div className="space-y-6 rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">Title *</label>
          <input
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="Post title"
            className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-lg font-semibold focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">Author *</label>
          <select
            name="author"
            value={form.author}
            onChange={handleChange}
            className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-400 focus:outline-none"
          >
            <option value="">Select author...</option>
            {authors.map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
          {authors.length === 0 && (
            <p className="mt-1.5 text-xs text-orange-500">
              You have no authors.{' '}
              <a href="/profile" className="underline">Create one in your profile.</a>
            </p>
          )}
        </div>

        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">Content *</label>
          <textarea
            name="content"
            value={form.content}
            onChange={handleChange}
            placeholder="Write your post content..."
            rows={14}
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm leading-relaxed focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Category</label>
            <select
              name="category"
              value={form.category}
              onChange={handleChange}
              className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-400 focus:outline-none"
            >
              <option value="">No category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>

        {tags.length > 0 && (
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">Tags</label>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <button
                  key={tag.id}
                  type="button"
                  onClick={() => toggleTag(tag.id)}
                  className={`rounded-full px-3 py-1 text-sm transition ${
                    form.tag_ids.includes(tag.id)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  #{tag.name}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <button
            onClick={() => handleSubmit('draft')}
            disabled={submitting}
            className="flex items-center gap-2 rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60"
          >
            <Save className="h-4 w-4" /> Save Draft
          </button>
          <button
            onClick={() => handleSubmit('published')}
            disabled={submitting}
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            <Send className="h-4 w-4" /> Publish
          </button>
        </div>
      </div>
    </div>
  );
}
