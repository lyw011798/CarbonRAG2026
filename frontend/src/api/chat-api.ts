import type { ApiChatMessage, ChatRequest, ChatResponse } from '../types/chat'

const CHAT_PATH = '/chat'

export class ChatApiError extends Error {
  readonly status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ChatApiError'
    this.status = status
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const isApiChatMessage = (value: unknown): value is ApiChatMessage =>
  isRecord(value) &&
  (value.role === 'assistant' || value.role === 'user') &&
  typeof value.content === 'string' &&
  value.content.trim().length > 0

const getChatEndpoint = (): string => {
  const apiBaseUrl = import.meta.env.VITE_CHAT_API_BASE_URL?.trim()

  if (!apiBaseUrl) {
    return CHAT_PATH
  }

  return `${apiBaseUrl.replace(/\/+$/, '')}${CHAT_PATH}`
}

const readErrorDetail = async (response: Response): Promise<string> => {
  try {
    const body = await response.json()

    if (isRecord(body) && typeof body.error === 'string' && body.error.trim()) {
      return body.error.trim()
    }

    if (isRecord(body) && typeof body.message === 'string' && body.message.trim()) {
      return body.message.trim()
    }
  } catch (error) {
    if (error instanceof SyntaxError) {
      return response.statusText || 'The server returned an unreadable error response.'
    }

    throw new ChatApiError('The chat error response could not be read.')
  }

  return response.statusText || 'The server returned an error response.'
}

export const sendChatMessage = async (
  messages: ApiChatMessage[],
  signal?: AbortSignal,
): Promise<ApiChatMessage> => {
  const requestBody: ChatRequest = { messages }

  try {
    const response = await fetch(getChatEndpoint(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      signal,
    })

    if (!response.ok) {
      const detail = await readErrorDetail(response)
      throw new ChatApiError(`Chat request failed (${response.status}): ${detail}`, response.status)
    }

    const body: unknown = await response.json()

    if (!isRecord(body) || !isApiChatMessage(body.message)) {
      throw new ChatApiError(
        'The chat response could not be read because it did not include a valid assistant message.',
      )
    }

    const chatResponse: ChatResponse = { message: body.message }

    if (chatResponse.message.role !== 'assistant') {
      throw new ChatApiError('The chat response could not be read because the returned role was not assistant.')
    }

    return chatResponse.message
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error
    }

    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ChatApiError('The chat request was cancelled before it completed.')
    }

    throw new ChatApiError('Unable to reach the chat API. Check your connection and try again.')
  }
}
