import { z } from 'zod'

// SECURITY-05: Zod runtime validation for all incoming WebSocket messages

export const AgeGroupSchema = z.enum(['adult', 'teen', 'child', 'elder'])
export const RelationshipSchema = z.enum(['owner', 'family', 'guest'])
export const MappingStateSchema = z.enum(['idle', 'onboarding', 'active', 'trip_end'])

export const RoleAttributesSchema = z.object({
  driver: z.boolean(),
  age_group: AgeGroupSchema,
  relationship: RelationshipSchema,
  account_owner: z.boolean(),
})

export const ActorInfoSchema = z.object({
  actor_id: z.string().min(1),
  name: z.string().min(1),
  role_attrs: RoleAttributesSchema,
  seat_channel: z.number().int().min(0).max(3),
})

export const PolicyDecisionSchema = z.object({
  allowed: z.boolean(),
  rule_id: z.string().nullable(),
  reason: z.string().nullable(),
  actor_id: z.string().min(1),
  tool_name: z.string().min(1),
})

export const ConversationMessageSchema = z.object({
  id: z.string().min(1),
  type: z.enum(['utterance', 'agent_response']),
  actor_id: z.string().min(1),
  text: z.string(),
  timestamp: z.string(),
  policy_decision: PolicyDecisionSchema.nullable().optional(),
  tool_used: z.string().nullable().optional(),
})

export const WsMessageSchema = z.object({
  type: z.enum([
    'trip_start',
    'trip_end',
    'audio_chunk',
    'transcription',
    'agent_response',
    'mapping_update',
    'state_update',
    'permission_update',
    'error',
  ]),
  payload: z.record(z.unknown()),
})

export const MappingUpdatePayloadSchema = z.object({
  spk_label: z.string().min(1),
  actor_id: z.string().min(1),
})

export const StateUpdatePayloadSchema = z.object({
  state: MappingStateSchema,
})

export const PermissionUpdatePayloadSchema = z.object({
  actor_id: z.string().min(1),
  permissions: z.record(z.enum(['allow', 'deny', 'conditional'])),
})

export const VehicleProfileSchema = z.object({
  vehicle_id: z.string().min(1),
  actor_id: z.string().min(1),
  name: z.string().min(1),
  age_group: AgeGroupSchema,
  relationship: RelationshipSchema,
  account_owner: z.boolean(),
  default_seat_channel: z.number().int().min(0).max(3).nullable(),
  preferences_summary: z.string().nullable(),
})
