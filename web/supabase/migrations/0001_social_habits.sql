-- ============================================================================
-- HabitFlow Social — schema, RLS and trusted scoring (PostgreSQL / Supabase)
--
-- Apply with:  supabase db push        (or paste into the SQL editor)
--
-- Design notes
--   * Every score, streak and percentage is derived from `completions` rows.
--     Nothing score-like is stored where a browser could write it.
--   * RLS is the security boundary. The browser only holds the anon key.
--   * Habit names, notes and schedules are never exposed to other users:
--     friends receive aggregates, never rows.
-- ============================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id           uuid primary key references auth.users (id) on delete cascade,
  username     text not null,
  display_name text not null default 'New member',
  avatar_url   text,
  bio          text,
  created_at   timestamptz not null default now(),
  constraint profiles_username_format check (username = lower(username) and username ~ '^[a-z0-9_]{3,20}$'),
  constraint profiles_display_length check (char_length(btrim(display_name)) between 1 and 60),
  constraint profiles_bio_length check (bio is null or char_length(bio) <= 280)
);
create unique index if not exists profiles_username_key on public.profiles (username);

create table if not exists public.habits (
  id            uuid primary key default gen_random_uuid(),
  owner_id      uuid not null references public.profiles (id) on delete cascade,
  name          text not null,
  description   text,
  category      text not null default 'Other',
  schedule      text not null default 'daily',
  schedule_days smallint[] not null default '{}',
  target        text,
  archived      boolean not null default false,
  created_at    timestamptz not null default now(),
  constraint habits_name_length check (char_length(btrim(name)) between 1 and 80),
  constraint habits_description_length check (description is null or char_length(description) <= 400),
  constraint habits_category_check check (category in ('Health','Study','Fitness','Personal','Work','Social','Sleep','Other')),
  constraint habits_schedule_check check (schedule in ('daily','weekdays','weekends','weekly','monthly')),
  constraint habits_target_length check (target is null or char_length(target) <= 24)
);
create index if not exists habits_owner_idx on public.habits (owner_id) where archived = false;

create table if not exists public.completions (
  id           bigint generated always as identity primary key,
  habit_id     uuid not null references public.habits (id) on delete cascade,
  owner_id     uuid not null references public.profiles (id) on delete cascade,
  completed_on date not null,
  created_at   timestamptz not null default now(),
  constraint completions_unique_day unique (habit_id, completed_on),
  constraint completions_not_future check (completed_on <= current_date),
  constraint completions_window check (completed_on >= current_date - 400)
);
create index if not exists completions_owner_day_idx on public.completions (owner_id, completed_on desc);

create type public.friendship_status as enum ('pending', 'accepted', 'rejected');

create table if not exists public.friendships (
  id           uuid primary key default gen_random_uuid(),
  requester    uuid not null references public.profiles (id) on delete cascade,
  addressee    uuid not null references public.profiles (id) on delete cascade,
  status       public.friendship_status not null default 'pending',
  created_at   timestamptz not null default now(),
  responded_at timestamptz,
  constraint friendships_not_self check (requester <> addressee)
);
-- one relationship per pair, in either direction
create unique index if not exists friendships_pair_key
  on public.friendships (least(requester, addressee), greatest(requester, addressee));
create index if not exists friendships_addressee_idx on public.friendships (addressee, status);
create index if not exists friendships_requester_idx on public.friendships (requester, status);

