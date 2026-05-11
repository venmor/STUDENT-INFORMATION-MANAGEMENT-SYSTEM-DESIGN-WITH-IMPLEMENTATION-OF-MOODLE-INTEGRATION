import * as Tabs from '@radix-ui/react-tabs'

import type { CourseSection } from '@/types'

export function SectionTabs({
  onChange,
  sections,
  value,
}: {
  onChange: (sectionId: string) => void
  sections: CourseSection[]
  value: string
}) {
  return (
    <Tabs.Root value={value} onValueChange={onChange}>
      <Tabs.List className="flex flex-wrap gap-2">
        {sections.map((section) => (
          <Tabs.Trigger
            key={section.id}
            value={section.id}
            className="rounded-full border border-neutral-200 bg-white px-4 py-2 text-sm font-medium text-neutral-700 data-[state=active]:border-primary data-[state=active]:bg-primary data-[state=active]:text-white"
          >
            {section.course_code}-{section.section_code}
          </Tabs.Trigger>
        ))}
      </Tabs.List>
    </Tabs.Root>
  )
}
