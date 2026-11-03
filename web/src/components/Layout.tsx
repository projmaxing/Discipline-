import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  Activity,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Settings,
  Trophy,
  Users,
} from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { Avatar, cx } from './ui'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/habits', label: 'Habits', icon: ListChecks },
  { to: '/friends', label: 'Friends', icon: Users },
  { to: '/leaderboard', label: 'Leaderboard', icon: Trophy },
  { to: '/activity', label: 'Activity', icon: Activity },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Layout() {
  const { profile, signOut } = useAuth()
  const location = useLocation()
  const current = NAV.find((item) => location.pathname.startsWith(item.to))

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[248px] flex-col border-r border-white/[0.06] bg-ink-900/80 backdrop-blur-xl lg:flex">
        <div className="flex items-center gap-3 px-5 pb-6 pt-6">
          <div className="grid h-10 w-10 place-items-center rounded-xl border border-neon/40 bg-neon/15 text-neon">
            <ListChecks size={20} />
          </div>
          <div>
            <div className="font-display text-[15px] font-bold leading-tight text-slate-50">HabitFlow</div>
            <div className="text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-500">Social command center</div>
          </div>
        </div>

        <div className="px-5 pb-2 text-[9px] font-semibold uppercase tracking-[0.18em] text-slate-600">Workspace</div>
        <nav className="flex flex-1 flex-col gap-1 px-3">
          {NAV.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cx(
                    'group relative flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition',
                    isActive
                      ? 'bg-white/[0.06] text-slate-50'
                      : 'text-slate-400 hover:bg-white/[0.03] hover:text-slate-200',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className={cx(
                        'absolute left-0 h-5 w-[3px] rounded-r-full bg-neon transition-opacity',
                        isActive ? 'opacity-100' : 'opacity-0',
                      )}
                    />
                    <Icon size={17} className={isActive ? 'text-neon' : 'text-slate-500 group-hover:text-slate-300'} />
                    {item.label}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>

        <div className="border-t border-white/[0.06] p-3">
          <div className="flex items-center gap-3 rounded-xl px-2 py-2">
            <Avatar name={profile?.display_name ?? 'You'} src={profile?.avatar_url} size={34} />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-slate-100">{profile?.display_name ?? 'Loading'}</div>
              <div className="truncate text-[11px] text-slate-500">@{profile?.username ?? '—'}</div>
            </div>
            <button
              onClick={() => void signOut()}
              title="Sign out"
              className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 transition hover:bg-white/[0.06] hover:text-rose"
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col lg:pl-[248px]">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-white/[0.06] bg-ink-950/70 px-4 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="hidden font-semibold uppercase tracking-[0.16em] sm:inline">HabitFlow</span>
            <span className="hidden text-slate-700 sm:inline">/</span>
            <span className="font-semibold text-slate-300">{current?.label ?? 'Overview'}</span>
          </div>
          <div className="flex items-center gap-3">
            <NavLink
              to="/settings"
              className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-300 transition hover:border-white/20 sm:flex"
            >
              <Avatar name={profile?.display_name ?? 'You'} src={profile?.avatar_url} size={20} />
              @{profile?.username ?? '—'}
            </NavLink>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1180px] flex-1 px-4 pb-24 pt-6 sm:px-6 lg:pb-10">
          <Outlet />
        </main>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-30 flex items-center justify-around border-t border-white/[0.06] bg-ink-900/95 px-2 py-2 backdrop-blur-xl lg:hidden">
        {NAV.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cx(
                  'flex flex-1 flex-col items-center gap-1 rounded-lg py-1.5 text-[10px] font-medium transition',
                  isActive ? 'text-neon' : 'text-slate-500',
                )
              }
            >
              <Icon size={18} />
              {item.label}
            </NavLink>
          )
        })}
      </nav>
    </div>
  )
}
