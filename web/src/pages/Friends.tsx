import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowUpRight,
  Check,
  Loader2,
  Search,
  ShieldOff,
  UserMinus,
  UserPlus,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import {
  blockUser,
  fetchBlockedIds,
  fetchFriendships,
  fetchProfilesByIds,
  removeFriendship,
  respondToRequest,
  searchProfiles,
  sendFriendRequest,
  unblockUser,
} from '../lib/data'
import type { Friendship, Profile, SearchResult } from '../lib/types'
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

type Tab = 'friends' | 'requests' | 'discover'

export function Friends() {
  const { profile } = useAuth()
  const me = profile?.id ?? ''
  const [tab, setTab] = useState<Tab>('friends')
  const [friendships, setFriendships] = useState<Friendship[]>([])
  const [profiles, setProfiles] = useState<Record<string, Profile>>({})
  const [blocked, setBlocked] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busyKey, setBusyKey] = useState('')

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [searching, setSearching] = useState(false)

  const load = useCallback(async () => {
    if (!me) return
    setLoading(true)
    setError('')
    try {
      const [rows, blockedIds] = await Promise.all([fetchFriendships(), fetchBlockedIds()])
      const ids = Array.from(
        new Set(rows.flatMap((row) => [row.requester, row.addressee]).filter((id) => id !== me)),
      )
      const people = await fetchProfilesByIds(ids)
      setFriendships(rows)
      setBlocked(blockedIds)
      setProfiles(Object.fromEntries(people.map((person) => [person.id, person])))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load your friends.')
    } finally {
      setLoading(false)
    }
  }, [me])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([])
      return
    }
    let active = true
    setSearching(true)
    const timer = window.setTimeout(async () => {
      try {
        const rows = await searchProfiles(query.trim())
        if (active) setResults(rows)
      } catch {
        if (active) setResults([])
      } finally {
        if (active) setSearching(false)
      }
    }, 300)
    return () => {
      active = false
      window.clearTimeout(timer)
    }
  }, [query])

  const incoming = useMemo(
    () => friendships.filter((row) => row.addressee === me && row.status === 'pending'),
    [friendships, me],
  )
  const outgoing = useMemo(
    () => friendships.filter((row) => row.requester === me && row.status === 'pending'),
    [friendships, me],
  )
  const accepted = useMemo(
    () => friendships.filter((row) => row.status === 'accepted'),
    [friendships],
  )

  const friendIdOf = (row: Friendship) => (row.requester === me ? row.addressee : row.requester)

  const act = async (key: string, action: () => Promise<void>) => {
    setBusyKey(key)
    setError('')
    try {
      await action()
      await load()
      if (query) {
        setResults(await searchProfiles(query.trim()))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'That action failed.')
    } finally {
      setBusyKey('')
    }
  }

  if (loading) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner label="Loading friends" />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-50">Friends</h1>
          <p className="mt-1 text-sm text-slate-500">Mutual requests only — nobody can follow you silently</p>
        </div>
        <Segmented<Tab>
          value={tab}
          onChange={setTab}
          options={[
            { value: 'friends', label: `Friends ${accepted.length || ''}`.trim() },
            { value: 'requests', label: `Requests ${incoming.length + outgoing.length || ''}`.trim() },
            { value: 'discover', label: 'Find people' },
          ]}
        />
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      {tab === 'friends' ? (
        <Card>
          <SectionTitle title="Your circle" hint="Comparing completion rates, never habit names" />
          {accepted.length ? (
            <ul className="divide-y divide-white/[0.04]">
              {accepted.map((row) => {
                const person = profiles[friendIdOf(row)]
                const key = `friend-${row.id}`
                return (
                  <li key={row.id} className="flex flex-wrap items-center gap-3 py-3">
                    <Avatar name={person?.display_name ?? 'Friend'} src={person?.avatar_url} size={38} />
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-slate-100">
                        {person?.display_name ?? 'Unknown member'}
                      </div>
                      <div className="truncate text-[11px] text-slate-500">@{person?.username ?? '—'}</div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {person ? (
                        <Link to={`/u/${person.username}`} className="btn-ghost px-3 py-1.5 text-xs">
                          Compare <ArrowUpRight size={13} />
                        </Link>
                      ) : null}
                      <button
                        onClick={() => void act(`${key}-remove`, () => removeFriendship(row.id))}
                        disabled={busyKey === `${key}-remove`}
                        className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 transition hover:bg-rose/10 hover:text-rose"
                        title="Remove friend"
                      >
                        {busyKey === `${key}-remove` ? <Loader2 size={14} className="animate-spin" /> : <UserMinus size={14} />}
                      </button>
                      {person ? (
                        <button
                          onClick={() => void act(`${key}-block`, () => blockUser(person.id))}
                          className="grid h-8 w-8 place-items-center rounded-lg text-slate-500 transition hover:bg-rose/10 hover:text-rose"
                          title="Block member"
                        >
                          <ShieldOff size={14} />
                        </button>
                      ) : null}
                    </div>
                  </li>
                )
              })}
            </ul>
          ) : (
            <EmptyState
              icon={<Users size={20} />}
              title="No friends yet"
              body="Search by username and send a request. Once accepted you can compare weekly completion rates."
              action={<Button onClick={() => setTab('discover')}>Find people</Button>}
            />
          )}
        </Card>
      ) : null}

      {tab === 'requests' ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <SectionTitle title="Incoming" hint={`${incoming.length} waiting`} />
            {incoming.length ? (
              <ul className="space-y-2">
                {incoming.map((row) => {
                  const person = profiles[row.requester]
                  return (
                    <li key={row.id} className="flex items-center gap-3 rounded-xl border border-white/[0.06] p-3">
                      <Avatar name={person?.display_name ?? 'Member'} src={person?.avatar_url} size={34} />
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-sm text-slate-100">{person?.display_name ?? 'Member'}</div>
                        <div className="truncate text-[11px] text-slate-500">@{person?.username ?? '—'}</div>
                      </div>
                      <button
                        onClick={() => void act(`in-${row.id}`, () => respondToRequest(row.id, true))}
                        disabled={busyKey === `in-${row.id}`}
                        className="grid h-8 w-8 place-items-center rounded-lg border border-mint/30 bg-mint/10 text-mint"
                        title="Accept"
                      >
                        <Check size={14} />
                      </button>
                      <button
                        onClick={() => void act(`in-${row.id}-no`, () => respondToRequest(row.id, false))}
                        disabled={busyKey === `in-${row.id}-no`}
                        className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-slate-400"
                        title="Reject"
                      >
                        <X size={14} />
                      </button>
                    </li>
                  )
                })}
              </ul>
            ) : (
              <p className="py-6 text-center text-xs text-slate-500">No incoming requests.</p>
            )}
          </Card>

          <Card>
            <SectionTitle title="Sent" hint="Waiting for the other side" />
            {outgoing.length ? (
              <ul className="space-y-2">
                {outgoing.map((row) => {
                  const person = profiles[row.addressee]
                  return (
                    <li key={row.id} className="flex items-center gap-3 rounded-xl border border-white/[0.06] p-3">
                      <Avatar name={person?.display_name ?? 'Member'} src={person?.avatar_url} size={34} />
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-sm text-slate-100">{person?.display_name ?? 'Member'}</div>
                        <div className="truncate text-[11px] text-slate-500">@{person?.username ?? '—'}</div>
                      </div>
                      <button
                        onClick={() => void act(`out-${row.id}`, () => removeFriendship(row.id))}
                        className="text-[11px] font-semibold text-slate-500 hover:text-rose"
                      >
                        Cancel
                      </button>
                    </li>
                  )
                })}
              </ul>
            ) : (
              <p className="py-6 text-center text-xs text-slate-500">No pending requests.</p>
            )}
          </Card>
        </div>
      ) : null}

      {tab === 'discover' ? (
        <Card>
          <SectionTitle title="Find people" hint="Search by username (at least two characters)" />
          <div className="relative">
            <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="field pl-9"
              placeholder="search usernames"
            />
            {searching ? <Loader2 size={14} className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-slate-500" /> : null}
          </div>

          <div className="mt-4 space-y-2">
            {query.trim().length < 2 ? (
              <p className="py-6 text-center text-xs text-slate-500">Type a username to search.</p>
            ) : results.length ? (
              results.map((result) => (
                <div key={result.id} className="flex items-center gap-3 rounded-xl border border-white/[0.06] p-3">
                  <Avatar name={result.display_name} src={result.avatar_url} size={34} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm text-slate-100">{result.display_name}</div>
                    <div className="truncate text-[11px] text-slate-500">@{result.username}</div>
                  </div>
                  {result.relationship === 'friend' ? (
                    <span className="chip">Friends</span>
                  ) : result.relationship === 'request_sent' ? (
                    <span className="chip">Requested</span>
                  ) : result.relationship === 'request_received' ? (
                    <Button variant="ghost" className="px-3 py-1.5 text-xs" onClick={() => setTab('requests')}>
                      Review request
                    </Button>
                  ) : (
                    <Button
                      className="px-3 py-1.5 text-xs"
                      onClick={() => void act(`add-${result.id}`, () => sendFriendRequest(result.id))}
                      disabled={busyKey === `add-${result.id}`}
                    >
                      <UserPlus size={13} /> Add
                    </Button>
                  )}
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-xs text-slate-500">No members match that username.</p>
            )}
          </div>

          {blocked.length ? (
            <div className="mt-6 border-t border-white/[0.06] pt-4">
              <SectionTitle title="Blocked" hint="They cannot find or compare with you" />
              <div className="flex flex-wrap gap-2">
                {blocked.map((id) => (
                  <button
                    key={id}
                    onClick={() => void act(`unblock-${id}`, () => unblockUser(id))}
                    className={cx(
                      'chip transition hover:border-white/25',
                      busyKey === `unblock-${id}` && 'opacity-60',
                    )}
                  >
                    {profiles[id]?.username ?? id.slice(0, 8)} · unblock
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  )
}
