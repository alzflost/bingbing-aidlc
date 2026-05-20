# Unit of Work Plan

## Context
- 서비스 구조 확정: API Service + Agent Service + Reflection Lambda + React UI
- 인프라: Terraform
- 11개 컴포넌트가 3개 서비스 + 1개 클라이언트에 분배됨

---

## Questions

### Question 1: 개발 순서 전략
유닛 간 개발 순서를 어떻게 할까요?

A) 순차 — 인프라 → 백엔드(API → Agent) → 프론트엔드 순서
B) 병렬 — 인프라 + 백엔드 + 프론트엔드 동시 (인터페이스 먼저 정의)
C) Critical Path 우선 — Speaker Mapping → Agent → 나머지 병렬
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 2: 모노레포 vs 멀티레포
코드 저장소 구조를 확인합니다.

A) 모노레포 — 단일 레포에 모든 서비스 + 인프라 + 프론트엔드
B) 멀티레포 — 서비스별 별도 레포
C) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Execution Plan (답변 후 실행)

- [x] Step 1: 유닛 정의 (unit-of-work.md)
- [x] Step 2: 유닛 간 의존성 매트릭스 (unit-of-work-dependency.md)
- [x] Step 3: 스토리-유닛 매핑 (unit-of-work-story-map.md)
- [x] Step 4: 코드 구조 정의 (Greenfield)

---

답변 완료 후 알려주세요.
