import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { supabaseConfigured } from '../lib/supabase'
import './ProfileMenu.css'

interface ProfileMenuProps {
  anchorRef: React.RefObject<HTMLElement>
  onClose: () => void
}

export default function ProfileMenu({ anchorRef, onClose }: ProfileMenuProps) {
  const { user, updateProfile } = useAuth()
  const [mode, setMode] = useState<'menu' | 'username' | 'password'>('menu')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newUsername, setNewUsername] = useState(user?.name || '')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState('')
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node) && anchorRef.current && !anchorRef.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [onClose, anchorRef])

  const handleUpdateUsername = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!supabaseConfigured && !currentPassword?.trim()) {
      setError('Current password required for PokerID')
      return
    }
    try {
      await updateProfile(currentPassword, newUsername)
      setMode('menu')
      setCurrentPassword('')
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed')
    }
  }

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }
    try {
      await updateProfile(currentPassword, undefined, newPassword)
      setMode('menu')
      setCurrentPassword('')
      setNewPassword('')
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed')
    }
  }

  const showProfileEdit = true

  return (
    <div ref={menuRef} className="profile-menu">
      {mode === 'menu' && (
        <>
          <div className="profile-menu-user">
            <strong>{user?.name || user?.email}</strong>
            <span className="profile-menu-email">{user?.email}</span>
          </div>
          {showProfileEdit && (
            <>
              <button type="button" className="profile-menu-item" onClick={() => setMode('username')}>
                Rename profile
              </button>
              <button type="button" className="profile-menu-item" onClick={() => { setMode('password'); setNewUsername(''); setNewPassword(''); setError(''); }}>
                Change password
              </button>
            </>
          )}
        </>
      )}
      {mode === 'username' && (
        <form onSubmit={handleUpdateUsername} className="profile-menu-form">
          <h4>Change username</h4>
          {!supabaseConfigured && (
            <input
              type="password"
              placeholder="Current password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="neu-input"
              required
            />
          )}
          <input
            type="text"
            placeholder="New username"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            className="neu-input"
            required
          />
          {error && <p className="profile-menu-error">{error}</p>}
          <div className="profile-menu-actions">
            <button type="button" className="neu-btn" onClick={() => setMode('menu')}>Cancel</button>
            <button type="submit" className="neu-btn neu-btn-primary">Save</button>
          </div>
        </form>
      )}
      {mode === 'password' && (
        <form onSubmit={handleUpdatePassword} className="profile-menu-form">
          <h4>Change password</h4>
          <input
            type="password"
            placeholder="Current password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            className="neu-input"
            required
          />
          <input
            type="password"
            placeholder="New password (min 6 chars)"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="neu-input"
            required
          />
          {error && <p className="profile-menu-error">{error}</p>}
          <div className="profile-menu-actions">
            <button type="button" className="neu-btn" onClick={() => setMode('menu')}>Cancel</button>
            <button type="submit" className="neu-btn neu-btn-primary">Save</button>
          </div>
        </form>
      )}
    </div>
  )
}
