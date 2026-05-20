import { describe, it, expect, beforeEach } from 'vitest'
import fc from 'fast-check'
import { useProfileStore } from '@/stores/profileStore'
import type { VehicleProfile, PermissionSet, MemorySnapshot } from '@/types'

describe('profileStore', () => {
  beforeEach(() => {
    useProfileStore.setState({
      vehicleProfiles: [],
      currentPermissions: {},
      memoryState: {},
    })
  })

  describe('loadProfiles', () => {
    it('should replace vehicleProfiles', () => {
      const profiles: VehicleProfile[] = [
        {
          vehicle_id: 'v1',
          actor_id: 'actor_father',
          name: '아빠',
          age_group: 'adult',
          relationship: 'owner',
          account_owner: true,
          default_seat_channel: 0,
          preferences_summary: '고기 선호',
        },
      ]
      useProfileStore.getState().loadProfiles(profiles)
      expect(useProfileStore.getState().vehicleProfiles).toEqual(profiles)
    })
  })

  describe('updatePermissions', () => {
    it('should set permissions for actor', () => {
      const perms: PermissionSet = {
        navigation: 'allow',
        vehicle_control: 'allow',
        music: 'allow',
        phone: 'allow',
        web_search: 'allow',
      }
      useProfileStore.getState().updatePermissions('actor_father', perms)
      expect(useProfileStore.getState().currentPermissions['actor_father']).toEqual(perms)
    })

    it('should not affect other actors permissions', () => {
      const perms1: PermissionSet = { navigation: 'allow' }
      const perms2: PermissionSet = { navigation: 'deny' }
      useProfileStore.getState().updatePermissions('actor_father', perms1)
      useProfileStore.getState().updatePermissions('actor_child', perms2)
      expect(useProfileStore.getState().currentPermissions['actor_father']).toEqual(perms1)
      expect(useProfileStore.getState().currentPermissions['actor_child']).toEqual(perms2)
    })
  })

  describe('updateMemory', () => {
    it('should set memory snapshot for actor', () => {
      const snapshot: MemorySnapshot = {
        stm_count: 5,
        ltm_summary: '비건 선호',
        last_reflection: '2026-05-20',
      }
      useProfileStore.getState().updateMemory('actor_mother', snapshot)
      expect(useProfileStore.getState().memoryState['actor_mother']).toEqual(snapshot)
    })
  })

  // PBT: permissions update is idempotent (PBT-04)
  describe('PBT: permissions idempotency', () => {
    it('setting same permissions twice yields same state', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 20 }),
          fc.dictionary(
            fc.constantFrom('navigation', 'vehicle_control', 'music', 'phone', 'web_search'),
            fc.constantFrom('allow', 'deny', 'conditional') as fc.Arbitrary<'allow' | 'deny' | 'conditional'>
          ),
          (actorId, perms) => {
            useProfileStore.setState({ currentPermissions: {} })
            useProfileStore.getState().updatePermissions(actorId, perms)
            const state1 = { ...useProfileStore.getState().currentPermissions }
            useProfileStore.getState().updatePermissions(actorId, perms)
            const state2 = { ...useProfileStore.getState().currentPermissions }
            expect(state1).toEqual(state2)
          }
        )
      )
    })
  })
})
