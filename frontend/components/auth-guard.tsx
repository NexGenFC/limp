'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

import { useAuthStore } from '@/lib/stores/auth-store';
import type { UserRole } from '@/lib/stores/auth-store';

interface AuthGuardProps {
  children: React.ReactNode;
  roles?: UserRole[];
}

export function AuthGuard({ children, roles }: AuthGuardProps) {
  const router = useRouter();
  const { accessToken, user } = useAuthStore();
  const [storeReady, setStoreReady] = useState(false);

  useEffect(() => {
    const p = useAuthStore.persist;
    if (!p) {
      queueMicrotask(() => setStoreReady(true));
      return;
    }
    const done = () => setStoreReady(true);
    const unsub = p.onFinishHydration(done);
    if (p.hasHydrated()) queueMicrotask(done);
    return unsub;
  }, []);

  useEffect(() => {
    if (!storeReady) return;
    if (!accessToken) {
      router.replace('/login');
      return;
    }
    if (roles && user && !roles.includes(user.role)) {
      router.replace('/403');
    }
  }, [accessToken, user, roles, router, storeReady]);

  if (!storeReady) {
    return (
      <div className="text-muted-foreground flex min-h-[40vh] items-center justify-center text-sm">
        Loading…
      </div>
    );
  }
  if (!accessToken) return null;
  if (roles && user && !roles.includes(user.role)) return null;

  return <>{children}</>;
}
