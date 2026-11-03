# Migrating HabitFlow desktop → HabitFlow web

The desktop application is **preserved**: `habit.py` is unchanged, still runs, and
its data lives at `~/.habitflow/data.json`. Nothing in this repository deletes or
rewrites that file.

## Data shape

```jsonc
{
  "tasks": [{ "id": "...", "name": "Drink 4L of water", "category": "Health",
              "recurrence": "Daily", "recurrence_days": [], "daily_target": "4L",
              "notes": "...", "pinned": true }],
  "completions": { "2026-10-29": ["task-id", "..."] },
  "settings": { "xp": 130, "theme": "dark", "window_alpha": 0.93 }
}
```

The web app stores the same concepts in normalised tables. The importer maps them
one-to-one and leaves the source file alone.

## Field mapping

| Desktop | Web | Notes |
| --- | --- | --- |
| `tasks[].name` | `habits.name` | 1–80 characters, trimmed |
| `tasks[].notes` | `habits.description` | truncated to 400 characters by the schema check |
| `tasks[].category` | `habits.category` | unknown values fall back to `Other` |
| `tasks[].recurrence` | `habits.schedule` | `Daily→daily`, `Weekdays→weekdays`, `Weekends→weekends`, `Weekly→weekly`, `Monthly→monthly` |
| `tasks[].recurrence_days` | `habits.schedule_days` | kept only for `weekly` |
| `tasks[].daily_target` | `habits.target` | 24 characters max |
| `tasks[].pinned` | — | not carried over: the web list is short and filterable instead |
| `completions[date][]` | `completions.completed_on` | one row per habit/day |
| `settings.xp` | derived | the web app recomputes XP/level from completion history |
| `settings.theme` | — | the web app is dark-only by design |
| desktop `id` | new UUID | mapped in memory during the import only |

Dates outside the last 400 days, malformed dates, and dates in the future are
skipped, because the schema rejects them by design.

## Import behaviour

- **Additive.** Existing web habits are untouched; nothing is overwritten.
- **Idempotent per row.** Completions are upserted on `(habit_id, completed_on)`, so
  importing the same file twice does not duplicate anything.
- **Local file never modified.** Export or copy `~/.habitflow/data.json` yourself and
  upload it; the browser reads the file you choose.
- **No automatic synchronisation.** Desktop and web are independent after the import.

## Equivalent calculations

| Concept | Desktop (`habit.py`) | Web |
| --- | --- | --- |
| XP per completion | 10 | 10 |
| Perfect-day bonus | 50 | 50 (per achievement earned in the window) |
| Levels | `LEVELS = [0, 100, 250, 500, …]` | same thresholds in `lib/scoring.ts` |
| Streak | consecutive perfect days, today skipped when incomplete | same rule in `user_streak()` |
| Completion % | completed ÷ scheduled | same rule in `user_daily()` |

## New in the web version

Friends, requests, blocks, comparison, leaderboards, activity feed, achievements
awarded server-side, privacy controls, email accounts with password recovery.

## Deliberately not implemented

- Pinning habits (desktop convenience; the web list has search + category filters).
- Light theme and window transparency (desktop visual preferences).
- Local JSON export/backup from the web app — Supabase is the source of truth now;
  use the dashboard's database export if you need a dump.

## Post-setup checklist

Run these once against your live project, in this order:

1. **Signup** — create an account; confirm the `profiles` row and default
   `privacy_settings` row were created by the trigger.
2. **Habit CRUD** — create, edit, complete, uncomplete, delete. Confirm one
   `completions` row per habit/day even after double-clicking.
3. **RLS** — in the browser console, attempt `supabase.from('habits').select()` while
   signed in as a second account: you must see only your own rows.
4. **Forgery** — try inserting a completion with another user's `owner_id` or
   `habit_id`: the insert must be rejected by policy.
5. **Friends** — send, accept, reject and cancel requests between two accounts.
   Confirm a duplicate or reciprocal request is refused.
6. **Privacy** — set an account to `private`/`share_stats=false` and confirm the
   compare endpoint raises rather than returning data.
7. **Blocks** — block a friend and confirm they disappear from search, comparison and
   the leaderboard.
8. **Scoring** — complete every habit for a day and confirm `perfect_day` appears in
   `achievements` and the feed, and that points in `leaderboard()` change accordingly.
9. **Recovery** — request a password reset and follow the emailed `/reset` link.
10. **Import** — upload a real `data.json` and verify habit/completion counts plus a
    spot-checked day.
