'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { AuthGuard } from '@/components/auth-guard';
import { AppShell } from '@/components/app-shell';
import { Button } from '@/components/ui/button';
import {
  fetchDistricts,
  fetchTaluks,
  fetchHoblis,
  fetchVillages,
} from '@/lib/api/geography';
import { createLandFile, type LandFileCreate } from '@/lib/api/land';

function Select({
  label,
  value,
  onChange,
  options,
  disabled,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { id: number; name: string }[];
  disabled?: boolean;
  placeholder?: string;
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="border-input bg-background ring-ring/20 flex h-9 w-full rounded-lg border px-3 text-sm outline-none transition focus:ring-2 disabled:opacity-50"
      >
        <option value="">{placeholder ?? `Select ${label}`}</option>
        {options.map((o) => (
          <option key={o.id} value={String(o.id)}>
            {o.name}
          </option>
        ))}
      </select>
    </div>
  );
}

function Input({
  label,
  required,
  ...props
}: {
  label: string;
} & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">
        {label}
        {required && <span className="text-destructive ml-0.5">*</span>}
      </label>
      <input
        {...props}
        required={required}
        className="border-input bg-background ring-ring/20 placeholder:text-muted-foreground flex h-9 w-full rounded-lg border px-3 text-sm outline-none transition focus:ring-2"
      />
    </div>
  );
}

export default function NewLandFilePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [districtId, setDistrictId] = useState('');
  const [talukId, setTalukId] = useState('');
  const [hobliId, setHobliId] = useState('');
  const [villageId, setVillageId] = useState('');

  const [surveyNumber, setSurveyNumber] = useState('');
  const [hissa, setHissa] = useState('');
  const [extentAcres, setExtentAcres] = useState('');
  const [extentGuntas, setExtentGuntas] = useState('');
  const [extentSqft, setExtentSqft] = useState('');
  const [classification, setClassification] = useState('AGRICULTURAL');

  const [error, setError] = useState<string | null>(null);

  const districts = useQuery({
    queryKey: ['districts'],
    queryFn: fetchDistricts,
  });
  const taluks = useQuery({
    queryKey: ['taluks', districtId],
    queryFn: () => fetchTaluks(Number(districtId)),
    enabled: !!districtId,
  });
  const hoblis = useQuery({
    queryKey: ['hoblis', talukId],
    queryFn: () => fetchHoblis(Number(talukId)),
    enabled: !!talukId,
  });
  const villages = useQuery({
    queryKey: ['villages', hobliId],
    queryFn: () => fetchVillages(Number(hobliId)),
    enabled: !!hobliId,
  });

  const mutation = useMutation({
    mutationFn: createLandFile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['land-files'] });
      router.push('/land');
    },
    onError: () => setError('Failed to create land file.'),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!villageId) {
      setError('Please select the full geography cascade down to village.');
      return;
    }
    const payload: LandFileCreate = {
      village: Number(villageId),
      survey_number: surveyNumber,
      classification,
    };
    if (hissa) payload.hissa = hissa;
    if (extentAcres) payload.extent_acres = extentAcres;
    if (extentGuntas) payload.extent_guntas = extentGuntas;
    if (extentSqft) payload.extent_sqft = extentSqft;
    mutation.mutate(payload);
  }

  return (
    <AuthGuard roles={['FOUNDER', 'MANAGEMENT']}>
      <AppShell>
        <div className="mx-auto max-w-xl space-y-6">
          <h1 className="text-2xl font-semibold tracking-tight">
            New Land File
          </h1>

          <form
            onSubmit={handleSubmit}
            className="border-border bg-card space-y-5 rounded-xl border p-6 shadow-sm"
          >
            <p className="text-muted-foreground text-sm font-medium">
              Geography
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <Select
                label="District"
                value={districtId}
                onChange={(v) => {
                  setDistrictId(v);
                  setTalukId('');
                  setHobliId('');
                  setVillageId('');
                }}
                options={districts.data ?? []}
              />
              <Select
                label="Taluk"
                value={talukId}
                onChange={(v) => {
                  setTalukId(v);
                  setHobliId('');
                  setVillageId('');
                }}
                options={taluks.data ?? []}
                disabled={!districtId}
              />
              <Select
                label="Hobli"
                value={hobliId}
                onChange={(v) => {
                  setHobliId(v);
                  setVillageId('');
                }}
                options={hoblis.data ?? []}
                disabled={!talukId}
              />
              <Select
                label="Village"
                value={villageId}
                onChange={setVillageId}
                options={villages.data ?? []}
                disabled={!hobliId}
              />
            </div>

            <hr className="border-border" />
            <p className="text-muted-foreground text-sm font-medium">
              Land Details
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              <Input
                label="Survey Number"
                required
                value={surveyNumber}
                onChange={(e) => setSurveyNumber(e.target.value)}
                placeholder="e.g. 101"
              />
              <Input
                label="Hissa"
                value={hissa}
                onChange={(e) => setHissa(e.target.value)}
                placeholder="e.g. A"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-3">
              <Input
                label="Acres"
                type="number"
                step="0.0001"
                value={extentAcres}
                onChange={(e) => setExtentAcres(e.target.value)}
              />
              <Input
                label="Guntas"
                type="number"
                step="0.0001"
                value={extentGuntas}
                onChange={(e) => setExtentGuntas(e.target.value)}
              />
              <Input
                label="Sq Ft"
                type="number"
                step="0.01"
                value={extentSqft}
                onChange={(e) => setExtentSqft(e.target.value)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">Classification</label>
              <select
                value={classification}
                onChange={(e) => setClassification(e.target.value)}
                className="border-input bg-background ring-ring/20 flex h-9 w-full rounded-lg border px-3 text-sm outline-none transition focus:ring-2"
              >
                <option value="AGRICULTURAL">Agricultural</option>
                <option value="CONVERTED">Converted</option>
                <option value="APPROVED_SITE">Approved Site</option>
              </select>
            </div>

            {error && (
              <p className="text-destructive text-sm font-medium">{error}</p>
            )}

            <div className="flex gap-3">
              <Button type="submit" size="lg" disabled={mutation.isPending}>
                {mutation.isPending ? 'Creating\u2026' : 'Create Land File'}
              </Button>
              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </AppShell>
    </AuthGuard>
  );
}
