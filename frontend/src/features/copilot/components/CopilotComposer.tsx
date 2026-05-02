import { useRef, useState } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'

const MAX_QUESTION_LENGTH = 1000

export function CopilotComposer({
  disabled,
  onSubmit,
}: {
  disabled: boolean
  onSubmit: (question: string) => void
}) {
  const [question, setQuestion] = useState('')
  const [error, setError] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const canSend = question.trim().length > 0 && question.length <= MAX_QUESTION_LENGTH && !disabled

  function submit() {
    const cleaned = question.trim()
    if (!cleaned) {
      setError('Enter a question before sending.')
      return
    }
    if (cleaned.length > MAX_QUESTION_LENGTH) {
      setError(`Question must be ${MAX_QUESTION_LENGTH} characters or fewer.`)
      return
    }
    setError('')
    onSubmit(cleaned)
    setQuestion('')
    window.setTimeout(() => textareaRef.current?.focus(), 0)
  }

  return (
    <form
      className="sticky bottom-0 rounded-lg border border-neutral-200 bg-white p-4 shadow-card"
      onSubmit={(event) => {
        event.preventDefault()
        submit()
      }}
    >
      <label htmlFor="copilot-question" className="block text-sm font-semibold text-neutral-800">
        Ask the AI co-pilot
      </label>
      <textarea
        ref={textareaRef}
        id="copilot-question"
        className="mt-2 min-h-24 w-full resize-y rounded-lg border border-neutral-300 px-4 py-3 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
        placeholder="Ask about registration, deadlines, grades, documents, or academic rules..."
        value={question}
        disabled={disabled}
        maxLength={MAX_QUESTION_LENGTH + 1}
        aria-describedby="copilot-question-hint copilot-question-error"
        onChange={(event) => {
          setQuestion(event.target.value)
          setError('')
        }}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault()
            submit()
          }
        }}
      />
      <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p id="copilot-question-hint" className="text-xs text-neutral-500">
            Press Enter to send, Shift+Enter for a new line.
          </p>
          {error ? (
            <p id="copilot-question-error" role="alert" className="mt-1 text-sm text-danger">
              {error}
            </p>
          ) : null}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-neutral-500">{question.length}/{MAX_QUESTION_LENGTH}</span>
          <Button type="submit" disabled={!canSend} icon={<PaperAirplaneIcon className="h-4 w-4" aria-hidden="true" />}>
            Send
          </Button>
        </div>
      </div>
    </form>
  )
}
