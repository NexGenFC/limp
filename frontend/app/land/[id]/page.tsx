'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useParams } from 'next/navigation';

import { AuthGuard } from '@/components/auth-guard';
import { AppShell } from '@/components/app-shell';
import { fetchLandFile } from '@/lib/api/land';
import { useAuthStore } from '@/lib/stores/auth-store';

function Field({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-muted-foreground text-xs font-medium uppercase tracking-wider">
        {label}
      </dt>
      <dd className="mt-0.5 text-sm">{value ?? '\u2014'}</dd>
    </div>
  );
}

export default function LandDetailPage() {
  const { id } = useParams<{ id: string }>();
  const accessToken = useAuthStore((s) => s.accessToken);

  const { data, isLoading, error } = useQuery({
    queryKey: ['land-file', id],
    queryFn: () => fetchLandFile(id),
    enabled: !!id && !!accessToken,
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
        <div className="mx-auto max-w-2xl space-y-6">
          <div className="flex items-center gap-3">
            <Link
              href="/land"
              className="text-muted-foreground hover:text-foreground text-sm"
            >
              &larr; Land Files
            </Link>
          </div>

          {isLoading && (
            <p className="text-muted-foreground py-12 text-center">
              Loading...
            </p>
          )}
          {error && (
            <p className="text-destructive py-6 text-center">
              Failed to load land file.
            </p>
          )}

          {data && (
            <div className="border-border bg-card space-y-6 rounded-xl border p-6 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-xl font-semibold tracking-tight">
                    {data.land_id}
                  </h1>
                  <p className="text-muted-foreground text-sm">
                    {data.village_name}, {data.hobli_name}, {data.taluk_name},{' '}
                    {data.district_name}
                  </p>
                </div>
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    data.status === 'ACTIVE'
                      ? 'bg-emerald-100 text-emerald-800'
                      : data.status === 'UNDER_NEGOTIATION'
                        ? 'bg-amber-100 text-amber-800'
                        : data.status === 'COMMITTED'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {data.status.replace(/_/g, ' ')}
                </span>
              </div>

              <hr className="border-border" />

              <dl className="grid gap-4 sm:grid-cols-3">
                <Field
                  label="Survey Number"
                  value={`${data.survey_number}${data.hissa ? ` / ${data.hissa}` : ''}`}
                />
                <Field label="Classification" value={data.classification} />
                <Field label="Extent (Acres)" value={data.extent_acres} />
                <Field label="Extent (Guntas)" value={data.extent_guntas} />
                <Field label="Extent (Sq Ft)" value={data.extent_sqft} />
                <Field
                  label="Investment Range"
                  value={
                    data.investment_min || data.investment_max
                      ? `${data.investment_min ?? '?'} \u2013 ${data.investment_max ?? '?'}`
                      : '\u2014'
                  }
                />
              </dl>

              <hr className="border-border" />

              <dl className="grid gap-4 sm:grid-cols-2">
                <Field
                  label="Created"
                  value={new Date(data.created_at).toLocaleString('en-IN')}
                />
                <Field
                  label="Updated"
                  value={new Date(data.updated_at).toLocaleString('en-IN')}
                />
              </dl>
            </div>
          )}
        </div>
      </AppShell>
    </AuthGuard>
  );
}
