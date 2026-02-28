import { useState } from 'react'
import { Link } from 'react-router-dom'
import './LiveGame.css'

interface Player {
  id: string
  name: string
  buyIn: number
  cashOut: number
}

function genId() {
  return Math.random().toString(36).slice(2, 11)
}

export default function LiveGame() {
  const [players, setPlayers] = useState<Player[]>([
    { id: genId(), name: 'Player 1', buyIn: 0, cashOut: 0 },
    { id: genId(), name: 'Player 2', buyIn: 0, cashOut: 0 },
  ])
  const [newName, setNewName] = useState('')

  const totalBuyIn = players.reduce((s, p) => s + p.buyIn, 0)
  const totalCashOut = players.reduce((s, p) => s + p.cashOut, 0)
  const totalProfit = totalCashOut - totalBuyIn

  const updatePlayer = (id: string, updates: Partial<Player>) => {
    setPlayers((prev) => prev.map((p) => (p.id === id ? { ...p, ...updates } : p)))
  }

  const addPlayer = () => {
    if (newName.trim()) {
      setPlayers((prev) => [...prev, { id: genId(), name: newName.trim(), buyIn: 0, cashOut: 0 }])
      setNewName('')
    } else {
      setPlayers((prev) => [...prev, { id: genId(), name: `Player ${prev.length + 1}`, buyIn: 0, cashOut: 0 }])
    }
  }

  const removePlayer = (id: string) => {
    if (players.length <= 2) return
    setPlayers((prev) => prev.filter((p) => p.id !== id))
  }

  const profits = players.map((p) => ({ ...p, profit: p.cashOut - p.buyIn }))
  const winners = profits.filter((p) => p.profit > 0)
  const losers = profits.filter((p) => p.profit < 0)

  const settlements: { from: string; to: string; amount: number }[] = []
  const losersCopy = losers.map((l) => ({ ...l, remaining: -l.profit }))
  let wi = 0
  for (const loser of losersCopy) {
    let toPay = loser.remaining
    while (toPay > 0.01 && wi < winners.length) {
      const winner = winners[wi]
      const needed = winner.profit - (settlements.filter((s) => s.to === winner.name).reduce((a, s) => a + s.amount, 0))
      if (needed <= 0) {
        wi++
        continue
      }
      const pay = Math.min(toPay, needed)
      settlements.push({ from: loser.name, to: winner.name, amount: Math.round(pay * 100) / 100 })
      toPay -= pay
      loser.remaining -= pay
      if (needed <= pay) wi++
    }
  }

  return (
    <div className="live-game-page">
      <header className="live-game-header">
        <h1>Live game</h1>
        <Link to="/dashboard" className="neu-btn">Back</Link>
      </header>
      <p className="live-game-desc">Track buy-ins and cash-outs. We calculate who pays whom.</p>

      <div className="live-game-totals neu-raised">
        <div className="totals-row">
          <span>Total buy-ins</span>
          <span>${totalBuyIn.toFixed(2)}</span>
        </div>
        <div className="totals-row">
          <span>Total cash-out</span>
          <span>${totalCashOut.toFixed(2)}</span>
        </div>
        <div className={`totals-row total-profit ${totalProfit >= 0 ? 'win' : 'loss'}`}>
          <span>Net</span>
          <span>${totalProfit.toFixed(2)}</span>
        </div>
      </div>

      <div className="live-game-players">
        {players.map((p) => (
          <div key={p.id} className="player-card">
            <input
              type="text"
              className="player-name neu-input"
              value={p.name}
              onChange={(e) => updatePlayer(p.id, { name: e.target.value })}
              placeholder="Name"
            />
            <div className="player-inputs">
              <div>
                <label>Buy-in $</label>
                <input
                  type="number"
                  step="0.01"
                  value={p.buyIn || ''}
                  onChange={(e) => updatePlayer(p.id, { buyIn: parseFloat(e.target.value) || 0 })}
                  className="neu-input"
                />
              </div>
              <div>
                <label>Cash-out $</label>
                <input
                  type="number"
                  step="0.01"
                  value={p.cashOut || ''}
                  onChange={(e) => updatePlayer(p.id, { cashOut: parseFloat(e.target.value) || 0 })}
                  className="neu-input"
                />
              </div>
            </div>
            <div className={`player-profit ${p.cashOut - p.buyIn >= 0 ? 'win' : 'loss'}`}>
              {p.cashOut - p.buyIn >= 0 ? '+' : ''}{(p.cashOut - p.buyIn).toFixed(2)}
            </div>
            <button type="button" className="remove-btn" onClick={() => removePlayer(p.id)} disabled={players.length <= 2}>
              &times;
            </button>
          </div>
        ))}
      </div>

      <div className="add-player-row">
        <input
          type="text"
          className="neu-input"
          placeholder="New player name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addPlayer()}
        />
        <button type="button" className="neu-btn neu-btn-primary" onClick={addPlayer}>
          + Add player
        </button>
      </div>

      {settlements.length > 0 && (
        <div className="settlements neu-raised">
          <h3>Settlements</h3>
          {settlements.map((s, i) => (
            <div key={i} className="settlement-row">
              <span className="from">{s.from}</span>
              <span className="arrow">&rarr;</span>
              <span className="to">{s.to}</span>
              <span className="amount">${s.amount.toFixed(2)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
