import { create } from 'zustand';

export type UserRole =
  | 'FOUNDER'
  | 'MANAGEMENT'
  | 'IN_HOUSE_ADVOCATE'
  | 'EXTERNAL_ADVOCATE'
  | 'REVENUE_TEAM'
  | 'SURVEYOR_INHOUSE'
  | 'SURVEYOR_FREELANCE'
  | 'FIELD_STAFF';

export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  role: UserRole;
}

type AuthState = {
  accessToken: string | null;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  setSession: (token, user) => set({ accessToken: token, user }),
  clearSession: () => set({ accessToken: null, user: null }),
}));
