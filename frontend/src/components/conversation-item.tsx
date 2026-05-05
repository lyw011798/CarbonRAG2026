import { useState } from "react";
import type { Conversation } from "../types/conversation";

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  isSummarizing?: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRename: (id: string, newTitle: string) => void;
  onSummary: (id: string) => void;
}

export const ConversationItem = ({
  conversation,
  isActive,
  isSummarizing = false,
  onSelect,
  onDelete,
  onRename,
  onSummary,
}: ConversationItemProps) => {
  const [isRenaming, setIsRenaming] = useState(false);
  const [editedTitle, setEditedTitle] = useState(conversation.title);

  const handleRenameStart = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsRenaming(true);
    setEditedTitle(conversation.title);
  };

  const handleRenameSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (editedTitle.trim()) {
      onRename(conversation.id, editedTitle.trim());
    }
    setIsRenaming(false);
  };

  const handleRenameCancel = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditedTitle(conversation.title);
    setIsRenaming(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleRenameSave(e as any);
    } else if (e.key === "Escape") {
      handleRenameCancel(e as any);
    }
  };

  const handleSummary = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Generate a summary?`)) {
      onSummary(conversation.id);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Delete conversation "${conversation.title}"?`)) {
      onDelete(conversation.id);
    }
  };

  return (
    <div
      onClick={() => onSelect(conversation.id)}
      className={`group flex items-center justify-between gap-2 rounded px-3 py-2 cursor-pointer transition-colors ${
        isActive ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-700"
      }`}
    >
      <div className="flex-1 min-w-0">
        {isRenaming ? (
          <input
            autoFocus
            type="text"
            value={editedTitle}
            onChange={(e) => setEditedTitle(e.target.value)}
            onKeyDown={handleKeyDown}
            onClick={(e) => e.stopPropagation()}
            className="w-full bg-gray-600 text-white px-2 py-1 rounded text-sm"
          />
        ) : (
          <div className="truncate text-sm">{conversation.title}</div>
        )}
      </div>

      <div
        className={`flex items-center gap-1 ${isRenaming ? "opacity-100" : "opacity-0 group-hover:opacity-100"} transition-opacity`}
      >
        {isRenaming ? (
          <>
            <button
              onClick={handleRenameSave}
              className="p-1 hover:bg-gray-600 rounded text-xs"
              title="Save"
            >
              ✓
            </button>
            <button
              onClick={handleRenameCancel}
              className="p-1 hover:bg-gray-600 rounded text-xs"
              title="Cancel"
            >
              ✕
            </button>
          </>
        ) : (
          <>
            {isSummarizing ? (
              <div className="p-1 text-cyan-400" title="Generating...">
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              </div>
            ) : (
              <button
                onClick={handleSummary}
                className="p-1 hover:bg-blue-900 rounded text-xs"
                title="Summary"
              >
                📚︎
              </button>
            )}
            <button
              onClick={handleRenameStart}
              className="p-1 hover:bg-gray-600 rounded text-xs"
              title="Rename"
            >
              ✎
            </button>
            <button
              onClick={handleDelete}
              className="p-1 hover:bg-red-600 rounded text-xs"
              title="Delete"
            >
              🗑
            </button>
          </>
        )}
      </div>
    </div>
  );
};
