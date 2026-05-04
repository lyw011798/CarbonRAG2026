import { useCallback, useEffect, useMemo, useState } from 'react'
import type { Conversation } from '../types/conversation'
import type { ChatMessage } from '../types/chat'
import { conversationStorage } from '../utils/localStorage'

interface UseConversationHistoryResult {
  conversations: Conversation[]
  activeConversationId: string | null
  activeConversation: Conversation | null
  createConversation: () => Conversation
  clearAllHistory: () => void
  updateConversation: (id: string, messages: ChatMessage[]) => void
  deleteConversation: (id: string) => void
  renameConversation: (id: string, newTitle: string) => void
  setActiveConversation: (id: string) => void
}

const generateId = (): string => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const createNewConversation = (): Conversation => ({
  id: generateId(),
  title: 'New Chat',
  messages: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
})

export const useConversationHistory = (): UseConversationHistoryResult => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)

  // Load conversations from localStorage on mount
  useEffect(() => {
    const loaded = conversationStorage.load()
    setConversations(loaded)

    // Auto-create new conversation
    const newConversation = createNewConversation()
    const allConversations = [...loaded, newConversation]
    setConversations(allConversations)
    setActiveConversationId(newConversation.id)
    conversationStorage.save(allConversations)
  }, [])

  const createConversation = useCallback((): Conversation => {
    const newConversation = createNewConversation()
    setConversations((currentConversations) => {
      const updated = [newConversation, ...currentConversations]
      conversationStorage.save(updated)
      return updated
    })
    setActiveConversationId(newConversation.id)
    return newConversation
  }, [])

  const clearAllHistory = useCallback((): void => {
    const newConversation = createNewConversation()
    conversationStorage.clear()
    conversationStorage.save([newConversation])
    setConversations([newConversation])
    setActiveConversationId(newConversation.id)
  }, [])

  const updateConversation = useCallback(
    (id: string, messages: ChatMessage[]): void => {
      setConversations((currentConversations) => {
        const updated = currentConversations.map((conv) =>
          conv.id === id
            ? {
                ...conv,
                messages,
                updatedAt: new Date().toISOString(),
              }
            : conv,
        )
        conversationStorage.save(updated)
        return updated
      })
    },
    [],
  )

  const deleteConversation = useCallback(
    (id: string): void => {
      setConversations((currentConversations) => {
        const updated = currentConversations.filter((conv) => conv.id !== id)
        conversationStorage.save(updated)

        if (activeConversationId === id) {
          if (updated.length > 0) {
            setActiveConversationId(updated[0].id)
          } else {
            const newConversation = createNewConversation()
            setActiveConversationId(newConversation.id)
            conversationStorage.save([newConversation])
            return [newConversation]
          }
        }

        return updated
      })
    },
    [activeConversationId],
  )

  const renameConversation = useCallback(
    (id: string, newTitle: string): void => {
      setConversations((currentConversations) => {
        const updated = currentConversations.map((conv) =>
          conv.id === id
            ? {
                ...conv,
                title: newTitle,
                updatedAt: new Date().toISOString(),
              }
            : conv,
        )
        conversationStorage.save(updated)
        return updated
      })
    },
    [],
  )

  const setActiveConversation = useCallback((id: string): void => {
    setActiveConversationId(id)
  }, [])

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeConversationId) ?? null,
    [conversations, activeConversationId],
  )

  return {
    conversations,
    activeConversationId,
    activeConversation,
    createConversation,
    clearAllHistory,
    updateConversation,
    deleteConversation,
    renameConversation,
    setActiveConversation,
  }
}
