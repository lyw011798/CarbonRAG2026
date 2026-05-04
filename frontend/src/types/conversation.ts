import type { ChatMessage } from './chat'

export interface Conversation {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

export type ConversationSummary = Omit<Conversation, 'messages'>
