import { useEffect, useRef } from 'react'
import { ErrorBanner } from './error-banner'
import { MessageBubble } from './message-bubble'
import type { ChatMessage } from '../types/chat'

type MessageListProps = {
  messages: ChatMessage[]
  isLoading: boolean
  errorMessage: string | null
  onDismissError: () => void
}

const LoadingIndicator = () => (
  <div className="flex justify-start">
    <div className="rounded-3xl rounded-bl-md border border-white/10 bg-white/[0.08] px-5 py-4 text-slate-100 shadow-xl shadow-slate-950/30">
      <div className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">Assistant</div>
      <div className="flex items-center gap-2" aria-label="Assistant is thinking">
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-200 [animation-delay:-0.2s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-200 [animation-delay:-0.1s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-cyan-200" />
      </div>
    </div>
  </div>
)

const EmptyState = () => (
  <div className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center py-16 text-center">
    <div className="mb-5 rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-cyan-200">
      Ready to chat
    </div>
    <h2 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
      Explore carbon market knowledge conversationally.
    </h2>
    <p className="mt-4 text-sm leading-7 text-slate-300 md:text-base">
      Ask about Taiwan carbon policy, market mechanisms, or document insights.
      Your messages stay in this browser session and are sent to the chat API.
    </p>
  </div>
)

export const MessageList = ({ messages, isLoading, errorMessage, onDismissError }: MessageListProps) => {
  const endRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isLoading, errorMessage])

  return (
    <section
      className="min-h-0 flex-1 overflow-y-auto px-4 py-6 md:px-8"
      aria-label="Conversation history"
    >
      <div className="mx-auto flex min-h-full max-w-5xl flex-col gap-5">
        {messages.length === 0 ? <EmptyState /> : messages.map((message) => <MessageBubble key={message.id} message={message} />)}
        {isLoading ? <LoadingIndicator /> : null}
        {errorMessage ? <ErrorBanner message={errorMessage} onDismiss={onDismissError} /> : null}
        <div ref={endRef} />
      </div>
    </section>
  )
}
