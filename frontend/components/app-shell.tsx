'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { RoleGuard } from '@/components/role-guard';
import { Button, buttonVariants } from '@/components/ui/button';
import { useAuthStore } from '@/lib/stores/auth-store';
import { cn } from '@/lib/utils';

const ROLE_LABEL: Record<string, string> = {
  FOUNDER: 'Founder',
  MANAGEMENT: 'Management',
  IN_HOUSE_ADVOCATE: 'In-House Advocate',
  EXTERNAL_ADVOCATE: 'External Advocate',
  REVENUE_TEAM: 'Revenue Team',
  SURVEYOR_INHOUSE: 'Surveyor (IH)',
  SURVEYOR_FREELANCE: 'Surveyor (FL)',
  FIELD_STAFF: 'Field Staff',
};

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(`${href}/`);
  return (
    <Link
      href={href}
      className={cn(
        buttonVariants({ variant: active ? 'secondary' : 'ghost' }),
        'justify-start',
      )}
    >
      {children}
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, clearSession } = useAuthStore();

  function handleLogout() {
    clearSession();
    router.replace('/login');
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-border bg-sidebar text-sidebar-foreground flex w-full flex-col border-b md:w-56 md:border-r md:border-b-0">
        <div className="flex h-14 items-center px-4 font-semibold tracking-tight">
          LIMP
        </div>
        <nav className="flex flex-row gap-1 px-2 pb-3 md:flex-col md:px-3 md:pb-0">
          <NavLink href="/">Home</NavLink>

          <RoleGuard
            roles={[
              'FOUNDER',
              'MANAGEMENT',
              'IN_HOUSE_ADVOCATE',
              'REVENUE_TEAM',
              'SURVEYOR_INHOUSE',
            ]}
          >
            <NavLink href="/land">Land Files</NavLink>
          </RoleGuard>
        </nav>

        {user && (
          <div className="border-border mt-auto border-t px-4 py-3">
            <p className="truncate text-sm font-medium">{user.email}</p>
            <p className="text-muted-foreground text-xs">
              {ROLE_LABEL[user.role] ?? user.role}
            </p>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2 w-full justify-start"
              onClick={handleLogout}
            >
              Sign out
            </Button>
          </div>
        )}
      </aside>
      <main className="bg-background text-foreground min-h-screen flex-1 p-6">
        {children}
      </main>
    </div>
  );
}
