import { Database, KeyRound, ShieldAlert, Terminal } from 'lucide-react'

const STEPS = [
  {
    icon: Database,
    title: '1 — Create a Supabase project',
    body: 'Copy the Project URL and the anon public key from Project Settings → API. The anon key is designed to be public: Row Level Security is what protects your data.',
  },
  {
    icon: Terminal,
    title: '2 — Apply the schema',
    body: 'Run web/supabase/migrations/0001_social_habits.sql in the Supabase SQL editor (or `supabase db push`). It creates the tables, helper functions and every RLS policy.',
  },
  {
    icon: KeyRound,
    title: '3 — Add the environment variables',
    body: 'Create web/.env with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY, then restart the dev server. Never add the service_role key to the frontend.',
  },
  {
    icon: ShieldAlert,
    title: '4 — Configure auth redirects',
    body: 'In Authentication → URL Configuration set your site URL and add /reset as a redirect target so password recovery links work.',
  },
]

export function Setup() {
  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-5 py-14">
      <span className="chip mb-5 self-start">
        <ShieldAlert size={12} className="text-amber" /> Backend not configured
      </span>
      <h1 className="font-display text-3xl font-bold text-slate-50">HabitFlow needs a Supabase project</h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-400">
        This build ships without credentials, so it will not pretend to sign you in or store anything. Add two public
        values and the full app — auth, habits, friends, leaderboards — activates.
      </p>

      <div className="mt-8 space-y-3">
        {STEPS.map((step) => {
          const Icon = step.icon
          return (
            <div key={step.title} className="panel flex gap-4 p-4">
              <span className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-neon">
                <Icon size={16} />
              </span>
              <div>
                <h2 className="text-sm font-semibold text-slate-100">{step.title}</h2>
                <p className="mt-1 text-xs leading-relaxed text-slate-500">{step.body}</p>
              </div>
            </div>
          )
        })}
      </div>

      <pre className="mt-6 overflow-x-auto rounded-xl border border-white/10 bg-black/50 p-4 text-[11px] leading-relaxed text-slate-300">
        <code>{`# web/.env
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key`}</code>
      </pre>

      <p className="mt-4 text-xs text-slate-500">
        Full instructions, including the optional desktop-data import, live in <code>web/README.md</code>.
      </p>
    </div>
  )
}
