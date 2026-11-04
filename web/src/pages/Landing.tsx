import { Link } from 'react-router-dom'
import { ArrowRight, ChevronRight, Crown, Flame, Lock, ShieldCheck, Swords, Trophy, Users, Zap } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { isConfigured } from '../lib/supabase'
import { ProgressRing } from '../components/ui'

const FEATURES = [
  {
    icon: Flame,
    title: 'Streaks that bite',
    body: 'Perfect days stack into streaks, and a single missed day resets the run. The chain is the game.',
    tone: '#FFB84D',
  },
  {
    icon: Users,
    title: 'Squad, not followers',
    body: 'Mutual requests only. Compare consistency with people who actually know you.',
    tone: '#38E8FF',
  },
  {
    icon: Trophy,
    title: 'Ranked ladder',
    body: 'Points come from validated completions, computed by the database — never by the browser.',
    tone: '#C4B0FF',
  },
  {
    icon: ShieldCheck,
    title: 'Private by default',
    body: 'Friends get aggregates. Habit names, notes and schedules never leave your account.',
    tone: '#3CE6A0',
  },
]

const DEMO_QUESTS = [
  { name: 'Morning run', xp: '+10 XP', done: true },
  { name: 'Deep work block', xp: '+10 XP', done: true },
  { name: 'Read 20 pages', xp: '+10 XP', done: true },
  { name: 'Sleep before midnight', xp: '+10 XP', done: false },
]

const DEMO_LADDER = [
  { rank: 1, name: 'you', points: '1240' },
  { rank: 2, name: 'mara', points: '1180' },
  { rank: 3, name: 'dev', points: '960' },
]

