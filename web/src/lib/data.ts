import { isoDayLocal, addDays } from './scoring'
import { requireClient } from './supabase'
import type {
  Achievement,
  ActivityEvent,
  Category,
  CompareStats,
  Completion,
  Friendship,
  Habit,
  LeaderboardRow,
  PrivacySettings,
  Profile,
  Schedule,
  SearchResult,
} from './types'

const client = () => requireClient()

function fail(error: { message: string } | null): never {
  throw new Error(error?.message ?? 'Unexpected database error')
}

export interface HabitInput {
  name: string
  description?: string | null
  category: Category
  schedule: Schedule
  schedule_days: number[]
  target?: string | null
}

export async function fetchProfile(userId: string): Promise<Profile | null> {
  const { data, error } = await client()
    .from('profiles')
    .select('id, username, display_name, avatar_url, bio, created_at')
    .eq('id', userId)
    .maybeSingle()
  if (error) fail(error)
  return (data as Profile | null) ?? null
}

export async function updateProfile(
  userId: string,
  patch: Partial<Pick<Profile, 'username' | 'display_name' | 'bio' | 'avatar_url'>>,
): Promise<Profile> {
  const { data, error } = await client()
    .from('profiles')
    .update(patch)
    .eq('id', userId)
    .select('id, username, display_name, avatar_url, bio, created_at')
    .single()
  if (error) fail(error)
  return data as Profile
}

export async function fetchPrivacy(userId: string): Promise<PrivacySettings | null> {
  const { data, error } = await client()
    .from('privacy_settings')
    .select('*')
    .eq('user_id', userId)
    .maybeSingle()
  if (error) fail(error)
  return (data as PrivacySettings | null) ?? null
}

export async function updatePrivacy(
  userId: string,
  patch: Partial<PrivacySettings>,
): Promise<PrivacySettings> {
  const { data, error } = await client()
    .from('privacy_settings')
    .upsert({ user_id: userId, ...patch, updated_at: new Date().toISOString() })
    .select('*')
    .single()
  if (error) fail(error)
  return data as PrivacySettings
}

export async function fetchHabits(): Promise<Habit[]> {
  const { data, error } = await client()
    .from('habits')
    .select('*')
    .eq('archived', false)
    .order('created_at', { ascending: true })
  if (error) fail(error)
  return (data as Habit[]) ?? []
}

export async function createHabit(ownerId: string, input: HabitInput): Promise<Habit> {
  const { data, error } = await client()
    .from('habits')
    .insert({ ...input, owner_id: ownerId })
    .select('*')
    .single()
  if (error) fail(error)
  return data as Habit
}

export async function updateHabit(habitId: string, input: HabitInput): Promise<Habit> {
  const { data, error } = await client()
    .from('habits')
    .update(input)
    .eq('id', habitId)
    .select('*')
    .single()
  if (error) fail(error)
  return data as Habit
}

export async function archiveHabit(habitId: string): Promise<void> {
  const { error } = await client().from('habits').update({ archived: true }).eq('id', habitId)
  if (error) fail(error)
}

export async function fetchCompletions(days = 120): Promise<Completion[]> {
  const since = isoDayLocal(addDays(new Date(), -(days - 1)))
  const { data, error } = await client()
    .from('completions')
    .select('id, habit_id, owner_id, completed_on, created_at')
    .gte('completed_on', since)
    .order('completed_on', { ascending: true })
  if (error) fail(error)
  return (data as Completion[]) ?? []
}

export async function setCompletion(
  habitId: string,
  ownerId: string,
  day: string,
  done: boolean,
): Promise<void> {
  if (done) {
    const { error } = await client()
      .from('completions')
      .insert({ habit_id: habitId, owner_id: ownerId, completed_on: day })
    // 23505 = already logged; treat as success so double clicks are harmless
    if (error && error.code !== '23505') fail(error)
    return
  }
  const { error } = await client()
    .from('completions')
    .delete()
    .eq('habit_id', habitId)
    .eq('completed_on', day)
  if (error) fail(error)
}

export async function fetchFriendships(): Promise<Friendship[]> {
  const { data, error } = await client().from('friendships').select('*').order('created_at', { ascending: false })
  if (error) fail(error)
  return (data as Friendship[]) ?? []
}

export async function fetchProfilesByIds(ids: string[]): Promise<Profile[]> {
  if (!ids.length) return []
  const { data, error } = await client()
    .from('profiles')
    .select('id, username, display_name, avatar_url, bio, created_at')
    .in('id', ids)
  if (error) fail(error)
  return (data as Profile[]) ?? []
}

export async function sendFriendRequest(addressee: string): Promise<void> {
  const { data: auth } = await client().auth.getUser()
  const me = auth.user?.id
  if (!me) throw new Error('You need to sign in first.')
  const { error } = await client()
    .from('friendships')
    .insert({ requester: me, addressee, status: 'pending' })
  if (error) {
    if (error.code === '23505') throw new Error('A request already exists with this person.')
    fail(error)
  }
}

export async function respondToRequest(id: string, accept: boolean): Promise<void> {
  const { error } = await client()
    .from('friendships')
    .update({ status: accept ? 'accepted' : 'rejected', responded_at: new Date().toISOString() })
    .eq('id', id)
  if (error) fail(error)
}

export async function removeFriendship(id: string): Promise<void> {
  const { error } = await client().from('friendships').delete().eq('id', id)
  if (error) fail(error)
}

export async function blockUser(userId: string): Promise<void> {
  const { data: auth } = await client().auth.getUser()
  const me = auth.user?.id
  if (!me) throw new Error('You need to sign in first.')
  const { error } = await client().from('blocks').insert({ blocker: me, blocked: userId })
  if (error && error.code !== '23505') fail(error)
}

