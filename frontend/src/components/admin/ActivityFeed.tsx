import type { ReactNode } from 'react'

export function ActivityFeed({ items }: { items: ReactNode[] }) {
  return <div className="space-y-3">{items.map((item, index) => <div key={index}>{item}</div>)}</div>
}
