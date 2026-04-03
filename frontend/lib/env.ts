import { z } from 'zod';

const publicEnvSchema = z.object({
  NEXT_PUBLIC_API_URL: z.string().url().optional(),
});

export type PublicEnv = z.infer<typeof publicEnvSchema>;

export function getPublicEnv(): PublicEnv {
  return publicEnvSchema.parse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  });
}

export function getApiBaseUrl(): string {
  const v = process.env.NEXT_PUBLIC_API_URL;
  if (!v) return 'http://localhost:8000';
  return v.replace(/\/$/, '');
}
