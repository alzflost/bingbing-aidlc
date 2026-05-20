import { create } from 'zustand'
import type { ConversationMessage, QueuedUtterance } from '@/types'

interface ConversationState {
  messages: ConversationMessage[]
  pendingQueue: QueuedUtterance[]

  addMessage: (msg: ConversationMessage) => void
  addToQueue: (utterance: QueuedUtterance) => void
  removeFromQueue: (id: string) => void
  clearMessages: () => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  messages: [],
  pendingQueue: [],

  addMessage: (msg) =>
    set((s) => ({ messages: [...s.messages, msg] })),

  addToQueue: (utterance) =>
    set((s) => ({ pendingQueue: [...s.pendingQueue, utterance] })),

  removeFromQueue: (id) =>
    set((s) => ({ pendingQueue: s.pendingQueue.filter((u) => u.id !== id) })),

  clearMessages: () => set({ messages: [], pendingQueue: [] }),
}))
