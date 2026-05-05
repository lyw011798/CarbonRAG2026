import { useCallback } from 'react'
import { ChatHeader } from './chat-header'
import { ChatInput } from './chat-input'
import { MessageList } from './message-list'
import { ConversationSidebar } from './conversation-sidebar'
import { useChat } from '../hooks/use-chat'
import { useConversationHistory } from '../hooks/useConversationHistory'

export const ChatApp = () => {
  const {
    conversations,
    activeConversationId,
    activeConversation,
    summarizingId,
    createConversation,
    clearAllHistory,
    updateConversation,
    deleteConversation,
    renameConversation,
    summaryConversation,
    setActiveConversation,
  } = useConversationHistory()

  const handleMessagesChange = useCallback(
    (messages: any[]) => {
      if (activeConversationId) {
        updateConversation(activeConversationId, messages)
      }
    },
    [activeConversationId, updateConversation],
  )

  const { errorMessage, isLoading, submitMessage, clearError } = useChat({
      messages: activeConversation?.messages ?? [],
      onMessagesChange: handleMessagesChange,
    })

  return (
    <div className="flex h-screen bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.16),transparent_34%),linear-gradient(135deg,#020617_0%,#0f172a_52%,#111827_100%)]">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        summarizingId={summarizingId}
        onSelectConversation={setActiveConversation}
        onCreateConversation={createConversation}
        onClearAllHistory={clearAllHistory}
        onDeleteConversation={deleteConversation}
        onRenameConversation={renameConversation}
        onSummaryConversation={summaryConversation}
      />

      {/* Main Chat Area */}
      <main key={activeConversationId ?? 'no-conversation'} className="flex-1 flex flex-col min-w-0">
        <ChatHeader />
        <MessageList
          messages={activeConversation?.messages ?? []}
          isLoading={isLoading}
          errorMessage={errorMessage}
          onDismissError={clearError}
        />
        <ChatInput isLoading={isLoading} onSubmit={submitMessage} />
      </main>
    </div>
  )
}
