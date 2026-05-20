import { describe, it, expect, beforeEach } from 'vitest'
import fc from 'fast-check'
import { useTripStore } from '@/stores/tripStore'
import type { ActorInfo } from '@/types'

describe('tripStore', () => {
  beforeEach(() => {
    useTripStore.setState({
      tripId: null,
      vehicleId: '',
      state: 'idle',
      seatOccupancy: { 0: null, 1: null, 2: null, 3: null },
      driverActorId: null,
      speakerMappings: {},
    })
  })

  // Example-based tests
  describe('startTrip', () => {
    it('should transition from idle to onboarding with a tripId', () => {
      useTripStore.getState().startTrip('vehicle-1', { 0: null, 1: null, 2: null, 3: null })

      const state = useTripStore.getState()
      expect(state.tripId).toBeTruthy()
      expect(state.vehicleId).toBe('vehicle-1')
      expect(state.state).toBe('onboarding')
      expect(state.speakerMappings).toEqual({})
    })
  })

  describe('endTrip', () => {
    it('should transition to trip_end and clear mappings', () => {
      useTripStore.getState().startTrip('vehicle-1', { 0: null, 1: null, 2: null, 3: null })
      useTripStore.getState().updateMapping('spk_0', 'actor_father')
      useTripStore.getState().endTrip()

      const state = useTripStore.getState()
      expect(state.tripId).toBeNull()
      expect(state.state).toBe('trip_end')
      expect(state.driverActorId).toBeNull()
      expect(state.speakerMappings).toEqual({})
    })
  })

  describe('updateMapping', () => {
    it('should add speaker mapping', () => {
      useTripStore.getState().updateMapping('spk_0', 'actor_father')
      expect(useTripStore.getState().speakerMappings).toEqual({ spk_0: 'actor_father' })
    })

    it('should overwrite existing mapping for same spk_label', () => {
      useTripStore.getState().updateMapping('spk_0', 'actor_father')
      useTripStore.getState().updateMapping('spk_0', 'actor_mother')
      expect(useTripStore.getState().speakerMappings.spk_0).toBe('actor_mother')
    })
  })

  describe('setSeatOccupancy', () => {
    it('should set actor at specific channel', () => {
      const actor: ActorInfo = {
        actor_id: 'actor_father',
        name: '아빠',
        role_attrs: { driver: true, age_group: 'adult', relationship: 'owner', account_owner: true },
        seat_channel: 0,
      }
      useTripStore.getState().setSeatOccupancy(0, actor)
      expect(useTripStore.getState().seatOccupancy[0]).toEqual(actor)
    })
  })

  // PBT-06: Stateful property — state transitions
  describe('PBT: state transitions', () => {
    const validStates = ['idle', 'onboarding', 'active', 'trip_end'] as const

    it('updateState always results in a valid MappingState', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(...validStates),
          (newState) => {
            useTripStore.getState().updateState(newState)
            expect(validStates).toContain(useTripStore.getState().state)
          }
        )
      )
    })

    it('speakerMappings: same spk_label always maps to same actor_id (last write wins)', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 10 }),
          fc.string({ minLength: 1, maxLength: 20 }),
          (spkLabel, actorId) => {
            useTripStore.getState().updateMapping(spkLabel, actorId)
            expect(useTripStore.getState().speakerMappings[spkLabel]).toBe(actorId)
          }
        )
      )
    })
  })

  // PBT-03: Invariant — seat occupancy always has exactly 4 channels
  describe('PBT: seat occupancy invariant', () => {
    it('seatOccupancy always has channels 0-3', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 0, max: 3 }),
          fc.option(
            fc.record({
              actor_id: fc.string({ minLength: 1 }),
              name: fc.string({ minLength: 1 }),
              role_attrs: fc.record({
                driver: fc.boolean(),
                age_group: fc.constantFrom('adult', 'teen', 'child', 'elder'),
                relationship: fc.constantFrom('owner', 'family', 'guest'),
                account_owner: fc.boolean(),
              }),
              seat_channel: fc.integer({ min: 0, max: 3 }),
            }),
            { nil: null }
          ),
          (channel, actor) => {
            useTripStore.getState().setSeatOccupancy(channel, actor as ActorInfo | null)
            const occ = useTripStore.getState().seatOccupancy
            expect(Object.keys(occ).map(Number).sort()).toEqual([0, 1, 2, 3])
          }
        )
      )
    })
  })
})
