import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Activity as ActivityIcon,
  ArrowRight,
  ArrowUpRight,
  CalendarCheck,
  Flame,
  Sparkles,
  Trophy,
  Zap,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useAuth } from '../context/AuthProvider'
import {
  fetchAchievements,
  fetchActivity,
  fetchCompletions,
  fetchHabits,
  setCompletion,
} from '../lib/data'
import {
  completionMap,
  currentStreak,
  bestStreak,
  isoDayLocal,
  levelFromXp,
  pctOf,
  scheduledFor,
  seriesFor,
  XP_PER_TASK,
} from '../lib/scoring'
import { greeting, todayLong, timeAgo, weekdayShort } from '../lib/format'
import type { Achievement, ActivityEvent, Completion, Habit, Profile } from '../lib/types'
import { AchievementStrip } from '../components/Achievements'
import { HabitItem } from '../components/HabitItem'
import {
  Avatar,
  Button,
  Card,
  EmptyState,
  ErrorNote,
  ProgressRing,
  SectionTitle,
  Spinner,
  StatCard,
  cx,
} from '../components/ui'

type FeedRow = ActivityEvent & {
  profile: Pick<Profile, 'username' | 'display_name' | 'avatar_url'> | null
}

const KIND_ICON = {
  perfect_day: CalendarCheck,
  streak_milestone: Flame,
  achievement: Trophy,
  joined: Sparkles,
} as const