export function Landing() {
  const { session } = useAuth()
  const primaryTo = isConfigured ? (session ? '/dashboard' : '/register') : '/setup'
  const primaryLabel = isConfigured ? (session ? 'Enter command center' : 'Start season 01') : 'Connect backend'

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <Link to="/" className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-neon-sweep text-[#04121B] shadow-neon">
            <Swords size={19} strokeWidth={2.5} />
          </span>
          <span>
            <span className="block font-display text-[15px] font-extrabold tracking-tight text-slate-50">HabitFlow</span>
            <span className="block text-[9px] font-semibold uppercase tracking-[0.24em] text-slate-500">
              Social command center
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-2">
          {isConfigured ? (
            session ? (
              <Link to="/dashboard" className="btn-primary">
                Command center <ArrowRight size={15} />
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn-ghost">
                  Sign in
                </Link>
                <Link to="/register" className="btn-primary">
                  Play now
                </Link>
              </>
            )
          ) : (
            <>
              <span className="chip-live hidden sm:inline-flex">
                <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-mint" /> Preview
              </span>
              <Link to="/setup" className="btn-ghost">
                <Lock size={14} /> Setup
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-5 pb-20">
        <section className="rise grid gap-12 py-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:py-16">
          <div>
            <span className="chip border-cyan/25 bg-cyan/10 text-cyan">
              <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-cyan" /> Season 01 · live ladder
            </span>
            <h1 className="mt-5 font-display text-[2.7rem] font-extrabold leading-[1.02] tracking-tight text-slate-50 sm:text-6xl">
              Discipline is a
              <span className="glow-text"> multiplayer game</span>.
            </h1>
            <p className="mt-5 max-w-xl text-sm leading-relaxed text-slate-400">
              Turn your routines into quests, stack perfect days into streaks, and defend your rank against a squad
              that actually knows you. Private by design — nobody sees your habit names.
            </p>

            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link to={primaryTo} className="btn-primary">
                {primaryLabel} <ChevronRight size={16} />
              </Link>
              {isConfigured ? (
                <Link to="/login" className="btn-ghost">
                  I already play
                </Link>
              ) : (
                <Link to="/setup" className="btn-ghost">
                  What do I need?
                </Link>
              )}
            </div>

            {!isConfigured ? (
              <p className="mt-4 max-w-md text-[11px] leading-relaxed text-amber/80">
                Preview build — the interface is live, but accounts and persistence activate once a Supabase project is
                connected. Nothing here pretends to save data.
              </p>
            ) : null}

            <dl className="mt-8 grid max-w-md grid-cols-3 gap-3">
              {[
                ['10 XP', 'per quest'],
                ['50 XP', 'perfect day'],
                ['0', 'habit names shared'],
              ].map(([value, label]) => (
                <div key={label} className="tile p-3" style={{ ['--tone' as string]: 'rgba(76,141,255,.6)' } as never}>
                  <dt className="font-display text-lg font-extrabold text-slate-50">{value}</dt>
                  <dd className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-slate-500">{label}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="hud relative overflow-hidden p-5 sm:p-6">
            <div className="pointer-events-none absolute -right-20 -top-24 h-56 w-56 animate-drift rounded-full bg-neon/25 blur-3xl" />
            <div className="relative flex items-center justify-between">
              <div>
                <div className="font-mono text-[9px] uppercase tracking-[0.24em] text-cyan">Today · quest log</div>
                <div className="mt-1 font-display text-xl font-extrabold text-slate-50">Season run</div>
                <div className="mt-1 flex items-center gap-1.5 text-[11px] text-amber">
                  <Flame size={12} /> 12-day streak
                </div>
              </div>
              <ProgressRing pct={86} size={112} stroke={9} caption="complete" />
            </div>

            <div className="relative mt-5 space-y-2">
              {DEMO_QUESTS.map((quest) => (
                <div key={quest.name} className="flex items-center gap-3 rounded-xl border border-white/[0.07] bg-white/[0.025] px-3 py-2.5">
                  <span
                    className={
                      quest.done
                        ? 'grid h-6 w-6 place-items-center rounded-md bg-mint text-[#04121B] shadow-[0_0_14px_rgba(60,230,160,.5)]'
                        : 'h-6 w-6 rounded-md border border-white/20 bg-black/40'
                    }
                  >
                    {quest.done ? <span className="text-[11px] font-bold">✓</span> : null}
                  </span>
                  <span className={quest.done ? 'flex-1 text-xs text-slate-400 line-through' : 'flex-1 text-xs text-slate-200'}>
                    {quest.name}
                  </span>
                  <span className="font-mono text-[9px] text-cyan">{quest.xp}</span>
                </div>
              ))}
            </div>

            <div className="relative mt-5">
              <div className="flex items-center justify-between text-[9px] font-semibold uppercase tracking-[0.16em]">
                <span className="text-cyan">Lv 6 · Strategist</span>
                <span className="font-mono text-slate-500">420/500 XP</span>
              </div>
              <div className="xp-track mt-2">
                <span className="xp-fill" style={{ width: '84%' }} />
              </div>
            </div>

            <div className="relative mt-5">
              <div className="divider-glow mb-3" />
              <div className="space-y-1.5">
                {DEMO_LADDER.map((row) => (
                  <div key={row.rank} className="flex items-center gap-2.5 text-[11px]">
                    <span className="grid h-5 w-5 place-items-center rounded-md border border-white/10 font-mono text-[9px] text-slate-400">
                      {row.rank}
                    </span>
                    <span className={row.name === 'you' ? 'flex-1 font-semibold text-cyan' : 'flex-1 text-slate-400'}>
                      @{row.name}
                    </span>
                    <span className="font-mono text-slate-300">{row.points}</span>
                    {row.rank === 1 ? <Crown size={12} className="text-gold" /> : null}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => {
            const Icon = feature.icon
            return (
              <div key={feature.title} className="tile p-4" style={{ ['--tone' as string]: feature.tone } as never}>
                <span
                  className="grid h-9 w-9 place-items-center rounded-xl border"
                  style={{ borderColor: `${feature.tone}44`, background: `${feature.tone}14`, color: feature.tone }}
                >
                  <Icon size={16} />
                </span>
                <h2 className="mt-3 font-display text-sm font-bold text-slate-100">{feature.title}</h2>
                <p className="mt-1 text-[11px] leading-relaxed text-slate-500">{feature.body}</p>
              </div>
            )
          })}
        </section>

        <section className="hud relative mt-10 overflow-hidden p-7 text-center sm:p-10">
          <div className="pointer-events-none absolute inset-x-0 -bottom-24 h-48 bg-neon/10 blur-3xl" />
          <h2 className="relative font-display text-2xl font-extrabold text-slate-50 sm:text-3xl">
            Your streak is waiting.
          </h2>
          <p className="relative mx-auto mt-2 max-w-lg text-xs leading-relaxed text-slate-400">
            One quest today is enough to start. Twelve days from now it is a rank.
          </p>
          <div className="relative mt-6 flex flex-wrap justify-center gap-3">
            <Link to={primaryTo} className="btn-primary">
              <Zap size={15} /> {primaryLabel}
            </Link>
            <Link to="/setup" className="btn-ghost">
              How it works
            </Link>
          </div>
        </section>

        <footer className="mt-8 flex flex-wrap items-center justify-between gap-2 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
          <span>HabitFlow · social command center</span>
          <span className="inline-flex items-center gap-1.5">
            <ShieldCheck size={11} /> row level security
          </span>
        </footer>
      </main>
    </div>
  )
}
