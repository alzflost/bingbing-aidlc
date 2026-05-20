# Business Logic Model — Reflection Lambda (Unit 4)

## 트리거
- EventBridge 이벤트: `trip.ended` (source: api-service)
- Payload: `{trip_id, vehicle_id, driver_actor_id, ended_at}`

## 처리 흐름

```
EventBridge trip.ended 수신
  │
  ├─ 1. Valkey에서 트립 데이터 로드
  │     - trip:{trip_id}:state → TripSession
  │     - trip:{trip_id}:actor:* → 각 actor별 발화 이력
  │
  ├─ 2. 화자별 분리 처리
  │     FOR EACH actor_id in trip_session.speaker_mappings:
  │       │
  │       ├─ IF relationship == GUEST:
  │       │     → 발화 데이터 삭제 (프라이버시)
  │       │     → SKIP LTM 승격
  │       │
  │       ├─ IF 임시 프로파일 (temp_profile 존재):
  │       │     → 운전자에게 등록 확인 요청 플래그 설정
  │       │     → 발화 데이터는 보존 (확인 대기)
  │       │
  │       └─ IF 등록된 가족:
  │             → Step 3 (패턴 추출)
  │
  ├─ 3. LLM 기반 패턴 추출 (등록 가족만)
  │     - Claude Haiku 4.5 호출:
  │       prompt: "다음은 {name}의 이번 트립 발화 이력입니다.
  │               선호도, 관심사, 행동 패턴을 JSON으로 요약해주세요.
  │               기존 프로파일: {current_ltm_preferences}"
  │       input: actor별 발화 이력 전체
  │       output: Pattern[] (category, key, value, confidence_delta)
  │
  ├─ 4. LTM 승격 (AgentCore Memory)
  │     FOR EACH pattern in patterns:
  │       - 기존 LTM preference 조회
  │       - confidence_delta 적용 (기존 값 + delta, max 1.0)
  │       - AgentCore Memory putEvent 호출
  │
  ├─ 5. STM 정리
  │     - 등록 가족: LTM 승격 완료 후 STM 삭제
  │     - 게스트: 즉시 삭제 (Step 2에서 처리)
  │     - 임시 프로파일: 24시간 TTL 설정 (운전자 확인 대기)
  │
  └─ 6. 완료 이벤트 발행
        - EventBridge: `reflection.completed` (trip_id, results_summary)
```

## 에러 처리

| 에러 | 대응 |
|---|---|
| Valkey 연결 실패 | 3회 재시도 (exponential backoff) → 실패 시 DLQ |
| Claude 호출 실패 | STM 데이터 보존 + 에러 로깅 + 다음 시동 시 재시도 플래그 |
| AgentCore Memory 쓰기 실패 | 개별 actor 실패 시 나머지 계속 처리 + 실패 건 재시도 |
| Lambda 타임아웃 (5분) | 처리 중인 actor까지만 완료 + 나머지 재시도 이벤트 발행 |

## 미등록 가족 등록 확인 흐름

```
Reflection 완료 후:
  - 임시 프로파일 존재 시 → Valkey에 플래그 설정
  - 다음 트립 시작 시 API Service가 플래그 확인
  - 운전자에게 WebSocket으로 확인 요청 전송
  - 운전자 승인 → DDB에 영구 등록
  - 운전자 거부 → STM에서 삭제
```
