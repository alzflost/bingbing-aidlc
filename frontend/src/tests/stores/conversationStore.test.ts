import { describe, it, expect, beforeEach } from 'vitest'
import fc from 'fast-check'
import { useConversationStore } from '@/stores/conversationStore'
import type { ConversationMessage, QueuedUtterance } from '@/types'

describe('conversationStore', () => {
  beforeEach(() => {
    useConversationStore.setState({ messages: [], pendingQueue: [] })
  })

  describe('addMessage', () => {
    it('should append message to messages array', () => {
      const msg: ConversationMessage = {
        id: 'msg-1',
        type: 'utterance',
        actor_id: 'actor_father',
        text: '배고프다',
        timestamp: new Date().toISOString(),
      }
      useConversationStore.getState().addMessage(msg)
      expect(useConversationStore.getState().messages).toHaveLength(1)
      expect(useConversationStore.getState().messages[0]).toEqual(msg)
    })

    it('should preserve message order', () => {
      const msg1: ConversationMessage = {
        id: 'msg-1', type: 'utterance', actor_id: 'a1', text: 'first', timestamp: '2026-01-01T00:00:00Z',
      }
      const msg2: ConversationMessage = {
        id: 'msg-2', type: 'agent_response', actor_id: 'a1', text: 'second', timestamp: '2026-01-01T00:00:01Z',
      }
      useConversationStore.getState().addMessage(msg1)
      useConversationStore.getState().addMessage(msg2)
      const msgs = useConversationStore.getState().messages
      expect(msgs[0].id).toBe('msg-1')
      expect(msgs[1].id).toBe('msg-2')
    })
  })

  describe('pendingQueue', () => {
    it('should add and remove from queue', () => {
      const q: QueuedUtterance = {
        id: 'q-1', actor_id: 'actor_child', transcript: '만화 틀어줘', timestamp: new Date().toISOString(),
      }
      useConversationStore.getState().addToQueue(q)
      expect(useConversationStore.getState().pendingQueue).toHaveLength(1)

      useConversationStore.getState().removeFromQueue('q-1')
      expect(useConversationStore.getState().pendingQueue).toHaveLength(0)
    })

    it('removeFromQueue with non-existent id does nothing', () => {
      const q: QueuedUtterance = {
        id: 'q-1', actor_id: 'actor_child', transcript: 'test', timestamp: new Date().toISOString(),
      }
      useConversationStore.getState().addToQueue(q)
      useConversationStore.getState().removeFromQueue('non-existent')
      expect(useConversationStore.getState().pendingQueue).toHaveLength(1)
    })
  })

  describe('clearMessages', () => {
    it('should clear both messages and pendingQueue', () => {
      useConversationStore.getState().addMessage({
        id: 'msg-1', type: 'utterance', actor_id: 'a1', text: 'hi', timestamp: new Date().toISOString(),
      })
      useConversationStore.getState().addToQueue({
        id: 'q-1', actor_id: 'a1', transcript: 'hi', timestamp: new Date().toISOString(),
      })
      useConversationStore.getState().clearMessages()
      expect(useConversationStore.getState().messages).toHaveLength(0)
      expect(useConversationStore.getState().pendingQueue).toHaveLength(0)
    })
  })

  // PBT-06: Stateful — messages array grows monotonically
  describe('PBT: message ordering invariant', () => {
    it('messages array length always increases by 1 per addMessage', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.record({
              id: fc.uuid(),
              type: fc.constantFrom('utterance', 'agent_response') as fc.Arbitrary<'utterance' | 'agent_response'>,
              actor_id: fc.string({ minLength: 1, maxLength: 20 }),
              text: fc.string({ maxLength: 200 }),
              timestamp: fc.date().map((d) => d.toISOString()),
            }),
            { minLength: 1, maxLength: 50 }
          ),
          (messages) => {
            useConversationStore.setState({ messages: [], pendingQueue: [] })
            for (let i = 0; i < messages.length; i++) {
              useConversationStore.getState().addMessage(messages[i])
              expect(useConversationStore.getState().messages).toHaveLength(i + 1)
            }
          }
        )
      )
    })
  })
})
