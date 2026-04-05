import { apiClient } from '@/lib/api/client';
import type { AuthUser } from '@/lib/stores/auth-store';

interface Envelope<T> {
  success: boolean;
  data: T;
  meta?: Record<string, unknown>;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

export async function loginApi(
  email: string,
  password: string
): Promise<TokenPair> {
  const res = await apiClient.post<Envelope<TokenPair>>('/auth/login/', {
    email,
    password,
  });
  return res.data.data;
}

export async function refreshTokenApi(refresh: string): Promise<TokenPair> {
  const res = await apiClient.post<Envelope<TokenPair>>('/auth/refresh/', {
    refresh,
  });
  return res.data.data;
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await apiClient.get<Envelope<AuthUser>>('/auth/me/');
  return res.data.data;
}
