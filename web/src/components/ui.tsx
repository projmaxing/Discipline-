import {
  useEffect,
  useId,
  type ButtonHTMLAttributes,
  type CSSProperties,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
} from 'react'
import { X } from 'lucide-react'

export function cx(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(' ')
}

export function Card({
  children,
  className,
  accent,
}: {
  children: ReactNode
  className?: string
  accent?: string
}) {
  return (
    <div className={cx('panel relative p-5', className)}>
      {accent ? (
        <span
          className="pointer-events-none absolute inset-x-5 -top-px h-px"
          style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
        />
      ) : null}
      {children}
    </div>
  )
}

export function Button({
  variant = 'primary',
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' | 'danger' | 'gold' }) {
  const map = {
    primary: 'btn-primary',
    ghost: 'btn-ghost',
    danger: 'btn-danger',
    gold: 'btn-gold',
  } as const
  return <button className={cx(map[variant], className)} {...props} />
}

export function Field({
  label,
  hint,
  error,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string; hint?: string; error?: string }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <input className={cx('field', error && 'border-rose/60')} {...props} />
      {error ? (
        <span className="mt-1.5 block text-xs text-rose">{error}</span>
      ) : hint ? (
        <span className="mt-1.5 block text-xs text-slate-500">{hint}</span>
      ) : null}
    </label>
  )
}

export function SelectField({
  label,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="label mb-1.5 block">{label}</span>
      <select className={cx('field appearance-none')} {...props}>
        {children}
      </select>
    </label>
  )
}

export function Avatar({
  name,
  src,
  size = 40,
  ring = false,
}: {
  name: string
  src?: string | null
  size?: number
  ring?: boolean
}) {
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')

  const inner = src ? (
    <img
      src={src}
      alt={name}
      width={size}
      height={size}
      style={{ width: size, height: size }}
      className="rounded-full border border-white/10 object-cover"
    />
  ) : (
    <span
      style={{ width: size, height: size, fontSize: Math.max(11, size * 0.36) }}
      className="flex items-center justify-center rounded-full border border-neon/30 bg-gradient-to-br from-neon/25 to-violet/20 font-semibold text-neon-soft"
    >
      {initials || '?'}
    </span>
  )

  if (!ring) return <span className="shrink-0">{inner}</span>

  return (
    <span
      className="medal-ring relative inline-grid shrink-0 place-items-center rounded-full p-[2px]"
      style={{ width: size + 6, height: size + 6 }}
    >
      <span className="grid place-items-center rounded-full bg-ink-950 p-[2px]">{inner}</span>
    </span>
  )
}

