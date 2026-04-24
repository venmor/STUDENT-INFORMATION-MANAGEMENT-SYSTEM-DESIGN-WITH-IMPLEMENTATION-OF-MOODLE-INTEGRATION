import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { getNavigationItems } from '@/app/navigation'
import { useAuth } from '@/auth/auth-context'

export function AppShell() {
  const navigate = useNavigate()
  const { session, logoutUser } = useAuth()

  if (!session) {
    return null
  }

  const navItems = getNavigationItems(session.user.primaryRole)

  return (
    <div className="min-h-screen bg-transparent">
      <div className="mx-auto flex min-h-screen w-full max-w-[1600px] flex-col gap-4 p-4 lg:flex-row lg:p-6">
        <aside className="w-full rounded-[2rem] border border-white/60 bg-[linear-gradient(160deg,rgba(15,23,42,0.94),rgba(15,118,110,0.86))] p-5 text-white shadow-[0_28px_100px_rgba(15,23,42,0.24)] lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)] lg:w-[280px]">
          <div className="mb-8">
            <p className="text-xs uppercase tracking-[0.32em] text-orange-200">Modern SIS</p>
            <h1 className="mt-3 text-2xl font-semibold">{session.user.fullName}</h1>
            <p className="mt-1 text-sm text-slate-200">{session.user.primaryRole}</p>
          </div>

          <nav className="flex flex-wrap gap-2 lg:flex-col">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-2xl px-4 py-3 text-sm transition ${
                    isActive
                      ? 'bg-white text-slate-900 shadow-[0_10px_30px_rgba(255,255,255,0.18)]'
                      : 'bg-white/8 text-slate-100 hover:bg-white/14'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-8 rounded-[1.5rem] border border-white/10 bg-white/8 p-4 text-sm text-slate-100">
            <p className="font-semibold">Route policy</p>
            <p className="mt-2 text-slate-200">
              UI access mirrors the backend role model. Wrong-role routes render a forbidden state instead of
              redirecting to login.
            </p>
          </div>

          <div className="mt-4 flex flex-col gap-3">
            <button
              type="button"
              onClick={() => navigate('/account/password')}
              className="min-h-11 rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-left text-sm text-white transition hover:bg-white/16"
            >
              Change password
            </button>
            <button
              type="button"
              onClick={() => {
                logoutUser()
                navigate('/login', { replace: true })
              }}
              className="min-h-11 rounded-2xl border border-orange-300/30 bg-orange-500/16 px-4 py-3 text-left text-sm text-white transition hover:bg-orange-500/24"
            >
              Sign out
            </button>
          </div>
        </aside>

        <main className="flex-1 pb-8">
          {session.user.mustResetPassword ? (
            <div className="mb-4 rounded-[1.5rem] border border-orange-300 bg-orange-50 px-4 py-4 text-sm text-slate-800">
              This account must change its temporary password before regular use.
            </div>
          ) : null}
          <div className="space-y-5">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
