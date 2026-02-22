import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiUrl } from '../lib/api'
import { Link } from 'react-router-dom'
import './Winnings.css'

interface WinningsEntry {
  id: string
  session_date: string
  buy_in: number
  cash_out: number
  profit: number
  hours?: number
  notes?: string
}

export default function Winnings() {
  const { user } = useAuth()
  const [entries, setEntries] = useState<WinningsEntry[]>([])
  const [allEntries, setAllEntries] = useState<WinningsEntry[]>([])
  const [period, setPeriod] = useState<'all' | 'daily' | 'monthly' | 'yearly'>('all')
  const [showForm, setShowForm] = useState(false)
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().slice(0, 10))
  const [buyIn, setBuyIn] = useState('')
  const [cashOut, setCashOut] = useState('')
  const [hours, setHours] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [deleteErr, setDeleteErr] = useState('')

  const loadEntries = () => {
    if (!user?.id) return
    fetch(apiUrl(`/api/winnings?user_id=${encodeURIComponent(user.id)}&period=${period}`))
      .then((r) => r.json())
      .then((d) => setEntries(d.entries || []))
      .catch(() => setEntries([]))
    fetch(apiUrl(`/api/winnings?user_id=${encodeURIComponent(user.id)}&period=all`))
      .then((r) => r.json())
      .then((d) => setAllEntries(d.entries || []))
      .catch(() => setAllEntries([]))
  }

  useEffect(loadEntries, [user?.id, period])

  const addEntry = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user?.id) return
    setLoading(true)
    try {
      const res = await fetch(apiUrl('/api/winnings'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          session_date: sessionDate,
          buy_in: parseFloat(buyIn) || 0,
          cash_out: parseFloat(cashOut) || 0,
          hours: parseFloat(hours) || 0,
          notes: notes.trim(),
        }),
      })
      if (!res.ok) throw new Error('Failed to save')
      setBuyIn('')
      setCashOut('')
      setHours('')
      setNotes('')
      setSessionDate(new Date().toISOString().slice(0, 10))
      setShowForm(false)
      loadEntries()
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }

  const deleteEntry = async (id: string) => {
    if (!user?.id) return
    setDeleteErr('')
    try {
      const res = await fetch(apiUrl(`/api/winnings/${id}?user_id=${encodeURIComponent(user.id)}`), { method: 'DELETE' })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        throw new Error(d.detail || 'Delete failed')
      }
      loadEntries()
    } catch (err) {
      setDeleteErr(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const totalProfit = allEntries.reduce((s, e) => s + e.profit, 0)
  const totalBuyIn = allEntries.reduce((s, e) => s + e.buy_in, 0)
  const totalCashOut = allEntries.reduce((s, e) => s + e.cash_out, 0)
  const totalSessions = allEntries.length
  const totalHours = allEntries.reduce((s, e) => s + (e.hours || 0), 0)
  const profitableSessions = allEntries.filter((e) => e.profit > 0).length
  const profitableRatio = totalSessions > 0 ? (profitableSessions / totalSessions) * 100 : 0
  const profitPerHour = totalHours > 0 ? totalProfit / totalHours : 0

  const byMonth: Record<string, number> = {}
  allEntries.forEach((e) => {
    const m = e.session_date.slice(0, 7)
    byMonth[m] = (byMonth[m] || 0) + e.profit
  })
  const monthLabels = Object.keys(byMonth).sort()
  const maxProfit = Math.max(...monthLabels.map((m) => byMonth[m]), 0.01)
  const minProfit = Math.min(...monthLabels.map((m) => byMonth[m]), -0.01)

  if (!user) {
    return (
      <div className="winnings-page">
        <p>Please sign in to track winnings.</p>
        <Link to="/">Go to login</Link>
      </div>
    )
  }

  const cumulative: { month: string; profit: number }[] = []
  let running = 0
  monthLabels.forEach((m) => {
    running += byMonth[m]
    cumulative.push({ month: m, profit: running })
  })
  const maxAbs = Math.max(...cumulative.map((c) => Math.abs(c.profit)), 1)
  const minY = Math.min(0, ...cumulative.map((c) => c.profit))
  const maxY = Math.max(0, ...cumulative.map((c) => c.profit))
  const rangeY = maxY - minY || 1

  return (
    <div className="winnings-page">
      <header className="winnings-header" style={{ gridColumn: '1 / -1' }}>
        <h1>Poker winnings</h1>
        <Link to="/dashboard" className="neu-btn">Back to simulator</Link>
      </header>
      <div className="winnings-main">
      <div className="winnings-filters">
        {(['all', 'daily', 'monthly', 'yearly'] as const).map((p) => (
          <button
            key={p}
            type="button"
            className={`neu-btn ${period === p ? 'active' : ''}`}
            onClick={() => setPeriod(p)}
          >
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>
      <div className="winnings-stats neu-raised">
        <div className="stat">
          <span className="stat-label">Total profit</span>
          <span className={`stat-value ${totalProfit >= 0 ? 'win' : 'loss'}`}>${totalProfit.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total sessions</span>
          <span className="stat-value">{totalSessions}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total hours</span>
          <span className="stat-value">{totalHours.toFixed(1)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Profitable ratio</span>
          <span className="stat-value">{profitableRatio.toFixed(0)}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">Profit / hour</span>
          <span className={`stat-value ${profitPerHour >= 0 ? 'win' : 'loss'}`}>${profitPerHour.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total buy-ins</span>
          <span className="stat-value">${totalBuyIn.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total cash-out</span>
          <span className="stat-value">${totalCashOut.toFixed(2)}</span>
        </div>
      </div>
      <button type="button" className="neu-btn neu-btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Cancel' : '+ Add session'}
      </button>
      {showForm && (
        <form onSubmit={addEntry} className="winnings-form neu-raised">
          <div className="form-row">
            <label>Date</label>
            <input type="date" value={sessionDate} onChange={(e) => setSessionDate(e.target.value)} className="neu-input" required />
          </div>
          <div className="form-row">
            <label>Buy-in ($)</label>
            <input type="number" step="0.01" min="0" value={buyIn} onChange={(e) => setBuyIn(e.target.value)} className="neu-input" placeholder="0" />
          </div>
          <div className="form-row">
            <label>Cash-out ($) — 0 allowed</label>
            <input type="number" step="0.01" min="0" value={cashOut} onChange={(e) => setCashOut(e.target.value)} className="neu-input" placeholder="0" />
          </div>
          <div className="form-row">
            <label>Hours played</label>
            <input type="number" step="0.25" min="0" value={hours} onChange={(e) => setHours(e.target.value)} className="neu-input" placeholder="0" />
          </div>
          <div className="form-row">
            <label>Notes</label>
            <input type="text" value={notes} onChange={(e) => setNotes(e.target.value)} className="neu-input" placeholder="Optional" />
          </div>
          <button type="submit" className="neu-btn neu-btn-primary" disabled={loading}>
            {loading ? 'Saving…' : 'Save'}
          </button>
        </form>
      )}
      {deleteErr && <p className="winnings-error">{deleteErr}</p>}
      <div className="winnings-list">
        {entries.length === 0 ? (
          <p className="empty-msg">No entries yet. Add a session to track your winnings.</p>
        ) : (
          entries.map((e) => (
            <div key={e.id} className="winnings-item neu-raised">
              <div className="item-date">{e.session_date}</div>
              <div className="item-details">
                Buy-in: ${e.buy_in.toFixed(2)} → Cash-out: ${e.cash_out.toFixed(2)}
                {e.hours ? ` · ${e.hours}h` : ''}
                <span className={`profit ${e.profit >= 0 ? 'win' : 'loss'}`}>
                  {e.profit >= 0 ? '+' : ''}{e.profit.toFixed(2)}
                </span>
              </div>
              {e.notes && <div className="item-notes">{e.notes}</div>}
              <button type="button" className="delete-btn" onClick={() => deleteEntry(e.id)}>Delete</button>
            </div>
          ))
        )}
      </div>
      </div>
      {monthLabels.length > 0 && (
        <div className="winnings-graph-wrap">
          <div className="winnings-graph neu-raised">
            <h3>Profit over time</h3>
            <div className="graph-line-wrap">
              <svg className="graph-line-svg" viewBox="0 0 200 100" preserveAspectRatio="none">
                {cumulative.length > 1 && (
                  <path
                    d={cumulative.map((c, i) => {
                      const x = (i / (cumulative.length - 1)) * 200
                      const y = 90 - ((c.profit - minY) / rangeY) * 80
                      return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                    }).join(' ')}
                    fill="none"
                    stroke="var(--neu-accent)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
                {minY < 0 && maxY > 0 && (
                  <line x1="0" y1={90 - ((0 - minY) / rangeY) * 80} x2="200" y2={90 - ((0 - minY) / rangeY) * 80} stroke="var(--neu-text-muted)" strokeWidth="0.5" strokeDasharray="2" />
                )}
              </svg>
            </div>
            <div className="graph-line-labels">
              {monthLabels[0] && <span>{monthLabels[0]}</span>}
              {monthLabels[monthLabels.length - 1] && <span>{monthLabels[monthLabels.length - 1]}</span>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
