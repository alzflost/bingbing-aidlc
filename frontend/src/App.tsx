import { Header } from '@/components/Header'
import { SeatMap } from '@/components/SeatMap'
import { ConversationStream } from '@/components/ConversationStream'
import { ChatInput } from '@/components/ChatInput'
import { DriverAuth } from '@/components/DriverAuth'
import { PermissionDashboard } from '@/components/PermissionDashboard'
import { MemoryPanel } from '@/components/MemoryPanel'
import { EvaluationPanel } from '@/components/EvaluationPanel'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useTripStore } from '@/stores/tripStore'
import type { VehicleProfile } from '@/types'

const WS_URL = import.meta.env.DEV
  ? 'ws://localhost:8080/ws/trip'
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/trip`

export function App() {
  const { connected, send, sendTripStart, sendTripEnd } = useWebSocket(WS_URL)
  const tripState = useTripStore((s) => s.state)
  const startTrip = useTripStore((s) => s.startTrip)
  const endTrip = useTripStore((s) => s.endTrip)
  const setDriverActorId = useTripStore((s) => s.setDriverActorId)
  const setSeatOccupancy = useTripStore((s) => s.setSeatOccupancy)

  const handleDriverSelect = (profile: VehicleProfile) => {
    setDriverActorId(profile.actor_id)
    setSeatOccupancy(0, {
      actor_id: profile.actor_id,
      name: profile.name,
      role_attrs: {
        driver: true,
        age_group: profile.age_group,
        relationship: profile.relationship,
        account_owner: profile.account_owner,
      },
      seat_channel: 0,
    })
    sendTripStart(profile.vehicle_id, { 0: profile.actor_id }, profile.actor_id)
    useTripStore.getState().updateState('active')
  }

  const handleStartTrip = () => {
    startTrip('vehicle-demo-001', { 0: null, 1: null, 2: null, 3: null })
  }

  const handleEndTrip = () => {
    sendTripEnd()
    endTrip()
  }

  return (
    <div data-testid="app-root" className="h-screen flex flex-col bg-gray-900 text-white">
      <Header connected={connected} />

      <div className="flex-1 flex overflow-hidden">
        {/* Main Panel */}
        <main className="flex-1 flex flex-col p-4 gap-4 overflow-y-auto">
          {tripState === 'idle' && (
            <div className="flex items-center justify-center h-full">
              <button
                data-testid="start-trip-button"
                onClick={handleStartTrip}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors"
              >
                시동 ON (트립 시작)
              </button>
            </div>
          )}

          {tripState === 'onboarding' && <DriverAuth onSelect={handleDriverSelect} />}

          {(tripState === 'active' || tripState === 'trip_end') && (
            <>
              <SeatMap />
              <div className="flex-1 min-h-0">
                <ConversationStream />
              </div>
              {tripState === 'active' && (
                <>
                  <ChatInput send={send} />
                  <button
                    data-testid="end-trip-button"
                    onClick={handleEndTrip}
                    className="px-4 py-2 bg-red-700 hover:bg-red-600 rounded text-sm transition-colors self-end"
                  >
                    시동 OFF (트립 종료)
                  </button>
                </>
              )}
            </>
          )}
        </main>

        {/* Side Panel */}
        <aside className="w-72 border-l border-gray-700 p-4 overflow-y-auto space-y-6">
          <PermissionDashboard />
          <MemoryPanel />
          <EvaluationPanel />
        </aside>
      </div>
    </div>
  )
}
