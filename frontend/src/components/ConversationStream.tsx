import { useRef, useEffect } from 'react'
import { useConversationStore } from '@/stores/conversationStore'
import { useTripStore } from '@/stores/tripStore'
import type { ConversationMessage, ActorInfo } from '@/types'

function getActorColor(
  actorId: string,
  seatOccupancy: Record<number, ActorInfo | null>
): string {
  for (const seat of Object.values(seatOccupancy)) {
    if (seat?.actor_id === actorId) {
      if (seat.role_attrs.age_group === 'child') return 'text-child'
      if (seat.role_attrs.age_group === 'elder') return 'text-elder'
      if (seat.role_attrs.relationship === 'guest') return 'text-guest'
      return 'text-driver'
    }
  }
  return 'text-gray-300'
}

function MessageBubble({ msg }: { msg: ConversationMessage }) {
  const seatOccupancy = useTripStore((s) => s.seatOccupancy)
  const isAgent = msg.type === 'agent_response'
  const blocked = msg.policy_decision && !msg.policy_decision.allowed

  const color = isAgent ? 'text-gray-100' : getActorColor(msg.actor_id, seatOccupancy)

  return (
    <div
      data-testid={`message-bubble-${msg.id}`}
      className={`flex flex-col gap-0.5 ${isAgent ? 'items-start' : 'items-end'}`}
    >
      <div
        className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
          isAgent ? 'bg-gray-700' : 'bg-gray-800'
        }`}
      >
        <span className={`font-medium text-xs ${color}`}>
          {isAgent ? '🤖 Agent' : msg.actor_id}
        </span>
        <p className="mt-0.5 text-gray-100">{msg.text}</p>
        {blocked && (
          <span
            data-testid={`message-blocked-${msg.id}`}
            className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-red-900 text-red-300"
          >
            차단: {msg.policy_decision?.reason}
          </span>
        )}
        {msg.tool_used && (
          <span
            data-testid={`message-tool-${msg.id}`}
            className="inline-block mt-1 text-[10px] px-1.5 py-0.5 rounded bg-indigo-900 text-indigo-300"
          >
            🔧 {msg.tool_used}
          </span>
        )}
      </div>
      <span className="text-[10px] text-gray-500 px-1">
        {new Date(msg.timestamp).toLocaleTimeString('ko-KR')}
      </span>
    </div>
  )
}

export function ConversationStream() {
  const messages = useConversationStore((s) => s.messages)
  const pendingQueue = useConversationStore((s) => s.pendingQueue)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <section aria-label="대화 스트림" data-testid="conversation-stream" className="flex flex-col h-full">
      <h2 className="text-sm font-semibold text-gray-300 mb-2">대화</h2>
      <div className="flex-1 overflow-y-auto space-y-2 pr-1">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}
        {pendingQueue.length > 0 && (
          <div data-testid="conversation-pending-queue" className="text-xs text-gray-500 italic">
            대기 중: {pendingQueue.map((q) => q.actor_id).join(', ')}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </section>
  )
}
