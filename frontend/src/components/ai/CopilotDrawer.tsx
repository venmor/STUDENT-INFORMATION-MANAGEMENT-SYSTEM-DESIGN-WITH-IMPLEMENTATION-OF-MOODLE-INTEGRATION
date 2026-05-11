import { Link } from 'react-router-dom'
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

export function CopilotDrawer() {
  return (
    <Link
      to="/student/copilot"
      aria-label="Open AI Co-pilot"
      className="fixed bottom-6 right-6 z-30 inline-flex min-h-14 items-center gap-3 rounded-lg bg-primary px-4 text-sm font-semibold text-white shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2"
    >
      <ChatBubbleLeftRightIcon className="h-5 w-5" aria-hidden="true" />
      AI Co-pilot
    </Link>
  )
}
