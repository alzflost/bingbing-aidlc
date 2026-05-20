# Component Dependencies

## 의존성 매트릭스

| From ↓ / To → | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | C11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1: Voice Ingestion | — | ✅ | | | | | | | | ✅ | |
| C2: Speaker Mapping | | — | | | ✅ | ✅ | | | | ✅ | |
| C3: Policy Enforcer | | | — | | | ✅ | | | ✅ | | |
| C4: Orchestrator | | | ✅ | — | ✅ | ✅ | ✅ | | ✅ | | |
| C5: Memory Manager | | | | | — | | | | | | |
| C6: Persona Registry | | | | | ✅ | — | | | | | |
| C7: Tool Registry | | | | | | | — | | | | |
| C8: Reflection Agent | | | | | ✅ | | | — | | | |
| C9: Eval Collector | | | | | | | | | — | | |
| C10: WS Gateway | ✅ | | | | | | | | | — | |
| C11: Demo UI | | | | | | | | | | ✅ | — |

## 통신 패턴

### 동기 (Request-Response)
- C10 → C1: 오디오 청크 전달
- C1 → C2: Transcription + spk_label 전달
- C2 → C5: 프로파일 조회 (매핑 확인용)
- C2 → C6: 페르소나 조회/자동 생성
- C4 → C3: 권한 평가 요청
- C4 → C5: 메모리 조회/저장
- C4 → C6: 페르소나 프롬프트 조회
- C4 → C7: 도구 실행
- C6 → C5: 페르소나 프로파일 저장

### 비동기 (Event-Driven)
- API Service → EventBridge → C8: 트립 종료 이벤트
- C4 → C9: 평가 이벤트 발행 (fire-and-forget)
- C3 → C9: 가드레일 이벤트 발행

### 실시간 스트리밍
- C11 ↔ C10: WebSocket 양방향
- C1 ↔ Transcribe: AWS SDK 스트리밍

## 외부 서비스 의존성

| 컴포넌트 | 외부 서비스 | 프로토콜 |
|---|---|---|
| C1 | Amazon Transcribe Streaming | AWS SDK (HTTP/2) |
| C3 | AgentCore Policy | HTTPS REST |
| C4 | Amazon Bedrock (Claude Haiku 4.5) | AWS SDK (HTTPS) |
| C5 | AgentCore Memory | HTTPS REST |
| C5 | Amazon ElastiCache (Valkey) | Redis Protocol (TLS) |
| C2 | Amazon ElastiCache (Valkey) | Redis Protocol (TLS) |
| C8 | AgentCore Memory | HTTPS REST |
| C8 | Amazon ElastiCache (Valkey) | Redis Protocol (TLS) |
| C9 | AgentCore Evaluations | HTTPS REST |

## 데이터 흐름 (트립 라이프사이클)

```
시동 ON
  │
  ├─ tripId 생성
  ├─ Speaker Mapping → Idle → Onboarding
  ├─ Valkey: trip:{tripId}:state = "onboarding"
  │
  ▼
화자 인식 (반복)
  │
  ├─ Transcribe → spk_label
  ├─ Speaker Mapping: spk_label → actor_id
  ├─ Valkey: trip:{tripId}:mapping:{spk_label} = actor_id
  │
  ▼
발화 처리 (반복)
  │
  ├─ Policy Enforcer: 권한 확인
  ├─ Orchestrator: 페르소나 프롬프트 + LLM 호출
  ├─ Valkey STM: trip:{tripId}:actor:{actor_id}:utterances (append)
  ├─ Evaluation Collector: 지표 기록
  │
  ▼
시동 OFF
  │
  ├─ EventBridge: trip.ended 이벤트
  ├─ Reflection Lambda: STM 분석 → LTM 승격
  ├─ Valkey: trip:{tripId}:* 삭제 (게스트 즉시, 등록자는 LTM 승격 후)
  └─ Speaker Mapping → Trip-end → Idle
```
