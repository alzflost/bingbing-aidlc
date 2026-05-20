# NFR Requirements — All Units

## 1. Performance

| 지표 | 목표 | 적용 유닛 |
|---|---|---|
| End-to-end 응답 지연 | ≤ 3초 (P95) | API + Agent |
| Transcribe diarization 수신 | ≤ 1초 | API |
| AgentCore Policy 평가 | ≤ 500ms | Agent |
| AgentCore Memory 조회 | ≤ 1초 | Agent |
| WebSocket 메시지 전달 | ≤ 100ms | API |
| Frontend 렌더링 (FCP) | ≤ 1.5초 | Frontend |
| Lambda cold start | ≤ 3초 | Reflection |
| 동시 발화 버퍼 윈도우 | 500ms 고정 | API |

## 2. Scalability

| 지표 | 목표 | 적용 유닛 |
|---|---|---|
| 동시 트립 수 | 100+ (ECS 수평 확장) | API + Agent |
| 트립당 최대 화자 | 5명 (Transcribe 제한) | API |
| Valkey 동시 연결 | 1000+ | API + Agent + Lambda |
| DynamoDB 읽기 용량 | On-demand (자동) | API + Agent |

## 3. Availability

| 지표 | 목표 | 적용 유닛 |
|---|---|---|
| 서비스 가용성 | 99.9% | API + Agent |
| Transcribe fallback | 연결 실패 3회 → 자동 전환 | API |
| ECS 태스크 최소 수 | 2 (multi-AZ) | API + Agent |
| Lambda 동시 실행 | 10 (reserved concurrency) | Reflection |

## 4. Security (SECURITY-01 ~ SECURITY-15 전체 적용)

| 규칙 | 구현 | 유닛 |
|---|---|---|
| SECURITY-01 (암호화) | Valkey TLS + DDB 서버사이드 암호화 + HTTPS 전체 | Infra |
| SECURITY-03 (로깅) | 구조화 로깅 (structlog) + CloudWatch | All |
| SECURITY-04 (HTTP 헤더) | CSP, HSTS, X-Content-Type-Options | API |
| SECURITY-05 (입력 검증) | Pydantic 스키마 검증 (Python), Zod (Frontend) | API + Agent + Frontend |
| SECURITY-06 (최소 권한) | IAM Role per service, specific ARNs | Infra |
| SECURITY-07 (네트워크) | Private subnet, SG 최소 포트 | Infra |
| SECURITY-08 (접근 제어) | JWT (WebSocket), IAM (내부) | API |
| SECURITY-09 (하드닝) | No default creds, generic errors | All |
| SECURITY-10 (공급망) | uv.lock 고정, 취약점 스캔 | All |
| SECURITY-11 (보안 설계) | Policy Enforcer 분리, rate limiting | Agent + API |
| SECURITY-12 (인증) | JWT + 세션 만료 + secure cookies | API + Frontend |
| SECURITY-15 (예외 처리) | Global error handler, fail-closed | All |

## 5. Testing (PBT 전체 적용)

| 규칙 | 구현 | 유닛 |
|---|---|---|
| PBT-01 (설계 시 속성 식별) | Functional Design에 Testable Properties 포함 | All |
| PBT-02 (Round-trip) | 직렬화/역직렬화 테스트 | Shared models |
| PBT-03 (Invariant) | Speaker Mapping 상태 전이 불변성 | API |
| PBT-04 (Idempotency) | Policy 평가 멱등성 | Agent |
| PBT-06 (Stateful) | Speaker Mapping state machine | API |
| PBT-07 (Generator 품질) | 도메인 생성기 (Utterance, RoleAttributes) | All |
| PBT-08 (Shrinking) | Hypothesis seed 로깅 | Python units |
| PBT-09 (프레임워크) | Python: Hypothesis, TypeScript: fast-check | All |
| PBT-10 (보완 전략) | PBT + example-based 병행 | All |

## 6. Reliability

| 지표 | 구현 | 유닛 |
|---|---|---|
| Circuit breaker | AgentCore API 호출 시 (3회 실패 → open) | Agent |
| Retry with backoff | Valkey, DDB, Bedrock 호출 | All |
| Dead letter queue | Reflection Lambda 실패 이벤트 | Lambda |
| Health check | /health 엔드포인트 (ALB + ECS) | API + Agent |
| Graceful shutdown | SIGTERM 처리, 진행 중 요청 완료 후 종료 | API + Agent |

## 7. Observability

| 항목 | 구현 | 유닛 |
|---|---|---|
| 구조화 로깅 | structlog (Python), pino (Frontend) | All |
| 메트릭 | CloudWatch custom metrics | All |
| 트레이싱 | X-Ray (ECS + Lambda) | All |
| 알림 | CloudWatch Alarms → SNS | Infra |
| 대시보드 | CloudWatch Dashboard | Infra |
