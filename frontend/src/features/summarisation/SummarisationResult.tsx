import { useState } from 'react'

import { Button } from '@/components/ui/Button'

interface SummarisationResultProps {
  keyIssues: string[]
  recommendedActions: string[]
  urgencyLevel: string
  onApprove: (output: { key_issues: string[]; recommended_actions: string[]; urgency_level: string }) => void
  onDiscard: () => void
  isApproving: boolean
}

export function SummarisationResult({
  keyIssues,
  recommendedActions,
  urgencyLevel,
  onApprove,
  onDiscard,
  isApproving,
}: SummarisationResultProps) {
  const [issues, setIssues] = useState<string[]>(keyIssues)
  const [actions, setActions] = useState<string[]>(recommendedActions)
  const [urgency, setUrgency] = useState(urgencyLevel)

  const updateItem = (
    list: string[],
    setList: (value: string[]) => void,
    index: number,
    value: string,
  ) => {
    const updated = [...list]
    updated[index] = value
    setList(updated)
  }

  const removeItem = (list: string[], setList: (value: string[]) => void, index: number) => {
    setList(list.filter((_, i) => i !== index))
  }

  const addItem = (list: string[], setList: (value: string[]) => void) => {
    if (list.length < 5) {
      setList([...list, ''])
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm font-medium text-neutral-700">Urgency level</label>
        <select
          className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          value={urgency}
          onChange={(e) => setUrgency(e.target.value)}
          disabled={isApproving}
        >
          <option value="Routine">Routine</option>
          <option value="Follow-up Needed">Follow-up Needed</option>
          <option value="Urgent">Urgent</option>
        </select>
      </div>

      <EditableList
        label="Key issues"
        items={issues}
        onUpdate={(index, value) => updateItem(issues, setIssues, index, value)}
        onRemove={(index) => removeItem(issues, setIssues, index)}
        onAdd={() => addItem(issues, setIssues)}
        disabled={isApproving}
      />

      <EditableList
        label="Recommended actions"
        items={actions}
        onUpdate={(index, value) => updateItem(actions, setActions, index, value)}
        onRemove={(index) => removeItem(actions, setActions, index)}
        onAdd={() => addItem(actions, setActions)}
        disabled={isApproving}
      />

      <div className="flex gap-3">
        <Button
          onClick={() =>
            onApprove({
              key_issues: issues.filter(Boolean),
              recommended_actions: actions.filter(Boolean),
              urgency_level: urgency,
            })
          }
          loading={isApproving}
          disabled={isApproving || issues.filter(Boolean).length === 0}
        >
          Approve and save
        </Button>
        <Button variant="secondary" onClick={onDiscard} disabled={isApproving}>
          Discard
        </Button>
      </div>
    </div>
  )
}

function EditableList({
  label,
  items,
  onUpdate,
  onRemove,
  onAdd,
  disabled,
}: {
  label: string
  items: string[]
  onUpdate: (index: number, value: string) => void
  onRemove: (index: number) => void
  onAdd: () => void
  disabled: boolean
}) {
  return (
    <div>
      <label className="text-sm font-medium text-neutral-700">{label}</label>
      <div className="mt-2 space-y-2">
        {items.map((item, index) => (
          <div key={index} className="flex gap-2">
            <input
              type="text"
              className="flex-1 rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              value={item}
              onChange={(e) => onUpdate(index, e.target.value)}
              disabled={disabled}
            />
            <button
              type="button"
              className="rounded-lg border border-neutral-300 px-2 py-1 text-sm text-neutral-500 hover:bg-neutral-100 disabled:opacity-50"
              onClick={() => onRemove(index)}
              disabled={disabled}
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      {items.length < 5 && (
        <button
          type="button"
          className="mt-2 text-sm text-primary hover:underline disabled:opacity-50"
          onClick={onAdd}
          disabled={disabled}
        >
          + Add item
        </button>
      )}
    </div>
  )
}
