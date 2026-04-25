import * as SelectPrimitive from '@radix-ui/react-select'
import { CheckIcon, ChevronDownIcon } from '@heroicons/react/24/solid'

import { cn } from '@/utils/cn'

export function Select({
  id,
  items,
  label,
  onValueChange,
  placeholder,
  value,
}: {
  id?: string
  items: Array<{ label: string; value: string }>
  label: string
  onValueChange: (value: string) => void
  placeholder?: string
  value?: string
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-neutral-700">
        {label}
      </label>
      <SelectPrimitive.Root value={value} onValueChange={onValueChange}>
        <SelectPrimitive.Trigger
          id={id}
          className={cn(
            'flex w-full items-center justify-between rounded-lg border border-neutral-300 bg-white px-4 py-2.5 text-left text-neutral-900',
            'focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none',
          )}
        >
          <SelectPrimitive.Value placeholder={placeholder} />
          <SelectPrimitive.Icon>
            <ChevronDownIcon className="h-4 w-4 text-neutral-500" />
          </SelectPrimitive.Icon>
        </SelectPrimitive.Trigger>
        <SelectPrimitive.Portal>
          <SelectPrimitive.Content
            position="popper"
            className="z-50 overflow-hidden rounded-lg border border-neutral-200 bg-white shadow-modal"
          >
            <SelectPrimitive.Viewport className="p-1">
              {items.map((item) => (
                <SelectPrimitive.Item
                  key={item.value}
                  value={item.value}
                  className="relative flex cursor-pointer select-none items-center rounded-md py-2 pl-8 pr-3 text-sm text-neutral-900 outline-none data-[highlighted]:bg-primary-light"
                >
                  <SelectPrimitive.ItemIndicator className="absolute left-2 inline-flex items-center">
                    <CheckIcon className="h-4 w-4 text-primary" />
                  </SelectPrimitive.ItemIndicator>
                  <SelectPrimitive.ItemText>{item.label}</SelectPrimitive.ItemText>
                </SelectPrimitive.Item>
              ))}
            </SelectPrimitive.Viewport>
          </SelectPrimitive.Content>
        </SelectPrimitive.Portal>
      </SelectPrimitive.Root>
    </div>
  )
}
