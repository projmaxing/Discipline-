import type { Category, Schedule } from './types'

export const CATEGORY_TONE: Record<Category, string> = {
  Health: '#34D399',
  Study: '#2E8BFF',
  Fitness: '#F2B33D',
  Personal: '#B79CFF',
  Work: '#22D3EE',
  Social: '#F0616B',
  Sleep: '#8B5CF6',
  Other: '#94A3B8',
}

export const SCHEDULE_LABEL: Record<Schedule, string> = {
  daily: 'Every day',
  weekdays: 'Weekdays',
  weekends: 'Weekends',
  weekly: 'Weekly',
  monthly: 'Monthly',
}
