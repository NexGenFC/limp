'use client';

import { useEffect, useRef } from 'react';

import { refreshTokenApi } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/stores/auth-store';

const REFRESH_INTERVAL_MS = 8 * 60 * 1000; // 8 minutes (proactive; access expires at 10)

export function useTokenRefresh() {
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    function scheduleRefresh() {
      if (timerRef.current) clearInterval(timerRef.current);

      timerRef.current = setInterval(async () => {
        const { refreshToken, setTokens, clearSession } =
          useAuthStore.getState();
        if (!refreshToken) return;

        try {
          const pair = await refreshTokenApi(refreshToken);
          setTokens(pair.access, pair.refresh);
        } catch {
          clearSession();
        }
      }, REFRESH_INTERVAL_MS);
    }

    const unsub = useAuthStore.subscribe((state, prev) => {
      if (state.accessToken && !prev.accessToken) {
        scheduleRefresh();
      }
      if (!state.accessToken && prev.accessToken) {
        if (timerRef.current) clearInterval(timerRef.current);
      }
    });

    if (useAuthStore.getState().accessToken) {
      scheduleRefresh();
    }

    return () => {
      unsub();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);
}