export function Dashboard() {
  const { profile } = useAuth()
  const [habits, setHabits] = useState<Habit[]>([])
  const [completions, setCompletions] = useState<Completion[]>([])
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [feed, setFeed] = useState<FeedRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState<string | null>(null)

  const today = new Date()
  const todayKey = isoDayLocal(today)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [habitRows, completionRows, achievementRows, feedRows] = await Promise.all([
        fetchHabits(),
        fetchCompletions(120),
        fetchAchievements(profile?.id ?? ''),
        fetchActivity(8),
      ])
      setHabits(habitRows)
      setCompletions(completionRows)
      setAchievements(achievementRows)
      setFeed(feedRows)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load your dashboard.')
    } finally {
      setLoading(false)
    }
  }, [profile?.id])

  useEffect(() => {
    void load()
  }, [load])

  const byDay = useMemo(() => completionMap(completions), [completions])
  const dueToday = useMemo(() => scheduledFor(habits, today), [habits, today])
  const doneIds = byDay.get(todayKey) ?? new Set<string>()
  const doneToday = dueToday.filter((habit) => doneIds.has(habit.id)).length
  const pctToday = pctOf(doneToday, dueToday.length)

  const series = useMemo(() => seriesFor(habits, completions, 120), [habits, completions])
  const last30 = series.slice(-30)
  const week = series.slice(-7)
  const streak = currentStreak(series)
  const best = bestStreak(series)
  const weekDue = week.reduce((sum, day) => sum + day.due, 0)
  const weekDone = week.reduce((sum, day) => sum + day.done, 0)
  const weekPct = pctOf(weekDone, weekDue)
  const perfectDays = series.filter((day) => day.due > 0 && day.done >= day.due).length
  const xp = completions.length * XP_PER_TASK + perfectDays * 50
  const level = levelFromXp(xp)
  const earned = useMemo(() => new Set(achievements.map((row) => row.code)), [achievements])

  const chartData = week.map((day) => ({ label: weekdayShort(day.day), pct: pctOf(day.done, day.due) }))

  const toggle = async (habit: Habit) => {
    if (!profile) return
    const already = doneIds.has(habit.id)
    const previous = completions
    setBusyId(habit.id)
    if (already) {
      setCompletions((rows) => rows.filter((row) => !(row.habit_id === habit.id && row.completed_on === todayKey)))
    } else {
      setCompletions((rows) => [
        ...rows,
        {
          id: Date.now(),
          habit_id: habit.id,
          owner_id: habit.owner_id,
          completed_on: todayKey,
          created_at: new Date().toISOString(),
        },
      ])
    }
    try {
      await setCompletion(habit.id, habit.owner_id, todayKey, !already)
      if (!already) {
        const [achievementRows, feedRows] = await Promise.all([
          fetchAchievements(profile.id),
          fetchActivity(8),
        ])
        setAchievements(achievementRows)
        setFeed(feedRows)
      }
    } catch (err) {
      setCompletions(previous)
      setError(err instanceof Error ? err.message : 'Could not save that completion.')
    } finally {
      setBusyId(null)
    }
  }

  if (loading) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner label="Loading your command center" />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-50">
            {greeting()}
            {profile?.display_name ? `, ${profile.display_name.split(' ')[0]}` : ''}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {todayLong()} · {dueToday.length ? `${dueToday.length - doneToday} habits left today` : 'no habits scheduled'}
          </p>
        </div>
        <Link to="/habits" className="btn-ghost">
          Manage habits <ArrowUpRight size={15} />
        </Link>
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      <section className="rise rounded-xl2 border border-neon/20 bg-gradient-to-br from-neon/[0.08] via-ink-850 to-ink-850 p-5">
        <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center">
          <ProgressRing pct={pctToday} caption="of today's habits" />
          <div className="min-w-0 flex-1">
            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-cyan">Today's progress</div>
            <div className="mt-1.5 flex flex-wrap items-baseline gap-2">
              <span className="font-display text-3xl font-bold text-slate-50">
                {doneToday} of {dueToday.length}
              </span>
              <span className="text-sm text-slate-400">completed</span>
              <span
                className={cx(
                  'text-xs font-semibold',
                  pctToday >= 100 ? 'text-mint' : pctToday >= 50 ? 'text-neon-soft' : 'text-amber',
                )}
              >
                {pctToday >= 100 ? 'Flawless day' : pctToday >= 50 ? 'Strong momentum' : dueToday.length ? 'Warming up' : 'Rest day'}
              </span>
            </div>

            <div className="mt-3 flex gap-1">
              {dueToday.length ? (
                dueToday.map((habit) => (
                  <span
                    key={habit.id}
                    className={cx(
                      'h-1.5 flex-1 rounded-full transition-colors',
                      doneIds.has(habit.id) ? 'bg-mint' : 'bg-white/10',
                    )}
                  />
                ))
              ) : (
                <span className="h-1.5 flex-1 rounded-full bg-white/10" />
              )}
            </div>

            <p className="mt-3 text-xs text-slate-500">
              {dueToday.length
                ? `${Math.max(0, dueToday.length - doneToday)} remaining · +${doneToday * XP_PER_TASK} XP earned today`
                : 'Nothing scheduled today — add a habit or enjoy the rest.'}
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <Link to="/habits" className="btn-primary">
                <Zap size={15} /> {dueToday.length ? "Continue today's habits" : 'Create a habit'}
              </Link>
              <Link to="/leaderboard" className="btn-ghost">
                <Trophy size={15} /> View leaderboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Day streak" value={`${streak}`} hint={`best ${best}`} icon={<Flame size={15} />} accent="text-amber" />
        <StatCard label="Best streak" value={`${best}`} hint="personal record" icon={<Trophy size={15} />} accent="text-violet-soft" />
        <StatCard label="This week" value={`${weekPct}%`} hint={`${weekDone}/${weekDue} scheduled`} icon={<ActivityIcon size={15} />} accent="text-mint" />
        <StatCard
          label="Level"
          value={`L${level.level}`}
          hint={`${level.name} · ${level.inLevel}/${level.forLevel} XP`}
          icon={<Zap size={15} />}
          accent="text-cyan"
        />
      </section>

      <div className="grid gap-5 lg:grid-cols-[1.25fr_1fr]">
        <section>
          <SectionTitle
            title="Today's habits"
            hint="Scheduled for today, ordered as you created them"
            action={
              <span className="chip">
                {doneToday}/{dueToday.length}
              </span>
            }
          />
          {dueToday.length ? (
            <div className="space-y-2">
              {dueToday.map((habit) => (
                <HabitItem
                  key={habit.id}
                  habit={habit}
                  done={doneIds.has(habit.id)}
                  busy={busyId === habit.id}
                  onToggle={() => void toggle(habit)}
                  showActions={false}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<CalendarCheck size={20} />}
              title="No habits scheduled today"
              body="Create your first habit and it appears here with a streak counter."
              action={
                <Link to="/habits" className="btn-primary">
                  Create a habit
                </Link>
              }
            />
          )}
        </section>

        <div className="space-y-5">
          <Card>
            <SectionTitle title="This week" hint="Completion rate per day" />
            <div className="h-[168px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 8, right: 4, left: -22, bottom: 0 }}>
                  <CartesianGrid stroke="#161d28" vertical={false} />
                  <XAxis dataKey="label" stroke="#5b6879" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis domain={[0, 100]} stroke="#5b6879" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                    contentStyle={{
                      background: '#0A0D13',
                      border: '1px solid #202937',
                      borderRadius: 12,
                      fontSize: 12,
                    }}
                    formatter={(value) => [`${value}%`, 'Completed']}
                  />
                  <Bar dataKey="pct" radius={[6, 6, 6, 6]} maxBarSize={26}>
                    {chartData.map((entry, index) => (
                      <Cell key={index} fill={entry.pct === 0 ? '#1a2230' : entry.label === weekdayShort(todayKey) ? '#22D3EE' : '#2E8BFF'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <SectionTitle title="Milestones" hint="Earned automatically from your records" />
            <AchievementStrip earned={earned} />
          </Card>
        </div>
      </div>

      <Card>
        <SectionTitle
          title="Friend activity"
          hint="Only what friends chose to share"
          action={
            <Link to="/activity" className="text-xs font-semibold text-neon hover:underline">
              Open feed
            </Link>
          }
        />
        {feed.length ? (
          <ul className="divide-y divide-white/[0.04]">
            {feed.slice(0, 5).map((row) => {
              const Icon = KIND_ICON[row.kind] ?? Sparkles
              return (
                <li key={row.id} className="flex items-center gap-3 py-2.5">
                  <Avatar name={row.profile?.display_name ?? 'Member'} src={row.profile?.avatar_url} size={30} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs text-slate-300">
                      <span className="font-semibold text-slate-100">
                        {row.profile?.display_name ?? 'A member'}
                      </span>{' '}
                      {row.title.toLowerCase()}
                    </div>
                    <div className="text-[10px] text-slate-600">{timeAgo(row.created_at)}</div>
                  </div>
                  <Icon size={14} className="text-slate-600" />
                </li>
              )
            })}
          </ul>
        ) : (
          <p className="py-4 text-xs text-slate-500">
            Nothing shared yet. Add friends to see perfect days and streak milestones here.
          </p>
        )}
      </Card>

      <div className="flex justify-center pb-2">
        <Link to="/leaderboard" className="inline-flex items-center gap-1.5 text-xs text-slate-500 transition hover:text-slate-300">
          Compare consistency with friends <ArrowRight size={13} />
        </Link>
      </div>
    </div>
  )
}
