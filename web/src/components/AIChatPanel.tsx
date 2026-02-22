import { useState, useRef, useEffect } from 'react'
import { apiUrl } from '../lib/api'
import './AIChatPanel.css'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

interface AIChatPanelProps {
  open: boolean
  onClose: () => void
  context?: { winPct?: number; handName?: string; boardLen?: number }
}

export default function AIChatPanel({ open, onClose, context }: AIChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', text: 'Ask me anything about poker strategy, hand analysis, or odds. I\'m here to help!' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const res = await fetch(apiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          context: context || {},
        }),
      })
      const data = await res.json().catch(() => ({}))
      const reply = data.reply || data.message || 'I couldn\'t process that. Try asking about poker strategy, pot odds, or hand rankings.'
      setMessages((m) => [...m, { role: 'assistant', text: reply }])
    } catch {
      setMessages((m) => [
        ...m,
        { role: 'assistant', text: 'Connection error. Make sure the API is running.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="ai-chat-panel-overlay" onClick={onClose}>
      <div className="ai-chat-panel neu-raised" onClick={(e) => e.stopPropagation()}>
        <div className="ai-chat-header">
          <h3>Poker AI assistant</h3>
          <button type="button" className="ai-chat-close" onClick={onClose} aria-label="Close">
            &times;
          </button>
        </div>
        <div className="ai-chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`ai-chat-msg ${msg.role}`}>
              {msg.text}
            </div>
          ))}
          {loading && <div className="ai-chat-msg assistant">Thinking…</div>}
          <div ref={bottomRef} />
        </div>
        <div className="ai-chat-input-wrap">
          <input
            type="text"
            className="neu-input ai-chat-input"
            placeholder="Ask about poker..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            disabled={loading}
          />
          <button type="button" className="neu-btn neu-btn-primary" onClick={sendMessage} disabled={loading || !input.trim()}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
