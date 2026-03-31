"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";
import { useState } from "react";

export default function Navbar() {
  const { user, isAuthenticated, logout, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/");
    setMobileOpen(false);
  };

  const navLink = (href: string, label: string) => {
    const active = pathname === href || pathname.startsWith(href + "/");
    return (
      <Link
        href={href}
        onClick={() => setMobileOpen(false)}
        className={`text-sm font-medium transition-colors duration-150 ${
          active
            ? "text-brand-400"
            : "text-neutral-400 hover:text-neutral-100"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-bold tracking-tight text-neutral-50 hover:text-brand-400 transition-colors"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            className="shrink-0"
          >
            <rect width="24" height="24" rx="6" fill="#0ea5e9" />
            <path
              d="M7 8h10M7 12h7M7 16h5"
              stroke="white"
              strokeWidth="1.8"
              strokeLinecap="round"
            />
          </svg>
          <span>BlogApp</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-6 md:flex">
          {navLink("/", "Feed")}
          {isAuthenticated && navLink("/dashboard", "Dashboard")}
          {isAuthenticated && navLink("/notifications", "Notifications")}
        </nav>

        {/* Desktop auth */}
        <div className="hidden items-center gap-3 md:flex">
          {isLoading ? (
            <div className="h-8 w-24 animate-pulse rounded-md bg-neutral-800" />
          ) : isAuthenticated ? (
            <>
              <span className="text-sm text-neutral-400">
                {user?.handle ? `@${user.handle}` : user?.username}
              </span>
              <Link
                href="/dashboard/new"
                className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-500 transition-colors"
              >
                New Post
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-md border border-neutral-700 px-3 py-1.5 text-sm font-medium text-neutral-300 hover:border-neutral-600 hover:text-neutral-100 transition-colors"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm font-medium text-neutral-400 hover:text-neutral-100 transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="rounded-md bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-500 transition-colors"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="flex items-center justify-center rounded-md p-2 text-neutral-400 hover:text-neutral-100 md:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-neutral-800 bg-neutral-950 px-4 pb-4 pt-2 md:hidden">
          <div className="flex flex-col gap-3">
            {navLink("/", "Feed")}
            {isAuthenticated && navLink("/dashboard", "Dashboard")}
            {isAuthenticated && navLink("/notifications", "Notifications")}
            <hr className="border-neutral-800" />
            {isLoading ? null : isAuthenticated ? (
              <>
                <span className="text-sm text-neutral-500">
                  {user?.handle ? `@${user.handle}` : user?.username}
                </span>
                <Link
                  href="/dashboard/new"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-md bg-brand-600 px-3 py-2 text-center text-sm font-medium text-white hover:bg-brand-500 transition-colors"
                >
                  New Post
                </Link>
                <button
                  onClick={handleLogout}
                  className="rounded-md border border-neutral-700 px-3 py-2 text-sm font-medium text-neutral-300 hover:text-neutral-100 transition-colors"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setMobileOpen(false)}
                  className="text-sm font-medium text-neutral-400 hover:text-neutral-100"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-md bg-brand-600 px-3 py-2 text-center text-sm font-medium text-white hover:bg-brand-500 transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
