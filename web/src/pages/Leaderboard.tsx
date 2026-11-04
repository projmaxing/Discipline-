import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Crown, Flame, Medal, Trophy } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { fetchLeaderboard } from '../lib/data'
import type { LeaderboardRow } from '../lib/types'
import {
  Avatar,
  Card,
  EmptyState,
  ErrorNote,
  SectionTitle,
  Segmented,
  Spinner,
  cx,
} from '../components/ui'

type Scope = 'friends' | 'global'

const PODIUM = [
  { place: 2, ring: 'medal-ring-silver', height: 'h-20', color: '#CBD5E1' },
  { place: 1, ring: 'medal-ring-gold', height: 'h-28', color: '#FFC857' },
  { place: 3, ring: 'medal-ring-bronze', height: 'h-16', color: '#E0A271' },
] as const

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

  const podium = rows.slice(0, 3)
  const rest = rows.slice(3)

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="font-mono text-[10px] font-semibold uppercase tracking-[0.28em] text-cyan">Season 01</div>
          <h1 className="mt-1 font-display text-[1.9rem] font-extrabold text-slate-50 sm:text-4xl">Ranked ladder</h1>
          <p className="mt-1 text-sm text-slate-500">Weekly consistency, scored by the database</p>
        </div>
        <Segmented<Scope>
          value={scope}
          onChange={setScope}
          options={[
            { value: 'friends', label: 'Squad' },
            { value: 'global', label: 'Public' },
          ]}
        />
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      {loading ? (
        <Card>
          <div className="grid place-items-center py-20">
            <Spinner label="Ranking the ladder" />
          </div>
        </Card>
      ) : rows.length ? (
        <>
          <section className="hud relative overflow-hidden p-5 sm:p-7">
            <div className="pointer-events-none absolute inset-x-0 -top-24 h-48 bg-neon/10 blur-3xl" />
            <div className="relative mb-6 flex items-center justify-between">
              <div>
                <div className="font-mono text-[9px] uppercase tracking-[0.22em] text-cyan">Top of the ladder</div>
                <div className="mt-1 font-display text-lg font-extrabold text-slate-50">Podium</div>
              </div>
              <span className="chip">
                <Trophy size={11} className="text-gold" /> {rows.length} ranked
              </span>
            </div>

            <div className="relative grid grid-cols-3 items-end gap-2 sm:gap-4">
              {PODIUM.map((slot) => {
                const row = podium[slot.place - 1]
                if (!row) return <div key={slot.place} />
                const mine = row.user_id === profile?.id
                return (
                  <div key={row.user_id} className="flex flex-col items-center">
                    <Avatar name={row.display_name} src={row.avatar_url} size={slot.place === 1 ? 56 : 44} ring />
                    {slot.place === 1 ? <Crown size={16} className="mt-1 text-gold" /> : null}
                    <div className={cx('mt-1.5 max-w-full truncate text-center text-xs font-semibold', mine ? 'text-cyan' : 'text-slate-200')}>
                      {row.display_name}
                    </div>
                    <div className="font-mono text-[10px] text-slate-500">@{row.username}</div>
                    <div className="mt-3 w-full overflow-hidden rounded-t-xl border border-white/[0.08] bg-white/[0.02]">
                      <div className={cx('flex flex-col items-center justify-center gap-0.5', slot.height)}>
                        <span className="font-display text-lg font-extrabold" style={{ color: slot.color }}>
                          {slot.place}
                        </span>
                        <span className="font-mono text-[10px] text-slate-400">{row.points} pts</span>
                        <span className="inline-flex items-center gap-1 font-mono text-[9px] text-amber">
                          <Flame size={9} /> {row.streak}
                        </span>
                      </div>
                    </div>
                    <div className="h-1 w-full rounded-b bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                  </div>
                )
              })}
            </div>
          </section>

          <Card accent="#8B5CF6">
            <SectionTitle
              title="Full standings"
              hint="10 points per completion · 50 per achievement earned this week"
              accent="#8B5CF6"
              action={
                <span className="chip font-mono">
                  <Trophy size={11} className="text-amber" /> {rows.length}
                </span>
              }
            />
            <ul className="space-y-1.5">
              {rest.map((row, index) => {
                const rank = index + 4
                const mine = row.user_id === profile?.id
                return (
                  <li
                    key={row.user_id}
                    className={cx(
                      'flex items-center gap-3 rounded-xl border px-3 py-2.5 transition',
                      mine
                        ? 'border-cyan/30 bg-cyan/[0.07]'
                        : 'border-white/[0.06] bg-white/[0.015] hover:border-white/[0.12]',
                    )}
                  >
                    <span className="w-6 text-center font-mono text-[11px] font-semibold text-slate-500">{rank}</span>
                    <Avatar name={row.display_name} src={row.avatar_url} size={30} />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-[13px] font-semibold text-slate-100">
                        {row.display_name}
                        {mine ? <span className="ml-2 font-mono text-[9px] uppercase tracking-[0.14em] text-cyan">you</span> : null}
                      </div>
                      <div className="truncate font-mono text-[10px] text-slate-500">@{row.username}</div>
                    </div>
                    <div className="hidden w-16 text-right sm:block">
                      <div className="font-mono text-[11px] text-slate-300">{row.pct}%</div>
                      <div className="font-mono text-[9px] text-slate-600">
                        {row.done}/{row.due}
                      </div>
                    </div>
                    <div className="w-16 text-right font-mono text-sm font-semibold text-cyan">{row.points}</div>
                    <span className="inline-flex w-10 items-center justify-end gap-1 font-mono text-[10px] text-amber">
                      <Flame size={10} /> {row.streak}
                    </span>
                  </li>
                )
              })}
              {!rest.length ? (
                <li className="rounded-xl border border-dashed border-white/10 px-3 py-6 text-center font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
                  Podium is the whole ladder right now
                </li>
              ) : null}
            </ul>
          </Card>
        </>
      ) : (
        <Card>
          <EmptyState
            icon={<Trophy size={20} />}
            title={scope === 'friends' ? 'No squad on the board yet' : 'Nobody is public yet'}
            body={
              scope === 'friends'
                ? 'Add a friend and complete a quest — the board fills as soon as they accept.'
                : 'Members appear here only when their profile is public and they share stats.'
            }
            action={
              <Link to="/friends" className="btn-primary">
                Find squad
              </Link>
            }
          />
        </Card>
      )}

      <Card>
        <SectionTitle title="Scoring, in the open" hint="Transparent, and impossible to inflate from the browser" />
        <ul className="space-y-2 text-xs leading-relaxed text-slate-400">
          <li>
            <span className="font-semibold text-slate-200">Completion rate</span> = completed scheduled quests ÷ scheduled
            quests × 100. Days with nothing scheduled are ignored, not counted as failures.
          </li>
          <li>
            <span className="font-semibold text-slate-200">Points</span> = 10 × completions this week + 50 × achievements
            earned this week. A unique constraint blocks logging the same quest twice in a day.
          </li>
          <li>
            <span className="font-semibold text-slate-200">Streaks</span> count consecutive perfect days. An unfinished
            today does not break yesterday's run.
          </li>
          <li>Only aggregates leave the database — rivals never receive habit names, notes or schedules.</li>
        </ul>
        <div className="mt-4 flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-600">
          <Medal size={11} /> verified server-side
        </div>
      </Card>
    </div>
  )
}
