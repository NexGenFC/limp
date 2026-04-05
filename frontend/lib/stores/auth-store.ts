import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

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
  refreshToken: string | null;
  user: AuthUser | null;
  setSession: (access: string, refresh: string, user: AuthUser) => void;
  setTokens: (access: string, refresh: string) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setSession: (access, refresh, user) =>
        set({ accessToken: access, refreshToken: refresh, user }),
      setTokens: (access, refresh) =>
        set({ accessToken: access, refreshToken: refresh }),
      clearSession: () =>
        set({ accessToken: null, refreshToken: null, user: null }),
    }),
    {
      name: 'limp-auth',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
      skipHydration: true,
    }
  )
);
