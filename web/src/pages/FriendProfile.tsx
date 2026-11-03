import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, Flame, ShieldOff, Trophy, UserMinus } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import {
  blockUser,
  fetchAchievements,
  fetchCompareStats,
  fetchFriendships,
  fetchPublicProfileByUsername,
  removeFriendship,
} from '../lib/data'
import { pctOf } from '../lib/scoring'
import { formatDay } from '../lib/format'
import type { Achievement, AchievementCode, CompareStats, Profile } from '../lib/types'
import { AchievementStrip } from '../components/Achievements'
import {
  Avatar,
  Button,
  Card,
  ErrorNote,
  SectionTitle,
  Spinner,
  StatCard,
} from '../components/ui'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export function FriendProfile() {
  const { username } = useParams<{ username: string }>()
  const { profile: me } = useAuth()
  const navigate = useNavigate()
  const [person, setPerson] = useState<Profile | null>(null)
  const [stats, setStats] = useState<CompareStats | null>(null)
  const [mine, setMine] = useState<CompareStats | null>(null)
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [friendshipId, setFriendshipId] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    if (!username || !me) return
    setLoading(true)
    setError('')
    try {
      const found = await fetchPublicProfileByUsername(username)
      setPerson(found)
      if (!found) {
        setError('No member with that username.')
        return
      }
      const [theirStats, myStats, theirAchievements, friendships] = await Promise.all([
        fetchCompareStats(found.id),
        fetchCompareStats(me.id),
        fetchAchievements(found.id).catch(() => [] as Achievement[]),
        fetchFriendships(),
      ])
      setStats(theirStats)
      setMine(myStats)
      setAchievements(theirAchievements)
      const link = friendships.find(
        (row) =>
          row.status === 'accepted' &&
          ((row.requester === me.id && row.addressee === found.id) ||
            (row.requester === found.id && row.addressee === me.id)),
      )
      setFriendshipId(link?.id ?? null)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'This profile is private or you are not friends with this member.',
      )
    } finally {
      setLoading(false)
    }
  }, [me, username])

  useEffect(() => {
    void load()
  }, [load])

  const earned = useMemo(() => new Set(achievements.map((row) => row.code)) as Set<AchievementCode>, [achievements])

  const chartData = useMemo(() => {
    if (!stats) return []
    const ownByDay = new Map((mine?.series ?? []).map((day) => [day.day, pctOf(day.done, day.due)]))
    return stats.series.map((day) => ({
      label: formatDay(day.day).split(',')[0],
      them: pctOf(day.done, day.due),
      you: ownByDay.get(day.day) ?? 0,
    }))
  }, [mine, stats])

  if (loading) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner label="Loading profile" />
      </div>
    )
  }

  if (!person) {
    return (
      <div className="space-y-4">
        <Link to="/friends" className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300">
          <ArrowLeft size={14} /> Back to friends
        </Link>
        <Card>
          <div className="flex items-start gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl border border-amber/30 bg-amber/10 text-amber">
              <AlertTriangle size={16} />
            </span>
            <div>
              <h2 className="text-sm font-semibold text-slate-100">Profile unavailable</h2>
              <p className="mt-1 text-xs text-slate-500">{error || 'That member does not exist.'}</p>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <Link to="/friends" className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-slate-300">
        <ArrowLeft size={14} /> Back to friends
      </Link>

      <div className="flex flex-wrap items-center gap-4">
        <Avatar name={person.display_name} src={person.avatar_url} size={64} />
        <div className="min-w-0 flex-1">
          <h1 className="font-display text-2xl font-bold text-slate-50">{person.display_name}</h1>
          <p className="text-sm text-slate-500">@{person.username}</p>
          {person.bio ? <p className="mt-1 max-w-xl text-xs text-slate-400">{person.bio}</p> : null}
        </div>
        <div className="flex gap-2">
          {friendshipId ? (
            <Button
              variant="ghost"
              onClick={async () => {
                await removeFriendship(friendshipId)
                navigate('/friends')
              }}
            >
              <UserMinus size={15} /> Remove friend
            </Button>
          ) : null}
          <Button
            variant="danger"
            onClick={async () => {
              await blockUser(person.id)
              navigate('/friends')
            }}
          >
            <ShieldOff size={15} /> Block
          </Button>
        </div>
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      {stats ? (
        <>
          <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <StatCard
              label="Today"
              value={`${pctOf(stats.today.done, stats.today.due)}%`}
              hint={`${stats.today.done}/${stats.today.due} scheduled`}
              icon={<Trophy size={15} />}
              accent="text-mint"
            />
            <StatCard
              label="This week"
              value={`${pctOf(stats.week.done, stats.week.due)}%`}
              hint={`${stats.week.done}/${stats.week.due} scheduled`}
              icon={<Trophy size={15} />}
              accent="text-neon"
            />
            <StatCard
              label="Current streak"
              value={`${stats.streak}`}
              hint="consecutive perfect days"
              icon={<Flame size={15} />}
              accent="text-amber"
            />
            <StatCard
              label="Best streak"
              value={`${stats.best_streak}`}
              hint="personal record"
              icon={<Trophy size={15} />}
              accent="text-violet-soft"
            />
          </section>

          <Card>
            <SectionTitle title="Last 30 days" hint="Completion rate per day — you versus them" />
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 8, right: 8, left: -22, bottom: 0 }}>
                  <CartesianGrid stroke="#161d28" vertical={false} />
                  <XAxis dataKey="label" stroke="#5b6879" fontSize={10} tickLine={false} axisLine={false} interval={4} />
                  <YAxis domain={[0, 100]} stroke="#5b6879" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ background: '#0A0D13', border: '1px solid #202937', borderRadius: 12, fontSize: 12 }}
                  />
                  <Line type="monotone" dataKey="you" name="You" stroke="#22D3EE" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="them" name={person.display_name} stroke="#2E8BFF" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <SectionTitle title="Milestones" hint="Earned from validated completions only" />
            <AchievementStrip earned={earned} />
          </Card>
        </>
      ) : (
        <Card>
          <SectionTitle title="Stats are private" />
          <p className="text-xs leading-relaxed text-slate-500">
            This member has not shared consistency stats, or the friendship is not accepted yet. You can still see
            their profile because it is visible to you.
          </p>
        </Card>
      )}
    </div>
  )
}
