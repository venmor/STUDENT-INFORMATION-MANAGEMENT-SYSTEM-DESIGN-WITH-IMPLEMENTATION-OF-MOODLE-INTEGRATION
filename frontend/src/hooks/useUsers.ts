import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createUser, deactivateUser, getUsers, resetUserPassword } from '@/api/users'

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: getUsers,
  })
}

export function useUserMutations() {
  const queryClient = useQueryClient()

  return {
    createUser: useMutation({
      mutationFn: createUser,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
    }),
    deactivateUser: useMutation({
      mutationFn: deactivateUser,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
    }),
    resetUserPassword: useMutation({
      mutationFn: ({ userId, newPassword }: { userId: number; newPassword: string }) =>
        resetUserPassword(userId, newPassword),
    }),
  }
}
