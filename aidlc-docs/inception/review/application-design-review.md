# Application Design 비판적 검토

> 검토 대상 파일:
> - `inception/application-design/application-design.md`
> - `inception/application-design/components.md`
> - `inception/application-design/component-methods.md`
> - `inception/application-design/component-dependency.md`
> - `inception/application-design/services.md`

---

## 🔴 Critical Issues

### 1. "4단계 인식 전략" — 정의되지 않은 단계 존재

**파일**: `components.md` — C2: Speaker Mapping

C2 설명에 "4단계 인식 전략 실행"이라고 되어 있으나, 프로젝트 전체에서 정의된 매핑 전략은 3단계뿐:
- Primary: 좌석 채널 기반 (운전석 마이크 = 주 운전자 고정)
- Secondary: 트립 시작 1회 자기소개 (spk_N ↔ 페르소나 바인딩)
- Tertiary: 어휘/말투 콘텐츠 기반 휴리스틱 (어린이/노약자 보정)

4번째 단계가 무엇인지 어디에도 정의되어 있지 않음. 구현자가 "4번째 전략이 뭐지?" 하고 혼란에 빠지는 가장 위험한 종류의 오류.

---

### 2. 삭제된 기능 "동적 페르소나 자동 생성"이 설계에 잔존

**파일**: `component-methods.md` — C6: Persona Registry, `components.md` — C6

스토리(stories.md)에서 US-SYS-02(동적 페르소나 등록)를 삭제했음에도 불구하고:
- `component-methods.md`에 `auto_create_from_conversation()`, `auto_update_from_pattern()` 메서드가 존재
- `components.md` C6에 "동적 페르소나 자동 생성/업데이트" 책임 명시

문제점:
- 프라이버시 충돌: 동의 없이 대화에서 프로파일 자동 생성
- 스코프 크리프: 7시간 안에 구현 불가
- 스토리-설계 불일치: 요구사항에 없는 기능이 설계에 있으면 구현자가 뭘 만들어야 하는지 혼란

---

### 3. Orchestrator 프레임워크 무단 변경 (LangGraph → Strands Agent)

**파일**: `application-design.md` §3, `components.md` — C4

기획서에서 Orchestrator 구현을 "LangGraph"로 명시했으나, 설계 문서에서는 "Strands Agent 메인 루프"로 변경됨. 근거 없음.

LangGraph와 Strands Agent는 완전히 다른 프레임워크:
- LangGraph: LangChain 기반, 그래프 형태 워크플로우, Python 생태계
- Strands Agent: AWS 자체 에이전트 프레임워크

아키텍처 결정 기록(ADR) 없이 핵심 기술 스택이 변경됨. 어느 쪽을 쓸 건지 확정 필요.

---

## 🟠 High Issues

### 4. 7시간 타임박스에서 인프라 구성 불가능

**파일**: `application-design.md` §1, `services.md`

설계가 요구하는 인프라:
- ECS Fargate 클러스터 + 태스크 정의 + 서비스 2개
- ElastiCache(Valkey) 클러스터 (VPC, 서브넷, 보안그룹)
- EventBridge 규칙 + Lambda 배포
- 네트워킹 (VPC, 프라이빗 서브넷, NAT Gateway)

기획서 타임박스에서 인프라 세팅은 0:00~0:30(30분)으로 잡혀있는데, 이 아키텍처로는 인프라만 1~2시간 소요. 대안(로컬 Docker Compose, 단일 서비스, 사전 준비된 IaC)에 대한 언급 전무.

---

### 5. 동시 발화 감지/버퍼링 흐름 미정의

**파일**: `services.md`, `component-dependency.md`, `component-methods.md`

`/agent/concurrent` 엔드포인트와 `handle_concurrent_requests()` 메서드는 있지만:
- 누가 "동시 발화"를 감지하는지 불명확 (API Service? Agent Service?)
- 500ms 윈도우 내 발화를 모아서 보내는 버퍼링 로직의 위치 미정의
- API Service에서 개별 발화를 Agent Service로 보내면, Agent Service는 개별 요청으로 받는데 어떻게 "동시"를 판단하나?
- `component-dependency.md`의 데이터 흐름에서도 "발화 처리 (반복)"으로만 되어 있고, 동시 발화 감지 → 큐잉 → 우선순위 결정 흐름 누락

핵심 시나리오(S2: 동시 발화 충돌 해소)를 구현할 수 없는 상태.

---

### 6. WebSocket + Transcribe Streaming 브릿징 복잡도 과소평가

**파일**: `components.md` — C1, `component-methods.md` — C1

API Service가 동시에 관리해야 하는 것:
- 클라이언트 WebSocket 세션 유지
- Transcribe Streaming 세션 유지 (HTTP/2)
- 두 스트림 간 실시간 브릿징

에러 핸들링(Transcribe 세션 끊김, WebSocket 재연결, 오디오 버퍼링)에 대한 설계 전무.

기획서에서 "사전 녹음 + 좌석 채널 시뮬레이션으로 우회"를 리스크 대응으로 잡았는데, 설계에는 이 fallback 경로가 제대로 반영되지 않음. `switch_to_fallback()` 메서드가 있긴 하나, 트리거 조건과 데모 모드/실제 모드 전환 방법 미정의.

