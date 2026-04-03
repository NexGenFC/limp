import { AppShell } from '@/components/app-shell';

export default function HealthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
