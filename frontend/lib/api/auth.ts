import { apiClient } from '@/lib/api/client';
import type { AuthUser } from '@/lib/stores/auth-store';

interface LoginResponse {
  access: string;
  refresh: string;
}

interface MeResponse {
  success: boolean;
  data: AuthUser;
}

export async function loginApi(
  email: string,
  password: string,
): Promise<{ access: string; refresh: string }> {
  const res = await apiClient.post<LoginResponse>('/auth/login/', {
    email,
    password,
  });
  return res.data;
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await apiClient.get<MeResponse>('/auth/me/');
  return res.data.data;
}
