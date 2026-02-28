import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiUrl } from '../lib/api'
import { Link } from 'react-router-dom'
import './Friends.css'

interface Friend {
  id: string
  email: string
  name: string
}

interface InboxRequest {
  id: string
  email: string
  name: string
  from_id: string
}

export default function Friends() {
  const { user } = useAuth()
  const [friends, setFriends] = useState<Friend[]>([])
  const [inbox, setInbox] = useState<InboxRequest[]>([])
  const [sentTo, setSentTo] = useState<Set<string>>(new Set())
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<Friend[]>([])
  const [loading, setLoading] = useState(false)
  const [feedback, setFeedback] = useState('')

  const loadFriends = () => {
    if (!user?.id) return
    fetch(apiUrl(`/api/friends?user_id=${encodeURIComponent(user.id)}`))
      .then((r) => r.json())
      .then((d) => setFriends(d.friends || []))
      .catch(() => setFriends([]))
  }

  const loadInbox = () => {
    if (!user?.id) return
    fetch(apiUrl(`/api/friends/inbox?user_id=${encodeURIComponent(user.id)}`))
      .then((r) => r.json())
      .then((d) => setInbox(d.requests || []))
      .catch(() => setInbox([]))
  }

  const loadSent = () => {
    if (!user?.id) return
    fetch(apiUrl(`/api/friends/sent?user_id=${encodeURIComponent(user.id)}`))
      .then((r) => r.json())
      .then((d) => setSentTo(new Set(d.sent_to || [])))
      .catch(() => setSentTo(new Set()))
  }

  useEffect(loadFriends, [user?.id])
  useEffect(loadInbox, [user?.id])
  useEffect(loadSent, [user?.id])

  const doSearch = () => {
    if (!user?.id || !search.trim()) return
    setLoading(true)
    setFeedback('')
    fetch(apiUrl(`/api/friends/search?user_id=${encodeURIComponent(user.id)}&q=${encodeURIComponent(search)}`))
      .then((r) => r.json())
      .then((d) => setResults(d.users || []))
      .catch(() => setResults([]))
      .finally(() => setLoading(false))
  }

  const sendRequest = async (friendId: string) => {
    if (!user?.id) return
    setFeedback('')
    try {
      const res = await fetch(apiUrl('/api/friends'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, friend_id: friendId }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Failed')
      setFeedback('Request sent! They must accept in their inbox.')
      loadSent()
      setResults((r) => r.filter((u) => u.id !== friendId))
    } catch (e) {
      setFeedback(e instanceof Error ? e.message : 'Failed')
    }
  }

  const acceptRequest = async (fromId: string) => {
    if (!user?.id) return
    try {
      const res = await fetch(apiUrl('/api/friends/accept'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, from_id: fromId }),
      })
      if (!res.ok) throw new Error('Failed')
      loadInbox()
      loadFriends()
      window.dispatchEvent(new CustomEvent('friends-inbox-update'))
    } catch {
      // ignore
    }
  }

  const declineRequest = async (fromId: string) => {
    if (!user?.id) return
    try {
      await fetch(apiUrl('/api/friends/decline'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, from_id: fromId }),
      })
      loadInbox()
      window.dispatchEvent(new CustomEvent('friends-inbox-update'))
    } catch {
      // ignore
    }
  }

  const removeFriend = async (friendId: string) => {
    if (!user?.id) return
    try {
      await fetch(apiUrl(`/api/friends/${friendId}?user_id=${encodeURIComponent(user.id)}`), { method: 'DELETE' })
      loadFriends()
    } catch {
      // ignore
    }
  }

  if (!user) {
    return (
      <div className="friends-page">
        <p>Please sign in to manage friends.</p>
        <Link to="/">Go to login</Link>
      </div>
    )
  }

  return (
    <div className="friends-page">
      <header className="friends-header">
        <h1>Friends</h1>
        <Link to="/dashboard" className="neu-btn">Back to simulator</Link>
      </header>

      {inbox.length > 0 && (
        <div className="friends-inbox neu-raised">
          <h3>Inbox — friend requests</h3>
          {inbox.map((r) => (
            <div key={r.from_id} className="friend-row inbox-row">
              <span>{r.name} ({r.email})</span>
              <div className="inbox-actions">
                <button type="button" className="neu-btn add-btn" onClick={() => acceptRequest(r.from_id)}>Accept</button>
                <button type="button" className="neu-btn" onClick={() => declineRequest(r.from_id)}>Decline</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="add-friend-section">
        <button
          type="button"
          className="neu-btn neu-btn-primary add-friend-btn"
          onClick={() => { setSearchOpen(!searchOpen); if (!searchOpen) setResults([]); setSearch(''); setFeedback(''); }}
        >
          + Add friend
        </button>
        {searchOpen && (
          <div className="friends-search neu-raised">
            <input
              type="text"
              className="neu-input"
              placeholder="Search by email or username..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && doSearch()}
            />
            <button type="button" className="neu-btn neu-btn-primary" onClick={doSearch} disabled={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
          </div>
        )}
      </div>
      {feedback && <p className="friends-feedback">{feedback}</p>}
      {searchOpen && results.length > 0 && (
        <div className="search-results">
          <h3>Search results</h3>
          {results.map((u) => (
            <div key={u.id} className="friend-row">
              <span>{u.name} ({u.email})</span>
              {sentTo.has(u.id) ? (
                <span className="request-sent">Request sent</span>
              ) : (
                <button type="button" className="neu-btn add-btn" onClick={() => sendRequest(u.id)}>Send request</button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="friends-list">
        <h3>Your friends</h3>
        {friends.length === 0 ? (
          <p className="empty-msg">No friends yet. Add friends — they must accept your request in their inbox.</p>
        ) : (
          friends.map((f) => (
            <div key={f.id} className="friend-row neu-raised">
              <span>{f.name} ({f.email})</span>
              <button type="button" className="neu-btn delete-friend-btn" onClick={() => removeFriend(f.id)}>Remove</button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
