import { create } from 'zustand'
import type { VehicleProfile, PermissionSet, MemorySnapshot } from '@/types'

interface ProfileState {
  vehicleProfiles: VehicleProfile[]
  currentPermissions: Record<string, PermissionSet>
  memoryState: Record<string, MemorySnapshot>

  loadProfiles: (profiles: VehicleProfile[]) => void
  updatePermissions: (actorId: string, perms: PermissionSet) => void
  updateMemory: (actorId: string, snapshot: MemorySnapshot) => void
}

export const useProfileStore = create<ProfileState>((set) => ({
  vehicleProfiles: [],
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
