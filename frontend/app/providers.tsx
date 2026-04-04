'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { useAuthStore } from '@/lib/stores/auth-store';
import { useTokenRefresh } from '@/lib/hooks/use-token-refresh';

function TokenRefreshGate() {
  useTokenRefresh();
  return null;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
          },
        },
      })
  );

  useEffect(() => {
    const p = useAuthStore.persist;
    if (p) void p.rehydrate();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <TokenRefreshGate />
      {children}
    </QueryClientProvider>
  );
}
