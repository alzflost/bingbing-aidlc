# Component Methods

> Note: 상세 비즈니스 로직은 Functional Design (CONSTRUCTION) 단계에서 정의.
> 여기서는 메서드 시그니처와 고수준 목적만 정의.

---

## C1: Voice Ingestion

```python
class VoiceIngestion:
    async def start_stream(trip_id: str, seat_channels: dict) -> StreamSession
    async def receive_audio_chunk(session_id: str, audio_data: bytes, channel: int) -> None
    async def get_transcription_result(session_id: str) -> TranscriptionEvent
    async def stop_stream(session_id: str) -> None
    async def switch_to_fallback(session_id: str, audio_file: str) -> None
```

## C2: Speaker Mapping

```python
class SpeakerMapping:
    async def initialize_trip(trip_id: str, seat_occupancy: dict) -> MappingState
    async def map_speaker(trip_id: str, spk_label: str, transcript: str) -> ActorId | None
    async def confirm_mapping(trip_id: str, spk_label: str, actor_id: str) -> None
    async def get_current_mappings(trip_id: str) -> dict[str, ActorId]
    async def handle_new_speaker(trip_id: str, spk_label: str) -> MappingAction
    async def get_state(trip_id: str) -> MappingState  # Idle/Onboarding/Active/Trip-end
    async def transition_state(trip_id: str, event: StateEvent) -> MappingState
    async def buffer_concurrent(trip_id: str, utterance: Utterance) -> list[Utterance] | None
    # buffer_concurrent: 500ms 윈도우 내 발화를 모아서 반환. 윈도우 만료 시 버퍼된 발화 리스트 반환.
    async def assign_driver_role(trip_id: str, spk_label: str) -> None
    # assign_driver_role: 운전석 채널 탑승자에게 driver=true 자동 부여
```

## C3: Policy Enforcer

```python
class PolicyEnforcer:
    async def evaluate_permission(actor_id: str, tool_name: str, context: RequestContext) -> PolicyDecision
    async def get_priority(actors: list[str], context: DrivingContext) -> list[PrioritizedRequest]
    async def check_content_filter(actor_id: str, content: str) -> FilterResult
    async def get_actor_permissions(actor_id: str) -> PermissionSet
```

## C4: Orchestrator

```python
class Orchestrator:
    async def process_utterance(trip_id: str, actor_id: str, transcript: str) -> AgentResponse
    async def get_persona_prompt(actor_id: str) -> str
    async def invoke_tool(actor_id: str, tool_name: str, params: dict) -> ToolResult
    async def generate_rejection(actor_id: str, tool_name: str, reason: str) -> str
    async def handle_concurrent_requests(requests: list[UtteranceRequest]) -> list[AgentResponse]
```

## C5: Memory Manager

```python
class MemoryManager:
    # STM (Valkey)
    async def store_utterance(trip_id: str, actor_id: str, utterance: Utterance) -> None
    async def get_trip_history(trip_id: str, actor_id: str) -> list[Utterance]
    async def clear_trip_stm(trip_id: str) -> None
    
    # LTM (AgentCore Memory)
    async def get_profile(actor_id: str) -> PersonaProfile
    async def update_profile(actor_id: str, updates: dict) -> None
    async def get_preferences(actor_id: str) -> Preferences
    async def store_episode(actor_id: str, episode: Episode) -> None
```

## C6: Persona Registry

```python
class PersonaRegistry:
    async def get_persona(actor_id: str) -> Persona
    async def get_persona_by_role(role_attrs: RoleAttributes) -> Persona
    async def list_presets() -> list[Persona]
    async def get_prompt_template(role_attrs: RoleAttributes) -> str
    async def get_response_style(role_attrs: RoleAttributes) -> ResponseStyle
```

## C7: Tool Registry

```python
class ToolRegistry:
    def register_tool(tool: ToolDefinition) -> None
    def get_tool(tool_name: str) -> ToolDefinition
    def list_tools() -> list[ToolDefinition]
    async def execute_tool(tool_name: str, params: dict, actor_id: str) -> ToolResult
    def get_tools_for_persona(actor_id: str) -> list[ToolDefinition]
```

## C8: Reflection Agent

```python
class ReflectionAgent:
    async def run_reflection(trip_id: str) -> ReflectionResult
    async def extract_patterns(actor_id: str, utterances: list[Utterance]) -> list[Pattern]
    async def promote_to_ltm(actor_id: str, patterns: list[Pattern]) -> None
    async def cleanup_stm(trip_id: str) -> None
```

## C9: Evaluation Collector

```python
class EvaluationCollector:
    async def record_speaker_accuracy(predicted: str, actual: str) -> None
    async def record_persona_consistency(actor_id: str, response: str, expected_style: dict) -> None
    async def record_guardrail_event(actor_id: str, tool: str, blocked: bool, should_block: bool) -> None
    async def get_metrics() -> EvaluationMetrics
    async def flush_to_agentcore() -> None
```

## C10: WebSocket Gateway

```python
class WebSocketGateway:
    async def on_connect(client_id: str, auth_token: str) -> ConnectionResult
    async def on_audio_message(client_id: str, audio_data: bytes) -> None
    async def send_transcription(client_id: str, event: TranscriptionEvent) -> None
    async def send_response(client_id: str, response: AgentResponse) -> None
    async def on_disconnect(client_id: str) -> None
    async def broadcast_state_update(trip_id: str, state: dict) -> None
```
