import { Link } from 'react-router-dom'
import './HandHierarchy.css'

const RANKINGS = [
  { rank: 1, name: 'Royal Flush', desc: 'A♠ K♠ Q♠ J♠ 10♠', ex: 'A-K-Q-J-10 of same suit' },
  { rank: 2, name: 'Straight Flush', desc: '9♥ 8♥ 7♥ 6♥ 5♥', ex: 'Five sequential cards, same suit' },
  { rank: 3, name: 'Four of a Kind', desc: 'K♠ K♥ K♦ K♣ 2♠', ex: 'Four cards of same rank' },
  { rank: 4, name: 'Full House', desc: 'Q♠ Q♥ Q♦ 3♣ 3♠', ex: 'Three of a kind + pair' },
  { rank: 5, name: 'Flush', desc: 'A♦ J♦ 9♦ 6♦ 2♦', ex: 'Five cards same suit, not sequential' },
  { rank: 6, name: 'Straight', desc: '9♠ 8♦ 7♥ 6♣ 5♠', ex: 'Five sequential cards, mixed suits' },
  { rank: 7, name: 'Three of a Kind', desc: '7♠ 7♥ 7♦ A♣ 2♠', ex: 'Three cards of same rank' },
  { rank: 8, name: 'Two Pair', desc: 'J♠ J♥ 4♦ 4♣ 9♠', ex: 'Two pairs of same rank' },
  { rank: 9, name: 'One Pair', desc: 'A♠ A♥ K♦ 8♣ 3♠', ex: 'Two cards of same rank' },
  { rank: 10, name: 'High Card', desc: 'A♠ K♦ 9♥ 5♣ 2♠', ex: 'No pair; highest card wins' },
]

export default function HandHierarchy() {
  const col1 = RANKINGS.filter((h) => h.rank <= 5)
  const col2 = RANKINGS.filter((h) => h.rank > 5)

  const renderCards = (desc: string) => {
    const cards = (desc || '').split(/\s+/).filter(Boolean)
    return (
      <span className="hand-cards" aria-label={desc}>
        {cards.map((c, i) => {
          const suit = c.slice(-1)
          const rank = c.slice(0, -1)
          const isRed = suit === '♦' || suit === '♥'
          return (
            <span key={`${c}-${i}`} className={`mini-card-square ${isRed ? 'red' : 'black'}`}>
              <span className="mini-card-rank">{rank}</span>
              <span className="mini-card-suit">{suit}</span>
            </span>
          )
        })}
      </span>
    )
  }

  return (
    <div className="hand-hierarchy-page">
      <header className="hand-hierarchy-header page-header">
        <h1>Hand Hierarchy</h1>
        <div className="page-header-right">
          <Link to="/dashboard" className="neu-btn">Back to simulator</Link>
        </div>
      </header>
      <p className="hand-hierarchy-intro">Poker hand rankings from strongest to weakest. Use as a quick reference at the table.</p>
      <div className="hand-hierarchy-cols">
        <div className="hand-hierarchy-col">
          {col1.map((h) => (
            <div key={h.rank} className="hand-hierarchy-item">
              <span className="hand-rank">#{h.rank}</span>
              <div className="hand-info">
                <strong>{h.name}</strong>
                <span className="hand-desc">{renderCards(h.desc)}</span>
                <span className="hand-ex">{h.ex}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="hand-hierarchy-col">
          {col2.map((h) => (
            <div key={h.rank} className="hand-hierarchy-item">
              <span className="hand-rank">#{h.rank}</span>
              <div className="hand-info">
                <strong>{h.name}</strong>
                <span className="hand-desc">{renderCards(h.desc)}</span>
                <span className="hand-ex">{h.ex}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
