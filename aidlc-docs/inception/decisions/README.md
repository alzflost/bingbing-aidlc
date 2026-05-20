# Architecture Decision Records (ADR)

> **Format**: MADR 간소화 (LG U+ ixi-drive 표준 차용 — `ARCH-C1-001`, `ARCH-C2-001` 동일 형식)
>
> **Sections**: 상태 / 결정일 / Context / Considered Options / Decision Outcome / Consequences

## ADR Index

| ID | 제목 | 상태 | 결정일 | 우선도 |
|---|---|---|---|---|
| [ADR-001](ADR-001-role-based-persona-model.md) | Role-based Persona Model | Accepted | 2026-05-20 | ⭐⭐⭐ |
| [ADR-002](ADR-002-strands-as-orchestrator.md) | Strands Agents SDK as Orchestrator | Accepted | 2026-05-20 | ⭐⭐⭐ |
| [ADR-003](ADR-003-two-tier-memory.md) | Two-tier Memory (Valkey Session Cache + AgentCore Long-term) | Accepted | 2026-05-20 | ⭐⭐⭐ |
| [ADR-004](ADR-004-trip-scoped-state-machine.md) | Trip-scoped State Machine & Identifier Lifecycle | Accepted | 2026-05-20 | ⭐⭐ |
| [ADR-005](ADR-005-natural-speaker-recognition.md) | Natural Speaker Recognition (3-step strategy) | Accepted | 2026-05-20 | ⭐⭐ |

## Conventions

- **상태**: Proposed / Accepted / Superseded / Deprecated
- **변경**: ADR은 immutable. 결정 변경 시 새 ADR을 만들고 이전 ADR을 `Superseded by ADR-NNN`으로 표시
- **위치**: 모든 ADR은 `aidlc-docs/inception/decisions/` 하위. Construction 단계에서 새 결정 발생 시 `aidlc-docs/construction/decisions/` 추가 가능

## Prior Art

ADR-002, ADR-003, ADR-004는 LG U+ ixi-drive (커넥티드카 AI 음성 에이전트 프로덕션 시스템)의 검증된 설계를 인용합니다. 산업 표준 prior art로 자리잡힌 디자인을 본 프로젝트에 차용함으로써 7시간 타임박스 내 신뢰성 있는 구현을 목표합니다.

ADR-001은 ixi-drive에 부재한 multi-speaker layer를 본 프로젝트가 추가하는 **차별화 결정**으로, prior art 없는 신규 결정입니다.

## Cross-Reference

- 본 ADR들은 `aidlc-docs/traceability-matrix.md` §1 ID 명명 규칙 + §6 D-06 + §8에서 참조
- 정본 산출물(requirements.md, components.md, services.md)과 충돌 시 정본이 우선하며, ADR은 결정 근거를 제공하는 보조 문서
