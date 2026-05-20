import { useProfileStore } from '@/stores/profileStore'
import { useTripStore } from '@/stores/tripStore'

const TOOLS = ['navigation', 'vehicle_control', 'music', 'phone', 'web_search']

function PermIcon({ status }: { status: 'allow' | 'deny' | 'conditional' | undefined }) {
  if (status === 'allow') return <span className="text-green-400" aria-label="허용">✓</span>
  if (status === 'deny') return <span className="text-red-400" aria-label="차단">✗</span>
  if (status === 'conditional') return <span className="text-yellow-400" aria-label="조건부">◐</span>
  return <span className="text-gray-600" aria-label="미정의">—</span>
}

export function PermissionDashboard() {
  const currentPermissions = useProfileStore((s) => s.currentPermissions)
  const seatOccupancy = useTripStore((s) => s.seatOccupancy)

  const actors = Object.values(seatOccupancy).filter(Boolean)

  return (
    <section aria-label="권한 대시보드" data-testid="permission-dashboard">
      <h2 className="text-sm font-semibold text-gray-300 mb-2">권한 매트릭스</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-gray-400 border-b border-gray-700">
              <th className="text-left py-1 pr-2">탑승자</th>
              {TOOLS.map((t) => (
                <th key={t} className="px-1 py-1 text-center">{t.slice(0, 4)}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {actors.map((actor) => {
              if (!actor) return null
              const perms = currentPermissions[actor.actor_id]
              return (
                <tr
                  key={actor.actor_id}
                  data-testid={`permission-row-${actor.actor_id}`}
                  className="border-b border-gray-800"
                >
                  <td className="py-1 pr-2 font-medium">{actor.name}</td>
                  {TOOLS.map((tool) => (
                    <td
                      key={tool}
                      data-testid={`permission-cell-${actor.actor_id}-${tool}`}
                      className="text-center py-1"
                    >
                      <PermIcon status={perms?.[tool]} />
                    </td>
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
