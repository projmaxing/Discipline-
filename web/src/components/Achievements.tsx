import { CalendarCheck, Flame, Layers, Sparkles, Trophy } from 'lucide-react'
import type { AchievementCode } from '../lib/types'
import { cx } from './ui'

export const ACHIEVEMENT_META: Record<
  AchievementCode,
  { title: string; description: string; icon: typeof Sparkles }
> = {
  first_light: {
    title: 'First light',
    description: 'Complete your first habit',
    icon: Sparkles,
  },
  perfect_day: {
    title: 'Perfect day',
    description: 'Finish every habit scheduled for a day',
    icon: CalendarCheck,
  },
  week_streak: {
    title: 'Week of fire',
    description: 'Seven consecutive perfect days',
    icon: Flame,
  },
  month_streak: {
    title: 'Month in motion',
    description: 'Thirty consecutive perfect days',
    icon: Trophy,
  },
  century: {
    title: 'Century',
    description: 'One hundred logged completions',
    icon: Layers,
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
              'flex flex-col gap-2 rounded-xl border p-3 transition',
              unlocked
                ? 'border-neon/30 bg-neon/[0.07]'
                : 'border-white/[0.06] bg-white/[0.015] opacity-70',
            )}
          >
            <span
              className={cx(
                'grid h-8 w-8 place-items-center rounded-lg border',
                unlocked
                  ? 'border-neon/40 bg-neon/15 text-neon'
                  : 'border-white/10 bg-white/[0.03] text-slate-500',
              )}
            >
              <Icon size={15} />
            </span>
            <div>
              <div className={cx('text-xs font-semibold', unlocked ? 'text-slate-100' : 'text-slate-400')}>
                {meta.title}
              </div>
              <div className="mt-0.5 text-[10px] leading-snug text-slate-500">
                {unlocked ? 'Unlocked' : 'Locked'}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
