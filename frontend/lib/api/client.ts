import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

import { getApiBaseUrl } from '@/lib/env';
import { useAuthStore } from '@/lib/stores/auth-store';

export const apiClient = axios.create({
  baseURL: `${getApiBaseUrl()}/api/v1`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue: {
  resolve: (v: unknown) => void;
  reject: (e: unknown) => void;
  config: InternalAxiosRequestConfig;
}[] = [];

function processQueue(newAccess: string | null) {
  pendingQueue.forEach(({ resolve, reject, config }) => {
    if (newAccess) {
      config.headers.Authorization = `Bearer ${newAccess}`;
      resolve(apiClient(config));
    } else {
      reject(new Error('refresh_failed'));
    }
  });
  pendingQueue = [];
}

apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const originalConfig = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };
    if (
      error.response?.status === 401 &&
      originalConfig &&
      !originalConfig._retry &&
      !originalConfig.url?.includes('/auth/login') &&
      !originalConfig.url?.includes('/auth/refresh')
    ) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject, config: originalConfig });
        });
      }
      originalConfig._retry = true;
      isRefreshing = true;

      const store = useAuthStore.getState();
      const refresh = store.refreshToken;
      if (!refresh) {
        store.clearSession();
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(
          `${getApiBaseUrl()}/api/v1/auth/refresh/`,
          { refresh },
          { headers: { 'Content-Type': 'application/json' } }
        );
        const data = res.data?.data ?? res.data;
        const newAccess: string = data.access;
        const newRefresh: string = data.refresh ?? refresh;
        store.setTokens(newAccess, newRefresh);
        originalConfig.headers.Authorization = `Bearer ${newAccess}`;
        processQueue(newAccess);
        return apiClient(originalConfig);
      } catch {
        store.clearSession();
        processQueue(null);
        return Promise.reject(error);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.status === 401) {
      useAuthStore.getState().clearSession();
    }
    return Promise.reject(error);
  }
);
