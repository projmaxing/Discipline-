import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthProvider'
import { isConfigured } from './lib/supabase'
import { Layout } from './components/Layout'
import { Setup } from './pages/Setup'
import { Landing } from './pages/Landing'
import { Forgot, Login, Register, Reset } from './pages/AuthPages'
import { Dashboard } from './pages/Dashboard'
import { Habits } from './pages/Habits'
import { Friends } from './pages/Friends'
import { Leaderboard } from './pages/Leaderboard'
import { ActivityFeed } from './pages/Activity'
import { Settings } from './pages/Settings'
import { FriendProfile } from './pages/FriendProfile'
import { Spinner } from './components/ui'

function Protected() {
  const { session, loading } = useAuth()
  if (loading) {
    return (
      <div className="grid min-h-screen place-items-center">
        <Spinner label="Restoring your session" />
      </div>
    )
  }
  if (!session) return <Navigate to="/login" replace />
  return <Layout />
}

export default function App() {
  if (!isConfigured) return <Setup />

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot" element={<Forgot />} />
      <Route path="/reset" element={<Reset />} />

      <Route element={<Protected />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/habits" element={<Habits />} />
        <Route path="/friends" element={<Friends />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/activity" element={<ActivityFeed />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/u/:username" element={<FriendProfile />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
