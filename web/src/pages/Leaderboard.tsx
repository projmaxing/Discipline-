import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Crown, Flame, Medal, Trophy } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { fetchLeaderboard } from '../lib/data'
import type { LeaderboardRow } from '../lib/types'
import {
  Avatar,
  Button,
  Card,
  EmptyState,
  ErrorNote,
  SectionTitle,
  Segmented,
  Spinner,
  cx,
} from '../components/ui'

type Scope = 'friends' | 'global'

export function Leaderboard() {
  const { profile } = useAuth()
  const [scope, setScope] = useState<Scope>('friends')
  const [rows, setRows] = useState<LeaderboardRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async (next: Scope) => {
    setLoading(true)
    setError('')
    try {
      setRows(await fetchLeaderboard(next))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the leaderboard.')
      setRows([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load(scope)
  }, [load, scope])

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-50">Leaderboard</h1>
          <p className="mt-1 text-sm text-slate-500">Weekly consistency, calculated by the database</p>
        </div>
        <Segmented<Scope>
          value={scope}
          onChange={setScope}
          options={[
            { value: 'friends', label: 'Friends' },
            { value: 'global', label: 'Public' },
          ]}
        />
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      <Card>
        <SectionTitle
          title="This week"
          hint="10 points per completion · 50 per achievement earned this week"
          action={
            <span className="chip">
              <Trophy size={11} className="text-amber" /> {rows.length} ranked
            </span>
          }
        />
        {loading ? (
          <div className="grid place-items-center py-16">
            <Spinner label="Ranking" />
          </div>
        ) : rows.length ? (
          <div className="-mx-2 overflow-x-auto">
            <table className="w-full min-w-[620px] border-separate border-spacing-y-1 px-2 text-sm">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-[0.14em] text-slate-500">
                  <th className="px-3 py-2 font-semibold">Rank</th>
                  <th className="px-3 py-2 font-semibold">Member</th>
                  <th className="px-3 py-2 text-right font-semibold">Week</th>
                  <th className="px-3 py-2 text-right font-semibold">Points</th>
                  <th className="px-3 py-2 text-right font-semibold">Streak</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => {
                  const mine = row.user_id === profile?.id
                  const rank = index + 1
                  return (
                    <tr
                      key={row.user_id}
                      className={cx(
                        'rounded-xl transition',
                        mine ? 'bg-neon/[0.08]' : 'bg-white/[0.015] hover:bg-white/[0.035]',
                      )}
                    >
                      <td className="rounded-l-xl px-3 py-3">
                        <span
                          className={cx(
                            'inline-flex h-7 w-7 items-center justify-center rounded-lg border text-xs font-bold',
                            rank === 1
                              ? 'border-amber/40 bg-amber/15 text-amber'
                              : rank === 2
                                ? 'border-slate-400/40 bg-slate-400/10 text-slate-300'
                                : rank === 3
                                  ? 'border-amber/25 bg-amber/[0.08] text-amber/80'
                                  : 'border-white/10 text-slate-500',
                          )}
                        >
                          {rank === 1 ? <Crown size={13} /> : rank <= 3 ? <Medal size={13} /> : rank}
                        </span>
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2.5">
                          <Avatar name={row.display_name} src={row.avatar_url} size={30} />
                          <div className="min-w-0">
                            <div className="truncate text-sm font-medium text-slate-100">
                              {row.display_name}
                              {mine ? <span className="ml-2 text-[10px] text-neon">you</span> : null}
                            </div>
                            <div className="truncate text-[11px] text-slate-500">@{row.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <div className="font-semibold text-slate-200">{row.pct}%</div>
                        <div className="text-[10px] text-slate-500">
                          {row.done}/{row.due}
                        </div>
                      </td>
                      <td className="px-3 py-3 text-right font-mono text-sm text-neon-soft">{row.points}</td>
                      <td className="rounded-r-xl px-3 py-3 text-right">
                        <span className="inline-flex items-center gap-1 text-xs text-amber">
                          <Flame size={11} /> {row.streak}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            icon={<Trophy size={20} />}
            title={scope === 'friends' ? 'No friends on the board yet' : 'Nobody is public yet'}
            body={
              scope === 'friends'
                ? 'Add a friend and complete a habit — the board fills as soon as they accept.'
                : 'Members appear here only when their profile is public and they share stats.'
            }
            action={
              <Link to="/friends" className="btn-primary">
                Find friends
              </Link>
            }
          />
        )}
      </Card>

      <Card>
        <SectionTitle title="How scoring works" hint="Transparent, and impossible to inflate from the browser" />
        <ul className="space-y-2 text-xs leading-relaxed text-slate-400">
          <li>
            <span className="font-semibold text-slate-200">Completion rate</span> = completed scheduled habits ÷
            scheduled habits × 100. Days with nothing scheduled are ignored, not counted as failures.
          </li>
          <li>
            <span className="font-semibold text-slate-200">Points</span> = 10 × completions this week + 50 ×
            achievements earned this week. Completions are written once per habit per day (a unique constraint blocks
            duplicates).
          </li>
          <li>
            <span className="font-semibold text-slate-200">Streaks</span> count consecutive perfect days. An unfinished
            today does not break yesterday's streak.
          </li>
          <li>Only aggregates leave the database — friend views never include habit names or notes.</li>
        </ul>
      </Card>
    </div>
  )
}
