import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

type ChatInputProps = {
  isLoading: boolean
  onSubmit: (message: string) => Promise<boolean>
}

export const ChatInput = ({ isLoading, onSubmit }: ChatInputProps) => {
  const [message, setMessage] = useState('')
  const trimmedMessage = message.trim()
  const isSubmitDisabled = isLoading || trimmedMessage.length === 0

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (isSubmitDisabled) {
      return
    }

    const wasSubmitted = await onSubmit(trimmedMessage)

    if (wasSubmitted) {
      setMessage('')
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      event.currentTarget.form?.requestSubmit()
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-white/10 bg-slate-950/85 px-4 py-4 backdrop-blur md:px-8"
    >
      <div className="mx-auto flex max-w-5xl items-end gap-3 rounded-3xl border border-white/10 bg-white/[0.08] p-2 shadow-2xl shadow-slate-950/40 focus-within:border-cyan-300/40">
        <label htmlFor="chat-message" className="sr-only">
          Message
        </label>
        <textarea
          id="chat-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about Taiwan carbon markets..."
          rows={1}
          disabled={isLoading}
          className="max-h-36 min-h-12 flex-1 resize-none bg-transparent px-4 py-3 text-sm leading-6 text-white placeholder:text-slate-500 focus:outline-none md:text-base"
        />
        <button
          type="submit"
          disabled={isSubmitDisabled}
          className="flex h-12 shrink-0 items-center justify-center rounded-2xl bg-cyan-300 px-5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 focus:outline-none focus:ring-2 focus:ring-cyan-200 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
        >
          {isLoading ? 'Sending' : 'Send'}
        </button>
      </div>
      <p className="mx-auto mt-3 max-w-5xl px-2 text-xs leading-5 text-slate-500">
        Press Enter to send. Use Shift + Enter for a new line.
      </p>
    </form>
  )
}