export async function unblockUser(userId: string): Promise<void> {
  const { data: auth } = await client().auth.getUser()
  const me = auth.user?.id
  if (!me) throw new Error('You need to sign in first.')
  const { error } = await client().from('blocks').delete().eq('blocker', me).eq('blocked', userId)
  if (error) fail(error)
}

export async function fetchBlockedIds(): Promise<string[]> {
  const { data, error } = await client().from('blocks').select('blocked')
  if (error) fail(error)
  return ((data as { blocked: string }[]) ?? []).map((row) => row.blocked)
}

export async function searchProfiles(query: string): Promise<SearchResult[]> {
  const { data, error } = await client().rpc('search_profiles', { p_query: query })
  if (error) fail(error)
  return (data as SearchResult[]) ?? []
}

export async function usernameAvailable(username: string): Promise<boolean> {
  const { data, error } = await client().rpc('username_available', { p_username: username })
  if (error) fail(error)
  return Boolean(data)
}

export async function fetchLeaderboard(scope: 'friends' | 'global'): Promise<LeaderboardRow[]> {
  const { data, error } = await client().rpc('leaderboard', { p_scope: scope, p_days: 7 })
  if (error) fail(error)
  return (data as LeaderboardRow[]) ?? []
}

export async function fetchCompareStats(userId: string): Promise<CompareStats> {
  const { data, error } = await client().rpc('compare_stats', { p_user: userId })
  if (error) fail(error)
  return data as CompareStats
}

export async function fetchAchievements(userId: string): Promise<Achievement[]> {
  const { data, error } = await client()
    .from('achievements')
    .select('*')
    .eq('user_id', userId)
    .order('earned_on', { ascending: false })
  if (error) fail(error)
  return (data as Achievement[]) ?? []
}

export async function fetchActivity(limit = 40): Promise<(ActivityEvent & { profile: Pick<Profile, 'username' | 'display_name' | 'avatar_url'> | null })[]> {
  const { data, error } = await client()
    .from('activity_events')
    .select('*, profile:profiles(username, display_name, avatar_url)')
    .order('created_at', { ascending: false })
    .limit(limit)
  if (error) fail(error)
  return (data as (ActivityEvent & { profile: Pick<Profile, 'username' | 'display_name' | 'avatar_url'> | null })[]) ?? []
}

export async function fetchPublicProfileByUsername(username: string): Promise<Profile | null> {
  const { data, error } = await client()
    .from('profiles')
    .select('id, username, display_name, avatar_url, bio, created_at')
    .eq('username', username.toLowerCase())
    .maybeSingle()
  if (error) fail(error)
  return (data as Profile | null) ?? null
}

// ---------------------------------------------------------------------------
// Legacy desktop import (~/.habitflow/data.json)
// ---------------------------------------------------------------------------
interface LegacyTask {
  id?: string
  name?: string
  category?: string
  recurrence?: string
  recurrence_days?: number[]
  daily_target?: string | null
  notes?: string | null
}

export interface LegacyPayload {
  tasks?: LegacyTask[]
  completions?: Record<string, string[]>
}

export interface ImportSummary {
  habits: number
  completions: number
  skipped: number
}

const LEGACY_SCHEDULE: Record<string, Schedule> = {
  daily: 'daily',
  weekdays: 'weekdays',
  weekends: 'weekends',
  weekly: 'weekly',
  monthly: 'monthly',
}

/**
 * Imports a desktop data.json without touching the original file. Nothing is
 * deleted locally, and existing habits in the account are left alone.
 */
export async function importLegacyData(ownerId: string, payload: LegacyPayload): Promise<ImportSummary> {
  const tasks = Array.isArray(payload.tasks) ? payload.tasks : []
  const completions = payload.completions && typeof payload.completions === 'object' ? payload.completions : {}
  const summary: ImportSummary = { habits: 0, completions: 0, skipped: 0 }
  const idMap = new Map<string, string>()

  for (const task of tasks) {
    const name = (task.name ?? '').trim()
    if (!name) {
      summary.skipped += 1
      continue
    }
    const category = (['Health', 'Study', 'Fitness', 'Personal', 'Work', 'Social', 'Sleep', 'Other'] as string[]).includes(
      String(task.category),
    )
      ? (task.category as Category)
      : 'Other'
    const schedule = LEGACY_SCHEDULE[String(task.recurrence ?? 'daily').toLowerCase()] ?? 'daily'
    const days = Array.isArray(task.recurrence_days) ? task.recurrence_days.filter((d) => d >= 0 && d <= 6) : []

    try {
      const habit = await createHabit(ownerId, {
        name,
        description: task.notes?.trim() || null,
        category,
        schedule,
        schedule_days: days,
        target: task.daily_target?.trim() || null,
      })
      if (task.id) idMap.set(task.id, habit.id)
      summary.habits += 1
    } catch {
      summary.skipped += 1
    }
  }

  const rows: { habit_id: string; owner_id: string; completed_on: string }[] = []
  const since = isoDayLocal(addDays(new Date(), -400))
  for (const [day, ids] of Object.entries(completions)) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day) || day > isoDayLocal(new Date()) || day < since) continue
    for (const legacyId of Array.isArray(ids) ? ids : []) {
      const habitId = idMap.get(legacyId)
      if (habitId) rows.push({ habit_id: habitId, owner_id: ownerId, completed_on: day })
    }
  }

  for (let index = 0; index < rows.length; index += 200) {
    const chunk = rows.slice(index, index + 200)
    const { error } = await client()
      .from('completions')
      .upsert(chunk, { onConflict: 'habit_id,completed_on', ignoreDuplicates: true })
    if (error) fail(error)
    summary.completions += chunk.length
  }

  return summary
}
