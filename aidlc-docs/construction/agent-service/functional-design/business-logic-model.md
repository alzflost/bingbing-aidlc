# Business Logic Model — Agent Service (Unit 3)

## 1. Orchestrator (Strands Agent)

### 발화 처리 흐름
```
/agent/process 수신 (actor_id, transcript, trip_id, context)
  │
  ├─ 1. Persona Registry: 역할 속성 조회 → ResponseStyle 결정
  ├─ 2. Memory Manager: LTM 프로파일 + STM 대화 이력 조회
  ├─ 3. Strands Agent 실행:
  │     - system_prompt = 페르소나 프롬프트 (shared/prompts/ YAML)
  │     - user_message = transcript
  │     - context = {role_attrs, preferences, conversation_history}
  │     - tools = Tool Registry에서 해당 페르소나 허용 도구만
  │
  ├─ 4. IF 도구 호출 요청:
  │     ├─ Policy Enforcer: CEDAR 평가
  │     ├─ IF allowed → Tool 실행 → 결과를 Agent에 반환
  │     └─ IF denied → 거절 응답 생성 (페르소나 톤)
  │
  ├─ 5. 응답 생성 완료
  ├─ 6. STM에 발화 + 응답 저장
  ├─ 7. Evaluation Collector: 지표 기록
  └─ 8. AgentResponse 반환
```

### 동시 발화 처리 (/agent/concurrent)
```
버퍼된 발화 리스트 수신 [{actor_id, transcript, context}, ...]
  │
  ├─ 1. 각 발화의 역할 속성 조회
  ├─ 2. 우선순위 결정:
  │     - driving_speed > 0 (주행 중):
  │       driver + safety_tool → P1 (절대 우선)
  │       driver + non_safety → P2
  │       adult family → P3
  │       elder → P4
  │       child/teen → P5
  │       guest → P6
  │     - driving_speed = 0 (정차 중):
  │       선착순 (timestamp 기반)
  │
  ├─ 3. 우선순위 순서대로 순차 처리 (각각 /agent/process 로직)
  └─ 4. 모든 응답 리스트 반환
```

## 2. Policy Enforcer (CEDAR)

### 정책 평가 흐름
```
evaluate_permission(actor_id, tool_name, context)
  │
  ├─ 1. actor_id → RoleAttributes 조회
  ├─ 2. AgentCore Policy API 호출:
  │     - principal: {role_attrs}
  │     - action: tool_name
  │     - resource: tool_resource
  │     - context: {driving_speed, seat_channel, time_of_day}
  │
  ├─ 3. CEDAR 평가 결과:
  │     - ALLOW → PolicyDecision(allowed=true)
  │     - DENY → PolicyDecision(allowed=false, reason, rule_id)
  │
  └─ 4. Evaluation Collector: 가드레일 이벤트 기록
```

### CEDAR 정책 규칙 (핵심)
```cedar
// 어린이 차량 제어 차단
forbid(
  principal in Role::"child",
  action in [Action::"vehicle_control", Action::"bt_call", Action::"navigation"],
  resource
);

// 어린이 + 고속 주행 중 좌석 환경 차단
forbid(
  principal in Role::"child",
  action == Action::"seat_control",
  resource
) when { context.driving_speed > 80 };

// 게스트 정보 조회만 허용
forbid(
  principal in Role::"guest",
  action,
  resource
) unless { action == Action::"web_search" };

// 운전자 전체 허용
permit(
  principal,
  action,
  resource
) when { principal.driver == true && principal.age_group == "adult" };

// 어르신 전화 발신 시 재확인 필요
permit(
  principal in Role::"elder",
  action == Action::"bt_call",
  resource
) when { context.confirmation_received == true };
```

## 3. Memory Manager

### STM 구조 (Valkey)
```
trip:{trip_id}:state → TripSession JSON
trip:{trip_id}:actor:{actor_id}:utterances → List[Utterance JSON]
trip:{trip_id}:actor:{actor_id}:temp_profile → 임시 프로파일 (미등록 가족)
trip:{trip_id}:buffer → ConcurrentBuffer JSON
```

### LTM 구조 (AgentCore Memory)
```
actor_id namespace:
  - preferences: {food: "vegan", music: "jazz", ...}
  - episodes: [{trip_id, summary, timestamp}, ...]
  - personality: {verbosity, interests, ...}
```

## 4. Persona Registry

### 프롬프트 로딩 (shared/prompts/ YAML)
```yaml
# shared/prompts/driver_adult.yaml
system_prompt: |
  당신은 차량 AI 어시스턴트입니다.
  현재 운전자({name})와 대화 중입니다.
  응답 스타일: 효율적, 정보 밀도 높음, 옵션 2-3개 제시
  호칭: 일상적, 짧게
  {preferences_context}
  
response_style:
  tone: efficient
  verbosity: high
  speech_rate: 1.0
  honorific: casual
  confirmation_required: false
```

### 역할 속성 → 프롬프트 매핑
```python
def get_prompt_template(role_attrs: RoleAttributes) -> str:
    if role_attrs.driver and role_attrs.age_group == AgeGroup.ADULT:
        return load_yaml("driver_adult.yaml")
    elif role_attrs.age_group == AgeGroup.CHILD:
        return load_yaml("child.yaml")
    elif role_attrs.age_group == AgeGroup.ELDER:
        return load_yaml("elder.yaml")
    elif role_attrs.relationship == Relationship.GUEST:
        return load_yaml("guest.yaml")
    else:  # adult passenger (family)
        return load_yaml("passenger_adult.yaml")
```

## 5. Tool Registry

### 도구 목록

| 도구 | 구현 | 설명 |
|---|---|---|
| web_search | 실제 (Tavily/Brave API) | 웹 검색 |
| navigation | mock | 목적지 변경, 경로 안내 |
| vehicle_control | mock | 차량 제어 (창문, 에어컨 등) |
| seat_control | mock | 좌석 환경 (온도, 시트) |
| music | mock | 음악 재생/변경 |
| bt_call | mock | 블루투스 전화 발신 |

### Mock 도구 응답 패턴
```python
# mock 도구는 시나리오별 사전 정의된 응답 반환
MOCK_RESPONSES = {
    "navigation": {"status": "ok", "message": "경로가 변경되었습니다."},
    "vehicle_control": {"status": "ok", "message": "창문을 열었습니다."},
    ...
}
```
