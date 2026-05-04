import type { Conversation } from '../types/conversation'

const STORAGE_KEY = 'carbonrag-conversations'

export const conversationStorage = {
  save: (conversations: Conversation[]): void => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations))
    } catch (error) {
      console.error('Failed to save conversations to localStorage:', error)
    }
  },

  load: (): Conversation[] => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch (error) {
      console.error('Failed to load conversations from localStorage:', error)
      return []
    }
  },

  clear: (): void => {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch (error) {
      console.error('Failed to clear conversations from localStorage:', error)
    }
  },
}
