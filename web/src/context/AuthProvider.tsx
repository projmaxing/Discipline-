import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'
import { fetchPrivacy, fetchProfile, usernameAvailable } from '../lib/data'
import type { PrivacySettings, Profile } from '../lib/types'

interface AuthContextValue {
  session: Session | null
  profile: Profile | null
  privacy: PrivacySettings | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, username: string, displayName: string) => Promise<{ needsConfirmation: boolean }>
  signOut: () => Promise<void>
  sendPasswordReset: (email: string) => Promise<void>
  updatePassword: (password: string) => Promise<void>
  refresh: () => Promise<void>
  applyProfile: (profile: Profile) => void
  applyPrivacy: (privacy: PrivacySettings) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [privacy, setPrivacy] = useState<PrivacySettings | null>(null)
  const [loading, setLoading] = useState(true)

  const loadAccount = useCallback(async (next: Session | null) => {
    if (!next?.user) {
      setProfile(null)
      setPrivacy(null)
      return
    }
    try {
      const [row, settings] = await Promise.all([
        fetchProfile(next.user.id),
        fetchPrivacy(next.user.id),
      ])
      setProfile(row)
      setPrivacy(settings)
    } catch {
      // A missing profile usually means the SQL migration has not been applied.
      setProfile(null)
      setPrivacy(null)
    }
  }, [])

  useEffect(() => {
    if (!supabase) {
      setLoading(false)
      return
    }
    let active = true

    supabase.auth.getSession().then(async ({ data }) => {
      if (!active) return
      setSession(data.session)
      await loadAccount(data.session)
      if (active) setLoading(false)
    })

    const { data: subscription } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next)
      void loadAccount(next)
    })

    return () => {
      active = false
      subscription.subscription.unsubscribe()
    }
  }, [loadAccount])

  const signIn = useCallback(async (email: string, password: string) => {
    if (!supabase) throw new Error('Supabase is not configured.')
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw new Error(error.message)
  }, [])

  const signUp = useCallback(
    async (email: string, password: string, username: string, displayName: string) => {
      if (!supabase) throw new Error('Supabase is not configured.')
      const normalized = username.trim().toLowerCase()
      const available = await usernameAvailable(normalized)
      if (!available) throw new Error('That username is taken. Try another one.')
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { username: normalized, display_name: displayName.trim() } },
      })
      if (error) throw new Error(error.message)
      return { needsConfirmation: !data.session }
    },
    [],
  )

  const signOut = useCallback(async () => {
    if (!supabase) return
    await supabase.auth.signOut()
    setProfile(null)
    setPrivacy(null)
  }, [])

  const sendPasswordReset = useCallback(async (email: string) => {
    if (!supabase) throw new Error('Supabase is not configured.')
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset`,
    })
    if (error) throw new Error(error.message)
  }, [])

  const updatePassword = useCallback(async (password: string) => {
    if (!supabase) throw new Error('Supabase is not configured.')
    const { error } = await supabase.auth.updateUser({ password })
    if (error) throw new Error(error.message)
  }, [])

  const refresh = useCallback(async () => {
    if (!supabase) return
    const { data } = await supabase.auth.getSession()
    setSession(data.session)
    await loadAccount(data.session)
  }, [loadAccount])

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      profile,
      privacy,
      loading,
      signIn,
      signUp,
      signOut,
      sendPasswordReset,
      updatePassword,
      refresh,
      applyProfile: setProfile,
      applyPrivacy: setPrivacy,
    }),
    [session, profile, privacy, loading, signIn, signUp, signOut, sendPasswordReset, updatePassword, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
