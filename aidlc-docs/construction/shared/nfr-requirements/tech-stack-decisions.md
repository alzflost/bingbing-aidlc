# Tech Stack Decisions — All Units

## Backend (Python)

| 항목 | 선택 | 버전 | 근거 |
|---|---|---|---|
| Runtime | Python | 3.12 | AWS Lambda 지원, Strands SDK 호환 |
| Package Manager | uv | latest | 빠른 의존성 해결, lockfile 지원 |
| Web Framework | FastAPI | 0.115+ | WebSocket 지원, async, Pydantic 통합 |
| Agent SDK | Strands Agents | latest | AWS 네이티브, 도구 호출 내장 |
| LLM | Claude Haiku 4.5 (Bedrock) | — | 빠른 응답, 비용 효율 |
| Validation | Pydantic | v2 | 타입 안전, 직렬화, FastAPI 통합 |
| Logging | structlog | latest | 구조화 로깅, JSON 출력 |
| HTTP Client | httpx | latest | async 지원, 타임아웃 관리 |
| Redis Client | redis-py | latest | Valkey 호환, IAM 인증 지원 |
| Testing | pytest + Hypothesis | latest | PBT 프레임워크 (PBT-09) |
| Linting | ruff | latest | 빠른 린팅 + 포매팅 |
| Type Checking | mypy | latest | 정적 타입 검사 |

## Frontend (TypeScript)

| 항목 | 선택 | 버전 | 근거 |
|---|---|---|---|
| Framework | React | 18+ | 컴포넌트 기반, 생태계 |
| Language | TypeScript | 5+ | 타입 안전 |
| Build | Vite | latest | 빠른 빌드, HMR |
| State | Zustand | latest | 경량, 간단 (Q5:A) |
| Validation | Zod | latest | 런타임 타입 검증 (SECURITY-05) |
| Styling | Tailwind CSS | latest | 유틸리티 기반, 빠른 개발 |
| Charts | Recharts | latest | Evaluation 대시보드 |
| WebSocket | native WebSocket API | — | 추가 라이브러리 불필요 |
| Testing | Vitest + fast-check | latest | PBT 프레임워크 (PBT-09) |
| Linting | ESLint + Prettier | latest | 코드 품질 |

## Infrastructure (Terraform)

| 항목 | 선택 | 버전 | 근거 |
|---|---|---|---|
| IaC | Terraform | 1.7+ | 리소스 블록 명확, 상태 관리 |
| Provider | AWS | 5.x | 최신 리소스 지원 |
| Backend | S3 + DynamoDB | — | 원격 상태 + 잠금 |
| Module 구조 | 8 modules | — | 관심사 분리 |

## AWS Services

| 서비스 | 용도 | 유닛 |
|---|---|---|
| ECS Fargate | API Service + Agent Service 컴퓨팅 | Infra |
| ElastiCache Valkey | STM + 상태 저장 (IAM 인증) | Infra |
| DynamoDB | vehicle_profiles (가족 등록) | Infra |
| Lambda | Reflection Agent | Infra |
| EventBridge | trip.ended 이벤트 라우팅 | Infra |
| ALB | HTTPS 종단 + WebSocket 라우팅 | Infra |
| Transcribe Streaming | 실시간 음성→텍스트 + diarization | API |
| Bedrock (Claude Haiku 4.5) | LLM 추론 | Agent + Lambda |
| AgentCore Memory | LTM (actor_id별 선호도/에피소드) | Agent + Lambda |
| AgentCore Policy (Verified Permissions) | CEDAR 정책 평가 | Agent |
| AgentCore Evaluations | 품질 지표 측정 | Agent |
| CloudWatch | 로깅 + 메트릭 + 알림 | All |
| X-Ray | 분산 트레이싱 | All |
| Secrets Manager | API 키, 외부 서비스 자격증명 | Infra |
| ACM | TLS 인증서 | Infra |

## PBT Testable Properties (PBT-01)

### API Service
| 컴포넌트 | 속성 | 카테고리 |
|---|---|---|
| Speaker Mapping | 상태 전이 유효성 (invalid state 불가) | Stateful (PBT-06) |
| Speaker Mapping | 매핑 후 actor_id 일관성 (같은 spk → 같은 actor) | Invariant (PBT-03) |
| Concurrent Buffer | 버퍼 크기 ≤ 좌석 수 | Invariant (PBT-03) |
| Concurrent Buffer | 500ms 윈도우 내 모든 발화 포함 | Invariant (PBT-03) |

### Agent Service
| 컴포넌트 | 속성 | 카테고리 |
|---|---|---|
| Policy Enforcer | 동일 입력 → 동일 결과 (멱등) | Idempotence (PBT-04) |
| Policy Enforcer | driver=true,adult → 항상 ALLOW (all tools) | Invariant (PBT-03) |
| Policy Enforcer | guest → 항상 DENY (except web_search) | Invariant (PBT-03) |
| Persona Registry | role_attrs → prompt 매핑 결정적 | Invariant (PBT-03) |
| Priority Resolver | 정렬 안정성 (같은 우선순위 → 순서 보존) | Invariant (PBT-03) |

### Shared Models
| 컴포넌트 | 속성 | 카테고리 |
|---|---|---|
| All Pydantic models | serialize → deserialize = identity | Round-trip (PBT-02) |
| RoleAttributes | 유효한 조합만 생성 가능 | Invariant (PBT-03) |

### Frontend
| 컴포넌트 | 속성 | 카테고리 |
|---|---|---|
| Zustand stores | action 적용 후 상태 일관성 | Stateful (PBT-06) |
| WebSocket message parsing | parse(serialize(msg)) = msg | Round-trip (PBT-02) |
