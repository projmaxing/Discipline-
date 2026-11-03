import { useState, type FormEvent, type ReactNode } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2, Sparkles } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { ErrorNote, Field, Notice } from '../components/ui'

function AuthShell({ title, subtitle, children, footer }: { title: string; subtitle: string; children: ReactNode; footer?: ReactNode }) {
  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-5 py-14">
      <Link to="/" className="mb-8 inline-flex items-center gap-2 text-xs text-slate-500 transition hover:text-slate-300">
        <ArrowLeft size={14} /> Back to home
      </Link>
      <div className="mb-6 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl border border-neon/40 bg-neon/15 text-neon">
          <Sparkles size={18} />
        </div>
        <div>
          <div className="font-display text-sm font-bold text-slate-50">HabitFlow</div>
          <div className="text-[9px] uppercase tracking-[0.18em] text-slate-500">Social command center</div>
        </div>
      </div>
      <h1 className="font-display text-2xl font-bold text-slate-50">{title}</h1>
      <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
      <div className="mt-6 space-y-4">{children}</div>
      {footer ? <div className="mt-6 text-xs text-slate-500">{footer}</div> : null}
    </div>
  )
}

function Submit({ label, busy }: { label: string; busy: boolean }) {
  return (
    <button type="submit" disabled={busy} className="btn-primary w-full">
      {busy ? <Loader2 size={15} className="animate-spin" /> : null}
      {busy ? 'Working' : label}
    </button>
  )
}

export function Login() {
  const { signIn, session } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  if (session) return <Navigate to="/dashboard" replace />

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await signIn(email.trim(), password)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not sign in.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Welcome back"
      subtitle="Sign in to protect your streak."
      footer={
        <span>
          New here?{' '}
          <Link to="/register" className="font-semibold text-neon hover:underline">
            Create an account
          </Link>
        </span>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {error ? <ErrorNote>{error}</ErrorNote> : null}
        <Field
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <Field
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="••••••••"
        />
        <Submit label="Sign in" busy={busy} />
      </form>
      <Link to="/forgot" className="inline-block text-xs text-slate-500 transition hover:text-slate-300">
        Forgot your password?
      </Link>
    </AuthShell>
  )
}

export function Register() {
  const { signUp, session } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  if (session) return <Navigate to="/dashboard" replace />

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    try {
      if (!/^[a-z0-9_]{3,20}$/.test(username)) {
        throw new Error('Usernames use 3–20 lowercase letters, numbers or underscores.')
      }
      const result = await signUp(email.trim(), password, username, displayName)
      if (result.needsConfirmation) {
        setNotice('Check your inbox to confirm your email, then sign in.')
      } else {
        navigate('/dashboard', { replace: true })
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the account.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="One profile, one streak, no public habit names."
      footer={
        <span>
          Already tracking?{' '}
          <Link to="/login" className="font-semibold text-neon hover:underline">
            Sign in
          </Link>
        </span>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {error ? <ErrorNote>{error}</ErrorNote> : null}
        {notice ? <Notice>{notice}</Notice> : null}
        <Field
          label="Display name"
          required
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          placeholder="Alex Rivera"
          maxLength={60}
        />
        <Field
          label="Username"
          required
          value={username}
          onChange={(event) => setUsername(event.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
          placeholder="alexr"
          maxLength={20}
          hint="Friends find you by this handle. Letters, numbers and underscores."
        />
        <Field
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <Field
          label="Password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="At least 8 characters"
        />
        <Submit label="Create account" busy={busy} />
      </form>
    </AuthShell>
  )
}

export function Forgot() {
  const { sendPasswordReset } = useAuth()
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await sendPasswordReset(email.trim())
      setSent(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send the reset email.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Reset your password"
      subtitle="We email you a secure link that returns you here."
      footer={
        <Link to="/login" className="font-semibold text-neon hover:underline">
          Back to sign in
        </Link>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        {error ? <ErrorNote>{error}</ErrorNote> : null}
        {sent ? <Notice>If that address has an account, a reset link is on its way.</Notice> : null}
        <Field
          label="Email"
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
        <Submit label="Send reset link" busy={busy} />
      </form>
    </AuthShell>
  )
}

export function Reset() {
  const { updatePassword, session, signOut } = useAuth()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      if (password.length < 8) throw new Error('Use at least 8 characters.')
      if (password !== confirm) throw new Error('Those passwords do not match.')
      await updatePassword(password)
      await signOut()
      navigate('/login', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not update the password.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell title="Choose a new password" subtitle="You are here from a recovery link.">
      {!session ? (
        <Notice>
          This page needs a valid recovery link. Request a fresh one from{' '}
          <Link to="/forgot" className="font-semibold underline">
            forgot password
          </Link>
          .
        </Notice>
      ) : (
        <form onSubmit={onSubmit} className="space-y-4">
          {error ? <ErrorNote>{error}</ErrorNote> : null}
          <Field
            label="New password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <Field
            label="Confirm password"
            type="password"
            required
            minLength={8}
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
          />
          <Submit label="Update password" busy={busy} />
        </form>
      )}
    </AuthShell>
  )
}
