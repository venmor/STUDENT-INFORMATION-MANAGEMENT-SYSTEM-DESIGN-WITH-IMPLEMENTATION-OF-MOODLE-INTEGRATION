import { Panel } from '@/components/ui/panel'

export function RoadmapPanel({
  title,
  requirement,
  description,
}: {
  title: string
  requirement: string
  description: string
}) {
  return (
    <Panel
      title={title}
      description={`Planned but not yet backed by a Phase 2 endpoint. Requirement reference: ${requirement}.`}
    >
      <p className="text-sm text-slate-600">{description}</p>
    </Panel>
  )
}
