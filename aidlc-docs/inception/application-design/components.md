# Components

## 서비스 구조: 경량 분리 (API Service + Agent Service)

---

## C1: Voice Ingestion (API Service)

| 항목 | 내용 |
|---|---|
| 책임 | 클라이언트로부터 오디오 스트림 수신, Transcribe Streaming 연결 관리, diarization 결과 수신 |
| 위치 | API Service (ECS Fargate) |
| 통신 | WebSocket (클라이언트 ↔ API), AWS SDK (API → Transcribe) |
| 상태 | Stateful (Transcribe 세션 유지) |

## C2: Speaker Mapping (API Service)

| 항목 | 내용 |
|---|---|
| 책임 | spk_N → actor_id 매핑, 4단계 인식 전략 실행, 상태 머신 관리 |
| 위치 | API Service (ECS Fargate) |
| 통신 | Valkey (상태 저장), AgentCore Memory (프로파일 조회) |
| 상태 | Stateful (Valkey에 매핑 상태 저장) |

## C3: Policy Enforcer (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | 페르소나별 도구 권한 검사, CEDAR 정책 평가, 동시 발화 우선순위 결정 |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | AgentCore Policy API |
| 상태 | Stateless (매 요청 시 정책 평가) |

## C4: Orchestrator (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | Strands Agent 메인 루프, 페르소나별 프롬프트 분기, 도구 호출 라우팅, 대화 관리 |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | Bedrock (Claude Haiku 4.5), Policy Enforcer, Memory Manager, Tool Registry |
| 상태 | Stateful (대화 컨텍스트 — Valkey STM) |

## C5: Memory Manager (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | STM(Valkey) 읽기/쓰기, LTM(AgentCore Memory) 조회/저장, actor_id 스코프 관리 |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | Valkey, AgentCore Memory API |
| 상태 | Stateless (외부 저장소 위임) |

## C6: Persona Registry (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | 페르소나 CRUD API, 프롬프트 템플릿 관리, 동적 페르소나 자동 생성/업데이트 |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | AgentCore Memory (페르소나 프로파일 저장) |
| 상태 | Stateless |

## C7: Tool Registry (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | 도구 정의 및 등록, 도구 실행 라우팅 (내비, 차량제어, 뮤직, 전화, 웹검색 등) |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | 외부 API (mock 또는 실제 차량 API) |
| 상태 | Stateless |

## C8: Reflection Agent (Lambda)

| 항목 | 내용 |
|---|---|
| 책임 | 트립 종료 시 화자별 에피소드 분석, STM → LTM 승격, 패턴 추출 |
| 위치 | AWS Lambda (이벤트 트리거) |
| 통신 | Valkey (STM 읽기), AgentCore Memory (LTM 쓰기) |
| 상태 | Stateless (이벤트 기반) |

## C9: Evaluation Collector (Agent Service)

| 항목 | 내용 |
|---|---|
| 책임 | 화자 식별 정확도, 페르소나 일관성, 가드레일 누락률 측정 및 AgentCore Evaluations 전송 |
| 위치 | Agent Service (ECS Fargate) |
| 통신 | AgentCore Evaluations API |
| 상태 | Stateless |

## C10: WebSocket Gateway (API Service)

| 항목 | 내용 |
|---|---|
| 책임 | WebSocket 연결 관리, 클라이언트 인증, 메시지 라우팅 (오디오 업스트림 + 응답 다운스트림) |
| 위치 | API Service (ECS Fargate) |
| 통신 | 클라이언트 ↔ WebSocket, 내부 → Agent Service |
| 상태 | Stateful (WebSocket 세션) |

## C11: Demo UI (React + TypeScript)

| 항목 | 내용 |
|---|---|
| 책임 | 좌석 배치도 시각화, 화자 라벨 + 응답 실시간 표시, 권한 대시보드, 메모리 상태, Evaluation 지표 |
| 위치 | 클라이언트 (브라우저) |
| 통신 | WebSocket (실시간), REST API (대시보드 데이터) |
| 상태 | 클라이언트 상태 (React state) |
