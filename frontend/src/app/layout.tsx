import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthContext";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: {
    default: "BlogApp — Modern Writing Platform",
    template: "%s | BlogApp",
  },
  description:
    "A clean, modern blog platform. Discover great writing, follow authors, and share your ideas.",
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000"
  ),
  openGraph: {
    type: "website",
    siteName: "BlogApp",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-neutral-950 text-neutral-100 antialiased">
        <AuthProvider>
          <Navbar />
          <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
            {children}
          </main>
          <footer className="mt-16 border-t border-neutral-800 py-8 text-center">
            <p className="text-sm text-neutral-600">
              &copy; {new Date().getFullYear()} BlogApp. Built with Next.js 14 &amp; Django REST Framework.
            </p>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
