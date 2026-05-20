import { useTripStore } from '@/stores/tripStore'

interface HeaderProps {
  connected: boolean
}

const STATE_LABELS: Record<string, string> = {
  idle: '대기',
  onboarding: '탑승 중',
  active: '운행 중',
  trip_end: '트립 종료',
}

export function Header({ connected }: HeaderProps) {
  const state = useTripStore((s) => s.state)
  const tripId = useTripStore((s) => s.tripId)

  return (
    <header
      data-testid="app-header"
      className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700"
    >
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-bold">Family Car Agent</h1>
        <span data-testid="header-trip-state" className="text-xs px-2 py-0.5 rounded bg-gray-700 text-gray-300">
          {STATE_LABELS[state] ?? state}
        </span>
      </div>
      <div className="flex items-center gap-3 text-xs">
        {tripId && (
          <span data-testid="header-trip-id" className="text-gray-400 font-mono">
            {tripId.slice(0, 8)}
          </span>
        )}
        <span
          data-testid="header-connection-status"
          className={`flex items-center gap-1 ${connected ? 'text-green-400' : 'text-red-400'}`}
        >
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`} />
          {connected ? '연결됨' : '끊김'}
        </span>
      </div>
    </header>
  )
}
