import { useState } from 'react'
import { QuickExitButton } from '@/components/wellbeing/QuickExitButton'
import { WellbeingCheckInForm } from '@/components/wellbeing/WellbeingCheckInForm'
import { WellbeingConsentPage } from '@/components/wellbeing/WellbeingConsentPage'
import { WellbeingEscalationScreen } from '@/components/wellbeing/WellbeingEscalationScreen'
import { useWellbeingConsent, useWellbeingHistory } from '@/hooks/useWellbeing'
import { Card, CardTitle } from '@/components/ui/Card'
import { formatDate } from '@/utils/formatters'
import type { WellbeingCheckIn } from '@/api/wellbeing'

export function StudentWellbeingPage() {
  const { data: consent, isLoading: isConsentLoading } = useWellbeingConsent()
  const { data: history = [] } = useWellbeingHistory()
  const [view, setView] = useState<'home' | 'escalate' | 'success'>('home')

  const handleComplete = (result: WellbeingCheckIn) => {
    if (result.triage_class === 'ESCALATE') {
      setView('escalate')
    } else {
      setView('success')
      setTimeout(() => setView('home'), 3000)
    }
  }

  if (isConsentLoading) {
    return <div className="animate-pulse h-64 bg-neutral-100 rounded-2xl" />
  }

  return (
    <div className="min-h-[70vh] rounded-2xl bg-wellbeing-soft px-4 py-8">
      <div className="relative mx-auto max-w-4xl space-y-6 pt-12">
        <QuickExitButton />

        {view === 'escalate' ? (
          <WellbeingEscalationScreen onBack={() => setView('home')} />
        ) : (
          <>
            {!consent?.is_enabled && (
              <WellbeingConsentPage onEnabled={() => setView('home')} />
            )}

            {consent?.is_enabled && view === 'home' && (
              <WellbeingCheckInForm onComplete={handleComplete} />
            )}

            {view === 'success' && (
              <Card className="p-8 text-center bg-green-50 border-green-100">
                <h3 className="text-xl font-bold text-green-800">Thank you</h3>
                <p className="text-green-700 mt-2">Your check-in has been received.</p>
              </Card>
            )}

            {consent?.is_enabled && history.length > 0 && (
              <Card>
                <CardTitle>Recent History</CardTitle>
                <div className="mt-4 space-y-3">
                  {history.slice(0, 5).map((item) => (
                    <div key={item.id} className="flex justify-between items-center py-2 border-b border-neutral-100 last:border-0">
                      <div>
                        <span className="font-medium text-neutral-900">Rating: {item.mood_rating}/5</span>
                        <span className="ml-3 text-xs text-neutral-500">{formatDate(item.created_at)}</span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        item.triage_class === 'ESCALATE' ? 'bg-red-100 text-red-700' :
                        item.triage_class === 'CONCERNING' ? 'bg-amber-100 text-amber-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {item.triage_class}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  )
}
