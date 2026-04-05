'use client';

import type { UserRole } from '@/lib/stores/auth-store';
import { useAuthStore } from '@/lib/stores/auth-store';

interface RoleGuardProps {
  roles: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({
  roles,
  children,
  fallback = null,
}: RoleGuardProps) {
  const user = useAuthStore((s) => s.user);
  if (!user || !roles.includes(user.role)) return <>{fallback}</>;
  return <>{children}</>;
}
