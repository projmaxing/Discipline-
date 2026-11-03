import { useCallback, useEffect, useState } from 'react'
import { Activity, CalendarCheck, Flame, Sparkles, Trophy } from 'lucide-react'
import { fetchActivity } from '../lib/data'
import { timeAgo } from '../lib/format'
import type { ActivityEvent, Profile } from '../lib/types'
import {
  Avatar,
  Card,
  EmptyState,
  ErrorNote,
  SectionTitle,
  Spinner,
} from '../components/ui'

type Row = ActivityEvent & {
  profile: Pick<Profile, 'username' | 'display_name' | 'avatar_url'> | null
}

const KIND = {
  perfect_day: { icon: CalendarCheck, tone: 'text-mint', label: 'Perfect day' },
  streak_milestone: { icon: Flame, tone: 'text-amber', label: 'Streak' },
  achievement: { icon: Trophy, tone: 'text-violet-soft', label: 'Achievement' },
  joined: { icon: Sparkles, tone: 'text-neon', label: 'Joined' },
} as const

export function ActivityFeed() {
  const [rows, setRows] = useState<Row[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setRows(await fetchActivity(50))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the feed.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-3xl font-bold text-slate-50">Activity</h1>
        <p className="mt-1 text-sm text-slate-500">
          Accountability, not a social network — only what people chose to share
        </p>
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      <Card>
        <SectionTitle
          title="Recent events"
          hint="Habit names and notes are never included"
          action={
            <span className="chip">
              <Activity size={11} /> {rows.length}
            </span>
          }
        />
        {loading ? (
          <div className="grid place-items-center py-16">
            <Spinner label="Loading feed" />
          </div>
        ) : rows.length ? (
          <ul className="divide-y divide-white/[0.04]">
            {rows.map((row) => {
              const meta = KIND[row.kind] ?? KIND.joined
              const Icon = meta.icon
              return (
                <li key={row.id} className="flex items-start gap-3 py-3">
                  <Avatar name={row.profile?.display_name ?? 'Member'} src={row.profile?.avatar_url} size={34} />
                  <div className="min-w-0 flex-1">
                    <div className="text-sm text-slate-300">
                      <span className="font-semibold text-slate-100">
                        {row.profile?.display_name ?? 'A member'}
                      </span>{' '}
                      <span className="text-slate-400">{row.title.charAt(0).toLowerCase() + row.title.slice(1)}</span>
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-[10px] text-slate-600">
                      <span className={meta.tone}>{meta.label}</span>
                      <span>·</span>
                      <span>{timeAgo(row.created_at)}</span>
                      {row.profile?.username ? <span>· @{row.profile.username}</span> : null}
                    </div>
                  </div>
                  <Icon size={15} className={meta.tone} />
                </li>
              )
            })}
          </ul>
        ) : (
          <EmptyState
            icon={<Activity size={20} />}
            title="Nothing shared yet"
            body="Friends' perfect days and streak milestones appear here once they start logging. Your own sharing is controlled in Settings."
          />
        )}
      </Card>
    </div>
  )
}