create table if not exists public.blocks (
  blocker    uuid not null references public.profiles (id) on delete cascade,
  blocked    uuid not null references public.profiles (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (blocker, blocked),
  constraint blocks_not_self check (blocker <> blocked)
);

create table if not exists public.privacy_settings (
  user_id            uuid primary key references public.profiles (id) on delete cascade,
  profile_visibility text not null default 'friends',
  share_activity     boolean not null default true,
  share_habit_names  boolean not null default false,
  share_stats        boolean not null default true,
  updated_at         timestamptz not null default now(),
  constraint privacy_visibility_check check (profile_visibility in ('public','friends','private'))
);

create table if not exists public.achievements (
  id        uuid primary key default gen_random_uuid(),
  user_id   uuid not null references public.profiles (id) on delete cascade,
  code      text not null,
  earned_on date not null default current_date,
  constraint achievements_code_check check (code in ('first_light','perfect_day','week_streak','month_streak','century')),
  constraint achievements_once unique (user_id, code)
);

create table if not exists public.activity_events (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references public.profiles (id) on delete cascade,
  kind       text not null,
  title      text not null,
  created_at timestamptz not null default now(),
  constraint activity_kind_check check (kind in ('perfect_day','streak_milestone','achievement','joined')),
  constraint activity_title_length check (char_length(title) <= 120)
);
create index if not exists activity_user_time_idx on public.activity_events (user_id, created_at desc);

-- ---------------------------------------------------------------------------
-- Relationship helpers (SECURITY DEFINER: they read rows the caller cannot)
-- ---------------------------------------------------------------------------
create or replace function public.is_blocked(a uuid, b uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.blocks
    where (blocker = a and blocked = b) or (blocker = b and blocked = a)
  );
$$;

create or replace function public.is_friend(a uuid, b uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.friendships f
    where f.status = 'accepted'
      and ((f.requester = a and f.addressee = b) or (f.requester = b and f.addressee = a))
  );
$$;

create or replace function public.can_view_profile(viewer uuid, target uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select case
    when viewer = target then true
    when public.is_blocked(viewer, target) then false
    else coalesce((
      select case p.profile_visibility
               when 'public' then true
               when 'friends' then public.is_friend(viewer, target)
               else false
             end
      from public.privacy_settings p where p.user_id = target
    ), false)
  end;
$$;

-- ---------------------------------------------------------------------------
-- Scheduling + progress (mirrors the desktop app's recurrence rules)
-- ---------------------------------------------------------------------------
create or replace function public.habit_due_on(p_schedule text, p_days smallint[], p_day date)
returns boolean language sql immutable as $$
  select case p_schedule
    when 'daily'    then true
    when 'weekdays' then extract(isodow from p_day) between 1 and 5
    when 'weekends' then extract(isodow from p_day) in (6, 7)
    when 'weekly'   then coalesce(extract(dow from p_day)::smallint = any (p_days), extract(isodow from p_day) = 1)
    when 'monthly'  then extract(day from p_day) = 1
    else false
  end;
$$;

create or replace function public.user_daily(p_user uuid, p_days int default 30)
returns table (day date, due int, done int)
language sql stable security definer set search_path = public as $$
  with span as (
    select generate_series(current_date - (greatest(p_days, 1) - 1), current_date, interval '1 day')::date as day
  )
  select s.day,
         count(h.id)::int as due,
         count(c.habit_id)::int as done
  from span s
  left join public.habits h
         on h.owner_id = p_user
        and not h.archived
        and public.habit_due_on(h.schedule, h.schedule_days, s.day)
  left join public.completions c
         on c.habit_id = h.id
        and c.completed_on = s.day
  group by s.day
  order by s.day;
$$;

-- Current streak: consecutive perfect days, counting today when already
-- complete and otherwise starting from yesterday.
create or replace function public.user_streak(p_user uuid)
returns int language plpgsql stable security definer set search_path = public as $$
declare
  d date := current_date;
  rec record;
  streak int := 0;
  guard int := 0;
begin
  select count(h.id)::int as due, count(c.habit_id)::int as done
    into rec
  from public.habits h
  left join public.completions c on c.habit_id = h.id and c.completed_on = d
  where h.owner_id = p_user and not h.archived
    and public.habit_due_on(h.schedule, h.schedule_days, d);

  if rec.due = 0 or rec.done < rec.due then
    d := d - 1;
  end if;

  loop
    guard := guard + 1;
    exit when guard > 400;
    select count(h.id)::int as due, count(c.habit_id)::int as done
      into rec
    from public.habits h
    left join public.completions c on c.habit_id = h.id and c.completed_on = d
    where h.owner_id = p_user and not h.archived
      and public.habit_due_on(h.schedule, h.schedule_days, d);
    exit when rec.due = 0 or rec.done < rec.due;
    streak := streak + 1;
    d := d - 1;
  end loop;

  return streak;
end;
$$;

create or replace function public.user_best_streak(p_user uuid)
returns int language plpgsql stable security definer set search_path = public as $$
declare
  rec record;
  run int := 0;
  best int := 0;
begin
  for rec in select * from public.user_daily(p_user, 400) order by day loop
    if rec.due = 0 then
      continue;                      -- no habits scheduled: neither builds nor breaks
    elsif rec.done >= rec.due then
      run := run + 1;
      best := greatest(best, run);
    else
      run := 0;
    end if;
  end loop;
  return best;
end;
$$;

-- ---------------------------------------------------------------------------
-- Friends-only comparison payload
-- ---------------------------------------------------------------------------
create or replace function public.compare_stats(p_user uuid)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare
  me uuid := auth.uid();
  allowed boolean := false;
  week_due int;
  week_done int;
  today_due int;
  today_done int;
  series jsonb;
begin
  if me is null then
    raise exception 'not authenticated' using errcode = '28000';
  end if;

  if me = p_user then
    allowed := true;
  elsif public.is_friend(me, p_user)
        and not public.is_blocked(me, p_user)
        and coalesce((select share_stats from public.privacy_settings where user_id = p_user), false) then
    allowed := true;
  end if;

  if not allowed then
    raise exception 'not authorised' using errcode = '42501';
  end if;

  select coalesce(sum(due), 0)::int, coalesce(sum(done), 0)::int
    into week_due, week_done
  from public.user_daily(p_user, 7);

  select due, done into today_due, today_done
  from public.user_daily(p_user, 1);

  select jsonb_agg(jsonb_build_object('day', day, 'due', due, 'done', done) order by day)
    into series
  from public.user_daily(p_user, 30);

  return jsonb_build_object(
    'user_id', p_user,
    'today', jsonb_build_object('due', coalesce(today_due, 0), 'done', coalesce(today_done, 0)),
    'week', jsonb_build_object('due', week_due, 'done', week_done),
    'streak', public.user_streak(p_user),
    'best_streak', public.user_best_streak(p_user),
    'series', coalesce(series, '[]'::jsonb)
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- Leaderboard: score = 10 per completion + 50 per achievement earned in window
-- ---------------------------------------------------------------------------
create or replace function public.leaderboard(p_scope text default 'friends', p_days int default 7)
returns table (
  user_id uuid, username text, display_name text, avatar_url text,
  done int, due int, pct int, points int, streak int
)
language plpgsql stable security definer set search_path = public as $$
declare
  me uuid := auth.uid();
  window_days int := greatest(1, least(coalesce(p_days, 7), 30));
begin
  if me is null then
    raise exception 'not authenticated' using errcode = '28000';
  end if;

  return query
  with visible as (
    select p.id, p.username, p.display_name, p.avatar_url
    from public.profiles p
    where p.id = me
       or (p_scope = 'friends' and public.is_friend(me, p.id) and not public.is_blocked(me, p.id))
       or (
         p_scope = 'global'
         and not public.is_blocked(me, p.id)
         and coalesce((
           select ps.profile_visibility = 'public' and ps.share_stats
           from public.privacy_settings ps where ps.user_id = p.id
         ), false)
       )
  ),
  totals as (
    select v.id,
           coalesce(sum(d.done), 0)::int as done,
           coalesce(sum(d.due), 0)::int as due
    from visible v
    left join lateral public.user_daily(v.id, window_days) d on true
    group by v.id
  ),
  scored as (
    select v.id, v.username, v.display_name, v.avatar_url,
           t.done, t.due,
           case when t.due = 0 then 0 else round(100.0 * t.done / t.due)::int end as pct,
           (t.done * 10 + 50 * coalesce((
              select count(*) from public.achievements a
              where a.user_id = v.id and a.earned_on >= current_date - (window_days - 1)
           ), 0))::int as points,
           public.user_streak(v.id) as streak
    from visible v join totals t on t.id = v.id
  )
  select s.id, s.username, s.display_name, s.avatar_url,
         s.done, s.due, s.pct, s.points, s.streak
  from scored s
  order by s.points desc, s.pct desc, s.username asc
  limit 100;
end;
$$;

-- ---------------------------------------------------------------------------
-- Search / public profile (limited fields, blocker-aware)
-- ---------------------------------------------------------------------------
create or replace function public.search_profiles(p_query text)
returns table (id uuid, username text, display_name text, avatar_url text, relationship text)
language sql stable security definer set search_path = public as $$
  with me as (select auth.uid() as uid)
  select p.id, p.username, p.display_name, p.avatar_url,
         case
           when exists (select 1 from public.friendships f
                        where f.status = 'accepted'
                          and ((f.requester = m.uid and f.addressee = p.id)
                            or (f.addressee = m.uid and f.requester = p.id))) then 'friend'
           when exists (select 1 from public.friendships f
                        where f.status = 'pending' and f.requester = m.uid and f.addressee = p.id) then 'request_sent'
           when exists (select 1 from public.friendships f
                        where f.status = 'pending' and f.addressee = m.uid and f.requester = p.id) then 'request_received'
           else 'none'
         end
  from public.profiles p, me m
  where m.uid is not null
    and p.id <> m.uid
    and char_length(btrim(p_query)) >= 2
    and p.username ilike '%' || btrim(p_query) || '%'
    and not public.is_blocked(m.uid, p.id)
  order by p.username
  limit 20;
$$;

create or replace function public.username_available(p_username text)
returns boolean language sql stable security definer set search_path = public as $$
  select p_username = lower(p_username)
     and p_username ~ '^[a-z0-9_]{3,20}$'
     and not exists (select 1 from public.profiles where username = p_username);
$$;

-- ---------------------------------------------------------------------------
-- Trusted writes: achievements + activity are derived server-side
-- ---------------------------------------------------------------------------
create or replace function public.handle_completion()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  v_due int;
  v_done int;
  v_streak int;
  v_total int;
begin
  select count(*)::int into v_total from public.completions where owner_id = new.owner_id;

  if v_total >= 1 then
    insert into public.achievements (user_id, code, earned_on)
    values (new.owner_id, 'first_light', new.completed_on)
    on conflict (user_id, code) do nothing;
  end if;

  if v_total >= 100 then
    insert into public.achievements (user_id, code) values (new.owner_id, 'century')
    on conflict (user_id, code) do nothing;
  end if;

  select count(h.id)::int, count(c.habit_id)::int
    into v_due, v_done
  from public.habits h
  left join public.completions c on c.habit_id = h.id and c.completed_on = new.completed_on
  where h.owner_id = new.owner_id and not h.archived
    and public.habit_due_on(h.schedule, h.schedule_days, new.completed_on);

  if v_due > 0 and v_done >= v_due then
    insert into public.achievements (user_id, code, earned_on)
    values (new.owner_id, 'perfect_day', new.completed_on)
    on conflict (user_id, code) do update
      set earned_on = least(public.achievements.earned_on, excluded.earned_on);

    insert into public.activity_events (user_id, kind, title)
    select new.owner_id, 'perfect_day', 'Completed every habit for a perfect day'
    where not exists (
      select 1 from public.activity_events
      where user_id = new.owner_id and kind = 'perfect_day' and created_at::date = current_date
    );
  end if;

  v_streak := public.user_streak(new.owner_id);

  if v_streak >= 7 then
    insert into public.achievements (user_id, code) values (new.owner_id, 'week_streak')
    on conflict (user_id, code) do nothing;
  end if;
  if v_streak >= 30 then
    insert into public.achievements (user_id, code) values (new.owner_id, 'month_streak')
    on conflict (user_id, code) do nothing;
  end if;

  if v_streak >= 7 then
    insert into public.activity_events (user_id, kind, title)
    select new.owner_id, 'streak_milestone', 'Reached a ' || v_streak || '-day streak'
    where not exists (
      select 1 from public.activity_events
      where user_id = new.owner_id and kind = 'streak_milestone'
        and created_at::date = current_date
    );
  end if;

  return new;
end;
$$;

drop trigger if exists on_completion_recorded on public.completions;
create trigger on_completion_recorded
  after insert on public.completions
  for each row execute function public.handle_completion();

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
declare
  base text;
  candidate text;
  attempt int := 0;
begin
  -- Prefer the username chosen at signup (stored in user metadata) when it is
  -- well formed and still free; otherwise derive one from the email address.
  base := regexp_replace(lower(split_part(coalesce(new.email, 'member'), '@', 1)), '[^a-z0-9_]', '', 'g');
  if char_length(base) < 3 then
    base := 'member';
  end if;
  base := left(base, 14);
  candidate := base;

  if (new.raw_user_meta_data ->> 'username') ~ '^[a-z0-9_]{3,20}$'
     and not exists (select 1 from public.profiles where username = new.raw_user_meta_data ->> 'username') then
    candidate := new.raw_user_meta_data ->> 'username';
  end if;

  while exists (select 1 from public.profiles where username = candidate) loop
    attempt := attempt + 1;
    candidate := left(base, 11) || '_' || attempt::text;
    if attempt > 40 then
      candidate := 'user_' || substr(replace(new.id::text, '-', ''), 1, 8);
      exit;
    end if;
  end loop;

  insert into public.profiles (id, username, display_name)
  values (
    new.id,
    candidate,
    coalesce(nullif(btrim(new.raw_user_meta_data ->> 'display_name'), ''), initcap(base))
  );

  insert into public.privacy_settings (user_id) values (new.id)
  on conflict (user_id) do nothing;

  insert into public.activity_events (user_id, kind, title)
  values (new.id, 'joined', 'Joined HabitFlow');

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
alter table public.profiles          enable row level security;
alter table public.habits            enable row level security;
alter table public.completions       enable row level security;
alter table public.friendships       enable row level security;
alter table public.blocks            enable row level security;
alter table public.privacy_settings  enable row level security;
alter table public.achievements      enable row level security;
alter table public.activity_events   enable row level security;

-- profiles ------------------------------------------------------------------
drop policy if exists profiles_read on public.profiles;
create policy profiles_read on public.profiles
  for select using (id = auth.uid() or public.can_view_profile(auth.uid(), id));

drop policy if exists profiles_insert on public.profiles;
create policy profiles_insert on public.profiles
  for insert with check (id = auth.uid());

drop policy if exists profiles_update on public.profiles;
create policy profiles_update on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

-- habits --------------------------------------------------------------------
drop policy if exists habits_read on public.habits;
create policy habits_read on public.habits
  for select using (owner_id = auth.uid());

drop policy if exists habits_insert on public.habits;
create policy habits_insert on public.habits
  for insert with check (owner_id = auth.uid());

drop policy if exists habits_update on public.habits;
create policy habits_update on public.habits
  for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());

drop policy if exists habits_delete on public.habits;
create policy habits_delete on public.habits
  for delete using (owner_id = auth.uid());

-- completions ---------------------------------------------------------------
-- Only the owner can read or write their records; friends read aggregates
-- through compare_stats()/leaderboard(), never raw rows.
drop policy if exists completions_read on public.completions;
create policy completions_read on public.completions
  for select using (owner_id = auth.uid());

drop policy if exists completions_insert on public.completions;
create policy completions_insert on public.completions
  for insert with check (
    owner_id = auth.uid()
    and exists (
      select 1 from public.habits h
      where h.id = habit_id and h.owner_id = auth.uid()
    )
  );

drop policy if exists completions_delete on public.completions;
create policy completions_delete on public.completions
  for delete using (owner_id = auth.uid());

-- friendships ---------------------------------------------------------------
drop policy if exists friendships_read on public.friendships;
create policy friendships_read on public.friendships
  for select using (requester = auth.uid() or addressee = auth.uid());

drop policy if exists friendships_insert on public.friendships;
create policy friendships_insert on public.friendships
  for insert with check (
    requester = auth.uid()
    and addressee <> auth.uid()
    and not public.is_blocked(auth.uid(), addressee)
  );

drop policy if exists friendships_respond on public.friendships;
create policy friendships_respond on public.friendships
  for update using (addressee = auth.uid() and status = 'pending')
  with check (addressee = auth.uid() and status in ('accepted', 'rejected'));

drop policy if exists friendships_delete on public.friendships;
create policy friendships_delete on public.friendships
  for delete using (requester = auth.uid() or addressee = auth.uid());

-- blocks --------------------------------------------------------------------
drop policy if exists blocks_read on public.blocks;
create policy blocks_read on public.blocks
  for select using (blocker = auth.uid() or blocked = auth.uid());

drop policy if exists blocks_write on public.blocks;
create policy blocks_write on public.blocks
  for insert with check (blocker = auth.uid());

drop policy if exists blocks_remove on public.blocks;
create policy blocks_remove on public.blocks
  for delete using (blocker = auth.uid());

-- privacy -------------------------------------------------------------------
drop policy if exists privacy_read on public.privacy_settings;
create policy privacy_read on public.privacy_settings
  for select using (user_id = auth.uid());

drop policy if exists privacy_write on public.privacy_settings;
create policy privacy_write on public.privacy_settings
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists privacy_insert on public.privacy_settings;
create policy privacy_insert on public.privacy_settings
  for insert with check (user_id = auth.uid());

-- achievements --------------------------------------------------------------
drop policy if exists achievements_read on public.achievements;
create policy achievements_read on public.achievements
  for select using (
    user_id = auth.uid()
    or (
      public.is_friend(auth.uid(), user_id)
      and not public.is_blocked(auth.uid(), user_id)
      and coalesce((select share_stats from public.privacy_settings where user_id = achievements.user_id), false)
    )
  );

-- no insert/update/delete policy: only triggers and definer functions write

-- activity ------------------------------------------------------------------
drop policy if exists activity_read on public.activity_events;
create policy activity_read on public.activity_events
  for select using (
    user_id = auth.uid()
    or (
      public.is_friend(auth.uid(), user_id)
      and not public.is_blocked(auth.uid(), user_id)
      and coalesce((select share_activity from public.privacy_settings where user_id = activity_events.user_id), false)
    )
  );

-- no insert policy on purpose: the trigger writes events, never the browser

-- ---------------------------------------------------------------------------
-- Grants: internal helpers stay unreachable from the browser
-- ---------------------------------------------------------------------------
revoke all on function public.user_daily(uuid, int) from public, anon, authenticated;
revoke all on function public.user_streak(uuid) from public, anon;
revoke all on function public.user_best_streak(uuid) from public, anon;
revoke all on function public.habit_due_on(text, smallint[], date) from public, anon;
revoke all on function public.is_blocked(uuid, uuid) from public, anon;
revoke all on function public.is_friend(uuid, uuid) from public, anon;
revoke all on function public.can_view_profile(uuid, uuid) from public, anon;
revoke all on function public.handle_completion() from public, anon, authenticated;
revoke all on function public.handle_new_user() from public, anon, authenticated;

grant usage on schema public to authenticated;

grant execute on function public.compare_stats(uuid) to authenticated;
grant execute on function public.leaderboard(text, int) to authenticated;
grant execute on function public.search_profiles(text) to authenticated;
grant execute on function public.username_available(text) to authenticated;
