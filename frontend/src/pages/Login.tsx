import { ShieldCheckIcon } from '@heroicons/react/24/outline'

import { LoginForm } from '@/components/auth/LoginForm'

export function LoginPage() {
  return (
    <div className="min-h-screen bg-neutral-50 lg:grid lg:grid-cols-2">
      <section className="hidden bg-primary px-10 py-14 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="max-w-lg">
          <div className="inline-flex items-center gap-4 rounded-2xl border border-white/10 bg-white/10 px-5 py-4">
            <img src="/sis-logo.svg" alt="" className="h-14 w-14" />
            <div>
              <p className="font-display text-3xl font-bold">Student Information System</p>
              <p className="mt-1 text-sm uppercase tracking-[0.2em] text-blue-100">Academic operations portal</p>
            </div>
          </div>
          <p className="mt-8 text-lg text-blue-100">
            Built for real academic records, controlled grade workflows, and role-specific accountability across
            the institution.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/8 p-6">
          <ShieldCheckIcon className="h-10 w-10" />
          <p className="mt-4 text-base font-semibold">Institution-ready academic record management</p>
          <p className="mt-2 text-sm text-blue-100">
            Built for real student records, real grades, and role-specific accountability.
          </p>
        </div>
      </section>
      <section className="flex items-center justify-center px-4 py-10 sm:px-6">
        <div className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white p-8 shadow-card">
          <div className="mb-8 inline-flex items-center gap-3 lg:hidden">
            <img src="/sis-logo.svg" alt="" className="h-12 w-12" />
            <div>
              <p className="font-display text-xl font-bold text-neutral-900">Student Information System</p>
              <p className="text-xs uppercase tracking-[0.16em] text-neutral-500">Academic operations portal</p>
            </div>
          </div>
          <h1 className="font-display text-2xl font-bold text-neutral-900">Sign in to the SIS</h1>
          <p className="mt-2 text-sm text-neutral-500">
            Use your issued account to access your role-specific dashboard.
          </p>
          <div className="mt-8">
            <LoginForm />
          </div>
          <p className="mt-6 text-center text-sm text-neutral-500">
            New applicant?{' '}
            <a href="/apply" className="font-medium text-primary hover:underline">
              Apply for admission
            </a>
          </p>
        </div>
      </section>
    </div>
  )
}
