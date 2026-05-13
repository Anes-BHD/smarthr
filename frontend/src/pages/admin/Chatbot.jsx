import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { Avatar } from '../../components/ui/index'
import { useAuth } from '../../context/AuthContext'

export default function Chatbot() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: 'Hello! I am SmartHR Assistant. How can I help you manage your HR tasks today?' }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = (e) => {
    e?.preventDefault()
    if (!input.trim()) return

    const newMsg = { id: Date.now(), role: 'user', text: input.trim() }
    setMessages(prev => [...prev, newMsg])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [
        ...prev, 
        { id: Date.now(), role: 'assistant', text: "I'm a mockup chatbot! Once you integrate a real backend AI service like OpenAI, I will be able to answer your questions and perform tasks on the SmartHR platform for you." }
      ])
      setIsTyping(false)
    }, 1500)
  }

  const displayName = `${user?.firstname ?? user?.name ?? ''} ${user?.lastname ?? ''}`.trim() || 'You'

  return (
    <>
      <div className="page-header" style={{ marginBottom: 16 }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={24} color="var(--c-primary)" />
          AI Assistant
        </h1>
        <p>Ask questions or get help navigating the SmartHR platform.</p>
      </div>

      <div className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 220px)', overflow: 'hidden' }}>
        
        {/* Messages Area */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800, margin: '0 auto' }}>
            {messages.map(m => (
              <div key={m.id} style={{ display: 'flex', gap: 16, alignItems: 'flex-start', flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}>
                <div style={{ flexShrink: 0 }}>
                  {m.role === 'user' 
                    ? <Avatar name={displayName} size="sm" />
                    : <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--c-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                        <Bot size={20} />
                      </div>
                  }
                </div>
                <div style={{
                  background: m.role === 'user' ? 'var(--c-primary)' : 'var(--c-surface3)',
                  color: m.role === 'user' ? '#fff' : 'var(--c-text)',
                  padding: '12px 18px',
                  borderRadius: '16px',
                  borderTopLeftRadius: m.role === 'assistant' ? 4 : 16,
                  borderTopRightRadius: m.role === 'user' ? 4 : 16,
                  maxWidth: '80%',
                  lineHeight: 1.5,
                  fontSize: '0.95rem'
                }}>
                  {m.text}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--c-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                  <Bot size={20} />
                </div>
                <div style={{ background: 'var(--c-surface3)', padding: '16px 18px', borderRadius: '16px', borderTopLeftRadius: 4, display: 'flex', gap: 6 }}>
                  <span className="typing-dot" style={{ animationDelay: '0s' }}></span>
                  <span className="typing-dot" style={{ animationDelay: '0.2s' }}></span>
                  <span className="typing-dot" style={{ animationDelay: '0.4s' }}></span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Input Area */}
        <div style={{ borderTop: '1px solid var(--c-border)', padding: '16px 24px', background: 'var(--c-surface2)' }}>
          <form onSubmit={handleSend} style={{ display: 'flex', gap: 12, maxWidth: 800, margin: '0 auto' }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type your message here..."
              style={{
                flex: 1, padding: '12px 20px', borderRadius: '24px', border: '1px solid var(--c-border)',
                background: 'var(--c-surface)', color: 'var(--c-text)', outline: 'none', fontSize: '0.95rem'
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              style={{
                background: 'var(--c-primary)', color: '#fff', border: 'none', borderRadius: '50%',
                width: 46, height: 46, display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: input.trim() && !isTyping ? 'pointer' : 'not-allowed', opacity: input.trim() && !isTyping ? 1 : 0.6,
                transition: 'all 0.2s'
              }}
            >
              <Send size={20} style={{ marginLeft: 2 }} />
            </button>
          </form>
        </div>

        <style>{`
          .typing-dot {
            width: 6px; height: 6px; background: var(--c-muted); borderRadius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
          }
          @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
          }
        `}</style>
      </div>
    </>
  )
}
