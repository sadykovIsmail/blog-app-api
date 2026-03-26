'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { BookOpen, PenSquare, User, LogOut, LogIn, Home } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-gray-200 bg-white shadow-sm">
      <div className="mx-auto max-w-6xl px-4">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-blue-600">
            <BookOpen className="h-6 w-6" />
            BlogApp
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600"
            >
              <Home className="h-4 w-4" />
              Feed
            </Link>

            {isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600"
                >
                  <PenSquare className="h-4 w-4" />
                  Dashboard
                </Link>
                <Link
                  href="/posts/new"
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  + New Post
                </Link>
                <Link
                  href="/profile"
                  className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600"
                >
                  <User className="h-4 w-4" />
                  {user?.username}
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-500"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="flex items-center gap-1 text-sm text-gray-600 hover:text-blue-600"
                >
                  <LogIn className="h-4 w-4" />
                  Login
                </Link>
                <Link
                  href="/register"
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
