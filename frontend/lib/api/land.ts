import { apiClient } from '@/lib/api/client';

export interface LandFile {
  id: string;
  land_id: string;
  village: number;
  village_name: string;
  hobli_name: string;
  taluk_name: string;
  district_name: string;
  survey_number: string;
  hissa: string;
  extent_acres: string;
  extent_guntas: string;
  extent_sqft: string;
  classification: string;
  status: string;
  proposed_by: number | null;
  investment_min: string | null;
  investment_max: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
  updated_by: number | null;
}

export interface LandFileCreate {
  village: number;
  survey_number: string;
  hissa?: string;
  extent_acres?: string;
  extent_guntas?: string;
  extent_sqft?: string;
  classification?: string;
  status?: string;
  proposed_by?: number | null;
  investment_min?: string | null;
  investment_max?: string | null;
}

interface Envelope<T> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown>;
}

export async function fetchLandFiles(): Promise<LandFile[]> {
  const res = await apiClient.get<Envelope<LandFile[]>>('/land/');
  return res.data.data;
}

export async function fetchLandFile(id: string): Promise<LandFile> {
  const res = await apiClient.get<Envelope<LandFile>>(`/land/${id}/`);
  return res.data.data;
}

export async function createLandFile(data: LandFileCreate): Promise<LandFile> {
  const res = await apiClient.post<Envelope<LandFile>>('/land/', data);
  return res.data.data;
}

export async function deleteLandFile(id: string): Promise<void> {
  await apiClient.delete(`/land/${id}/`);
}
