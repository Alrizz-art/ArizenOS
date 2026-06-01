import { useState, useCallback, useEffect, useRef } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import ChatPanel from './components/ChatPanel'
import HudOverlay from './components/HudOverlay'
import CommandPalette from './components/CommandPalette'
import './styles/nexus.css'

interface Message {
  id:        string
  role:      'user' | 'monarch' | 'system'
  content:   string
  timestamp: number
  streaming: boolean
}

export default function App() {
  const [messages,    setMessages]  = useState<Message[]>([])
  const [input,       setInput]     = useState('')
  const [isThinking,  setThinking]  = useState(false)
  const [paletteOpen, setPalette]   = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Ctrl+K command palette
  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setPalette(v => !v)
      }
    }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [])

  // Stream tokens from daemon
  useEffect(() => {
    const unsub = listen<{ messageId: string; token: string; done: boolean }>(
      'arizen://token',
      ({ payload }) => {
        setMessages(prev => prev.map(m =>
          m.id === payload.messageId
            ? { ...m, content: m.content + payload.token, streaming: !payload.done }
            : m
        ))
        if (payload.done) setThinking(false)
      }
    )
    return () => { unsub.then(fn => fn()) }
  }, [])

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isThinking) return

    const userMsg:   Message = { id: crypto.randomUUID(), role: 'user',    content: text.trim(), timestamp: Date.now(), streaming: false }
    const streamMsg: Message = { id: crypto.randomUUID(), role: 'monarch', content: '',          timestamp: Date.now(), streaming: true  }

    setMessages(prev => [...prev, userMsg, streamMsg])
    setInput('')
    setThinking(true)

    try {
      await invoke('send_to_monarch', { query: text.trim(), messageId: streamMsg.id })
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === streamMsg.id ? { ...m, content: String(err), streaming: false } : m
      ))
      setThinking(false)
    }
  }, [isThinking])

  return (
    <div className="nexus-root">
      <HudOverlay />
      {paletteOpen && <CommandPalette onClose={() => setPalette(false)} />}
      <ChatPanel messages={messages} input={input} inputRef={inputRef}
                 isThinking={isThinking} onInput={setInput} onSend={sendMessage} />
    </div>
  )
}
