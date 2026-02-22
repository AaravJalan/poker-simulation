import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'
import './Saved.css'

const RANKS = '23456789TJQKA'
const SUITS = '♣♦♥♠'

function cardLabel(card: number) {
  const r = RANKS[card % 13]
  return (r === 'T' ? '10' : r) + SUITS[Math.floor(card / 13)]
}

export default function Saved() {
  const { user } = useAuth()
  const [saved, setSaved] = useState<Array<{ holeCards: number[]; boardCards: number[]; numOpponents: number; result: { win_pct: number; tie_pct: number; loss_pct: number }; timestamp: number }>>([])

  useEffect(() => {
    if (user) {
      const key = `poker_saved_${user.email}`
      const data = JSON.parse(localStorage.getItem(key) || '[]')
      setSaved(data.reverse())
    }
  }, [user])

  const deleteItem = (i: number) => {
    if (!user) return
    const key = `poker_saved_${user.email}`
    const data = JSON.parse(localStorage.getItem(key) || '[]').reverse()
    data.splice(i, 1)
    localStorage.setItem(key, JSON.stringify(data.reverse().slice(-50)))
    setSaved([...data].reverse())
  }

  if (!user) {
    return (
      <div className="saved-page">
        <p>Please sign in to view saved simulations.</p>
        <Link to="/">Go to login</Link>
      </div>
    )
  }

  return (
    <div className="saved-page">
      <header className="saved-header">
        <h1>My simulations</h1>
        <Link to="/dashboard" className="neu-btn">Back to simulator</Link>
      </header>
      {saved.length === 0 ? (
        <p className="empty-msg">No saved simulations yet. Run a simulation and click "Save to My Simulations".</p>
      ) : (
        <div className="saved-list">
          {saved.map((s, i) => (
            <div key={i} className="saved-item neu-raised">
              <div className="saved-cards">
                <span className="saved-label">Hole:</span>
                {s.holeCards.map((c) => (
                  <span key={c} className="mini-card">{cardLabel(c)}</span>
                ))}
                <span className="saved-label">Board:</span>
                {s.boardCards.map((c) => (
                  <span key={c} className="mini-card">{cardLabel(c)}</span>
                ))}
              </div>
              <div className="saved-stats">
                Win {(s.result.win_pct * 100).toFixed(1)}% · Tie {(s.result.tie_pct * 100).toFixed(1)}% · Loss {(s.result.loss_pct * 100).toFixed(1)}%
              </div>
              <div className="saved-meta">
                vs {s.numOpponents} opponent{s.numOpponents > 1 ? 's' : ''} · {new Date(s.timestamp).toLocaleString()}
              </div>
              <button type="button" className="delete-btn" onClick={() => deleteItem(i)}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
