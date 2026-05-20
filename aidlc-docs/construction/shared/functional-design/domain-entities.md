# Domain Entities — Shared Models

## Core Entities

### VehicleProfile (DynamoDB)
```python
class VehicleProfile:
    vehicle_id: str           # PK
    actor_id: str             # SK (e.g., "actor_father", "actor_child_1")
    name: str                 # 표시 이름
    age_group: AgeGroup       # adult | teen | child | elder
    relationship: Relationship # owner | family | guest
    account_owner: bool       # 차량 계정 소유자 여부
    default_seat_channel: int | None  # 기본 좌석 채널 (0=운전석, 1=조수석, 2=뒷좌석L, 3=뒷좌석R)
    preferences_summary: str | None   # LTM 선호도 요약 (캐시)
```

### RoleAttributes (런타임)
```python
class RoleAttributes:
    driver: bool              # 현재 운전석 탑승 여부 (동적)
    age_group: AgeGroup
    relationship: Relationship
    account_owner: bool
```

### AgeGroup (Enum)
```python
class AgeGroup(str, Enum):
    ADULT = "adult"
    TEEN = "teen"
    CHILD = "child"
    ELDER = "elder"
```

### Relationship (Enum)
```python
class Relationship(str, Enum):
    OWNER = "owner"
    FAMILY = "family"
    GUEST = "guest"
```

### TripSession (Valkey)
```python
class TripSession:
    trip_id: str
    vehicle_id: str
    started_at: datetime
    state: MappingState       # idle | onboarding | active | trip_end
    seat_occupancy: dict[int, str | None]  # channel → actor_id (None = 미매핑)
    speaker_mappings: dict[str, str]       # spk_label → actor_id
    driver_actor_id: str | None
```

### MappingState (Enum)
```python
class MappingState(str, Enum):
    IDLE = "idle"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    TRIP_END = "trip_end"
```

### Utterance
```python
class Utterance:
    utterance_id: str
    trip_id: str
    actor_id: str
    spk_label: str
    transcript: str
    timestamp: datetime
    seat_channel: int
    confidence: float         # Transcribe 신뢰도
```

### AgentResponse
```python
class AgentResponse:
    response_id: str
    trip_id: str
    actor_id: str
    text: str
    tool_used: str | None
    tool_result: dict | None
    policy_decision: PolicyDecision | None
    persona_style: ResponseStyle
    latency_ms: int
```

### PolicyDecision
```python
class PolicyDecision:
    allowed: bool
    rule_id: str | None       # CEDAR 정책 ID
    reason: str | None
    actor_id: str
    tool_name: str
    context: dict             # driving_speed, seat_channel 등
```

### ResponseStyle
```python
class ResponseStyle:
    tone: str                 # efficient | collaborative | friendly | respectful | neutral
    verbosity: str            # high | medium | low | minimal
    speech_rate: float        # 1.0 = normal, 0.8 = slow
    honorific: str            # casual | polite | formal
    confirmation_required: bool  # 중요 동작 시 재확인
```

### ConcurrentBuffer
```python
class ConcurrentBuffer:
    trip_id: str
    buffer_start: datetime
    utterances: list[Utterance]
    window_ms: int = 500
```

### ReflectionResult
```python
class ReflectionResult:
    trip_id: str
    actor_id: str
    patterns: list[Pattern]
    promoted_to_ltm: bool

class Pattern:
    category: str             # preference | behavior | interest
    key: str                  # e.g., "food_preference"
    value: str                # e.g., "vegan"
    confidence_delta: float   # LTM confidence 변화량
```
