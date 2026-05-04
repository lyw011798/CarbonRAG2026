export type ChatRole = 'user' | 'assistant'

export type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  createdAt: string
}

export type ApiChatMessage = {
  role: ChatRole
  content: string
}

export type ChatRequest = {
  messages: ApiChatMessage[]
}

export type ChatResponse = {
  message: ApiChatMessage
}
