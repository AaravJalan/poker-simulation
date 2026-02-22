import { useState, useRef } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import ProfileMenu from './ProfileMenu'
import './Sidebar.css'

interface SidebarProps {
  onNav?: () => void
}

export default function Sidebar({ onNav }: SidebarProps) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [profileOpen, setProfileOpen] = useState(false)
  const profileAnchorRef = useRef<HTMLDivElement>(null)

  return (
    <aside className="sidebar">
      <div
        ref={profileAnchorRef}
        className="sidebar-user clickable"
        onClick={() => setProfileOpen((v) => !v)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setProfileOpen((v) => !v)}
      >
        <div className="user-avatar">
          {user?.name?.charAt(0)?.toUpperCase() || '?'}
        </div>
        <span className="user-name">{user?.name || user?.email || 'Guest'}</span>
        {profileOpen && <ProfileMenu anchorRef={profileAnchorRef} onClose={() => setProfileOpen(false)} />}
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Simulator
        </NavLink>
        <NavLink to="/saved" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          My simulations
        </NavLink>
        <NavLink to="/winnings" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Winnings
        </NavLink>
        <NavLink to="/friends" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Friends
        </NavLink>
        <NavLink to="/hands" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Hand hierarchy
        </NavLink>
        <NavLink to="/live-game" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Live game
        </NavLink>
        <NavLink to="/games" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`} onClick={onNav}>
          Games
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <button
          type="button"
          className="sidebar-btn theme-toggle"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? '☀️' : '🌙'} {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        <button type="button" className="sidebar-btn logout-btn" onClick={() => logout()}>
          Log out
        </button>
      </div>
    </aside>
  )
}
