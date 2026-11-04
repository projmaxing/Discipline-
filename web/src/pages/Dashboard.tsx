import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Activity as ActivityIcon,
  ArrowRight,
  ArrowUpRight,
  CalendarCheck,
  ChevronRight,
  Flame,
  Sparkles,
  Target,
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
  Card,
  EmptyState,
  ErrorNote,
  ProgressRing,
  SectionTitle,
  Spinner,
  StatCard,
  XPBar,
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

const KIND_TONE = {
  perfect_day: '#3CE6A0',
  streak_milestone: '#FFB84D',
  achievement: '#C4B0FF',
  joined: '#38E8FF',
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
          <div className="font-mono text-[10px] font-semibold uppercase tracking-[0.28em] text-cyan">
            Daily briefing
          </div>
          <h1 className="mt-1 font-display text-[1.9rem] font-extrabold leading-tight text-slate-50 sm:text-4xl">
            {greeting()}
            {profile?.display_name ? `, ${profile.display_name.split(' ')[0]}` : ''}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {todayLong()} ·{' '}
            {dueToday.length ? `${Math.max(0, dueToday.length - doneToday)} quests still open` : 'rest day — nothing scheduled'}
          </p>
        </div>
        <Link to="/habits" className="btn-ghost">
          Manage quests <ArrowUpRight size={15} />
        </Link>
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      <section className="hud rise relative overflow-hidden p-5 sm:p-7">
        <div className="pointer-events-none absolute -right-24 -top-32 h-72 w-72 animate-drift rounded-full bg-neon/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 left-1/3 h-64 w-64 animate-drift rounded-full bg-violet/15 blur-3xl" />

        <div className="relative flex flex-col items-start gap-7 sm:flex-row sm:items-center">
          <ProgressRing pct={pctToday} size={176} stroke={13} caption="daily completion" />

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="chip-live">
                <span className="h-1.5 w-1.5 animate-breathe rounded-full bg-mint" /> Season 01
              </span>
              <span className="chip border-amber/25 bg-amber/10 text-amber">
                <Flame size={11} /> {streak} day streak
              </span>
              <span className="chip">
                <Trophy size={11} className="text-violet-soft" /> best {best}
              </span>
            </div>

            <div className="mt-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
              <span className="font-display text-[2rem] font-extrabold leading-none text-slate-50">
                {doneToday}
                <span className="text-slate-600">/{dueToday.length}</span>
              </span>
              <span className="text-sm text-slate-400">quests cleared</span>
              <span
                className={cx(
                  'font-mono text-[11px] font-semibold uppercase tracking-[0.14em]',
                  pctToday >= 100 ? 'text-mint' : pctToday >= 50 ? 'text-cyan' : 'text-amber',
                )}
              >
                {pctToday >= 100 ? 'Perfect day' : pctToday >= 50 ? 'Momentum' : dueToday.length ? 'Warm-up' : 'Rest'}
              </span>
            </div>

            <div className="mt-3 flex gap-1">
              {dueToday.length ? (
                dueToday.map((habit) => (
                  <span key={habit.id} className={cx('seg', doneIds.has(habit.id) && 'seg-on')} />
                ))
              ) : (
                <span className="seg" />
              )}
            </div>

            <div className="mt-5 max-w-md">
              <XPBar
                value={level.fraction}
                level={level.level}
                name={level.name}
                inLevel={level.inLevel}
                forLevel={level.forLevel}
              />
            </div>

            <div className="mt-5 flex flex-wrap items-center gap-2">
              <Link to="/habits" className="btn-primary">
                <Zap size={15} /> {dueToday.length ? 'Open quest log' : 'Create a quest'} <ChevronRight size={15} />
              </Link>
              <Link to="/leaderboard" className="btn-ghost">
                <Trophy size={15} /> Ranked ladder
              </Link>
              <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
                +{doneToday * XP_PER_TASK} XP today
              </span>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Day streak"
          value={`${streak}`}
          hint={`record ${best}`}
          icon={<Flame size={14} />}
          accent="text-amber"
          tone="#FFB84D"
        />
        <StatCard
          label="This week"
          value={`${weekPct}%`}
          hint={`${weekDone}/${weekDue} cleared`}
          icon={<ActivityIcon size={14} />}
          accent="text-mint"
          tone="#3CE6A0"
        />
        <StatCard
          label="Level"
          value={`L${level.level}`}
          hint={level.name}
          icon={<Zap size={14} />}
          accent="text-cyan"
          tone="#38E8FF"
        />
        <StatCard
          label="Total XP"
          value={`${xp}`}
          hint={`${perfectDays} perfect days`}
          icon={<Target size={14} />}
          accent="text-violet-soft"
          tone="#8B5CF6"
        />
      </section>

      <div className="grid gap-5 lg:grid-cols-[1.25fr_1fr]">
        <section>
          <SectionTitle
            title="Today's quest log"
            hint="Scheduled for today — every cleared quest pays XP"
            accent="#38E8FF"
            action={
              <span className="chip font-mono">
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
              title="No quests scheduled today"
              body="A rest day counts as a rest day — create a quest and it lands here with its own streak."
              action={
                <Link to="/habits" className="btn-primary">
                  Create a quest
                </Link>
              }
            />
          )}
        </section>

        <div className="space-y-5">
          <Card accent="#4C8DFF">
            <SectionTitle
              title="Week form"
              hint="Completion rate by day"
              accent="#4C8DFF"
              action={<span className="font-mono text-lg font-bold text-slate-100">{weekPct}%</span>}
            />
            <div className="h-[168px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 8, right: 4, left: -24, bottom: 0 }}>
                  <defs>
                    <linearGradient id="barToday" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#7FE9FF" />
                      <stop offset="100%" stopColor="#4C8DFF" stopOpacity={0.5} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#151C2B" vertical={false} />
                  <XAxis dataKey="label" stroke="#5B6879" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#5B6879"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}`}
                  />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                    contentStyle={{
                      background: '#0A0E18',
                      border: '1px solid #253149',
                      borderRadius: 12,
                      fontSize: 12,
                    }}
                    formatter={(value) => [`${value}%`, 'Cleared']}
                  />
                  <Bar dataKey="pct" radius={[6, 6, 6, 6]} maxBarSize={26}>
                    {chartData.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={
                          entry.pct === 0
                            ? '#1A2233'
                            : entry.label === weekdayShort(todayKey)
                              ? 'url(#barToday)'
                              : '#2B4C86'
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card accent="#8B5CF6">
            <SectionTitle title="Milestones" hint="Unlocked automatically from your records" accent="#8B5CF6" />
            <AchievementStrip earned={earned} />
          </Card>
        </div>
      </div>

      <Card accent="#3CE6A0">
        <SectionTitle
          title="Squad feed"
          hint="Only what friends chose to share"
          accent="#3CE6A0"
          action={
            <Link to="/activity" className="inline-flex items-center gap-1 text-[11px] font-semibold text-cyan hover:underline">
              Open feed <ArrowRight size={12} />
            </Link>
          }
        />
        {feed.length ? (
          <ul className="divide-y divide-white/[0.05]">
            {feed.slice(0, 5).map((row) => {
              const Icon = KIND_ICON[row.kind] ?? Sparkles
              const tone = KIND_TONE[row.kind] ?? '#38E8FF'
              return (
                <li key={row.id} className="flex items-center gap-3 py-2.5">
                  <Avatar name={row.profile?.display_name ?? 'Member'} src={row.profile?.avatar_url} size={32} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-xs text-slate-300">
                      <span className="font-semibold text-slate-100">{row.profile?.display_name ?? 'A member'}</span>{' '}
                      {row.title.toLowerCase()}
                    </div>
                    <div className="font-mono text-[10px] text-slate-600">{timeAgo(row.created_at)}</div>
                  </div>
                  <span
                    className="grid h-7 w-7 place-items-center rounded-lg border"
                    style={{ borderColor: `${tone}40`, background: `${tone}14`, color: tone }}
                  >
                    <Icon size={13} />
                  </span>
                </li>
              )
            })}
          </ul>
        ) : (
          <p className="py-4 text-xs text-slate-500">
            Nothing shared yet. Add squad members to see perfect days and streak milestones here.
          </p>
        )}
      </Card>

      <div className="flex justify-center pb-2">
        <Link
          to="/leaderboard"
          className="inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-slate-500 transition hover:text-cyan"
        >
          Compare consistency with your squad <ArrowRight size={12} />
        </Link>
      </div>
    </div>
  )
}
