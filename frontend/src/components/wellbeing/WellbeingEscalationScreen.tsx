import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { PhoneIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

export function WellbeingEscalationScreen({ onBack }: { onBack: () => void }) {
  return (
    <Card className="p-8 border-red-100 bg-red-50/30">
      <div className="text-center space-y-4">
        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
          <PhoneIcon className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-neutral-900">We're here to help</h2>
        <p className="text-neutral-600 max-w-md mx-auto">
          Thank you for sharing. Based on your check-in, we've notified a Wellbeing Coordinator who
          will reach out to you soon. In the meantime, please consider these resources:
        </p>
      </div>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <div className="p-4 bg-white rounded-xl border border-red-100 space-y-2">
          <p className="font-bold text-neutral-900">University Counseling</p>
          <p className="text-sm text-neutral-500">Available 24/7 for urgent support</p>
          <p className="text-primary font-mono">+260 97 123 4567</p>
        </div>
        <div className="p-4 bg-white rounded-xl border border-red-100 space-y-2">
          <p className="font-bold text-neutral-900">Student Peer Support</p>
          <p className="text-sm text-neutral-500">Confidential chat with trained peers</p>
          <p className="text-primary font-mono">Shortcode: 1234</p>
        </div>
      </div>

      <div className="mt-8 flex justify-center">
        <Button variant="ghost" onClick={onBack}>Return to wellbeing home</Button>
      </div>
    </Card>
  )
}
