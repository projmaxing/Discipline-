# HabitFlow Web — social habit tracking

A full-stack rewrite of HabitFlow: habits, streaks and scores plus real friends,
comparison and leaderboards. The original Tkinter desktop app (`../habit.py`) is
kept untouched as a reference and for local-data export.

**Stack:** React 18 · TypeScript · Vite · Tailwind CSS · Supabase (Auth + Postgres) · Recharts · lucide-react

> **Status:** the frontend is complete and builds. It has **not** been run against a
> live Supabase project because no credentials were available in the build
> environment. Until you add `web/.env`, the app deliberately shows a setup screen
> instead of faking authentication. See *Verification* at the bottom.

---

## Quick start

```bash
cd web
npm install

# 1. create a Supabase project, then:
cp .env.example .env          # fill in VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY

# 2. apply the schema (Supabase SQL editor, or the CLI)
#    paste the whole of supabase/migrations/0001_social_habits.sql

# 3. run it
npm run dev                   # http://localhost:5173
```

### Supabase project settings

| Setting | Value |
| --- | --- |
| Authentication → Providers → Email | enabled (confirm email optional) |
| Authentication → URL Configuration → Site URL | `http://localhost:5173` in dev, your domain in production |
| Additional redirect URLs | `http://localhost:5173/reset` (and the production equivalent) |

Only the **anon** key belongs in the frontend. The `service_role` key must never be
used here — Row Level Security is the security boundary.

---

## Scripts

```bash
npm run dev        # Vite dev server (host 0.0.0.0, port 5173)
npm run typecheck  # tsc --noEmit
npm run build      # typecheck + production bundle into dist/
npm run preview    # serve the production build
```

---

## What is implemented

**Accounts** — email/password signup with username selection, login, logout,
persistent sessions, password reset by email, recovery page, profile editing
(display name, unique username, bio, avatar URL).

**Dashboard** — greeting, date, animated completion ring, completed vs scheduled
counts, today's checklist with optimistic completion, current and best streak,
weekly completion %, level and XP, weekly bar chart, achievement strip, friends'
activity preview.

**Habits** — create, edit, complete/uncomplete, delete; categories; descriptions;
targets; schedules (daily, weekdays, weekends, weekly with day picker, monthly);
search and category filters; empty states.

**Friends** — username search (blocker-aware), send request, accept/reject, cancel,
friends list, compare links, remove friend, block/unblock. Duplicate and reciprocal
requests are prevented by a canonical pair index in the database.

**Comparison** — today, week, streak, best streak plus a 30-day completion-rate
chart of you versus a friend. Friends only ever receive aggregates.

**Leaderboard** — friends and public scopes, ranked by a transparent score derived
from validated completions.

**Activity feed** — perfect days, streak milestones, achievements and joins from
you and accepted friends, subject to each member's sharing settings.

**Desktop import** — upload `~/.habitflow/data.json` in Settings to copy habits and
completion history into the account. The local file is never modified.

---

## Data model

`supabase/migrations/0001_social_habits.sql` creates:

| Table | Purpose | Key constraints |
| --- | --- | --- |
| `profiles` | public identity | unique lowercase `username`, format check |
| `habits` | owned habits | owner FK, category/schedule checks, archive flag |
| `completions` | one row per habit per day | `unique (habit_id, completed_on)`, no future dates, 400-day window |
| `friendships` | requests + accepted links | `unique (least, greatest)` pair, no self-pairs |
| `blocks` | one-directional blocks | composite PK, no self-blocks |
| `privacy_settings` | visibility + sharing | one row per profile |
| `achievements` | earned badges | `unique (user_id, code)`, definer-only writes |
| `activity_events` | feed events | trigger-only writes |

### Scheduling

`habit_due_on(schedule, schedule_days, day)` mirrors the desktop recurrence rules
and is used by every aggregate so due counts are always consistent.

