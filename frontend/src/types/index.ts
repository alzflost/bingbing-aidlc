// Domain types mirroring shared Python models

export type AgeGroup = 'adult' | 'teen' | 'child' | 'elder'
export type Relationship = 'owner' | 'family' | 'guest'
export type MappingState = 'idle' | 'onboarding' | 'active' | 'trip_end'

export interface VehicleProfile {
  vehicle_id: string
  actor_id: string
  name: string
  age_group: AgeGroup
  relationship: Relationship
  account_owner: boolean
  default_seat_channel: number | null
  preferences_summary: string | null
}

export interface RoleAttributes {
  driver: boolean
  age_group: AgeGroup
  relationship: Relationship
  account_owner: boolean
}

export interface ActorInfo {
  actor_id: string
  name: string
  role_attrs: RoleAttributes
  seat_channel: number
}

export interface Utterance {
  utterance_id: string
  trip_id: string
  actor_id: string
  spk_label: string
  transcript: string
  timestamp: string
  seat_channel: number
  confidence: number
}

export interface PolicyDecision {
  allowed: boolean
  rule_id: string | null
  reason: string | null
  actor_id: string
  tool_name: string
}

export interface ResponseStyle {
  tone: string
  verbosity: string
  speech_rate: number
  honorific: string
  confirmation_required: boolean
}

export interface AgentResponse {
  response_id: string
  trip_id: string
  actor_id: string
  text: string
  tool_used: string | null
  tool_result: Record<string, unknown> | null
  policy_decision: PolicyDecision | null
  persona_style: ResponseStyle
  latency_ms: number
}

export interface ConversationMessage {
  id: string
  type: 'utterance' | 'agent_response'
  actor_id: string
  text: string
  timestamp: string
  policy_decision?: PolicyDecision | null
  tool_used?: string | null
}

export interface QueuedUtterance {
  id: string
  actor_id: string
  transcript: string
  timestamp: string
}

export interface PermissionSet {
  [tool_name: string]: 'allow' | 'deny' | 'conditional'
}

export interface MemorySnapshot {
  stm_count: number
  ltm_summary: string | null
  last_reflection: string | null
}

// WebSocket message types
export type WsMessageType =
  | 'trip_start'
  | 'trip_end'
  | 'audio_chunk'
  | 'transcription'
  | 'agent_response'
  | 'mapping_update'
  | 'state_update'
  | 'permission_update'
  | 'error'

export interface WsMessage {
  type: WsMessageType
  payload: Record<string, unknown>
}
