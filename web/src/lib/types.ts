export type Category =
  | 'Health'
  | 'Study'
  | 'Fitness'
  | 'Personal'
  | 'Work'
  | 'Social'
  | 'Sleep'
  | 'Other'

export type Schedule = 'daily' | 'weekdays' | 'weekends' | 'weekly' | 'monthly'

export interface Profile {
  id: string
  username: string
  display_name: string
  avatar_url: string | null
  bio: string | null
  created_at: string
}

export interface Habit {
  id: string
  owner_id: string
  name: string
  description: string | null
  category: Category
  schedule: Schedule
  schedule_days: number[]
  target: string | null
  archived: boolean
  created_at: string
}

export interface Completion {
  id: number
  habit_id: string
  owner_id: string
  completed_on: string
  created_at: string
}

export type FriendshipStatus = 'pending' | 'accepted' | 'rejected'

export interface Friendship {
  id: string
  requester: string
  addressee: string
  status: FriendshipStatus
  created_at: string
  responded_at: string | null
}

export interface PrivacySettings {
  user_id: string
  profile_visibility: 'public' | 'friends' | 'private'
  share_activity: boolean
  share_habit_names: boolean
  share_stats: boolean
  updated_at: string
}

export type AchievementCode =
  | 'first_light'
  | 'perfect_day'
  | 'week_streak'
  | 'month_streak'
  | 'century'

export interface Achievement {
  id: string
  user_id: string
  code: AchievementCode
  earned_on: string
}

export type ActivityKind = 'perfect_day' | 'streak_milestone' | 'achievement' | 'joined'

export interface ActivityEvent {
  id: number
  user_id: string
  kind: ActivityKind
  title: string
  created_at: string
}

export interface LeaderboardRow {
  user_id: string
  username: string
  display_name: string
  avatar_url: string | null
  done: number
  due: number
  pct: number
  points: number
  streak: number
}

export interface SearchResult {
  id: string
  username: string
  display_name: string
  avatar_url: string | null
  relationship: 'friend' | 'request_sent' | 'request_received' | 'none'
}

export interface CompareDay {
  day: string
  due: number
  done: number
}

export interface CompareStats {
  user_id: string
  today: { due: number; done: number }
  week: { due: number; done: number }
  streak: number
  best_streak: number
  series: CompareDay[]
}

export interface DayProgress {
  day: string
  due: number
  done: number
}
