'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { authApi, authorsApi, bookmarksApi } from '@/lib/api';
import { Author } from '@/lib/types';
import { User, Globe, FileText, Bookmark, Plus } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading, refreshProfile } = useAuth();
  const router = useRouter();
  const [authors, setAuthors] = useState<Author[]>([]);
  const [bookmarkCount, setBookmarkCount] = useState(0);
  const [bio, setBio] = useState('');
  const [website, setWebsite] = useState('');
  const [saving, setSaving] = useState(false);
  const [newAuthor, setNewAuthor] = useState({ name: '', email: '' });
  const [showAuthorForm, setShowAuthorForm] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) router.push('/login');
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (user) {
      setBio(user.bio || '');
      setWebsite(user.website || '');
    }
  }, [user]);

  useEffect(() => {
    if (isAuthenticated) {
      authorsApi.list().then((r) => setAuthors(r.data.results || r.data));
      bookmarksApi.list().then((r) => setBookmarkCount(r.data.count || 0));
    }
  }, [isAuthenticated]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await authApi.updateProfile({ bio, website });
      await refreshProfile();
      toast.success('Profile updated!');
    } catch { toast.error('Failed to save'); }
    finally { setSaving(false); }
  };

  const handleCreateAuthor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await authorsApi.create(newAuthor);
      setAuthors((prev) => [...prev, res.data]);
      setNewAuthor({ name: '', email: '' });
      setShowAuthorForm(false);
      toast.success('Author created!');
    } catch { toast.error('Failed to create author'); }
  };

  if (isLoading || !user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">My Profile</h1>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100 text-2xl font-bold text-blue-600">
            {user.username[0].toUpperCase()}
          </div>
          <div>
            <h2 className="text-xl font-bold">{user.username}</h2>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Bio</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              rows={3}
              placeholder="Tell the world about yourself..."
              className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Website</label>
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-gray-400" />
              <input
                type="url"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                placeholder="https://yourwebsite.com"
                className="flex-1 rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-blue-400 focus:outline-none"
              />
            </div>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="rounded-xl bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-3 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <FileText className="h-8 w-8 text-blue-500" />
          <div>
            <div className="text-2xl font-bold">{authors.length}</div>
            <div className="text-sm text-gray-500">Author profiles</div>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <Bookmark className="h-8 w-8 text-yellow-500" />
          <div>
            <div className="text-2xl font-bold">{bookmarkCount}</div>
            <div className="text-sm text-gray-500">Bookmarks</div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="flex items-center gap-2 font-semibold">
            <User className="h-4 w-4 text-blue-600" /> Author Profiles
          </h3>
          <button
            onClick={() => setShowAuthorForm(!showAuthorForm)}
            className="flex items-center gap-1 rounded-lg bg-blue-50 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-100"
          >
            <Plus className="h-4 w-4" /> New Author
          </button>
        </div>

        {showAuthorForm && (
          <form onSubmit={handleCreateAuthor} className="mb-4 space-y-3 rounded-xl bg-gray-50 p-4">
            <input
              value={newAuthor.name}
              onChange={(e) => setNewAuthor({ ...newAuthor, name: e.target.value })}
              placeholder="Author name"
              required
              className="w-full rounded-xl border border-gray-200 px-4 py-2 text-sm focus:outline-none"
            />
            <input
              type="email"
              value={newAuthor.email}
              onChange={(e) => setNewAuthor({ ...newAuthor, email: e.target.value })}
              placeholder="Author email"
              required
              className="w-full rounded-xl border border-gray-200 px-4 py-2 text-sm focus:outline-none"
            />
            <button
              type="submit"
              className="rounded-xl bg-blue-600 px-4 py-1.5 text-sm font-medium text-white"
            >
              Create
            </button>
          </form>
        )}

        <ul className="space-y-2">
          {authors.map((author) => (
            <li key={author.id} className="flex items-center gap-3 rounded-xl bg-gray-50 px-4 py-3 text-sm">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
                {author.name[0].toUpperCase()}
              </div>
              <div>
                <div className="font-medium">{author.name}</div>
                <div className="text-xs text-gray-400">{author.email}</div>
              </div>
            </li>
          ))}
          {authors.length === 0 && (
            <p className="py-4 text-center text-sm text-gray-400">
              No author profiles yet. Create one to start posting.
            </p>
          )}
        </ul>
      </div>
    </div>
  );
}
