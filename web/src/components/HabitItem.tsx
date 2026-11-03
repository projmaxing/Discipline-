import {
  Activity,
  CalendarDays,
  Check,
  Clock,
  Flame,
  Pencil,
  Trash2,
  Users,
} from 'lucide-react'
import type { Habit } from '../lib/types'
import { CATEGORY_TONE, SCHEDULE_LABEL } from '../lib/theme'
import { cx } from './ui'

export function HabitItem({
  habit,
  done,
  busy,
  onToggle,
  onEdit,
  onDelete,
  showActions = true,
}: {
  habit: Habit
  done: boolean
  busy?: boolean
  onToggle: () => void
  onEdit?: () => void
  onDelete?: () => void
  showActions?: boolean
}) {
  const tone = CATEGORY_TONE[habit.category] ?? CATEGORY_TONE.Other

  return (
    <div
      style={{ borderLeftColor: done ? '#34D399' : tone, borderLeftWidth: 2 }}
      className={cx(
        'group flex items-start gap-3 rounded-xl2 border border-l-2 p-3.5 transition-colors',
        done
          ? 'border-mint/25 bg-mint/[0.05]'
          : 'border-white/[0.06] bg-white/[0.02] hover:border-white/[0.12]',
      )}
    >
      <button
        onClick={onToggle}
        disabled={busy}
        aria-pressed={done}
        aria-label={done ? `Mark ${habit.name} incomplete` : `Complete ${habit.name}`}
        className={cx(
          'mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-[9px] border transition-all duration-200',
          done
            ? 'animate-pop border-mint bg-mint text-ink-950'
            : 'border-white/20 text-transparent hover:border-neon/70 hover:bg-neon/10',
          busy && 'opacity-60',
        )}
      >
        <Check size={16} strokeWidth={3} />
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className={cx('truncate text-sm font-semibold', done ? 'text-slate-300' : 'text-slate-100')}>
            {habit.name}
          </span>
          {done ? (
            <span className="rounded-full border border-mint/30 bg-mint/10 px-2 py-0.5 text-[10px] font-semibold text-mint">
              Done
            </span>
          ) : null}
          {habit.target ? (
            <span className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[10px] text-slate-400">
              <Clock size={10} /> {habit.target}
            </span>
          ) : null}
        </div>

        <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-[11px] text-slate-500">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: tone }} />
            {habit.category}
          </span>
          <span className="text-slate-700">·</span>
          <span className="inline-flex items-center gap-1">
            <CalendarDays size={10} /> {SCHEDULE_LABEL[habit.schedule]}
          </span>
          {habit.description ? (
            <>
              <span className="text-slate-700">·</span>
              <span className="truncate">{habit.description}</span>
            </>
          ) : null}
        </div>
      </div>

      {showActions ? (
        <div className="flex shrink-0 items-center gap-1 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100">
          {onEdit ? (
            <button
              onClick={onEdit}
              aria-label={`Edit ${habit.name}`}
              className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 transition hover:bg-white/[0.06] hover:text-neon-soft"
            >
              <Pencil size={14} />
            </button>
          ) : null}
          {onDelete ? (
            <button
              onClick={onDelete}
              aria-label={`Delete ${habit.name}`}
              className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 transition hover:bg-rose/10 hover:text-rose"
            >
              <Trash2 size={14} />
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

export function EmptyHabitsIllustration() {
  return (
    <div className="relative grid h-14 w-14 place-items-center rounded-2xl border border-white/10 bg-white/[0.04] text-neon">
      <Activity size={22} />
      <span className="absolute -right-2 -top-2 grid h-6 w-6 place-items-center rounded-full border border-violet/40 bg-violet/15 text-violet-soft">
        <Users size={12} />
      </span>
      <span className="absolute -bottom-2 -left-2 grid h-6 w-6 place-items-center rounded-full border border-amber/40 bg-amber/15 text-amber">
        <Flame size={12} />
      </span>
    </div>
  )
}
