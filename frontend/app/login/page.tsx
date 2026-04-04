'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { loginApi, fetchMe } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/stores/auth-store';

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await loginApi(email, password);
      useAuthStore.getState().clearSession();
      useAuthStore.setState({
        accessToken: tokens.access,
        refreshToken: tokens.refresh,
      });
      const user = await fetchMe();
      setSession(tokens.access, tokens.refresh, user);
      router.replace('/');
    } catch (err: unknown) {
      const msg =
        err &&
        typeof err === 'object' &&
        'response' in err &&
        (err as { response?: { data?: { detail?: string } } }).response?.data
          ?.detail;
      setError(typeof msg === 'string' ? msg : 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-slate-50 to-slate-100 px-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold tracking-tight">LIMP</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Land Intelligence Management Platform
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="border-border bg-card space-y-4 rounded-xl border p-6 shadow-sm"
        >
          <div className="space-y-1.5">
            <label
              htmlFor="email"
              className="text-sm font-medium leading-none"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="border-input bg-background ring-ring/20 placeholder:text-muted-foreground flex h-9 w-full rounded-lg border px-3 text-sm outline-none transition focus:ring-2"
              placeholder="you@company.com"
            />
          </div>

          <div className="space-y-1.5">
            <label
              htmlFor="password"
              className="text-sm font-medium leading-none"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border-input bg-background ring-ring/20 placeholder:text-muted-foreground flex h-9 w-full rounded-lg border px-3 text-sm outline-none transition focus:ring-2"
            />
          </div>

          {error && (
            <p className="text-destructive text-sm font-medium">{error}</p>
          )}

          <Button
            type="submit"
            className="w-full"
            size="lg"
            disabled={loading}
          >
            {loading ? 'Signing in\u2026' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  );
}
