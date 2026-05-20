# Services

## 서비스 아키텍처: 경량 분리 (2 Services + 1 Lambda)

---

## SVC-1: API Service (ECS Fargate)

| 항목 | 내용 |
|---|---|
| 역할 | 클라이언트 대면, WebSocket 관리, 오디오 수신, Transcribe 연동, 화자 매핑 |
| 컴포넌트 | C1 (Voice Ingestion), C2 (Speaker Mapping), C10 (WebSocket Gateway) |
| 포트 | 8080 (HTTP/WS) |
| 스케일링 | 수평 확장 (WebSocket 세션 기반) |
| 상태 | Stateful (WebSocket + Transcribe 세션), 상태는 Valkey에 외부화 |

### 엔드포인트

| 경로 | 메서드 | 설명 |
|---|---|---|
| `/ws/trip` | WebSocket | 오디오 스트리밍 + 실시간 응답 |
| `/api/trip/start` | POST | 트립 시작 (시동 ON) |
| `/api/trip/end` | POST | 트립 종료 (시동 OFF) |
| `/api/trip/{id}/status` | GET | 트립 상태 조회 |
| `/api/trip/{id}/mappings` | GET | 현재 화자 매핑 상태 |
| `/api/metrics` | GET | Evaluation 지표 조회 (P2, optional) |
| `/health` | GET | 헬스체크 |

---

## SVC-2: Agent Service (ECS Fargate)

| 항목 | 내용 |
|---|---|
| 역할 | AI 에이전트 로직, 정책 평가, 메모리 관리, 도구 실행 |
| 컴포넌트 | C3 (Policy Enforcer), C4 (Orchestrator), C5 (Memory Manager), C6 (Persona Registry), C7 (Tool Registry), C9 (Evaluation Collector, optional) |
| 포트 | 8081 (HTTP 내부) |
| 스케일링 | 수평 확장 (요청 기반) |
| 상태 | Stateless (외부 저장소 위임) |

### 내부 API

| 경로 | 메서드 | 설명 |
|---|---|---|
| `/agent/process` | POST | 발화 처리 (actor_id + transcript → response) |
| `/agent/concurrent` | POST | 동시 발화 처리 (버퍼된 발화 리스트 → 우선순위 결정 → 순차 응답) |
| `/policy/evaluate` | POST | 권한 평가 |
| `/memory/profile/{actor_id}` | GET | 프로파일 조회 |
| `/memory/stm/{trip_id}` | GET/POST | STM 읽기/쓰기 |

---

## SVC-3: Reflection Lambda (AWS Lambda)

| 항목 | 내용 |
|---|---|
| 역할 | 트립 종료 이벤트 처리, 화자별 패턴 추출, STM → LTM 승격 |
| 컴포넌트 | C8 (Reflection Agent) |
| 트리거 | EventBridge (트립 종료 이벤트) 또는 API Service에서 직접 호출 |
| 타임아웃 | 5분 |
| 상태 | Stateless |

---

## 서비스 간 통신

```
Client (React)
    │
    │ WebSocket (오디오 + 응답)
    ▼
┌─────────────────────┐
│   API Service       │
│   (ECS Fargate)     │
│                     │
│  C10: WS Gateway    │──── Transcribe Streaming
│  C1: Voice Ingest   │
│  C2: Speaker Map    │──── Valkey (상태)
└─────────┬───────────┘
          │ HTTP (내부)
          ▼
┌─────────────────────┐
│   Agent Service     │
│   (ECS Fargate)     │
│                     │
│  C4: Orchestrator   │──── Bedrock (Claude Haiku 4.5)
│  C3: Policy         │──── AgentCore Policy
│  C5: Memory Mgr     │──── AgentCore Memory + Valkey
│  C6: Persona Reg    │
│  C7: Tool Registry  │
│  C9: Eval Collector │──── AgentCore Evaluations
└─────────┬───────────┘
          │ EventBridge
          ▼
┌─────────────────────┐
│  Reflection Lambda  │
│  C8: Reflection     │──── Valkey (STM) + AgentCore Memory (LTM)
└─────────────────────┘
```

---

## 오케스트레이션 흐름

1. **클라이언트** → WebSocket으로 오디오 청크 전송
2. **API Service** → Transcribe Streaming으로 전달, diarization 결과 수신
3. **API Service** → Speaker Mapping으로 spk_N → actor_id 매핑
4. **API Service** → Agent Service에 `{actor_id, transcript}` 전달
5. **Agent Service** → Policy 평가 → 허용 시 Orchestrator 실행 → 응답 생성
6. **API Service** → WebSocket으로 클라이언트에 응답 전송
7. **트립 종료** → EventBridge → Reflection Lambda 실행


---

## 인프라 전략

| 항목 | 구성 |
|---|---|
| IaC | Terraform |
| 컴퓨팅 | ECS Fargate (API Service + Agent Service) |
| 캐시/상태 | ElastiCache Valkey (VPC 내 프라이빗 서브넷) |
| 이벤트 | EventBridge + Lambda (Reflection) |
| 네트워크 | VPC, 프라이빗 서브넷, NAT Gateway, ALB (TLS 종단) |
| 시크릿 | Secrets Manager (Bedrock 자격증명 등) |
| 로깅 | CloudWatch Logs (구조화 로깅) |
| 모니터링 | CloudWatch Metrics + Alarms |

Terraform으로 전체 인프라를 코드화하여 `terraform apply` 한 번으로 배포.

---

## 동시 발화 감지 흐름 (상세)

```
Transcribe → spk_0 발화 수신
                │
                ▼
    C2: Speaker Mapping
    ├─ buffer_concurrent() 호출
    ├─ 500ms 타이머 시작 (또는 기존 타이머에 추가)
    │
    │  [500ms 이내 추가 발화 수신]
    │  ├─ spk_1 발화 → 버퍼에 추가
    │  └─ spk_2 발화 → 버퍼에 추가
    │
    │  [500ms 타이머 만료]
    ▼
    버퍼된 발화 리스트 반환
                │
                ▼
    IF 발화 1건 → /agent/process (단일 처리)
    IF 발화 2건+ → /agent/concurrent (동시 발화 처리)
                │
                ▼
    Agent Service: Policy 기반 우선순위 결정
    ├─ driver=true + 안전 요청 → 1순위
    ├─ driver=true + 비안전 → 2순위
    ├─ adult family → 3순위
    ├─ elder → 4순위
    ├─ child/teen → 5순위
    └─ guest → 6순위
                │
                ▼
    순차 처리 + 각 화자에게 개별 응답
```

---

## Transcribe 연동 모드 전환

| 모드 | 트리거 | 동작 |
|---|---|---|
| LIVE | 기본 모드 | 실시간 마이크 → Transcribe Streaming |
| FALLBACK | Transcribe 연결 실패 3회 | 사전 녹음 오디오 + mock diarization 결과 (graceful degradation) |
