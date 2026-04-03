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
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  clearSession: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      setSession: (token, user) => set({ accessToken: token, user }),
      clearSession: () => set({ accessToken: null, user: null }),
    }),
    {
      name: 'limp-auth',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
      }),
      skipHydration: true,
    },
  ),
);
