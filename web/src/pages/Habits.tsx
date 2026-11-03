import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { Filter, ListChecks, Plus, Search } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import {
  archiveHabit,
  createHabit,
  fetchCompletions,
  fetchHabits,
  setCompletion,
  updateHabit,
} from '../lib/data'
import { CATEGORIES, SCHEDULES, WEEKDAY_LABELS, isoDayLocal } from '../lib/scoring'
import { CATEGORY_TONE } from '../lib/theme'
import type { Category, Completion, Habit, Schedule } from '../lib/types'
import { HabitItem } from '../components/HabitItem'
import {
  Button,
  Card,
  EmptyState,
  ErrorNote,
  Field,
  Modal,
  SectionTitle,
  SelectField,
  Spinner,
  cx,
} from '../components/ui'

interface Draft {
  name: string
  description: string
  category: Category
  schedule: Schedule
  schedule_days: number[]
  target: string
}

const EMPTY_DRAFT: Draft = {
  name: '',
  description: '',
  category: 'Health',
  schedule: 'daily',
  schedule_days: [],
  target: '',
}

export function Habits() {
  const { profile } = useAuth()
  const [habits, setHabits] = useState<Habit[]>([])
  const [completions, setCompletions] = useState<Completion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<'All' | Category>('All')
  const [editorOpen, setEditorOpen] = useState(false)
  const [editing, setEditing] = useState<Habit | null>(null)
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<Habit | null>(null)
  const [busyId, setBusyId] = useState<string | null>(null)

  const todayKey = isoDayLocal(new Date())

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [habitRows, completionRows] = await Promise.all([fetchHabits(), fetchCompletions(7)])
      setHabits(habitRows)
      setCompletions(completionRows)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load habits.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const doneToday = useMemo(
    () => new Set(completions.filter((row) => row.completed_on === todayKey).map((row) => row.habit_id)),
    [completions, todayKey],
  )

  const visible = habits.filter((habit) => {
    const matchesQuery = habit.name.toLowerCase().includes(query.trim().toLowerCase())
    const matchesFilter = filter === 'All' || habit.category === filter
    return matchesQuery && matchesFilter
  })

  const openCreate = () => {
    setEditing(null)
    setDraft(EMPTY_DRAFT)
    setEditorOpen(true)
  }

  const openEdit = (habit: Habit) => {
    setEditing(habit)
    setDraft({
      name: habit.name,
      description: habit.description ?? '',
      category: habit.category,
      schedule: habit.schedule,
      schedule_days: habit.schedule_days ?? [],
      target: habit.target ?? '',
    })
    setEditorOpen(true)
  }

  const save = async (event: FormEvent) => {
    event.preventDefault()
    if (!profile) return
    setSaving(true)
    setError('')
    try {
      const input = {
        name: draft.name.trim(),
        description: draft.description.trim() || null,
        category: draft.category,
        schedule: draft.schedule,
        schedule_days: draft.schedule === 'weekly' ? draft.schedule_days : [],
        target: draft.target.trim() || null,
      }
      if (editing) {
        const updated = await updateHabit(editing.id, input)
        setHabits((rows) => rows.map((row) => (row.id === updated.id ? updated : row)))
      } else {
        const created = await createHabit(profile.id, input)
        setHabits((rows) => [...rows, created])
      }
      setEditorOpen(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save the habit.')
    } finally {
      setSaving(false)
    }
  }

  const confirmDelete = async () => {
    if (!deleting) return
    const target = deleting
    setDeleting(null)
    try {
      await archiveHabit(target.id)
      setHabits((rows) => rows.filter((row) => row.id !== target.id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete the habit.')
    }
  }

  const toggle = async (habit: Habit) => {
    const already = doneToday.has(habit.id)
    const previous = completions
    setBusyId(habit.id)
    setCompletions(
      already
        ? completions.filter((row) => !(row.habit_id === habit.id && row.completed_on === todayKey))
        : [
            ...completions,
            {
              id: Date.now(),
              habit_id: habit.id,
              owner_id: habit.owner_id,
              completed_on: todayKey,
              created_at: new Date().toISOString(),
            },
          ],
    )
    try {
      await setCompletion(habit.id, habit.owner_id, todayKey, !already)
    } catch (err) {
      setCompletions(previous)
      setError(err instanceof Error ? err.message : 'Could not save that completion.')
    } finally {
      setBusyId(null)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-50">Habits</h1>
          <p className="mt-1 text-sm text-slate-500">Create, edit and complete the routines that run your day</p>
        </div>
        <Button onClick={openCreate}>
          <Plus size={16} /> New habit
        </Button>
      </div>

      {error ? <ErrorNote>{error}</ErrorNote> : null}

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-[220px] flex-1">
          <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search habits"
            className="field pl-9"
          />
        </div>
        <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
          <Filter size={13} /> Filter
        </span>
        <div className="flex flex-wrap gap-1.5">
          {(['All', ...CATEGORIES] as ('All' | Category)[]).map((category) => (
            <button
              key={category}
              onClick={() => setFilter(category)}
              className={cx(
                'rounded-full border px-3 py-1.5 text-[11px] font-medium transition',
                filter === category
                  ? 'border-neon/50 bg-neon/15 text-neon-soft'
                  : 'border-white/10 bg-white/[0.03] text-slate-400 hover:border-white/20 hover:text-slate-200',
              )}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid place-items-center py-20">
          <Spinner label="Loading habits" />
        </div>
      ) : visible.length ? (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              {habits.filter((habit) => doneToday.has(habit.id)).length} of {habits.length} habits complete today
            </span>
            <span>{visible.length} shown</span>
          </div>
          {visible.map((habit) => (
            <HabitItem
              key={habit.id}
              habit={habit}
              done={doneToday.has(habit.id)}
              busy={busyId === habit.id}
              onToggle={() => void toggle(habit)}
              onEdit={() => openEdit(habit)}
              onDelete={() => setDeleting(habit)}
            />
          ))}
        </div>
      ) : (
        <Card>
          <EmptyState
            icon={<ListChecks size={20} />}
            title={habits.length ? 'No habits match this view' : 'Your first habit starts here'}
            body={
              habits.length
                ? 'Try a different category or clear the search field.'
                : 'Pick something small enough to do today. The dashboard will track the streak for you.'
            }
            action={
              habits.length ? (
                <Button
                  variant="ghost"
                  onClick={() => {
                    setQuery('')
                    setFilter('All')
                  }}
                >
                  Clear filters
                </Button>
              ) : (
                <Button onClick={openCreate}>
                  <Plus size={16} /> Create habit
                </Button>
              )
            }
          />
        </Card>
      )}

      <Modal
        open={editorOpen}
        onClose={() => setEditorOpen(false)}
        title={editing ? 'Edit habit' : 'New habit'}
        description={editing ? 'Changes apply to future days only.' : 'Small, specific habits survive longer.'}
        footer={
          <>
            <Button variant="ghost" onClick={() => setEditorOpen(false)}>
              Cancel
            </Button>
            <Button form="habit-form" type="submit" disabled={saving}>
              {saving ? 'Saving' : editing ? 'Save changes' : 'Create habit'}
            </Button>
          </>
        }
      >
        <form id="habit-form" onSubmit={save} className="space-y-4">
          <Field
            label="Habit name"
            required
            maxLength={80}
            value={draft.name}
            onChange={(event) => setDraft({ ...draft, name: event.target.value })}
            placeholder="Morning run"
          />
          <label className="block">
            <span className="label mb-1.5 block">Description</span>
            <textarea
              className="field min-h-[74px] resize-none"
              maxLength={400}
              value={draft.description}
              onChange={(event) => setDraft({ ...draft, description: event.target.value })}
              placeholder="Optional context or notes for yourself"
            />
          </label>
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField
              label="Category"
              value={draft.category}
              onChange={(event) => setDraft({ ...draft, category: event.target.value as Category })}
            >
              {CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </SelectField>
            <SelectField
              label="Schedule"
              value={draft.schedule}
              onChange={(event) => setDraft({ ...draft, schedule: event.target.value as Schedule })}
            >
              {SCHEDULES.map((schedule) => (
                <option key={schedule.value} value={schedule.value}>
                  {schedule.label}
                </option>
              ))}
            </SelectField>
          </div>

          {draft.schedule === 'weekly' ? (
            <div>
              <span className="label mb-1.5 block">Days</span>
              <div className="flex gap-1.5">
                {WEEKDAY_LABELS.map((label, index) => {
                  const active = draft.schedule_days.includes(index)
                  return (
                    <button
                      key={`${label}-${index}`}
                      type="button"
                      onClick={() =>
                        setDraft({
                          ...draft,
                          schedule_days: active
                            ? draft.schedule_days.filter((day) => day !== index)
                            : [...draft.schedule_days, index],
                        })
                      }
                      className={cx(
                        'h-9 w-9 rounded-lg border text-xs font-semibold transition',
                        active
                          ? 'border-neon/60 bg-neon/20 text-neon-soft'
                          : 'border-white/10 bg-white/[0.03] text-slate-400 hover:border-white/25',
                      )}
                    >
                      {label}
                    </button>
                  )
                })}
              </div>
            </div>
          ) : null}

          <Field
            label="Target (optional)"
            maxLength={24}
            value={draft.target}
            onChange={(event) => setDraft({ ...draft, target: event.target.value })}
            placeholder="45 min"
          />
        </form>
      </Modal>

      <Modal
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        title="Delete habit?"
        description="Completion history for this habit is removed too. This cannot be undone."
        width="max-w-md"
        footer={
          <>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Keep it
            </Button>
            <Button variant="danger" onClick={() => void confirmDelete()}>
              Delete habit
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-300">
          <span className="font-semibold text-slate-100">{deleting?.name}</span> and all of its logged days will be
          deleted.
        </p>
      </Modal>
    </div>
  )
}
