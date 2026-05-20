# ADR-004: Trip-scoped State Machine & Identifier Lifecycle

| 항목 | 내용 |
|------|------|
| **상태** | Accepted |
| **결정일** | 2026-05-20 |
| **연관 정본** | requirements.md FR-01.1, FR-05.3, stories.md US-SYS-01, components.md C2 |
| **연관 audit** | 2026-05-20T09:50:00Z (Application Design Q3:A Valkey 상태저장) |

## Context and Problem Statement

본 시스템의 모든 상호작용은 "차량 시동 ON ~ OFF" 사이의 **트립(Trip)** 단위로 묶인다. 화자 매핑 / 발화 이력 / 동시 발화 버퍼 / 메모리 승격이 모두 트립 라이프사이클에 종속되므로, 다음을 결정해야 한다.

- 트립 식별자(trip_id)와 화자 식별자(actor_id) 정의
- 트립 동안의 시스템 상태 머신
- 시동 OFF 시 정리 / 승격 흐름

## Considered Options

1. **Stateless — 매 발화마다 식별자 재계산** — 단순. 그러나 동시 발화 버퍼 / 매핑 상태 유지 불가
2. **In-memory 상태 (Agent Service 메모리)** — 빠르지만 컨테이너 재시작 시 트립 상태 소실
3. **Trip-scoped 상태 머신 + Valkey 외부화** — 트립 단위 컨텍스트를 Valkey에 저장. 컨테이너 재시작에도 복구 가능

## Decision Outcome

**옵션 3 (Trip-scoped State Machine + Valkey 외부화)를 채택**한다.

### 식별자 정의

| 식별자 | 형식 | 생성 시점 | 종료 시점 |
|---|---|---|---|
| `trip_id` | UUID v4 | 시동 ON | 시동 OFF + Reflection 완료 |
| `actor_id` | `actor_{role}_{n}` 또는 `actor_guest_{uuid}` | 화자 매핑 시 부여 | actor 단위는 영속 (LTM 키) |
| `session_key` | UUID | WebSocket 연결 시 | 연결 해제 시 |

`trip_id`는 STM 키 prefix(`trip:{trip_id}:*`)로 사용되어 트립 종료 시 일괄 삭제 가능.

### 상태 머신 (US-SYS-01)

```
[Idle]
   │ 시동 ON
   ▼
[Onboarding]  ── 좌석 점유 확인, 채널 매핑, 자기소개 요청 (필요 시)
   │
   ├─ 매핑 성공 ──────────────────┐
   ├─ 미매핑 채널 발화 → 자기소개   │
   └─ 자기소개 미응답 → guest 자동 │
                                  ▼
                              [Active]  ── 발화 처리 / 동시 발화 버퍼링
                                  │
                                  │ 좌석 변경 / 신규 탑승
                                  ├──→ [Re-mapping] (새 화자 인식 후 Active 복귀)
                                  │
                                  │ 시동 OFF
                                  ▼
                              [Trip-end]  ── Reflection Lambda 실행, STM → LTM 승격
                                  │
                                  ▼
                                [Idle]
```

### Valkey 키 스킴

| 키 | 용도 | TTL |
|---|---|---|
| `trip:{trip_id}:state` | 상태 머신 현재 상태 | 트립 종료 후 24h |
| `trip:{trip_id}:mapping:{spk_label}` | spk_N → actor_id 매핑 | 트립 종료 후 24h |
| `trip:{trip_id}:actor:{actor_id}:utterances` | STM 발화 이력 | 트립 종료 후 24h |
| `trip:{trip_id}:concurrent_buffer` | 500ms 동시 발화 버퍼 | 트립 종료 시 즉시 삭제 |

## Consequences

- ✅ **컨테이너 재시작 복원**: API Service / Agent Service 어느 쪽이 재시작돼도 Valkey에서 상태 복원 가능
- ✅ **트립 단위 정리 단순**: `trip:{trip_id}:*` 패턴 일괄 삭제로 정리 일관성 (게스트 즉시 삭제, 등록자 LTM 승격 후 삭제)
- ✅ **Reflection 재시도 가능**: STM이 24h 보존되므로 Reflection Lambda 실패 시 다음 시동 시 재시도 (US-S6-01 AC #4)
- ✅ **상태 머신 가시성**: state 키 단일 조회로 현재 트립 단계 파악 가능 — 데모 UI(C11)에서 직접 노출 가능
- ⚠️ **Valkey 의존성**: Valkey 장애 시 시스템 기능 정지. 데모 환경에선 단일 노드 허용, 프로덕션 시 클러스터 모드 + Multi-AZ 필요 (Out of Scope)
- ⚠️ **TTL 관리 필요**: 키 prefix 일관성 + TTL 설정 누락 시 메모리 누수 — Construction 단계 PBT로 invariant 검증 필요

## Prior Art

LG U+ **ixi-drive** `SPEC-IXICORE-AUTH-002__vehicle-trip-session-lifecycle__v1.0.md`에서 동일한 패턴을 채택 운영 중이다.

| 항목 | ixi-drive 정의 | 본 프로젝트 적용 |
|---|---|---|
| Trip 정의 | "차량 시동 ON부터 OFF까지의 단위 (운행 단위)" | 동일 |
| trip_id 생성 | "차량 시동 ON 시 AAPP에서 생성 (UUID v4)" | 동일 |
| 캐시 TTL | "Trip 정보 Valkey TTL 24시간" (FR-003, NFR-004) | 동일 |
| 캐시 우선 조회 | "세션키 발급 시 trip_id 있으면 Valkey 우선, DB 조회 최소화" (FR-004) | 본 프로젝트는 DB 미사용, Valkey + AgentCore Memory 조합 |
| Trip 종료 | "시동 OFF 시 Trip 종료 요청 + 통계 DB 저장" | 본 프로젝트는 시동 OFF 시 EventBridge → Reflection Lambda → AgentCore Memory 승격 |
| 식별자 분리 | Vehicle_UUID / memb_id / trip_id / session_key 4종 | 본 프로젝트는 단순화: trip_id / actor_id / session_key 3종 |

ixi-drive 표준을 본 프로젝트의 다중 화자 컨텍스트로 확장: 1 Trip이 N명의 actor_id를 포함하며, 각 actor는 Trip 내에서 독립적 발화 이력 / 권한 분기를 가진다.
