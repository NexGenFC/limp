'use client';

import Link from 'next/link';

import { AuthGuard } from '@/components/auth-guard';
import { AppShell } from '@/components/app-shell';
import { RoleGuard } from '@/components/role-guard';
import { useAuthStore } from '@/lib/stores/auth-store';

export default function Home() {
  const user = useAuthStore((s) => s.user);

  return (
    <AuthGuard>
      <AppShell>
        <div className="mx-auto max-w-2xl space-y-6">
          <div className="space-y-2">
            <p className="text-muted-foreground text-sm">
              Land Intelligence Management Platform
            </p>
            <h1 className="text-3xl font-semibold tracking-tight">
              Welcome{user ? `, ${user.first_name || user.email}` : ''}
            </h1>
            <p className="text-muted-foreground">
              Use the sidebar to navigate between modules. Your role (
              <span className="font-medium">
                {user?.role.replace(/_/g, ' ')}
              </span>
              ) determines which sections are visible.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <RoleGuard
              roles={[
                'FOUNDER',
                'MANAGEMENT',
                'IN_HOUSE_ADVOCATE',
                'REVENUE_TEAM',
                'SURVEYOR_INHOUSE',
              ]}
            >
              <Link
                href="/land"
                className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex h-9 items-center justify-center rounded-lg px-4 text-sm font-medium"
              >
                View Land Files
              </Link>
            </RoleGuard>
            <Link
              href="/health"
              className="border-border hover:bg-muted inline-flex h-9 items-center justify-center rounded-lg border px-4 text-sm font-medium"
            >
              Check Health
            </Link>
          </div>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
