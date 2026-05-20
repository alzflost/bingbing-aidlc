import { useProfileStore } from '@/stores/profileStore'
import { useTripStore } from '@/stores/tripStore'

export function MemoryPanel() {
  const memoryState = useProfileStore((s) => s.memoryState)
  const seatOccupancy = useTripStore((s) => s.seatOccupancy)

  const actors = Object.values(seatOccupancy).filter(Boolean)

  return (
    <section aria-label="메모리 상태" data-testid="memory-panel">
      <h2 className="text-sm font-semibold text-gray-300 mb-2">메모리 (STM / LTM)</h2>
      <div className="space-y-2">
        {actors.map((actor) => {
          if (!actor) return null
          const mem = memoryState[actor.actor_id]
          return (
            <div
              key={actor.actor_id}
              data-testid={`memory-card-${actor.actor_id}`}
              className="bg-gray-800 rounded p-2"
            >
              <div className="text-xs font-medium">{actor.name}</div>
              <div className="text-[10px] text-gray-400 mt-0.5">
                STM: {mem?.stm_count ?? 0}건
              </div>
              {mem?.ltm_summary && (
                <div className="text-[10px] text-gray-400 mt-0.5 truncate">
                  LTM: {mem.ltm_summary}
                </div>
              )}
              {mem?.last_reflection && (
                <div className="text-[10px] text-purple-400 mt-0.5">
                  Reflection: {mem.last_reflection}
                </div>
              )}
            </div>
          )
        })}
        {actors.length === 0 && (
          <div data-testid="memory-panel-empty" className="text-xs text-gray-500">
            탑승자 없음
          </div>
        )}
      </div>
    </section>
  )
}
