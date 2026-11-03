import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Flame, ShieldCheck, Sparkles, Trophy, Users } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'

const FEATURES = [
  {
    icon: Flame,
    title: 'Streaks that hold you',
    body: 'Perfect days build streaks, and streaks become the score you defend.',
  },
  {
    icon: Users,
    title: 'Friends, not followers',
    body: 'Mutual friend requests only. Compare consistency without exposing habit names.',
  },
  {
    icon: Trophy,
    title: 'Trusted leaderboards',
    body: 'Scores are derived from logged completions by the database, never the browser.',
  },
  {
    icon: ShieldCheck,
    title: 'Row Level Security',
    body: 'Every table is protected by policies, and friends only ever receive aggregates.',
  },
]

export function Landing() {
  const { session } = useAuth()
  const [ready] = useState(true)

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl border border-neon/40 bg-neon/15 text-neon">
            <Sparkles size={17} />
          </div>
          <div>
            <div className="font-display text-sm font-bold text-slate-50">HabitFlow</div>
            <div className="text-[9px] uppercase tracking-[0.18em] text-slate-500">Social command center</div>
          </div>
        </div>
        <nav className="flex items-center gap-2">
          {session ? (
            <Link to="/dashboard" className="btn-primary">
              Open dashboard <ArrowRight size={15} />
            </Link>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">
                Sign in
              </Link>
              <Link to="/register" className="btn-primary">
                Create account
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="mx-auto max-w-6xl px-5 pb-20">
        <section className="rise grid gap-10 py-14 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <span className="chip mb-5">
              <Flame size={12} className="text-amber" /> Discipline, with witnesses
            </span>
            <h1 className="font-display text-4xl font-bold leading-[1.05] text-slate-50 sm:text-5xl">
              Turn consistency into a
              <span className="bg-gradient-to-r from-neon via-cyan to-violet-soft bg-clip-text text-transparent"> leaderboard</span>.
            </h1>
            <p className="mt-5 max-w-xl text-sm leading-relaxed text-slate-400">
              HabitFlow is a habit tracker with a social layer that respects your privacy. Track daily habits and
              streaks, add real friends, and compare completion rates — never raw habit names.
            </p>
            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link to={session ? '/dashboard' : '/register'} className="btn-primary">
                {session ? 'Go to dashboard' : 'Start tracking'} <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="btn-ghost">
                I already have an account
              </Link>
            </div>
            <p className="mt-4 text-[11px] text-slate-600">
              {ready ? 'No credit card, no ads, no public habit titles.' : ''}
            </p>
          </div>

          <div className="glass p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[10px] uppercase tracking-[0.16em] text-cyan">Today's progress</div>
                <div className="mt-1 font-display text-3xl font-bold text-slate-50">86%</div>
              </div>
              <div className="grid h-16 w-16 place-items-center rounded-full border-4 border-neon/30 border-t-neon text-xs font-semibold text-slate-200">
                6/7
              </div>
            </div>
            <div className="mt-5 space-y-2.5">
              {[
                ['Morning run', true],
                ['Deep work block', true],
                ['Read 20 pages', true],
                ['Sleep before midnight', false],
              ].map(([label, done]) => (
                <div
                  key={String(label)}
                  className="flex items-center gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3 py-2.5"
                >
                  <span
                    className={
                      done
                        ? 'grid h-5 w-5 place-items-center rounded-md bg-mint text-ink-950'
                        : 'h-5 w-5 rounded-md border border-white/20'
                    }
                  >
                    {done ? '✓' : ''}
                  </span>
                  <span className="text-xs text-slate-300">{String(label)}</span>
                </div>
              ))}
            </div>
            <div className="mt-5 flex items-center justify-between rounded-xl border border-amber/20 bg-amber/[0.06] px-3 py-2.5">
              <span className="inline-flex items-center gap-2 text-xs text-amber">
                <Flame size={14} /> 12-day streak
              </span>
              <span className="text-[10px] text-slate-500">2 friends close behind</span>
            </div>
          </div>
        </section>

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((feature) => {
            const Icon = feature.icon
            return (
              <div key={feature.title} className="panel p-4">
                <span className="grid h-9 w-9 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-neon">
                  <Icon size={16} />
                </span>
                <h2 className="mt-3 text-sm font-semibold text-slate-100">{feature.title}</h2>
                <p className="mt-1 text-xs leading-relaxed text-slate-500">{feature.body}</p>
              </div>
            )
          })}
        </section>
      </main>
    </div>
  )
}