- `monthly` = first of the month (the desktop app's rule)
- `weekly` with no days selected = Monday
- `weekdays` = Mon–Fri, `weekends` = Sat/Sun

### Scoring (transparent, server-side)

- Completion rate = `completed scheduled habits / scheduled habits × 100`; days with
  nothing scheduled are ignored rather than counted as failures.
- Streak = consecutive perfect days; an unfinished *today* does not break yesterday's
  streak (same rule as the desktop app).
- Points = `10 × completions in window + 50 × achievements earned in window`.
- Best streak scans 400 days of derived daily progress.

All of it is computed inside `SECURITY DEFINER` functions from `completions` rows.
The browser cannot submit a score, and `user_daily`, `user_streak`, `user_best_streak`,
`habit_due_on`, `handle_completion` and `handle_new_user` have `EXECUTE` revoked from
`anon` and `authenticated`.

The relationship predicates `is_friend`, `is_blocked` and `can_view_profile` remain
executable by signed-in users because RLS policy expressions run with the caller's
privileges — revoking them would break every profile, achievement and activity read.
The exposure is limited to "does an accepted friendship/block exist between these two
ids"; habit names, notes, schedules and completion rows are never returned.

---

## Security model

Row Level Security is enabled on every table.

- **Habits** are readable and writable only by their owner. They are never exposed to
  friends — friends receive aggregate stats through `compare_stats()`.
- **Completions** are readable and writable only by the owner, and an insert must
  reference a habit the caller owns. The unique constraint blocks duplicate logging,
  so scores cannot be inflated by replaying writes.
- **Friendships** are visible only to the two parties. Only the addressee can accept
  or reject; blockers cannot be re-requested.
- **Blocks** cut both directions for profile visibility, friend search and
  comparison.
- **Achievements and activity events** have no client insert policy at all; they are
  written by triggers.
- **Privacy** is enforced inside `can_view_profile()`, `compare_stats()`,
  `leaderboard()` and the activity RLS policy — not only in the UI.
- Profile search returns a deliberately limited projection
  (`search_profiles()`), so bios and emails are not enumerable.

---

## Migrating desktop data

1. In the desktop app, export or locate `~/.habitflow/data.json`.
2. Sign in to the web app → **Settings → Import desktop data → Choose data.json**.
3. Review the summary: habits and completions imported, rows skipped.

Mapping details, what carries over and what does not live in
[`docs/MIGRATION.md`](docs/MIGRATION.md).

---

## Verification

Performed in this environment:

- `npm install` (184 packages), `npx tsc --noEmit` clean, `npm run build` exit 0
  (2,239 modules, 912 KB `dist`), production preview served with a 200 on both the
  HTML and the JS asset.
- **The migration was executed against a real PostgreSQL server**, with Supabase's
  `anon` / `authenticated` / `service_role` roles, `auth.uid()` and its default
  grants stubbed in, then attacked with 31 assertions as two different users. All
  passed:
  - the signup trigger created profiles and privacy rows; usernames were derived from
    email when no metadata was supplied;
  - duplicate completions were blocked by the unique index, and forged completions or
    forged habit ownership were rejected by RLS;
  - a stranger saw zero habits, completions, profiles, achievements and activity;
  - friend requests could only be created as `pending`, duplicates hit the pair index,
    self-requests were rejected, and comparison was denied until acceptance;
  - after acceptance the profile and aggregates became visible, habits stayed
    invisible, and the leaderboard score matched the formula (`10 + 2 × 50 = 110`);
  - `share_stats = false` denied comparison and hid achievements, blocking hid the
    profile and removed the user from the leaderboard, and unblocking restored it;
  - `user_daily`, `user_streak`, `user_best_streak` and `habit_due_on` were unreachable
    for `anon`/`authenticated`, leaving only the four intended RPCs.

This found and fixed two real defects: friend-visible achievements and activity were
silently denied because the policy read `privacy_settings` as the caller (whose own
policy hid the row), and three scoring helpers were still executable by signed-in
users, leaking other users' streaks.

**Not performed (no credentials / no browser automation available):**
- Signup, login, session persistence and password recovery against a hosted Supabase
  project. The SQL ran against stock PostgreSQL with Supabase's surface stubbed, not
  against the hosted service.
- Any browser interaction or cross-browser/mobile testing of the rendered app.

Treat the backend as *designed and reviewed*, not *verified*. The first thing to do
after connecting a project is walk through the manual test list in
[`docs/MIGRATION.md`](docs/MIGRATION.md#post-setup-checklist).
