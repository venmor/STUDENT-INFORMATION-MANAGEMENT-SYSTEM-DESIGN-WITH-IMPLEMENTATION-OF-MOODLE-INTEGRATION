import type { ReactNode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import { AuthProvider } from '@/auth/auth-context'
import type { Session } from '@/auth/auth-storage'

export function AppProviders({
  children,
  initialSession,
}: {
  children: ReactNode
  initialSession?: Session | null
}) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: false,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
          },
          mutations: {
            retry: false,
          },
        },
      }),
  )

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider initialSession={initialSession}>{children}</AuthProvider>
    </QueryClientProvider>
  )
}
