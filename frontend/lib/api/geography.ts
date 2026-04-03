import { apiClient } from '@/lib/api/client';

export interface District {
  id: number;
  name: string;
  state: string;
}
export interface Taluk {
  id: number;
  name: string;
  district: number;
}
export interface Hobli {
  id: number;
  name: string;
  taluk: number;
}
export interface Village {
  id: number;
  name: string;
  hobli: number;
}

interface Envelope<T> {
  success: boolean;
  data: T;
}

export async function fetchDistricts(): Promise<District[]> {
  const res = await apiClient.get<Envelope<District[]>>('/districts/');
  return res.data.data;
}

export async function fetchTaluks(districtId: number): Promise<Taluk[]> {
  const res = await apiClient.get<Envelope<Taluk[]>>(
    `/taluks/?district=${districtId}`,
  );
  return res.data.data;
}

export async function fetchHoblis(talukId: number): Promise<Hobli[]> {
  const res = await apiClient.get<Envelope<Hobli[]>>(
    `/hoblis/?taluk=${talukId}`,
  );
  return res.data.data;
}

export async function fetchVillages(hobliId: number): Promise<Village[]> {
  const res = await apiClient.get<Envelope<Village[]>>(
    `/villages/?hobli=${hobliId}`,
  );
  return res.data.data;
}
