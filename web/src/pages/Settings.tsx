import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Database, KeyRound, LogOut, ShieldCheck, Upload } from 'lucide-react'
import { useAuth } from '../context/AuthProvider'
import { importLegacyData, updatePrivacy, updateProfile, type ImportSummary, type LegacyPayload } from '../lib/data'
import type { PrivacySettings } from '../lib/types'
import {
  Button,
  Card,
  ErrorNote,
  Field,
  Notice,
  SectionTitle,
  SelectField,
  Spinner,
  Toggle,
  cx,
} from '../components/ui'

export function Settings() {
  const { profile, privacy, session, applyProfile, applyPrivacy, signOut, sendPasswordReset } = useAuth()
  const [displayName, setDisplayName] = useState(profile?.display_name ?? '')
  const [username, setUsername] = useState(profile?.username ?? '')
  const [bio, setBio] = useState(profile?.bio ?? '')
  const [avatar, setAvatar] = useState(profile?.avatar_url ?? '')
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [profileSaved, setProfileSaved] = useState(false)

  const [settings, setSettings] = useState<PrivacySettings | null>(privacy)
  const [savingPrivacy, setSavingPrivacy] = useState(false)
  const [privacyError, setPrivacyError] = useState('')

  const [summary, setSummary] = useState<ImportSummary | null>(null)
  const [importError, setImportError] = useState('')
  const [importing, setImporting] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const [resetSent, setResetSent] = useState(false)

  useEffect(() => {
    setDisplayName(profile?.display_name ?? '')
    setUsername(profile?.username ?? '')
    setBio(profile?.bio ?? '')
    setAvatar(profile?.avatar_url ?? '')
  }, [profile])

  useEffect(() => {
    setSettings(privacy)
  }, [privacy])

  const saveProfile = async (event: FormEvent) => {
    event.preventDefault()
    if (!profile) return
    setSavingProfile(true)
    setProfileError('')
    setProfileSaved(false)
    try {
      const updated = await updateProfile(profile.id, {
        display_name: displayName.trim(),
        username: username.trim().toLowerCase(),
        bio: bio.trim() || null,
        avatar_url: avatar.trim() || null,
      })
      applyProfile(updated)
      setProfileSaved(true)
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : 'Could not save your profile.')
    } finally {
      setSavingProfile(false)
    }
  }

  const patchPrivacy = useCallback(
    async (patch: Partial<PrivacySettings>) => {
      if (!profile || !settings) return
      const optimistic = { ...settings, ...patch }
      setSettings(optimistic)
      setSavingPrivacy(true)
      setPrivacyError('')
      try {
        const saved = await updatePrivacy(profile.id, patch)
        applyPrivacy(saved)
        setSettings(saved)
      } catch (err) {
        setSettings(settings)
        setPrivacyError(err instanceof Error ? err.message : 'Could not save privacy settings.')
      } finally {
        setSavingPrivacy(false)
      }
    },
    [applyPrivacy, profile, settings],
  )

  const handleImport = async (file: File) => {
    if (!profile) return
    setImporting(true)
    setImportError('')
    setSummary(null)
    try {
      const text = await file.text()
      const parsed = JSON.parse(text) as LegacyPayload
      if (!parsed || typeof parsed !== 'object' || (!parsed.tasks && !parsed.completions)) {
        throw new Error('That file is not a HabitFlow data.json export.')
      }
      const result = await importLegacyData(profile.id, parsed)
      setSummary(result)
    } catch (err) {
      setImportError(err instanceof Error ? err.message : 'Import failed.')
    } finally {
      setImporting(false)
    }
  }

  if (!profile) {
    return (
      <div className="grid place-items-center py-24">
        <Spinner label="Loading your account" />
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-display text-3xl font-bold text-slate-50">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">
          Signed in as {session?.user.email} · everything here stays on this account
        </p>
      </div>

      <Card>
        <SectionTitle title="Profile" hint="Your public identity inside HabitFlow" />
        <form onSubmit={saveProfile} className="space-y-4">
          {profileError ? <ErrorNote>{profileError}</ErrorNote> : null}
          {profileSaved ? <Notice>Profile saved.</Notice> : null}
          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              label="Display name"
              required
              maxLength={60}
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />
            <Field
              label="Username"
              required
              maxLength={20}
              value={username}
              onChange={(event) => setUsername(event.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
              hint="Changing this breaks old profile links."
            />
          </div>
          <label className="block">
            <span className="label mb-1.5 block">Bio</span>
            <textarea
              className="field min-h-[70px] resize-none"
              maxLength={280}
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              placeholder="One line about how you train."
            />
          </label>
          <Field
            label="Avatar URL"
            type="url"
            value={avatar}
            onChange={(event) => setAvatar(event.target.value)}
            placeholder="https://…"
            hint="Optional. Any image URL you control."
          />
          <div className="flex justify-end">
            <Button type="submit" disabled={savingProfile}>
              {savingProfile ? 'Saving' : 'Save profile'}
            </Button>
          </div>
        </form>
      </Card>

      <Card>
        <SectionTitle title="Privacy" hint="What friends and the public can see" />
        {privacyError ? <ErrorNote>{privacyError}</ErrorNote> : null}
        {settings ? (
          <>
            <SelectField
              label="Profile visibility"
              value={settings.profile_visibility}
              onChange={(event) =>
                void patchPrivacy({ profile_visibility: event.target.value as PrivacySettings['profile_visibility'] })
              }
            >
              <option value="public">Public — anyone can find and compare</option>
              <option value="friends">Friends only — recommended</option>
              <option value="private">Private — nobody but you</option>
            </SelectField>
            <div className="mt-2 divide-y divide-white/[0.05]">
              <Toggle
                label="Share consistency stats"
                description="Friends can compare completion rates, streaks and 30-day history."
                checked={settings.share_stats}
                onChange={(next) => void patchPrivacy({ share_stats: next })}
              />
              <Toggle
                label="Share activity"
                description="Perfect days and streak milestones appear in friends' feeds."
                checked={settings.share_activity}
                onChange={(next) => void patchPrivacy({ share_activity: next })}
              />
              <Toggle
                label="Share habit names"
                description="Off by default, and the app never sends habit names to friends regardless."
                checked={settings.share_habit_names}
                onChange={(next) => void patchPrivacy({ share_habit_names: next })}
              />
            </div>
            <p className={cx('mt-2 text-[11px] text-slate-600', savingPrivacy && 'text-slate-400')}>
              {savingPrivacy ? 'Saving…' : 'Privacy changes save immediately.'}
            </p>
          </>
        ) : (
          <p className="text-xs text-slate-500">Privacy settings are unavailable until the database migration is applied.</p>
        )}
      </Card>

      <Card>
        <SectionTitle
          title="Import desktop data"
          hint="Bring across habits and completion history from ~/.habitflow/data.json"
        />
        {importError ? <ErrorNote>{importError}</ErrorNote> : null}
        {summary ? (
          <Notice>
            Imported {summary.habits} habits and {summary.completions} completions
            {summary.skipped ? ` · ${summary.skipped} rows skipped` : ''}. Your local file was not modified.
          </Notice>
        ) : null}
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <input
            ref={fileRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) void handleImport(file)
              event.target.value = ''
            }}
          />
          <Button
            variant="ghost"
            onClick={() => fileRef.current?.click()}
            disabled={importing}
          >
            <Upload size={15} /> {importing ? 'Importing…' : 'Choose data.json'}
          </Button>
          <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-500">
            <Database size={12} /> Imports are additive; existing habits are untouched.
          </span>
        </div>
      </Card>

      <Card>
        <SectionTitle title="Account" hint="Password and session" />
        <div className="flex flex-wrap gap-3">
          <Button
            variant="ghost"
            onClick={async () => {
              if (!session?.user.email) return
              await sendPasswordReset(session.user.email)
              setResetSent(true)
            }}
          >
            <KeyRound size={15} /> {resetSent ? 'Reset link sent' : 'Send password reset'}
          </Button>
          <Button variant="danger" onClick={() => void signOut()}>
            <LogOut size={15} /> Sign out
          </Button>
        </div>
        <p className="mt-3 inline-flex items-center gap-1.5 text-[11px] text-slate-500">
          <ShieldCheck size={12} /> Passwords are handled by Supabase Auth; this app never stores them.
        </p>
      </Card>
    </div>
  )
}