---

## 🟡 Medium Issues

### 7. Claude Haiku 4.5 모델 선택 근거 없음

**파일**: `application-design.md` §2, `services.md`

기획서에서는 "Bedrock (Claude)"라고만 했는데, 설계에서 "Claude Haiku 4.5"로 구체화됨. 문제:
- Haiku는 경량 모델 — 페르소나별 프롬프트 분기 + 도구 호출 + 맞춤 톤 생성 품질 검증 없음
- 기획서에서 "Bedrock 모델 선택 기준"을 스티어링 파일에서 정의하겠다고 했는데, 그 기준 없이 모델 결정
- 데모 품질이 모델 성능에 직결 — Haiku로 "페르소나별 차등 톤"이 충분히 나오는지?

---

### 8. gRPC vs HTTP 미결정

**파일**: `services.md` — SVC-2: Agent Service

Agent Service 포트를 "8081 (gRPC 또는 HTTP 내부)"로 기재. 설계 문서에서 "또는"은 있으면 안 됨.

7시간 타임박스에서 gRPC는 과도함:
- proto 파일 정의 필요
- 코드 생성 파이프라인 필요
- 디버깅 복잡도 증가

HTTP로 확정하고 넘어가야 함.

---

### 9. 페르소나 CRUD API 불필요

**파일**: `services.md` — API Service 엔드포인트

`/api/personas` (GET/POST)와 `/api/personas/{id}` (GET/PUT/DELETE)가 정의되어 있으나:
- 페르소나는 5개로 고정 (아빠, 엄마, 아이, 할머니, 게스트)
- "페르소나 CRUD"는 요구사항에 없음
- 동적 생성은 스코프 외로 결정됨
- 7시간 안에 CRUD API까지 만들 이유 없음

데모에서 페르소나를 런타임에 추가/삭제할 일이 없음. Over-engineering.

---

### 10. Demo UI "풀 React" 비현실적

**파일**: `components.md` — C11

C11이 담당하는 것:
- 좌석 배치도 시각화
- 화자 라벨 + 응답 실시간 표시
- 권한 대시보드
- 메모리 상태
- Evaluation 지표

기획서 타임박스에서 UI mock은 5:30~6:30(1시간). React + TypeScript + WebSocket + 실시간 시각화 + 대시보드를 1시간에 만드는 건 비현실적. "데모용 UI mock"이면 정적 HTML이나 Streamlit 수준이어야 함.

---

## 🟢 Low Issues

### 11. 보안 설계가 데모 스코프에 과도

**파일**: `application-design.md` §5

SECURITY 규칙 8개 매핑:
- VPC, Security Group, Private Subnet
- WebSocket 인증, API 인증
- Rate Limiting

7시간 데모에서 이걸 다 구현하면 핵심 기능 개발 시간 부족. 프로덕션 수준과 데모 수준을 구분하지 않고 있음. "인증 없이 동작, 프로덕션 시 추가" 정도로 명시하고 넘어가야 함.

---

### 12. Evaluation Collector의 "actual" 값 출처 미정의

**파일**: `component-methods.md` — C9

`record_speaker_accuracy(predicted: str, actual: str)` — "actual"(실제 화자)을 어떻게 아는지 정의 없음.

데모 환경에서는 시뮬레이션이니까 정답을 알 수 있지만, 프로덕션에서는 voiceprint 없이 "실제 화자"를 알 방법 없음. 데모용 mock인지 실제 운영 지표인지 명확히 해야 함.

---

### 13. P2 기능이 설계에서 필수 컴포넌트로 취급

**파일**: `application-design.md` §3, `services.md`

스토리에서 P2(시간 여유 시)로 내린 US-SYS-02(평가 지표)가 설계에서는:
- C9(Evaluation Collector)로 정식 컴포넌트
- `/api/metrics` 엔드포인트 존재
- 서비스 아키텍처 다이어그램에 포함

P2면 "시간 여유 시"인데, 설계에서는 필수처럼 다뤄지고 있어 우선순위 혼란 유발.

---

## 종합 판단

| 심각도 | 건수 | 핵심 |
|---|---|---|
| 🔴 Critical | 3건 | 스펙 불일치, 삭제 기능 잔존, 기술 스택 미확정 |
| 🟠 High | 3건 | 타임박스 초과, 핵심 흐름 미정의, 복잡도 과소평가 |
| 🟡 Medium | 4건 | 모델 근거 없음, 프로토콜 미결정, 불필요 기능, 비현실적 UI |
| 🟢 Low | 3건 | 과도한 보안, 지표 출처 불명, 우선순위 혼란 |

이 설계는 "7시간 데모"가 아니라 "프로덕션 서비스"를 설계한 것처럼 보임. 수정 방향:
1. 삭제된 기능(동적 페르소나) 잔재 제거
2. 기술 스택 확정 (LangGraph vs Strands, HTTP 확정, 모델 선택 근거)
3. 타임박스 제약 반영한 인프라 단순화 (단일 서비스 or Docker Compose)
4. 동시 발화 감지 흐름 구체화
5. 데모 스코프와 프로덕션 스코프 명확 분리
