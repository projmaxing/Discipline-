import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  Activity,
  ChevronRight,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Settings,
  Swords,
  Trophy,
  Users,
  Zap,
} from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { Avatar, cx } from './ui'

const NAV = [
  { to: '/dashboard', label: 'Command', icon: LayoutDashboard },
  { to: '/habits', label: 'Quests', icon: ListChecks },
  { to: '/friends', label: 'Squad', icon: Users },
  { to: '/leaderboard', label: 'Ladder', icon: Trophy },
  { to: '/activity', label: 'Feed', icon: Activity },
]

const MOBILE_NAV = NAV

export function Layout() {
  const { profile, signOut } = useAuth()
  const location = useLocation()
  const current = [...NAV, { to: '/settings', label: 'Settings', icon: Settings }].find((item) =>
    location.pathname.startsWith(item.to),
  )

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[260px] flex-col border-r border-white/[0.06] bg-ink-950/80 backdrop-blur-2xl lg:flex">
        <div className="px-5 pb-5 pt-6">
          <NavLink to="/dashboard" className="flex items-center gap-3">
            <span className="relative grid h-10 w-10 place-items-center overflow-hidden rounded-xl bg-neon-sweep text-[#04121B] shadow-neon">
              <Swords size={19} strokeWidth={2.5} />
            </span>
            <span>
              <span className="block font-display text-[15px] font-extrabold tracking-tight text-slate-50">
                HabitFlow
              </span>
              <span className="block text-[9px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                Command center
              </span>
            </span>
          </NavLink>
        </div>

        <div className="mx-3 mb-4 rounded-xl2 border border-white/[0.07] bg-white/[0.025] p-3">
          <div className="flex items-center gap-3">
            <Avatar name={profile?.display_name ?? 'You'} src={profile?.avatar_url} size={38} ring />
            <div className="min-w-0 flex-1">
              <div className="truncate text-[13px] font-semibold text-slate-100">
                {profile?.display_name ?? 'Loading'}
              </div>
              <div className="truncate font-mono text-[10px] text-slate-500">@{profile?.username ?? '—'}</div>
            </div>
            <NavLink
              to="/settings"
              aria-label="Settings"
              className="grid h-7 w-7 place-items-center rounded-lg text-slate-500 transition hover:bg-white/[0.06] hover:text-slate-200"
            >
              <Settings size={14} />
            </NavLink>
          </div>
          <div className="mt-3 flex items-center justify-between text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-600">
            <span className="inline-flex items-center gap-1.5 text-cyan">
              <Zap size={10} /> Ranked season
            </span>
            <span>01</span>
          </div>
        </div>

        <div className="px-5 pb-2 text-[9px] font-semibold uppercase tracking-[0.24em] text-slate-600">Navigate</div>
        <nav className="flex flex-1 flex-col gap-1 px-3">
          {NAV.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cx(
                    'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-semibold transition',
                    isActive
                      ? 'bg-gradient-to-r from-neon/[0.16] to-transparent text-slate-50'
                      : 'text-slate-400 hover:bg-white/[0.03] hover:text-slate-200',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className={cx(
                        'absolute left-0 h-6 w-[2px] rounded-r-full bg-cyan transition-all',
                        isActive ? 'opacity-100 shadow-[0_0_12px_#38E8FF]' : 'opacity-0',
                      )}
                    />
                    <Icon size={17} className={isActive ? 'text-cyan' : 'text-slate-500 group-hover:text-slate-300'} />
                    <span className="flex-1">{item.label}</span>
                    {isActive ? <ChevronRight size={13} className="text-cyan/70" /> : null}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>

        <div className="border-t border-white/[0.06] p-3">
          <button
            onClick={() => void signOut()}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium text-slate-500 transition hover:bg-rose/10 hover:text-rose"
          >
            <LogOut size={15} /> Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col lg:pl-[260px]">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-white/[0.06] bg-ink-950/70 px-4 backdrop-blur-2xl sm:px-6">
          <div className="flex min-w-0 items-center gap-2.5">
            <span className="hidden h-4 w-[2px] rounded-full bg-gradient-to-b from-cyan to-violet sm:block" />
            <span className="truncate font-display text-sm font-bold tracking-tight text-slate-100">
              {current?.label ?? 'Overview'}
            </span>
            <span className="hidden font-mono text-[10px] uppercase tracking-[0.2em] text-slate-600 sm:inline">
              / habitflow
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="chip-live hidden sm:inline-flex">
              <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-mint" /> Live
            </span>
            <NavLink
              to="/settings"
              className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-2 py-1.5 pr-3 text-[11px] text-slate-300 transition hover:border-white/20"
            >
              <Avatar name={profile?.display_name ?? 'You'} src={profile?.avatar_url} size={22} />
              <span className="font-mono">@{profile?.username ?? '—'}</span>
            </NavLink>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1180px] flex-1 px-4 pb-28 pt-6 sm:px-6 lg:pb-10">
          <Outlet />
        </main>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-white/[0.07] bg-ink-950/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-2xl lg:hidden">
        <div className="flex items-stretch justify-around px-1 py-1.5">
          {MOBILE_NAV.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cx(
                    'relative flex flex-1 flex-col items-center gap-1 rounded-lg py-1.5 text-[9px] font-semibold uppercase tracking-[0.08em] transition',
                    isActive ? 'text-cyan' : 'text-slate-500',
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive ? (
                      <span className="absolute -top-1.5 h-[2px] w-6 rounded-full bg-cyan shadow-[0_0_12px_#38E8FF]" />
                    ) : null}
                    <Icon size={18} />
                    {item.label}
                  </>
                )}
              </NavLink>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
