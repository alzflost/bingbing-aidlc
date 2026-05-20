# Application Design — Family Profile Co-pilot

## 1. 아키텍처 개요

경량 분리 아키텍처: **API Service** + **Agent Service** + **Reflection Lambda**

```
┌─────────────┐     WebSocket      ┌──────────────────┐
│  React UI   │◄──────────────────►│   API Service    │
│  (Browser)  │                    │  (ECS Fargate)   │
└─────────────┘                    │                  │
                                   │  - WS Gateway    │
                                   │  - Voice Ingest  │──► Transcribe Streaming
                                   │  - Speaker Map   │──► Valkey (상태)
                                   └────────┬─────────┘
                                            │ HTTP (내부)
                                            ▼
                                   ┌──────────────────┐
                                   │  Agent Service   │
                                   │  (ECS Fargate)   │
                                   │                  │
                                   │  - Orchestrator  │──► Bedrock (Claude Haiku 4.5)
                                   │  - Policy        │──► AgentCore Policy (CEDAR)
                                   │  - Memory Mgr   │──► AgentCore Memory + Valkey
                                   │  - Persona Reg  │
                                   │  - Tool Registry │
                                   │  - Eval Collect  │──► AgentCore Evaluations
                                   └────────┬─────────┘
                                            │ EventBridge
                                            ▼
                                   ┌──────────────────┐
                                   │ Reflection Lambda│
                                   │                  │──► Valkey + AgentCore Memory
                                   └──────────────────┘
```

## 2. 핵심 설계 결정

| 결정 | 선택 | 근거 |
|---|---|---|
| 통신 방식 | WebSocket | 양방향 실시간 (오디오 업스트림 + 응답 다운스트림) |
| 서비스 구조 | 경량 분리 (2 services) | 빠른 개발 + 관심사 분리 (네트워크 I/O vs AI 로직) |
| 상태 저장 | Valkey (Redis) | 서비스 재시작에도 매핑 상태 유지, 트립 단위 TTL |
| Transcribe 연동 | 백엔드 (API Service) | 보안 (자격증명 서버사이드), 오디오 전처리 가능 |
| 이벤트 처리 | EventBridge + Lambda | 트립 종료 비동기 처리, 비용 효율 |

## 3. 컴포넌트 요약 (11개)

| # | 컴포넌트 | 서비스 | 핵심 책임 |
|---|---|---|---|
| C1 | Voice Ingestion | API | 오디오 수신 + Transcribe 연동 |
| C2 | Speaker Mapping | API | spk_N → actor_id 매핑 (4단계 전략) |
| C3 | Policy Enforcer | Agent | CEDAR 정책 평가 |
| C4 | Orchestrator | Agent | Strands Agent 메인 루프 |
| C5 | Memory Manager | Agent | STM/LTM 읽기/쓰기 |
| C6 | Persona Registry | Agent | 페르소나 CRUD + 자동 생성 |
| C7 | Tool Registry | Agent | 도구 정의/실행 |
| C8 | Reflection Agent | Lambda | 트립 종료 패턴 추출 |
| C9 | Evaluation Collector | Agent | 3개 지표 측정 |
| C10 | WebSocket Gateway | API | WS 연결 관리 |
| C11 | Demo UI | Client | React 풀 데모 |

## 4. 데이터 저장소

| 저장소 | 용도 | 데이터 |
|---|---|---|
| Valkey (ElastiCache) | STM + 상태 | 트립 발화 이력, 매핑 상태, 대화 컨텍스트 |
| AgentCore Memory | LTM | 페르소나 프로파일, 선호도, 에피소드 |
| AgentCore Policy | 정책 | CEDAR 규칙 (페르소나별 권한) |
| AgentCore Evaluations | 지표 | 식별 정확도, 일관성, 누락률 |

## 5. 보안 설계 (SECURITY 규칙 매핑)

| SECURITY 규칙 | 적용 위치 |
|---|---|
| SECURITY-01 (암호화) | Valkey TLS, 모든 AWS SDK 호출 HTTPS |
| SECURITY-04 (HTTP 헤더) | API Service 응답 헤더 |
| SECURITY-05 (입력 검증) | WebSocket 메시지 + REST API 파라미터 |
| SECURITY-06 (최소 권한) | ECS Task Role, Lambda Role |
| SECURITY-07 (네트워크) | VPC, Security Group, Private Subnet |
| SECURITY-08 (접근 제어) | WebSocket 인증, API 인증 |
| SECURITY-11 (보안 설계) | Policy Enforcer 분리, Rate Limiting |
| SECURITY-15 (예외 처리) | Global error handler, fail-closed |

## 6. 상세 문서 참조

- [components.md](components.md) — 컴포넌트 상세 정의
- [component-methods.md](component-methods.md) — 메서드 시그니처
- [services.md](services.md) — 서비스 레이어 설계
- [component-dependency.md](component-dependency.md) — 의존성 및 통신 패턴
