import { describe, it, expect } from 'vitest'
import fc from 'fast-check'
import {
  WsMessageSchema,
  ConversationMessageSchema,
  MappingUpdatePayloadSchema,
  StateUpdatePayloadSchema,
  PermissionUpdatePayloadSchema,
  VehicleProfileSchema,
  ActorInfoSchema,
} from '@/types/schemas'

// PBT-02: Round-trip property — serialize → parse = identity
describe('Zod Schema Validation (PBT-02: Round-trip)', () => {
  describe('WsMessageSchema', () => {
    it('rejects invalid message types', () => {
      const result = WsMessageSchema.safeParse({ type: 'invalid_type', payload: {} })
      expect(result.success).toBe(false)
    })

    it('accepts valid message types', () => {
      const validTypes = [
        'trip_start', 'trip_end', 'audio_chunk', 'transcription',
        'agent_response', 'mapping_update', 'state_update', 'permission_update', 'error',
      ]
      for (const type of validTypes) {
        const result = WsMessageSchema.safeParse({ type, payload: {} })
        expect(result.success).toBe(true)
      }
    })

    it('rejects missing payload', () => {
      const result = WsMessageSchema.safeParse({ type: 'trip_start' })
      expect(result.success).toBe(false)
    })
  })

  describe('ConversationMessageSchema round-trip', () => {
    it('parse(serialize(msg)) = msg for valid messages', () => {
      fc.assert(
        fc.property(
          fc.record({
            id: fc.uuid(),
            type: fc.constantFrom('utterance', 'agent_response') as fc.Arbitrary<'utterance' | 'agent_response'>,
            actor_id: fc.string({ minLength: 1, maxLength: 30 }),
            text: fc.string({ maxLength: 500 }),
            timestamp: fc.date().map((d) => d.toISOString()),
            policy_decision: fc.option(
              fc.record({
                allowed: fc.boolean(),
                rule_id: fc.option(fc.string({ minLength: 1 }), { nil: null }),
                reason: fc.option(fc.string({ minLength: 1 }), { nil: null }),
                actor_id: fc.string({ minLength: 1, maxLength: 30 }),
                tool_name: fc.string({ minLength: 1, maxLength: 30 }),
              }),
              { nil: undefined }
            ),
            tool_used: fc.option(fc.string({ minLength: 1 }), { nil: undefined }),
          }),
          (msg) => {
            const serialized = JSON.stringify(msg)
            const deserialized = JSON.parse(serialized)
            const result = ConversationMessageSchema.safeParse(deserialized)
            expect(result.success).toBe(true)
            if (result.success) {
              expect(result.data.id).toBe(msg.id)
              expect(result.data.type).toBe(msg.type)
              expect(result.data.actor_id).toBe(msg.actor_id)
              expect(result.data.text).toBe(msg.text)
            }
          }
        )
      )
    })
  })

  describe('MappingUpdatePayloadSchema', () => {
    it('rejects empty spk_label', () => {
      const result = MappingUpdatePayloadSchema.safeParse({ spk_label: '', actor_id: 'a1' })
      expect(result.success).toBe(false)
    })

    it('round-trip for valid payloads', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 10 }),
          fc.string({ minLength: 1, maxLength: 30 }),
          (spkLabel, actorId) => {
            const payload = { spk_label: spkLabel, actor_id: actorId }
            const serialized = JSON.stringify(payload)
            const result = MappingUpdatePayloadSchema.safeParse(JSON.parse(serialized))
            expect(result.success).toBe(true)
            if (result.success) {
              expect(result.data).toEqual(payload)
            }
          }
        )
      )
    })
  })

  describe('StateUpdatePayloadSchema', () => {
    it('rejects invalid states', () => {
      const result = StateUpdatePayloadSchema.safeParse({ state: 'invalid' })
      expect(result.success).toBe(false)
    })

    it('accepts all valid states', () => {
      for (const state of ['idle', 'onboarding', 'active', 'trip_end']) {
        const result = StateUpdatePayloadSchema.safeParse({ state })
        expect(result.success).toBe(true)
      }
    })
  })

  describe('PermissionUpdatePayloadSchema', () => {
    it('rejects invalid permission values', () => {
      const result = PermissionUpdatePayloadSchema.safeParse({
        actor_id: 'a1',
        permissions: { navigation: 'invalid_value' },
      })
      expect(result.success).toBe(false)
    })

    it('round-trip for valid permission updates', () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 20 }),
          fc.dictionary(
            fc.constantFrom('navigation', 'vehicle_control', 'music', 'phone', 'web_search'),
            fc.constantFrom('allow', 'deny', 'conditional')
          ),
          (actorId, permissions) => {
            const payload = { actor_id: actorId, permissions }
            const serialized = JSON.stringify(payload)
            const result = PermissionUpdatePayloadSchema.safeParse(JSON.parse(serialized))
            expect(result.success).toBe(true)
            if (result.success) {
              expect(result.data.actor_id).toBe(actorId)
            }
          }
        )
      )
    })
  })

  describe('VehicleProfileSchema', () => {
    it('rejects invalid age_group', () => {
      const result = VehicleProfileSchema.safeParse({
        vehicle_id: 'v1',
        actor_id: 'a1',
        name: 'Test',
        age_group: 'baby',
        relationship: 'owner',
        account_owner: true,
        default_seat_channel: 0,
        preferences_summary: null,
      })
      expect(result.success).toBe(false)
    })

    it('rejects seat_channel > 3', () => {
      const result = VehicleProfileSchema.safeParse({
        vehicle_id: 'v1',
        actor_id: 'a1',
        name: 'Test',
        age_group: 'adult',
        relationship: 'owner',
        account_owner: true,
        default_seat_channel: 5,
        preferences_summary: null,
      })
      expect(result.success).toBe(false)
    })
  })

  describe('ActorInfoSchema', () => {
    it('round-trip for valid actor info', () => {
      fc.assert(
        fc.property(
          fc.record({
            actor_id: fc.string({ minLength: 1, maxLength: 30 }),
            name: fc.string({ minLength: 1, maxLength: 30 }),
            role_attrs: fc.record({
              driver: fc.boolean(),
              age_group: fc.constantFrom('adult', 'teen', 'child', 'elder'),
              relationship: fc.constantFrom('owner', 'family', 'guest'),
              account_owner: fc.boolean(),
            }),
            seat_channel: fc.integer({ min: 0, max: 3 }),
          }),
          (actor) => {
            const serialized = JSON.stringify(actor)
            const result = ActorInfoSchema.safeParse(JSON.parse(serialized))
            expect(result.success).toBe(true)
            if (result.success) {
              expect(result.data).toEqual(actor)
            }
          }
        )
      )
    })
  })
})
