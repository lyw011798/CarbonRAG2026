import { ChatHeader } from './chat-header'
import { ChatInput } from './chat-input'
import { MessageList } from './message-list'
import { useChat } from '../hooks/use-chat'

export const ChatApp = () => {
  const { messages, errorMessage, isLoading, submitMessage, clearError } = useChat()

  return (
    <main className="flex min-h-svh flex-col bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.16),transparent_34%),linear-gradient(135deg,#020617_0%,#0f172a_52%,#111827_100%)]">
      <ChatHeader />
      <MessageList
        messages={messages}
        isLoading={isLoading}
        errorMessage={errorMessage}
        onDismissError={clearError}
      />
      <ChatInput isLoading={isLoading} onSubmit={submitMessage} />
    </main>
  )
}
