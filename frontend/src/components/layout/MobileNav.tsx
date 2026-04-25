import * as Dialog from '@radix-ui/react-dialog'
import { XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { Sidebar } from '@/components/layout/Sidebar'

export function MobileNav({
  onOpenChange,
  open,
}: {
  onOpenChange: (open: boolean) => void
  open: boolean
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden" />
        <Dialog.Content className="fixed inset-y-0 left-0 z-50 w-72 border-r border-neutral-200 bg-primary text-white shadow-modal focus:outline-none lg:hidden">
          <div className="flex items-center justify-between border-b border-white/10 px-4 py-4">
            <div className="flex items-center gap-3">
              <img src="/sis-logo.svg" alt="" className="h-10 w-10" />
              <div>
                <p className="font-display text-lg font-bold">Student Information System</p>
                <p className="text-sm text-blue-100">Navigation</p>
              </div>
            </div>
            <Dialog.Close asChild>
              <Button variant="ghost" size="sm" className="min-w-0 px-2 text-white hover:bg-white/10">
                <XMarkIcon className="h-5 w-5" />
              </Button>
            </Dialog.Close>
          </div>
          <Sidebar mobile />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
