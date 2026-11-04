import { CalendarCheck, Flame, Layers, Lock, Sparkles, Trophy } from 'lucide-react'
import type { AchievementCode } from '../lib/types'
import { cx } from './ui'

export const ACHIEVEMENT_META: Record<
  AchievementCode,
  { title: string; description: string; icon: typeof Sparkles; tone: string }
> = {
  first_light: {
    title: 'First light',
    description: 'Complete your first habit',
    icon: Sparkles,
    tone: '#38E8FF',
  },
  perfect_day: {
    title: 'Perfect day',
    description: 'Finish every habit scheduled for a day',
    icon: CalendarCheck,
    tone: '#3CE6A0',
  },
  week_streak: {
    title: 'Week of fire',
    description: 'Seven consecutive perfect days',
    icon: Flame,
    tone: '#FFB84D',
  },
  month_streak: {
    title: 'Month in motion',
    description: 'Thirty consecutive perfect days',
    icon: Trophy,
    tone: '#8B5CF6',
  },
  century: {
    title: 'Century',
    description: 'One hundred logged completions',
    icon: Layers,
    tone: '#FFC857',
  },
}

export const ACHIEVEMENT_ORDER: AchievementCode[] = [
  'first_light',
  'perfect_day',
  'week_streak',
  'month_streak',
  'century',
]

export function AchievementStrip({ earned }: { earned: Set<AchievementCode> }) {
  return (
    <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-5">
      {ACHIEVEMENT_ORDER.map((code) => {
        const meta = ACHIEVEMENT_META[code]
        const Icon = meta.icon
        const unlocked = earned.has(code)
        return (
          <div
            key={code}
            title={meta.description}
            className={cx(
              'relative overflow-hidden rounded-xl border p-3 transition',
              unlocked
                ? 'border-white/[0.12] bg-white/[0.04]'
                : 'border-white/[0.06] bg-white/[0.012] opacity-70',
            )}
          >
            {unlocked ? (
              <span
                className="pointer-events-none absolute inset-x-3 top-0 h-px"
                style={{ background: `linear-gradient(90deg, transparent, ${meta.tone}, transparent)` }}
              />
            ) : null}
            <span
              className={cx(
                'hex grid h-9 w-9 place-items-center border',
                unlocked ? 'border-transparent' : 'border-white/10 bg-white/[0.03] text-slate-600',
              )}
              style={
                unlocked
                  ? {
                      background: `linear-gradient(150deg, ${meta.tone}40, ${meta.tone}10)`,
                      color: meta.tone,
                      boxShadow: `0 0 20px -6px ${meta.tone}`,
                    }
                  : undefined
              }
            >
              {unlocked ? <Icon size={15} /> : <Lock size={13} />}
            </span>
            <div className="mt-2">
              <div className={cx('text-[11px] font-bold', unlocked ? 'text-slate-100' : 'text-slate-400')}>
                {meta.title}
              </div>
              <div
                className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.12em]"
                style={{ color: unlocked ? meta.tone : '#475569' }}
              >
                {unlocked ? 'Unlocked' : 'Locked'}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
