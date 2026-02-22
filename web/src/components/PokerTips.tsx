import { useState } from 'react'
import './PokerTips.css'

interface PokerTipsProps {
  winPct?: number
  handName?: string
  bestHand?: string
  boardLen: number
  strategyMessage?: string
}

const TIPS: Record<string, string[]> = {
  preflop: [
    'Position matters: play tighter from early position, looser from the button.',
    'Pocket pairs have ~12% to hit a set on the flop. Consider pot odds when calling.',
    'Suited connectors have implied odds — you can win big when you hit.',
    'Avoid playing too many hands. VPIP (voluntarily put $ in pot) of 20–25% is solid.',
  ],
  flop: [
    'Check your equity: if you have 33%+ vs one opponent, calling is often correct.',
    'Draws: flush draw has ~35% by the river, open-ended straight ~32%.',
    'Consider pot odds: (call amount) / (pot + call) = break-even equity.',
    'Continuation bets work best on dry boards (no draws) when you have equity.',
  ],
  turn: [
    'Your equity changes significantly on the turn. Re-evaluate draws.',
    'If you have 9+ outs, you often have the right odds to call one street.',
    'Rule of 2 and 4: outs × 2 on turn, × 4 on flop for approximate river %.',
  ],
  river: [
    'Bluff when the board favors your range. Value bet thin when you expect calls.',
    'Pot control: if your hand is marginal, consider checking to avoid big losses.',
  ],
}

function getTips(boardLen: number, winPct?: number, handName?: string): string[] {
  const tips: string[] = []
  const street = boardLen === 0 ? 'preflop' : boardLen === 3 ? 'flop' : boardLen === 4 ? 'turn' : 'river'
  tips.push(...(TIPS[street] || TIPS.preflop))
  if (winPct !== undefined) {
    if (winPct > 0.6) tips.unshift(`Strong hand! ${(winPct * 100).toFixed(0)}% equity — consider betting for value.`)
    else if (winPct < 0.35) tips.unshift(`Weak equity (${(winPct * 100).toFixed(0)}%). Consider folding unless you have a draw.`)
  }
  if (handName) {
    if (handName.includes('draw')) tips.unshift('You have a draw. Calculate pot odds before calling.')
    if (handName.includes('pair')) tips.unshift('Pair made. Consider if you’re ahead or need to improve.')
  }
  return tips.slice(0, 4)
}

export default function PokerTips({ winPct, handName, bestHand, boardLen, strategyMessage }: PokerTipsProps) {
  const [open, setOpen] = useState(false)
  const tips = getTips(boardLen, winPct, handName)

  return (
    <div className="poker-tips">
      <button
        type="button"
        className="poker-tips-toggle"
        onClick={() => setOpen(!open)}
      >
        🤖 AI tips {open ? '▼' : '▶'}
      </button>
      {open && (
        <div className="poker-tips-panel">
          {strategyMessage && (
            <p className="poker-tips-strategy"><strong>Strategy:</strong> {strategyMessage}</p>
          )}
          {bestHand && (
            <p className="poker-tips-best">Best possible: {bestHand}</p>
          )}
          <ul>
            {tips.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
