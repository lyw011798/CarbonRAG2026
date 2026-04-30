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

export const useChat = (): UseChatResult => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
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
      const nextMessages = [...messages, userMessage]

      setMessages(nextMessages)
      setErrorMessage(null)
      setIsLoading(true)

      try {
        const assistantMessage = await sendChatMessage(nextMessages.map(toApiMessage))

        setMessages([...nextMessages, createMessage('assistant', assistantMessage.content.trim())])
        return true
      } catch (error) {
        setErrorMessage(getErrorMessage(error))
        return false
      } finally {
        setIsLoading(false)
      }
    },
    [isLoading, messages],
  )

  return {
    messages,
    errorMessage,
    isLoading,
    submitMessage,
    clearError,
  }
}
