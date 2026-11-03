import type { Completion, DayProgress, Habit, Schedule } from './types'

/** Mirrors XP_PER_TASK / XP_PERFECT_DAY in the desktop app. */
export const XP_PER_TASK = 10
export const XP_PERFECT_DAY = 50

export const LEVELS = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 99999]
export const LEVEL_NAMES = [
  'Beginner',
  'Apprentice',
  'Operator',
  'Specialist',
  'Tactician',
  'Strategist',
  'Vanguard',
  'Sentinel',
  'Commander',
  'Legend',
  'Mythic',
]

export const CATEGORIES = [
  'Health',
  'Study',
  'Fitness',
  'Personal',
  'Work',
  'Social',
  'Sleep',
  'Other',
] as const

export const SCHEDULES: { value: Schedule; label: string }[] = [
  { value: 'daily', label: 'Every day' },
  { value: 'weekdays', label: 'Weekdays' },
  { value: 'weekends', label: 'Weekends' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
]

export const WEEKDAY_LABELS = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

export function isoDayLocal(date: Date): string {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function addDays(date: Date, delta: number): Date {
  const next = new Date(date)
  next.setDate(next.getDate() + delta)
  return next
}

/** Same recurrence rules as the desktop app and the SQL helper. */
export function habitDueOn(habit: Pick<Habit, 'schedule' | 'schedule_days'>, day: Date): boolean {
  switch (habit.schedule) {
    case 'daily':
      return true
    case 'weekdays':
      return day.getDay() >= 1 && day.getDay() <= 5
    case 'weekends':
      return day.getDay() === 0 || day.getDay() === 6
    case 'weekly':
      return habit.schedule_days.length ? habit.schedule_days.includes(day.getDay()) : day.getDay() === 1
    case 'monthly':
      return day.getDate() === 1
    default:
      return false
  }
}

export function completionMap(completions: Completion[]): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>()
  for (const row of completions) {
    const bucket = map.get(row.completed_on) ?? new Set<string>()
    bucket.add(row.habit_id)
    map.set(row.completed_on, bucket)
  }
  return map
}

export function scheduledFor(habits: Habit[], day: Date): Habit[] {
  return habits.filter((habit) => !habit.archived && habitDueOn(habit, day))
}

export function seriesFor(habits: Habit[], completions: Completion[], days: number): DayProgress[] {
  const byDay = completionMap(completions)
  const today = new Date()
  const out: DayProgress[] = []
  for (let offset = days - 1; offset >= 0; offset -= 1) {
    const day = addDays(today, -offset)
    const key = isoDayLocal(day)
    const due = scheduledFor(habits, day)
    const done = due.filter((habit) => byDay.get(key)?.has(habit.id)).length
    out.push({ day: key, due: due.length, done })
  }
  return out
}

/**
 * Consecutive perfect days. Today is skipped when still incomplete so an
 * unfinished morning does not wipe the streak — the same rule as user_streak.
 */
export function currentStreak(series: DayProgress[]): number {
  const days = [...series].sort((a, b) => (a.day < b.day ? -1 : 1))
  let index = days.length - 1
  if (index < 0) return 0
  const today = days[index]
  if (today.due === 0 || today.done < today.due) index -= 1
  let streak = 0
  for (; index >= 0; index -= 1) {
    const day = days[index]
    if (day.due === 0) continue
    if (day.done < day.due) break
    streak += 1
  }
  return streak
}

export function bestStreak(series: DayProgress[]): number {
  let run = 0
  let best = 0
  for (const day of series) {
    if (day.due === 0) continue
    if (day.done >= day.due) {
      run += 1
      best = Math.max(best, run)
    } else {
      run = 0
    }
  }
  return best
}

export function pctOf(done: number, due: number): number {
  return due > 0 ? Math.round((done / due) * 100) : 0
}

export function levelFromXp(xp: number): {
  level: number
  name: string
  inLevel: number
  forLevel: number
  fraction: number
} {
  const level = Math.max(1, LEVELS.findIndex((threshold, index) => xp < LEVELS[index + 1]) + 1)
  const bounded = Math.min(level, LEVEL_NAMES.length)
  const previous = LEVELS[bounded - 1] ?? 0
  const following = LEVELS[bounded] ?? LEVELS[LEVELS.length - 1]
  const inLevel = Math.max(0, xp - previous)
  const forLevel = Math.max(1, following - previous)
  return {
    level: bounded,
    name: LEVEL_NAMES[bounded - 1] ?? 'Beginner',
    inLevel,
    forLevel,
    fraction: Math.min(1, inLevel / forLevel),
  }
}

/** Same transparent formula as the SQL leaderboard function. */
export function dailyScore(done: number, achievementsInWindow: number): number {
  return done * XP_PER_TASK + achievementsInWindow * XP_PERFECT_DAY
}
