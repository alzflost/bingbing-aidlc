import { useTripStore } from '@/stores/tripStore'
import type { ActorInfo } from '@/types'

const SEAT_LABELS = ['운전석', '조수석', '뒷좌석 L', '뒷좌석 R']

function SeatCard({ channel, actor }: { channel: number; actor: ActorInfo | null }) {
  const driverActorId = useTripStore((s) => s.driverActorId)
  const speakerMappings = useTripStore((s) => s.speakerMappings)

  const isDriver = actor?.actor_id === driverActorId
  const isSpeaking = actor && Object.values(speakerMappings).includes(actor.actor_id)

  const roleColor = actor
    ? actor.role_attrs.age_group === 'child'
      ? 'border-child'
      : actor.role_attrs.age_group === 'elder'
        ? 'border-elder'
        : actor.role_attrs.relationship === 'guest'
          ? 'border-guest'
          : 'border-driver'
    : 'border-gray-600'

  return (
    <div
      data-testid={`seat-card-${channel}`}
      className={`relative rounded-lg border-2 p-4 transition-all ${roleColor} ${
        isSpeaking ? 'ring-2 ring-yellow-400 shadow-lg' : ''
      } ${actor ? 'bg-gray-800' : 'bg-gray-900 opacity-50'}`}
    >
      <div className="text-xs text-gray-400 mb-1">{SEAT_LABELS[channel]}</div>
      {actor ? (
        <>
          <div data-testid={`seat-actor-name-${channel}`} className="font-semibold text-sm">
            {actor.name}
          </div>
          <div className="flex gap-1 mt-1 flex-wrap">
            <span
              data-testid={`seat-age-badge-${channel}`}
              className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700"
            >
              {actor.role_attrs.age_group}
            </span>
            <span
              data-testid={`seat-rel-badge-${channel}`}
              className="text-[10px] px-1.5 py-0.5 rounded bg-gray-700"
            >
              {actor.role_attrs.relationship}
            </span>
            {isDriver && (
              <span
                data-testid={`seat-driver-badge-${channel}`}
                className="text-[10px] px-1.5 py-0.5 rounded bg-blue-600"
              >
                driver
              </span>
            )}
          </div>
        </>
      ) : (
        <div data-testid={`seat-empty-${channel}`} className="text-gray-500 text-sm">
          비어있음
        </div>
      )}
    </div>
  )
}

export function SeatMap() {
  const seatOccupancy = useTripStore((s) => s.seatOccupancy)

  return (
    <section aria-label="좌석 배치도" data-testid="seat-map">
      <h2 className="text-sm font-semibold text-gray-300 mb-2">좌석 배치도</h2>
      <div className="grid grid-cols-2 gap-2">
        {[0, 1, 2, 3].map((ch) => (
          <SeatCard key={ch} channel={ch} actor={seatOccupancy[ch]} />
        ))}
      </div>
    </section>
  )
}
