import * as RadixToast from '@radix-ui/react-toast'
import { XMarkIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'

import { useToast, type ToastVariant } from '@/hooks/useToast'
import { cn } from '@/utils/cn'

const variantStyles: Record<ToastVariant, string> = {
  success: 'border-l-4 border-l-success bg-white',
  error: 'border-l-4 border-l-danger bg-white',
  warning: 'border-l-4 border-l-warning bg-white',
  info: 'border-l-4 border-l-info bg-white',
}

const variantIcons: Record<ToastVariant, typeof CheckCircleIcon> = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
}

const variantIconColors: Record<ToastVariant, string> = {
  success: 'text-success',
  error: 'text-danger',
  warning: 'text-warning',
  info: 'text-info',
}

export function ToastViewport() {
  const { toasts, removeToast } = useToast()

  return (
    <RadixToast.Provider duration={5000}>
      {toasts.map((toast) => {
        const Icon = variantIcons[toast.variant]
        return (
          <RadixToast.Root
            key={toast.id}
            open
            onOpenChange={(open) => { if (!open) removeToast(toast.id) }}
            className={cn(
              'pointer-events-auto flex items-start gap-3 rounded-card p-4 shadow-lg',
              'data-[state=open]:animate-in data-[state=open]:slide-in-from-right',
              'data-[state=closed]:animate-out data-[state=closed]:fade-out',
              variantStyles[toast.variant],
            )}
          >
            <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', variantIconColors[toast.variant])} />
            <div className="flex-1">
              <RadixToast.Title className="text-sm font-semibold text-neutral-900">
                {toast.title}
              </RadixToast.Title>
              {toast.description && (
                <RadixToast.Description className="mt-1 text-sm text-neutral-500">
                  {toast.description}
                </RadixToast.Description>
              )}
            </div>
            <RadixToast.Close className="rounded p-1 text-neutral-400 hover:text-neutral-600">
              <XMarkIcon className="h-4 w-4" />
            </RadixToast.Close>
          </RadixToast.Root>
        )
      })}
      <RadixToast.Viewport className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-80 flex-col gap-2" />
    </RadixToast.Provider>
  )
}
