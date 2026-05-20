import { useTripStore } from '@/stores/tripStore'
import { useProfileStore } from '@/stores/profileStore'
import type { VehicleProfile } from '@/types'

interface DriverAuthProps {
  onSelect: (profile: VehicleProfile) => void
}

export function DriverAuth({ onSelect }: DriverAuthProps) {
  const state = useTripStore((s) => s.state)
  const vehicleProfiles = useProfileStore((s) => s.vehicleProfiles)

  if (state !== 'onboarding') return null

  return (
    <section aria-label="운전자 인증" data-testid="driver-auth" className="bg-gray-800 rounded-lg p-4">
      <h2 className="text-sm font-semibold text-gray-300 mb-3">운전자를 선택하세요</h2>
      <div className="grid grid-cols-2 gap-2">
        {vehicleProfiles.map((profile) => (
          <button
            key={profile.actor_id}
            data-testid={`driver-auth-profile-${profile.actor_id}`}
            onClick={() => onSelect(profile)}
            className="rounded-lg border border-gray-600 p-3 text-left hover:border-blue-400 hover:bg-gray-700 transition-colors"
          >
            <div className="font-medium text-sm">{profile.name}</div>
            <div className="text-xs text-gray-400 mt-0.5">
              {profile.age_group} · {profile.relationship}
            </div>
          </button>
        ))}
      </div>
    </section>
  )
}
