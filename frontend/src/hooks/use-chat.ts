import { useCallback, useState } from 'react'
import { ChatApiError, sendChatMessage } from '../api/chat-api'
import type { ApiChatMessage, ChatMessage, ChatRole } from '../types/chat'

type UseChatResult = {
  messages: ChatMessage[]
  errorMessage: string | null
  isLoading: boolean
  submitMessage: (content: string) => Promise<boolean>
  clearError: () => void
}

const createMessageId = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const createMessage = (role: ChatRole, content: string): ChatMessage => ({
  id: createMessageId(),
  role,
  content,
  createdAt: new Date().toISOString(),
})

const toApiMessage = (message: ChatMessage): ApiChatMessage => ({
  role: message.role,
  content: message.content,
})

const getErrorMessage = (error: unknown): string => {
  if (error instanceof ChatApiError || error instanceof Error) {
    return error.message
  }

  return 'An unexpected chat error occurred. Please try again.'
}

export const useChat = (options?: {
  messages?: ChatMessage[]
  onMessagesChange?: (messages: ChatMessage[]) => void
}): UseChatResult => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const clearError = useCallback(() => {
    setErrorMessage(null)
  }, [])

  const submitMessage = useCallback(
    async (content: string): Promise<boolean> => {
      const trimmedContent = content.trim()

      if (!trimmedContent || isLoading) {
        return false
      }

      const userMessage = createMessage('user', trimmedContent)
      const nextMessages = [...(options?.messages ?? []), userMessage]

      options?.onMessagesChange?.(nextMessages)
      setErrorMessage(null)
      setIsLoading(true)

      try {
        const assistantMessage = await sendChatMessage(
          nextMessages.map(toApiMessage),
        )

        const finalMessages = [
          ...nextMessages,
          createMessage('assistant', assistantMessage.content.trim()),
        ]
        options?.onMessagesChange?.(finalMessages)
        return true
      } catch (error) {
        setErrorMessage(getErrorMessage(error))
        return false
      } finally {
        setIsLoading(false)
      }
    },
    [isLoading, options],
  )

  return {
    messages: options?.messages ?? [],
    errorMessage,
    isLoading,
    submitMessage,
    clearError,
  }
}
