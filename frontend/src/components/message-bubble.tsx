import type { ChatMessage } from '../types/chat'

type MessageBubbleProps = {
  message: ChatMessage
}

const timeFormatter = new Intl.DateTimeFormat(undefined, {
  hour: '2-digit',
  minute: '2-digit',
})

export const MessageBubble = ({ message }: MessageBubbleProps) => {
  const isUser = message.role === 'user'
  const displayTime = timeFormatter.format(new Date(message.createdAt))

  return (
    <article className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[min(85%,42rem)] rounded-3xl px-5 py-4 shadow-xl ${
          isUser
            ? 'rounded-br-md bg-cyan-400 text-slate-950 shadow-cyan-950/20'
            : 'rounded-bl-md border border-white/10 bg-white/[0.08] text-slate-100 shadow-slate-950/30'
        }`}
      >
        <div className="mb-2 flex items-center gap-2">
          <span
            className={`text-xs font-semibold uppercase tracking-[0.18em] ${
              isUser ? 'text-slate-800' : 'text-cyan-200'
            }`}
          >
            {isUser ? 'You' : 'Assistant'}
          </span>
          <span className={`text-xs ${isUser ? 'text-slate-700' : 'text-slate-400'}`}>{displayTime}</span>
        </div>
        <p className="whitespace-pre-wrap text-left text-sm leading-7 md:text-base">{message.content}</p>
      </div>
    </article>
  )
}
