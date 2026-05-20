import { create } from 'zustand'
import type { ActorInfo, MappingState } from '@/types'

interface TripState {
  tripId: string | null
  vehicleId: string
  state: MappingState
  seatOccupancy: Record<number, ActorInfo | null>
  driverActorId: string | null
  speakerMappings: Record<string, string>

  startTrip: (vehicleId: string, seatData: Record<number, ActorInfo | null>) => void
  endTrip: () => void
  updateMapping: (spkLabel: string, actorId: string) => void
  updateState: (state: MappingState) => void
  setSeatOccupancy: (channel: number, actor: ActorInfo | null) => void
  setDriverActorId: (actorId: string) => void
}

export const useTripStore = create<TripState>((set) => ({
  tripId: null,
  vehicleId: '',
  state: 'idle',
  seatOccupancy: { 0: null, 1: null, 2: null, 3: null },
  driverActorId: null,
  speakerMappings: {},

  startTrip: (vehicleId, seatData) =>
    set({
      tripId: crypto.randomUUID(),
      vehicleId,
      state: 'onboarding',
      seatOccupancy: seatData,
      speakerMappings: {},
    }),

  endTrip: () =>
    set({
      tripId: null,
      state: 'trip_end',
      driverActorId: null,
      speakerMappings: {},
    }),

  updateMapping: (spkLabel, actorId) =>
    set((s) => ({
      speakerMappings: { ...s.speakerMappings, [spkLabel]: actorId },
    })),

  updateState: (state) => set({ state }),

  setSeatOccupancy: (channel, actor) =>
    set((s) => ({
      seatOccupancy: { ...s.seatOccupancy, [channel]: actor },
    })),

  setDriverActorId: (actorId) => set({ driverActorId: actorId }),
}))
