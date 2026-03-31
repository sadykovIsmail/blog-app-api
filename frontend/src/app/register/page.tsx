"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  handle?: string;
}

function validate(
  username: string,
  email: string,
  password: string
): FormErrors {
  const errors: FormErrors = {};
  if (!username.trim()) errors.username = "Username is required.";
  else if (username.length < 3) errors.username = "At least 3 characters.";

  if (!email.trim()) errors.email = "Email is required.";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    errors.email = "Enter a valid email.";

  if (!password) errors.password = "Password is required.";
  else if (password.length < 8)
    errors.password = "At least 8 characters required.";

  return errors;
}

export default function RegisterPage() {
  const { register, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [handle, setHandle] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FormErrors>({});

  if (!authLoading && isAuthenticated) {
    router.push("/dashboard");
    return null;
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    const errors = validate(username, email, password);
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    setFieldErrors({});
    setIsSubmitting(true);

    try {
      await register({
        username: username.trim(),
        email: email.trim(),
        password,
        handle: handle.trim() || undefined,
      });
      router.push("/login?registered=1");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Registration failed. Try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const strengthScore = (p: string): 0 | 1 | 2 | 3 => {
    if (p.length < 6) return 0;
    let score = 0;
    if (p.length >= 8) score++;
    if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++;
    if (/\d/.test(p) && /[^A-Za-z0-9]/.test(p)) score++;
    return score as 0 | 1 | 2 | 3;
  };
  const strength = strengthScore(password);
  const strengthLabels = ["Weak", "Fair", "Good", "Strong"];
  const strengthColors = [
    "bg-red-500",
    "bg-orange-500",
    "bg-yellow-500",
    "bg-green-500",
  ];

  return (
    <div className="flex min-h-[70vh] items-center justify-center py-8">
      <div className="w-full max-w-md">
        <div className="rounded-2xl border border-neutral-800 bg-neutral-900 p-8 shadow-2xl shadow-black/40">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600/20">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                className="text-brand-400"
              >
                <path
                  d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8zM19 8v6M22 11h-6"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-neutral-50">Create account</h1>
            <p className="mt-1 text-sm text-neutral-500">
              Join the writing community
            </p>
          </div>

          {/* Global error */}
          {error && (
            <div className="mb-4 flex items-start gap-2 rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-400">
              <svg
                width="16"
                height="16"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="mt-0.5 shrink-0"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
            {/* Username */}
            <div>
              <label
                htmlFor="username"
                className="mb-1.5 block text-sm font-medium text-neutral-300"
              >
                Username <span className="text-red-400">*</span>
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={isSubmitting}
                placeholder="john_doe"
                className={`w-full rounded-lg border bg-neutral-800 px-3 py-2.5 text-sm text-neutral-100 placeholder-neutral-600 transition-colors focus:outline-none focus:ring-1 disabled:opacity-60 ${
                  fieldErrors.username
                    ? "border-red-600 focus:border-red-500 focus:ring-red-500/30"
                    : "border-neutral-700 focus:border-brand-500 focus:ring-brand-500/30"
                }`}
              />
              {fieldErrors.username && (
                <p className="mt-1 text-xs text-red-400">
                  {fieldErrors.username}
                </p>
              )}
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-1.5 block text-sm font-medium text-neutral-300"
              >
                Email <span className="text-red-400">*</span>
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
                placeholder="you@example.com"
                className={`w-full rounded-lg border bg-neutral-800 px-3 py-2.5 text-sm text-neutral-100 placeholder-neutral-600 transition-colors focus:outline-none focus:ring-1 disabled:opacity-60 ${
                  fieldErrors.email
                    ? "border-red-600 focus:border-red-500 focus:ring-red-500/30"
                    : "border-neutral-700 focus:border-brand-500 focus:ring-brand-500/30"
                }`}
              />
              {fieldErrors.email && (
                <p className="mt-1 text-xs text-red-400">{fieldErrors.email}</p>
              )}
            </div>

            {/* Handle (optional) */}
            <div>
              <label
                htmlFor="handle"
                className="mb-1.5 block text-sm font-medium text-neutral-300"
              >
                Handle{" "}
                <span className="text-xs font-normal text-neutral-600">
                  (optional — e.g. johndoe)
                </span>
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500 text-sm select-none">
                  @
                </span>
                <input
                  id="handle"
                  type="text"
                  value={handle}
                  onChange={(e) => setHandle(e.target.value)}
                  disabled={isSubmitting}
                  placeholder="johndoe"
                  className="w-full rounded-lg border border-neutral-700 bg-neutral-800 py-2.5 pl-7 pr-3 text-sm text-neutral-100 placeholder-neutral-600 transition-colors focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30 disabled:opacity-60"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="mb-1.5 block text-sm font-medium text-neutral-300"
              >
                Password <span className="text-red-400">*</span>
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isSubmitting}
                  placeholder="Min. 8 characters"
                  className={`w-full rounded-lg border bg-neutral-800 px-3 py-2.5 pr-10 text-sm text-neutral-100 placeholder-neutral-600 transition-colors focus:outline-none focus:ring-1 disabled:opacity-60 ${
                    fieldErrors.password
                      ? "border-red-600 focus:border-red-500 focus:ring-red-500/30"
                      : "border-neutral-700 focus:border-brand-500 focus:ring-brand-500/30"
                  }`}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((s) => !s)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors"
                >
                  {showPassword ? (
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                      <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                    </svg>
                  ) : (
                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </button>
              </div>

              {/* Password strength */}
              {password && (
                <div className="mt-2">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        className={`h-1 flex-1 rounded-full transition-all ${
                          strength > i
                            ? strengthColors[strength]
                            : "bg-neutral-800"
                        }`}
                      />
                    ))}
                  </div>
                  <p className="mt-1 text-xs text-neutral-500">
                    Password strength:{" "}
                    <span
                      className={
                        strength === 0
                          ? "text-red-400"
                          : strength === 1
                          ? "text-orange-400"
                          : strength === 2
                          ? "text-yellow-400"
                          : "text-green-400"
                      }
                    >
                      {strengthLabels[strength]}
                    </span>
                  </p>
                </div>
              )}
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-red-400">
                  {fieldErrors.password}
                </p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting && (
                <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              )}
              {isSubmitting ? "Creating account…" : "Create Account"}
            </button>
          </form>

          {/* Terms */}
          <p className="mt-4 text-center text-xs text-neutral-600">
            By signing up, you agree to our Terms of Service.
          </p>

          <p className="mt-4 text-center text-sm text-neutral-500">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-brand-400 hover:text-brand-300 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
