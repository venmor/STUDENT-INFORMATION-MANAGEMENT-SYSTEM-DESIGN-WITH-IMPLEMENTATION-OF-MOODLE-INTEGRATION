import { EyeIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/stores/authStore'

export function ImpersonationBanner() {
  const impersonating = useAuthStore((s) => s.impersonating)
  const stopImpersonation = useAuthStore((s) => s.stopImpersonation)

  if (!impersonating) return null

  return (
    <div className="flex items-center justify-between bg-red-600 px-4 py-2 text-white">
      <div className="flex items-center gap-2">
        <EyeIcon className="h-5 w-5" />
        <span className="text-sm font-medium">
          Viewing as {impersonating.fullName || impersonating.username} ({impersonating.primaryRole}) — Read Only
        </span>
      </div>
      <Button
        size="sm"
        variant="outline"
        className="border-white text-white hover:bg-white/10"
        onClick={stopImpersonation}
      >
        Stop
      </Button>
    </div>
  )
}
