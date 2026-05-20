# Application Design Plan

## Context
- 기술 스택 확정: Strands SDK, Claude Haiku 4.5, Transcribe Streaming, Valkey, AgentCore (Memory/Policy/Evaluations), ECS Fargate + Lambda, React + TypeScript
- 7개 페르소나, 4단계 화자 인식 전략, 컨텍스트 기반 동시 발화 처리

---

## Questions

### Question 1: 백엔드-프론트엔드 통신 방식
React UI와 백엔드 간 실시간 통신 방식을 확인합니다.

A) WebSocket — 양방향 실시간 스트리밍 (화자 라벨 + 응답 실시간 표시)
B) SSE (Server-Sent Events) — 서버→클라이언트 단방향 스트리밍 + REST API
C) REST Polling — 주기적 폴링 (단순하지만 실시간성 떨어짐)
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: 마이크로서비스 vs 모놀리스
백엔드 서비스 구조를 확인합니다.

A) 모놀리스 — 단일 ECS 서비스에 모든 로직 포함 (빠른 개발)
B) 경량 분리 — API 서비스 + Agent 서비스 2개로 분리
C) 마이크로서비스 — 화자 매핑, 오케스트레이터, 메모리 각각 분리
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 3: 상태 관리 패턴
화자 매핑 상태 머신의 상태 저장 위치를 확인합니다.

A) Valkey(Redis)에 상태 저장 — 서비스 재시작에도 상태 유지
B) 인메모리 — 서비스 내 메모리에 상태 유지 (트립 단위이므로 충분)
C) DynamoDB — 영구 저장 + 이력 관리
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 4: Transcribe 연동 위치
Transcribe Streaming 연결을 어디서 관리할까요?

A) 백엔드 서비스 — 클라이언트가 오디오를 백엔드로 전송, 백엔드가 Transcribe 연결
B) 클라이언트 직접 — React에서 직접 Transcribe Streaming 연결 (STS 임시 자격증명)
C) 별도 미디어 서비스 — 오디오 처리 전용 서비스 분리
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Execution Plan (답변 후 실행)

- [x] Step 1: 컴포넌트 식별 및 책임 정의 (components.md)
- [x] Step 2: 컴포넌트 메서드 시그니처 정의 (component-methods.md)
- [x] Step 3: 서비스 레이어 설계 (services.md)
- [x] Step 4: 컴포넌트 의존성 및 통신 패턴 (component-dependency.md)
- [x] Step 5: 통합 설계 문서 (application-design.md)

---

답변 완료 후 알려주세요.
