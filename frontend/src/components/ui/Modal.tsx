import type { ReactNode } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'

export function Modal({
  children,
  description,
  onOpenChange,
  open,
  title,
  trigger,
}: {
  children: ReactNode
  description?: string
  onOpenChange?: (open: boolean) => void
  open?: boolean
  title: string
  trigger?: ReactNode
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      {trigger ? <Dialog.Trigger asChild>{trigger}</Dialog.Trigger> : null}
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[min(100%-2rem,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white p-6 shadow-modal focus:outline-none">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-lg font-semibold text-neutral-900">{title}</Dialog.Title>
              {description ? (
                <Dialog.Description className="mt-1 text-sm text-neutral-500">
                  {description}
                </Dialog.Description>
              ) : null}
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="sm" className="min-w-0 px-2" aria-label="Close dialog">
                <XMarkIcon className="h-4 w-4" />
              </Button>
            </Dialog.Close>
          </div>
          <div className="mt-5">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
