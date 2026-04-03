'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { useAuthStore } from '@/lib/stores/auth-store';
import type { UserRole } from '@/lib/stores/auth-store';

interface AuthGuardProps {
  children: React.ReactNode;
  roles?: UserRole[];
}

export function AuthGuard({ children, roles }: AuthGuardProps) {
  const router = useRouter();
  const { accessToken, user } = useAuthStore();

  useEffect(() => {
    if (!accessToken) {
      router.replace('/login');
      return;
    }
    if (roles && user && !roles.includes(user.role)) {
      router.replace('/403');
    }
  }, [accessToken, user, roles, router]);

  if (!accessToken) return null;
  if (roles && user && !roles.includes(user.role)) return null;

  return <>{children}</>;
}
