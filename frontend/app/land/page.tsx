'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';

import { AuthGuard } from '@/components/auth-guard';
import { AppShell } from '@/components/app-shell';
import { RoleGuard } from '@/components/role-guard';
import { Button } from '@/components/ui/button';
import { fetchLandFiles, type LandFile } from '@/lib/api/land';

const STATUS_BADGE: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-800',
  UNDER_NEGOTIATION: 'bg-amber-100 text-amber-800',
  COMMITTED: 'bg-blue-100 text-blue-800',
  CLOSED: 'bg-slate-200 text-slate-600',
};

function Badge({ label }: { label: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[label] ?? 'bg-slate-100 text-slate-700'}`}
    >
      {label.replace(/_/g, ' ')}
    </span>
  );
}

function LandTable({ data }: { data: LandFile[] }) {
  if (data.length === 0) {
    return (
      <p className="text-muted-foreground py-12 text-center">
        No land files yet.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="min-w-full text-sm">
        <thead className="bg-muted/50 border-b text-left">
          <tr>
            <th className="px-4 py-3 font-medium">Land ID</th>
            <th className="px-4 py-3 font-medium">Survey No</th>
            <th className="px-4 py-3 font-medium">Village</th>
            <th className="px-4 py-3 font-medium">Taluk</th>
            <th className="px-4 py-3 font-medium">District</th>
            <th className="px-4 py-3 font-medium">Acres</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((lf) => (
            <tr key={lf.id} className="hover:bg-muted/30 transition-colors">
              <td className="px-4 py-3">
                <Link
                  href={`/land/${lf.id}`}
                  className="text-primary font-medium underline-offset-2 hover:underline"
                >
                  {lf.land_id}
                </Link>
              </td>
              <td className="px-4 py-3">
                {lf.survey_number}
                {lf.hissa ? `/${lf.hissa}` : ''}
              </td>
              <td className="px-4 py-3">{lf.village_name}</td>
              <td className="px-4 py-3">{lf.taluk_name}</td>
              <td className="px-4 py-3">{lf.district_name}</td>
              <td className="px-4 py-3 tabular-nums">{lf.extent_acres}</td>
              <td className="px-4 py-3">
                <Badge label={lf.status} />
              </td>
              <td className="text-muted-foreground px-4 py-3 text-xs">
                {new Date(lf.created_at).toLocaleDateString('en-IN')}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function LandListPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['land-files'],
    queryFn: fetchLandFiles,
  });

  return (
    <AuthGuard
      roles={[
        'FOUNDER',
        'MANAGEMENT',
        'IN_HOUSE_ADVOCATE',
        'REVENUE_TEAM',
        'SURVEYOR_INHOUSE',
      ]}
    >
      <AppShell>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold tracking-tight">
              Land Files
            </h1>
            <RoleGuard roles={['FOUNDER', 'MANAGEMENT']}>
              <Link href="/land/new">
                <Button size="lg">+ New Land File</Button>
              </Link>
            </RoleGuard>
          </div>

          {isLoading && (
            <p className="text-muted-foreground py-12 text-center">
              Loading...
            </p>
          )}
          {error && (
            <p className="text-destructive py-6 text-center">
              Failed to load land files.
            </p>
          )}
          {data && <LandTable data={data} />}
        </div>
      </AppShell>
    </AuthGuard>
  );
}