export function ProgressRing({
  pct,
  size = 148,
  stroke = 10,
  caption,
  tone = 'neon',
}: {
  pct: number
  size?: number
  stroke?: number
  caption?: string
  tone?: 'neon' | 'gold' | 'mint'
}) {
  const id = useId().replace(/:/g, '')
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, Math.round(pct)))
  const offset = circumference * (1 - clamped / 100)
  const stops =
    tone === 'gold'
      ? ['#FFE9A8', '#FFC857', '#FF9A3D']
      : tone === 'mint'
        ? ['#3CE6A0', '#38E8FF', '#4C8DFF']
        : ['#7FE9FF', '#4C8DFF', '#8B5CF6']

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90 overflow-visible">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#121828" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`url(#ring-${id})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: 'stroke-dashoffset 800ms cubic-bezier(.22,.8,.3,1)',
            filter: 'drop-shadow(0 0 10px rgba(76,141,255,0.55))',
          }}
        />
        <defs>
          <linearGradient id={`ring-${id}`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={stops[0]} />
            <stop offset="60%" stopColor={stops[1]} />
            <stop offset="100%" stopColor={stops[2]} />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-[2rem] font-extrabold leading-none tracking-tight text-slate-50">
          {clamped}
          <span className="text-base font-bold text-slate-500">%</span>
        </span>
        {caption ? (
          <span className="mt-1.5 text-[9px] font-semibold uppercase tracking-[0.2em] text-slate-500">{caption}</span>
        ) : null}
      </div>
    </div>
  )
}

export function XPBar({
  value,
  level,
  name,
  inLevel,
  forLevel,
}: {
  value: number
  level: number
  name: string
  inLevel: number
  forLevel: number
}) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)))
  return (
    <div>
      <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-[0.18em]">
        <span className="text-cyan">
          Lv {level} · {name}
        </span>
        <span className="font-mono text-slate-500">
          {inLevel}/{forLevel} XP
        </span>
      </div>
      <div className="xp-track mt-2">
        <span className="xp-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export function StatCard({
  label,
  value,
  hint,
  icon,
  accent = 'text-neon',
  tone,
}: {
  label: string
  value: string
  hint?: string
  icon: ReactNode
  accent?: string
  tone?: string
}) {
  return (
    <div className="tile p-4" style={{ ['--tone' as string]: tone ?? 'rgba(76,141,255,.7)' } as CSSProperties}>
      <div className="flex items-start justify-between gap-2">
        <span className={cx('text-[10px] font-semibold uppercase tracking-[0.16em]', accent)}>{label}</span>
        <span className="grid h-7 w-7 place-items-center rounded-lg border border-white/10 bg-white/[0.04] text-slate-300">
          {icon}
        </span>
      </div>
      <div className="mt-3 font-display text-[1.7rem] font-extrabold leading-none tracking-tight text-slate-50">
        {value}
      </div>
      {hint ? <div className="mt-1.5 font-mono text-[10px] text-slate-500">{hint}</div> : null}
    </div>
  )
}

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode
  tone?: 'neutral' | 'success' | 'warning' | 'violet'
}) {
  const tones = {
    neutral: 'border-white/10 bg-white/[0.04] text-slate-300',
    success: 'border-mint/30 bg-mint/10 text-mint',
    warning: 'border-amber/30 bg-amber/10 text-amber',
    violet: 'border-violet/30 bg-violet/10 text-violet-soft',
  } as const
  return (
    <span className={cx('inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium', tones[tone])}>
      {children}
    </span>
  )
}

export function SectionTitle({
  title,
  hint,
  action,
  accent = '#4C8DFF',
}: {
  title: string
  hint?: string
  action?: ReactNode
  accent?: string
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div className="flex items-start gap-3">
        <span
          className="mt-1 h-4 w-[3px] shrink-0 rounded-full"
          style={{ background: accent, boxShadow: `0 0 12px ${accent}` }}
        />
        <div>
          <h2 className="font-display text-[15px] font-bold tracking-tight text-slate-50">{title}</h2>
          {hint ? <p className="mt-0.5 text-[11px] text-slate-500">{hint}</p> : null}
        </div>
      </div>
      {action}
    </div>
  )
}

export function EmptyState({
  icon,
  title,
  body,
  action,
}: {
  icon: ReactNode
  title: string
  body: string
  action?: ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl2 border border-dashed border-white/10 bg-white/[0.015] px-6 py-12 text-center">
      <div className="mb-3 grid h-11 w-11 place-items-center rounded-xl border border-neon/25 bg-neon/10 text-neon shadow-neon">
        {icon}
      </div>
      <h3 className="font-display text-sm font-bold text-slate-100">{title}</h3>
      <p className="mt-1 max-w-sm text-xs leading-relaxed text-slate-500">{body}</p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-400">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/15 border-t-cyan" />
      {label ?? 'Loading'}
    </div>
  )
}

export function Modal({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  width = 'max-w-lg',
}: {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  width?: string
}) {
  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = previous
    }
  }, [open, onClose])

  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/75 p-3 backdrop-blur-sm sm:items-center">
      <button aria-label="Close dialog" className="absolute inset-0 cursor-default" onClick={onClose} />
      <div className={cx('hud rise relative w-full', width)}>
        <span className="pointer-events-none absolute inset-x-8 top-0 h-px bg-gradient-to-r from-transparent via-neon/70 to-transparent" />
        <div className="flex items-start justify-between gap-4 border-b border-white/[0.07] px-5 py-4">
          <div>
            <h2 className="font-display text-base font-bold text-slate-100">{title}</h2>
            {description ? <p className="mt-0.5 text-xs text-slate-500">{description}</p> : null}
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-slate-400 transition hover:border-white/20 hover:text-slate-200"
          >
            <X size={16} />
          </button>
        </div>
        <div className="max-h-[70vh] overflow-y-auto px-5 py-4">{children}</div>
        {footer ? (
          <div className="flex justify-end gap-2 border-t border-white/[0.07] px-5 py-3">{footer}</div>
        ) : null}
      </div>
    </div>
  )
}

export function Toggle({
  checked,
  onChange,
  label,
  description,
}: {
  checked: boolean
  onChange: (next: boolean) => void
  label: string
  description?: string
}) {
  return (
    <div className="flex items-start justify-between gap-4 py-3">
      <div>
        <div className="text-sm font-medium text-slate-200">{label}</div>
        {description ? <p className="mt-0.5 text-xs text-slate-500">{description}</p> : null}
      </div>
      <button
        role="switch"
        aria-checked={checked}
        aria-label={label}
        onClick={() => onChange(!checked)}
        className={cx(
          'relative mt-0.5 h-6 w-11 shrink-0 rounded-full border transition',
          checked ? 'border-neon/60 bg-gradient-to-r from-cyan to-neon shadow-neon' : 'border-white/10 bg-white/10',
        )}
      >
        <span
          className={cx(
            'absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all',
            checked ? 'left-[24px]' : 'left-0.5',
          )}
        />
      </button>
    </div>
  )
}

export function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[]
  value: T
  onChange: (next: T) => void
}) {
  return (
    <div className="inline-flex rounded-xl border border-white/10 bg-black/40 p-1 backdrop-blur">
      {options.map((option) => {
        const active = option.value === value
        return (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={cx(
              'relative rounded-lg px-3 py-1.5 text-xs font-semibold transition',
              active
                ? 'bg-gradient-to-r from-cyan/25 to-violet/25 text-slate-50 shadow-[inset_0_1px_0_rgba(255,255,255,.15)]'
                : 'text-slate-400 hover:text-slate-200',
            )}
          >
            {option.label}
          </button>
        )
      })}
    </div>
  )
}

export function ErrorNote({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-rose/30 bg-rose/10 px-3.5 py-2.5 text-xs text-rose">{children}</div>
  )
}

export function Notice({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-mint/25 bg-mint/10 px-3.5 py-2.5 text-xs text-mint">{children}</div>
  )
}
