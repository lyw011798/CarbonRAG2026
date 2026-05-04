import { useState, useMemo } from 'react'
import type { Conversation } from '../types/conversation'
import { ConversationItem } from './conversation-item'

interface ConversationSidebarProps {
  conversations: Conversation[]
  activeConversationId: string | null
  onSelectConversation: (id: string) => void
  onCreateConversation: () => void
  onClearAllHistory: () => void
  onDeleteConversation: (id: string) => void
  onRenameConversation: (id: string, newTitle: string) => void
}

export const ConversationSidebar = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onClearAllHistory,
  onDeleteConversation,
  onRenameConversation,
}: ConversationSidebarProps) => {
  const [searchQuery, setSearchQuery] = useState('')

  // Sort by updatedAt descending, then filter by search query
  const filteredConversations = useMemo(() => {
    const sorted = [...conversations].sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    )

    if (!searchQuery.trim()) {
      return sorted
    }

    const query = searchQuery.toLowerCase()
    return sorted.filter((conv) =>
      conv.title.toLowerCase().includes(query),
    )
  }, [conversations, searchQuery])

  return (
    <div className="w-64 bg-gradient-to-b from-slate-900 to-slate-950 border-r border-slate-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <button
          onClick={onCreateConversation}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors text-sm"
        >
          <span>+</span>
          <span>New Chat</span>
        </button>
        <button
          onClick={() => {
            if (window.confirm('Clear all chat history? This cannot be undone.')) {
              onClearAllHistory()
            }
          }}
          className="mt-2 w-full flex items-center justify-center gap-2 px-3 py-2 rounded border border-red-500/40 bg-red-500/10 text-red-200 hover:bg-red-500/20 hover:border-red-400 transition-colors text-sm font-medium"
          title="Clear all history"
        >
          <span>Clear All History</span>
        </button>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-slate-700">
        <input
          type="text"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 rounded bg-slate-800 text-gray-200 text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {filteredConversations.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">
            {conversations.length === 0
              ? 'No conversations yet'
              : 'No conversations found'}
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {filteredConversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === activeConversationId}
                onSelect={onSelectConversation}
                onDelete={onDeleteConversation}
                onRename={onRenameConversation}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
