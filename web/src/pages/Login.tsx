import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { supabaseConfigured } from '../lib/supabase'
import { apiUrl } from '../lib/api'
import './Login.css'

export default function Login() {
  const { loginWithGoogle, loginWithPokerID, signUpWithPokerID, isAuthenticated, loading } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [pokerIdError, setPokerIdError] = useState('')
  const [apiDown, setApiDown] = useState(false)

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard')
  }, [isAuthenticated, navigate])

  useEffect(() => {
    if (showForm && !supabaseConfigured) {
      fetch(apiUrl('/api/health')).then((r) => setApiDown(!r.ok)).catch(() => setApiDown(true))
    } else {
      setApiDown(false)
    }
  }, [showForm])

  const handlePokerID = async (e: React.FormEvent) => {
    e.preventDefault()
    setPokerIdError('')
    if (apiDown) {
      setPokerIdError('API not running. Start it with: ./run_api.sh from project root.')
      return
    }
    try {
      if (isSignUp) {
        await signUpWithPokerID(email.trim(), password, username.trim())
      } else {
        await loginWithPokerID(email.trim(), password)
      }
      navigate('/dashboard')
    } catch (err: unknown) {
      setPokerIdError(err instanceof Error ? err.message : 'Login failed')
    }
  }

  const handleGoogle = async () => {
    try {
      await loginWithGoogle()
      // Google OAuth redirects away; on return, auth state updates and useEffect navigates
    } catch {
      setPokerIdError('Google sign-in failed')
    }
  }

  if (loading) return <div className="login-page"><div className="loading-spinner">Loading…</div></div>

  if (showForm) {
    return (
      <div className="login-page login-form-only">
        <button
          type="button"
          className="login-theme-toggle"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <div className="login-card neu-raised">
          <button type="button" className="login-back" onClick={() => setShowForm(false)}>← Back</button>
          <h2>{isSignUp ? 'Create account' : 'Sign in'}</h2>
          <p className="tagline">PokerID (email + password{isSignUp ? ', display name required' : ''})</p>

          {supabaseConfigured && (
            <>
              <button type="button" className="neu-btn google-btn" onClick={handleGoogle}>
                <span className="google-icon">G</span> Continue with Google
              </button>
              <div className="divider">
                <span>or</span>
              </div>
            </>
          )}

          <form onSubmit={handlePokerID}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="neu-input"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="neu-input"
                required
              />
            </div>
            {isSignUp && (
              <div className="form-group">
                <label htmlFor="username">Display name</label>
                <input
                  id="username"
                  type="text"
                  placeholder="Your name"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="neu-input"
                  required
                />
              </div>
            )}
            <button type="submit" className="neu-btn neu-btn-primary login-btn">
              {isSignUp ? 'Create PokerID account' : 'Sign in with PokerID'}
            </button>
          </form>
          {apiDown && <p className="error-msg">API not running. Run ./run_api.sh from project root, then refresh.</p>}
        {pokerIdError && <p className="error-msg">{pokerIdError}</p>}
          <p className="switch-mode">
            <button type="button" className="link-btn" onClick={() => setIsSignUp(!isSignUp)}>
              {isSignUp ? 'Already have an account? Sign in' : 'New? Create PokerID account'}
            </button>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="login-page potbot-style">
      <button
        type="button"
        className="login-theme-toggle"
        onClick={toggleTheme}
        title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>
      <header className="login-header">
        <span className="login-logo">♠</span>
        <h1>Poker Simulation</h1>
        <p className="login-tagline">Monte Carlo Texas Hold'em — Win %, EV strategy & live probability</p>
      </header>
      <div className="login-actions">
        {supabaseConfigured && (
          <button
            type="button"
            className="login-cta google-cta"
            onClick={handleGoogle}
          >
            <span className="google-icon">G</span> Continue with Gmail
          </button>
        )}
        <button
          type="button"
          className="login-cta primary-cta"
          onClick={() => { setIsSignUp(true); setShowForm(true) }}
        >
          Get Started
        </button>
        <button
          type="button"
          className="login-cta secondary-cta"
          onClick={() => { setIsSignUp(false); setShowForm(true) }}
        >
          Sign in
        </button>
      </div>
      <p className="login-features-hint">Live probability • Hand analysis • Monte Carlo equity</p>
      <div className="login-features">
        <div className="login-feature-card">
          <span className="feature-icon">📊</span>
          <h3>Live probability</h3>
          <p>Win % updates as you pick 2nd, 3rd, 4th, 5th board cards.</p>
        </div>
        <div className="login-feature-card">
          <span className="feature-icon">🎴</span>
          <h3>Hand analysis</h3>
          <p>Best possible hand, hand distribution, and exploitative guidance.</p>
        </div>
        <div className="login-feature-card">
          <span className="feature-icon">⚡</span>
          <h3>Monte Carlo equity</h3>
          <p>EV by street. FOLD/CALL/RAISE recommendations with reasoning.</p>
        </div>
      </div>
    </div>
  )
}
