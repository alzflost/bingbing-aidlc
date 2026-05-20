# ADR-003: Two-tier Memory (Valkey Session Cache + Bedrock AgentCore Long-term)

| 항목 | 내용 |
|------|------|
| **상태** | Accepted |
| **결정일** | 2026-05-20 |
| **연관 정본** | requirements.md FR-05, application-design.md §4, components.md C5 |
| **연관 audit** | 2026-05-20T09:10:00Z (Verification Q7:B Valkey + AgentCore) |

## Context and Problem Statement

화자별 페르소나 프로파일 / 트립 단위 발화 이력 / 이전 트립 컨텍스트를 관리하기 위한 메모리 계층 구조 결정이 필요하다.

요구사항:

- **트립 단위 발화 이력**: 시동 ON ~ OFF 동안의 화자별 발화 기록 (FR-05.1)
- **actor_id별 페르소나 프로파일**: 선호도 / 응답 스타일 / 권한 — 트립 간 영속 (FR-05.2)
- **Reflection 단계 LTM 승격**: 트립 종료 시 STM → LTM 분리 저장 (FR-05.3)
- **빠른 조회**: WebSocket 연결 직후 환영 메시지에 LTM 활용 (FR-07.1, NFR-01.1)
- **프라이버시**: 게스트 발화 미저장, 어린이 발화 부모 권한 하에서만 저장 (FR-05.4, FR-05.5)

## Considered Options

1. **Bedrock AgentCore Memory 단일 사용** — 모든 메모리를 영구 저장소에 직접
2. **Valkey 단일 사용** — 모든 메모리를 인메모리 캐시에. Long-term은 수동 영속화 구현
3. **Two-tier (Valkey Session Cache + Bedrock AgentCore Long-term)** — 세션 단위는 Valkey, 영속은 Bedrock
4. **DynamoDB + Valkey** — 자체 영속화. AgentCore 미사용

## Decision Outcome

**옵션 3 (Two-tier: Valkey + Bedrock AgentCore Memory)을 채택**한다.

| 계층 | 저장소 | 용도 | 라이프사이클 |
|---|---|---|---|
| **STM (Session Cache)** | Valkey (ElastiCache) | 트립 발화 이력, 매핑 상태, 대화 컨텍스트 | 트립 종료 후 24시간 TTL |
| **LTM (Long-term)** | Bedrock AgentCore Memory | actor_id별 페르소나 프로파일, Preference, Episode | 영속 (사용자 삭제 시까지) |

| 동작 | 흐름 |
|---|---|
| 트립 시작 | Valkey 조회 → miss 시 Bedrock 백그라운드 로드 → 즉시 환영 가능 |
| 발화 처리 | Valkey STM 누적 |
| 트립 종료 | Reflection Lambda → Bedrock CreateEvent (STM → LTM 승격) → Valkey 정리 |
| 게스트 | STM에만 저장 후 트립 종료 시 즉시 삭제 (LTM 미승격) |

## Consequences

- ✅ **빠른 시작**: Valkey 조회 < 10ms로 환영 메시지 지연 최소화 — NFR-01.1 (E2E 3초 P95) 충족 여유 확보
- ✅ **영구 개인화**: Bedrock AgentCore Memory가 Preference / Summary 자동 추출 — Reflection 로직 부담 경감 (FR-02.4 자동 패턴 학습 부분 활용)
- ✅ **AgentCore 4종 활용 명분**: AgentCore Memory가 LTM 정본 — 평가 항목 "AgentCore 활용도"에 직접 기여
- ✅ **프라이버시 분리 자연스러움**: 게스트 / 어린이 발화는 STM에서 멈추고 LTM 미승격 (FR-05.4, FR-05.5)
- ✅ **prior art 검증**: 동일 패턴이 프로덕션 운영 중 (Prior Art 섹션)
- ⚠️ **두 저장소 동기화 책임**: Reflection 단계가 정상 동작해야 LTM 일관성 유지. Reflection 실패 시 STM 보존 + 다음 시동 시 재시도 (US-S6-01 AC #4 반영)
- ⚠️ **운영 비용 증가**: Valkey 클러스터 + AgentCore Memory 양쪽 비용 발생 — 데모 스코프에서는 무시 가능

## Prior Art

LG U+ **ixi-drive** `SPEC-IXICORE-MEMORY-001__memory-architecture__v1.0.md` (v1.2)에서 정확히 동일한 구조를 정의·운영 중이다.

| 항목 | ixi-drive 정의 | 본 프로젝트 적용 |
|---|---|---|
| 계층 | "Session Cache (Valkey) + Amazon Bedrock AgentCore Memory" | 동일 |
| Trip 단위 | "1 Trip = 1 Event" | 동일 |
| 즉시 로드 | "WebSocket 연결 시 < 10ms 내 Memory 로드" | 동일 목표 |
| 자동 추출 | "Bedrock이 Preference/Summary 자동 생성" | 동일 활용 |
| Memory Tool | `get_memory(strategy, query, actor_id, date_range)` | 동일 시그니처 채택 후보 (component-methods.md C5 참조) |

차이점: ixi-drive는 `actor_id = User UUID` 단일 사용자 스코프, 본 프로젝트는 `actor_id = role-attributed persona instance` 다중 화자 스코프 (ADR-001 차별화 적용 지점).
