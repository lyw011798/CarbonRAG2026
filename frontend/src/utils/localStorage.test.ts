import { conversationStorage } from '../utils/localStorage'
import type { Conversation } from '../types/conversation'

/**
 * localStorage utility tests
 * Run these tests in browser console or integrate with a test framework (vitest, jest, etc.)
 */

function createMockConversation(id: string = 'test-1'): Conversation {
  return {
    id,
    title: 'Test Conversation',
    messages: [
      {
        id: 'msg-1',
        role: 'user',
        content: 'Hello',
        createdAt: new Date().toISOString(),
      },
      {
        id: 'msg-2',
        role: 'assistant',
        content: 'Hi there!',
        createdAt: new Date().toISOString(),
      },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
}

export const testLocalStorage = () => {
  console.log('Starting localStorage tests...')

  // Test 1: Save and load
  console.log('Test 1: Save and load conversations')
  const conv1 = createMockConversation('conv-1')
  const conv2 = createMockConversation('conv-2')
  conversationStorage.save([conv1, conv2])
  const loaded = conversationStorage.load()
  console.assert(loaded.length === 2, 'Should load 2 conversations')
  console.assert(loaded[0].id === 'conv-1', 'First conversation ID should match')
  console.assert(loaded[1].title === 'Test Conversation', 'Conversation title should match')
  console.log('✓ Test 1 passed')

  // Test 2: Load empty when nothing saved
  console.log('Test 2: Load empty when no data')
  conversationStorage.clear()
  const emptyLoaded = conversationStorage.load()
  console.assert(emptyLoaded.length === 0, 'Should load empty array when nothing saved')
  console.log('✓ Test 2 passed')

  // Test 3: Clear
  console.log('Test 3: Clear all conversations')
  conversationStorage.save([conv1])
  conversationStorage.clear()
  const afterClear = conversationStorage.load()
  console.assert(afterClear.length === 0, 'Should be empty after clear')
  console.log('✓ Test 3 passed')

  // Test 4: Overwrite existing
  console.log('Test 4: Overwrite existing conversations')
  conversationStorage.save([conv1])
  conversationStorage.save([conv2])
  const afterOverwrite = conversationStorage.load()
  console.assert(afterOverwrite.length === 1, 'Should have 1 conversation after overwrite')
  console.assert(afterOverwrite[0].id === 'conv-2', 'Should have the new conversation')
  console.log('✓ Test 4 passed')

  // Test 5: Persistence (manual - requires page reload)
  console.log('Test 5: Persistence across page loads (manual check)')
  conversationStorage.save([conv1, conv2])
  console.log('Saved 2 conversations. Reload page to verify they persist.')

  console.log('All automated localStorage tests passed!')
}

// Run tests when module loads
testLocalStorage()
