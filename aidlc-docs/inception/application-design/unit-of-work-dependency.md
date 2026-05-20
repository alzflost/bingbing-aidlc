# Unit of Work — Dependency Matrix

## 의존성 매트릭스

| From ↓ / To → | U1 Infra | U2 API | U3 Agent | U4 Lambda | U5 Frontend |
|---|---|---|---|---|---|
| U1: Infrastructure | — | | | | |
| U2: API Service | ✅ 배포 대상 | — | ✅ HTTP 호출 | | |
| U3: Agent Service | ✅ 배포 대상 | | — | | |
| U4: Reflection Lambda | ✅ 배포 대상 | | | — | |
| U5: Frontend | ✅ ALB 엔드포인트 | ✅ WebSocket | | | — |

## 의존성 상세

### U1 → 모든 유닛
- 모든 서비스는 U1이 생성한 인프라 위에 배포
- 하지만 **인터페이스 정의는 인프라 없이 가능** → 병렬 개발 OK

### U2 → U3
- API Service가 Agent Service의 HTTP API를 호출
- **인터페이스 계약**: `/agent/process`, `/agent/concurrent`, `/policy/evaluate`
- 개발 시: Agent Service mock으로 API Service 독립 개발 가능

### U5 → U2
- Frontend가 API Service의 WebSocket + REST API 사용
- **인터페이스 계약**: `ws://host/ws/trip`, `/api/trip/*`
- 개발 시: WebSocket mock으로 Frontend 독립 개발 가능

### U4 → Valkey + AgentCore
- Lambda는 Valkey(STM)와 AgentCore Memory(LTM)에 직접 접근
- 다른 유닛과 런타임 의존성 없음 (이벤트 기반)

## 병렬 개발 전략

```
Phase 0: 인터페이스 정의 (모든 유닛 공통)
  ├─ API Service ↔ Agent Service HTTP 계약
  ├─ Frontend ↔ API Service WebSocket 계약
  └─ shared/models/ 공통 데이터 모델
         │
         ▼
Phase 1: 병렬 개발 시작
  ├─ U1: Terraform 모듈 작성
  ├─ U2: API Service (Agent mock 사용)
  ├─ U3: Agent Service (독립 테스트)
  ├─ U4: Reflection Lambda (독립 테스트)
  └─ U5: Frontend (WebSocket mock 사용)
         │
         ▼
Phase 2: 통합
  ├─ U1 배포 → U2, U3, U4 배포
  ├─ U2 ↔ U3 통합 테스트
  ├─ U5 → U2 통합 테스트
  └─ E2E 시나리오 테스트 (S1, S2, S3, S4)
```

## 공유 리소스

| 리소스 | 위치 | 사용 유닛 |
|---|---|---|
| 데이터 모델 (Python) | `shared/models/` | U2, U3, U4 |
| CEDAR 정책 파일 | `shared/policies/` | U3 (로드), U1 (AgentCore 등록) |
| 페르소나 프롬프트 | `shared/prompts/` | U3 |
| TypeScript 타입 | `frontend/src/types/` | U5 |
