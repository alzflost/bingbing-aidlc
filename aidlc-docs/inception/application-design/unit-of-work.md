# Units of Work

## 개발 전략
- **순서**: 병렬 (인터페이스 먼저 정의 후 동시 개발)
- **레포**: 모노레포 (단일 레포에 모든 서비스 + 인프라 + 프론트엔드)

---

## Unit 1: Infrastructure (Terraform)

| 항목 | 내용 |
|---|---|
| 책임 | AWS 인프라 전체 프로비저닝 |
| 산출물 | Terraform 모듈 (VPC, ECS, ElastiCache, Lambda, EventBridge, ALB, IAM, CloudWatch) |
| 의존성 | 없음 (다른 유닛보다 먼저 또는 동시 시작) |
| 완료 기준 | `terraform apply` 성공, 모든 리소스 생성 확인 |

### 포함 리소스
- VPC + Private/Public Subnets + NAT Gateway
- ALB (TLS 종단) + Target Groups
- ECS Cluster + Task Definitions (API Service, Agent Service)
- ElastiCache Valkey (Redis-compatible, IAM 인증 모드 — user/password 미사용)
- DynamoDB Table (vehicle_profiles — 차량별 등록 가족 프로파일)
- Lambda Function (Reflection)
- EventBridge Rule (trip.ended)
- IAM Roles (ECS Task, Lambda, 최소 권한)
- CloudWatch Log Groups + Alarms
- Secrets Manager (API keys)
- Security Groups (서비스 간 통신 규칙)

### AgentCore 셋업 (Terraform)
- AgentCore Memory Store — `aws_bedrockagent_agent_memory` 리소스 (actor_id별 namespace)
- AgentCore Policy Store — `aws_verifiedpermissions_policy_store` + `aws_verifiedpermissions_policy` 리소스로 CEDAR 정책 등록
- AgentCore Evaluations — 해당 Terraform 리소스 존재 시 사용, 미지원 시 custom provider 또는 `terraform-provider-shell`로 래핑

> 모든 인프라는 Terraform 리소스 블록으로 관리. CLI 스크립트나 CloudFormation 미사용.

### DynamoDB: vehicle_profiles 테이블

| PK | SK | 속성 |
|---|---|---|
| vehicle_id | actor_id | name, age_group, relationship, account_owner, default_seat_channel, preferences_summary |

용도:
- 차량에 등록된 가족 목록 조회 (회원가입 대체)
- 좌석 채널 ↔ actor_id 기본 매핑 정보
- Speaker Mapping 시 "이 차에 누가 등록되어 있는가" 참조
- AgentCore Memory(LTM)는 선호도/에피소드 저장, DDB는 "신원 정보" 저장

---

## Unit 2: API Service (Python)

| 항목 | 내용 |
|---|---|
| 책임 | WebSocket 관리, 음성 수신, Transcribe 연동, 화자 매핑, 동시 발화 버퍼링 |
| 컴포넌트 | C1 (Voice Ingestion), C2 (Speaker Mapping), C10 (WebSocket Gateway) |
| 의존성 | Unit 1 (인프라), Unit 3 (Agent Service API 인터페이스) |
| 완료 기준 | WebSocket 연결 + Transcribe 스트리밍 + 화자 매핑 동작 |

### 핵심 기능
- WebSocket 서버 (인증 포함)
- Transcribe Streaming 연동 (LIVE + FALLBACK)
- Speaker Mapping State Machine (3단계 + driver 자동 부여)
- 500ms 동시 발화 버퍼링
- Valkey 상태 저장/조회 (IAM 인증)
- DynamoDB vehicle_profiles 조회 (등록 가족 확인)
- Agent Service HTTP 호출

---

## Unit 3: Agent Service (Python)

