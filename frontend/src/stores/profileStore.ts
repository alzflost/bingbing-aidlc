import { create } from 'zustand'
import type { VehicleProfile, PermissionSet, MemorySnapshot } from '@/types'

const DEMO_PROFILES: VehicleProfile[] = [
  {
    vehicle_id: 'vehicle-demo-001',
    actor_id: 'actor_father',
    name: '아빠',
    age_group: 'adult',
    relationship: 'owner',
    account_owner: true,
    default_seat_channel: 0,
    preferences_summary: null,
  },
  {
    vehicle_id: 'vehicle-demo-001',
    actor_id: 'actor_mother',
    name: '엄마',
    age_group: 'adult',
    relationship: 'family',
    account_owner: false,
    default_seat_channel: 1,
    preferences_summary: null,
  },
  {
    vehicle_id: 'vehicle-demo-001',
    actor_id: 'actor_child_1',
    name: '민수',
    age_group: 'child',
    relationship: 'family',
    account_owner: false,
    default_seat_channel: 2,
    preferences_summary: null,
  },
  {
    vehicle_id: 'vehicle-demo-001',
    actor_id: 'actor_elder_1',
    name: '할머니',
    age_group: 'elder',
    relationship: 'family',
    account_owner: false,
    default_seat_channel: 3,
    preferences_summary: null,
  },
]

interface ProfileState {
  vehicleProfiles: VehicleProfile[]
  currentPermissions: Record<string, PermissionSet>
  memoryState: Record<string, MemorySnapshot>

  loadProfiles: (profiles: VehicleProfile[]) => void
  updatePermissions: (actorId: string, perms: PermissionSet) => void
  updateMemory: (actorId: string, snapshot: MemorySnapshot) => void
}

export const useProfileStore = create<ProfileState>((set) => ({
  vehicleProfiles: DEMO_PROFILES,
  currentPermissions: {},
  memoryState: {},

  loadProfiles: (profiles) => set({ vehicleProfiles: profiles }),

  updatePermissions: (actorId, perms) =>
    set((s) => ({
      currentPermissions: { ...s.currentPermissions, [actorId]: perms },
    })),

  updateMemory: (actorId, snapshot) =>
    set((s) => ({
      memoryState: { ...s.memoryState, [actorId]: snapshot },
    })),
}))
