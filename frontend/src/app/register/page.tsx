'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { BookOpen } from 'lucide-react';
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    try {
      await authApi.register(form);
      await login(form.username, form.password);
      toast.success('Account created! Welcome!');
      router.push('/dashboard');
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: Record<string, string[]> } };
        if (axiosErr.response?.data) {
          const data = axiosErr.response.data;
          const fieldErrors: Record<string, string> = {};
          Object.entries(data).forEach(([key, val]) => {
            fieldErrors[key] = Array.isArray(val) ? val[0] : String(val);
          });
          setErrors(fieldErrors);
        }
      }
      toast.error('Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: 'username', label: 'Username', type: 'text', autoComplete: 'username' },
    { name: 'email', label: 'Email', type: 'email', autoComplete: 'email' },
    { name: 'password', label: 'Password', type: 'password', autoComplete: 'new-password' },
    { name: 'password2', label: 'Confirm Password', type: 'password', autoComplete: 'new-password' },
  ] as const;

  return (
    <div className="flex min-h-[70vh] items-center justify-center">
      <div className="w-full max-w-md rounded-2xl border border-gray-100 bg-white p-8 shadow-lg">
        <div className="mb-8 text-center">
          <BookOpen className="mx-auto mb-3 h-10 w-10 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Create account</h1>
          <p className="mt-1 text-sm text-gray-500">Start sharing your ideas</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map(({ name, label, type, autoComplete }) => (
            <div key={name}>
              <label className="mb-1.5 block text-sm font-medium text-gray-700">{label}</label>
              <input
                type={type}
                name={name}
                value={form[name]}
                onChange={handleChange}
                required
                autoComplete={autoComplete}
                className={`w-full rounded-xl border px-4 py-2.5 text-sm focus:outline-none focus:ring-2 ${
                  errors[name]
                    ? 'border-red-300 focus:border-red-400 focus:ring-red-100'
                    : 'border-gray-200 focus:border-blue-400 focus:ring-blue-100'
                }`}
              />
              {errors[name] && <p className="mt-1 text-xs text-red-500">{errors[name]}</p>}
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-blue-600 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-blue-600 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