| 항목 | 내용 |
|---|---|
| 책임 | AI 에이전트 로직, 정책 평가, 메모리 관리, 도구 실행, 페르소나 엔진 |
| 컴포넌트 | C3 (Policy Enforcer), C4 (Orchestrator), C5 (Memory Manager), C6 (Persona Registry), C7 (Tool Registry), C9 (Evaluation Collector) |
| 의존성 | Unit 1 (인프라), AgentCore APIs (Memory, Policy, Evaluations) |
| 완료 기준 | 발화 입력 → 페르소나 맞춤 응답 생성 + 정책 평가 동작 |

### 핵심 기능
- Strands Agent 오케스트레이터
- CEDAR 정책 평가 (AgentCore Policy)
- 역할 속성 기반 페르소나 엔진 (5개 프리셋)
- AgentCore Memory 연동 (actor_id 스코프)
- Valkey STM 읽기/쓰기
- 도구 레지스트리 + 실행
- Claude Haiku 4.5 호출

---

## Unit 4: Reflection Lambda (Python)

| 항목 | 내용 |
|---|---|
| 책임 | 트립 종료 시 화자별 패턴 추출, STM → LTM 승격 |
| 컴포넌트 | C8 (Reflection Agent) |
| 의존성 | Unit 1 (인프라), Valkey (STM 읽기), AgentCore Memory (LTM 쓰기) |
| 완료 기준 | EventBridge 트리거 → STM 분석 → LTM 저장 동작 |

### 핵심 기능
- EventBridge 이벤트 수신 (trip.ended)
- Valkey STM 읽기 (화자별 발화 이력)
- 패턴 추출 (Claude 호출)
- AgentCore Memory LTM 저장
- 게스트 데이터 삭제

---

## Unit 5: Frontend (React + TypeScript)

| 항목 | 내용 |
|---|---|
| 책임 | 실시간 UI, 좌석 배치도, 권한 대시보드, 메모리 상태, Evaluation 지표 |
| 컴포넌트 | C11 (Demo UI) |
| 의존성 | Unit 2 (WebSocket API), Unit 1 (ALB 엔드포인트) |
| 완료 기준 | WebSocket 연결 + 실시간 화자/응답 표시 + 대시보드 동작 |

### 핵심 기능
- WebSocket 클라이언트 (오디오 전송 + 응답 수신)
- 좌석 배치도 시각화 (화자 라벨 실시간)
- 대화 스트림 (페르소나별 색상 구분)
- 권한 매트릭스 대시보드
- 메모리 상태 표시 (STM/LTM)
- Evaluation 지표 차트

---

## 코드 구조 (모노레포)

```
family-car-agent/
├── terraform/                  # Unit 1: Infrastructure
│   ├── modules/
│   │   ├── vpc/
│   │   ├── ecs/
│   │   ├── elasticache/        # Valkey (IAM 인증 모드)
│   │   ├── dynamodb/           # vehicle_profiles 테이블
│   │   ├── agentcore/          # Memory Store + Policy Store + Evaluations
│   │   ├── lambda/
│   │   ├── eventbridge/
│   │   └── alb/
│   ├── environments/
│   │   └── prod/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── services/
│   ├── api-service/            # Unit 2: API Service
│   │   ├── src/
│   │   │   ├── websocket/
│   │   │   ├── voice/
│   │   │   ├── mapping/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── agent-service/          # Unit 3: Agent Service
│   │   ├── src/
│   │   │   ├── orchestrator/
│   │   │   ├── policy/
│   │   │   ├── memory/
│   │   │   ├── persona/
│   │   │   ├── tools/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   └── reflection-lambda/      # Unit 4: Reflection Lambda
│       ├── src/
│       │   └── handler.py
│       ├── tests/
│       └── pyproject.toml
├── frontend/                   # Unit 5: Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
├── shared/                     # 공유 모듈
│   ├── models/                 # 공통 데이터 모델
│   ├── policies/               # CEDAR 정책 파일
│   └── prompts/                # 페르소나 프롬프트 템플릿
├── aidlc-docs/                 # AI-DLC 문서
└── pyproject.toml              # 루트 (uv workspace)
```
