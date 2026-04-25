export function WellbeingEscalationScreen() {
  return (
    <div className="rounded-2xl border border-wellbeing-muted bg-white">
      <div className="rounded-t-2xl bg-danger px-6 py-4 text-white">
        <h3 className="text-xl font-semibold">A support team member has been notified.</h3>
        <p className="mt-2 text-sm text-red-100">
          A member of the wellbeing team will contact you. You do not need to do anything right now.
        </p>
      </div>
      <div className="space-y-3 px-6 py-5 text-sm text-neutral-700">
        <p className="font-semibold">If you need to talk to someone right now:</p>
        <p>University Counselling Centre: +260-21-1-123456</p>
        <p>24-hour helpline: 116</p>
      </div>
    </div>
  )
}
