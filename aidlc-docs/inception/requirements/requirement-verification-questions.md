# Requirements Verification Questions

기획 자료(`requirements/family-profile-co-pilot-idea.md`)를 분석한 결과, 구현 수준의 명확성을 위해 아래 질문들에 답변 부탁드립니다.
각 질문의 `[Answer]:` 태그 뒤에 선택지 문자를 기입해주세요.

---

## Question 1: 프로젝트 실행 범위
이번 AI-DLC 세션에서 구현할 범위를 확인합니다. 7시간 타임박스 전체를 커버할 건지, 핵심 Critical Path만 먼저 할 건지요?

A) Critical Path 우선 — Speaker Mapping + AgentCore Memory + 페르소나 프롬프트 (S1, S3, S4 시연 가능 수준)
B) 전체 스코프 — 7개 시나리오 모두 + 데모 UI + Reflection Agent 포함
C) Critical Path + 데모 UI — 핵심 기능 + 시연용 프론트엔드까지
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 2: 음성 입력 처리 방식
실제 마이크 입력 vs 시뮬레이션 중 어떤 방식으로 구현할까요?

A) 완전 시뮬레이션 — 사전 녹음된 오디오 파일 + mock diarization 결과로 데모
B) Transcribe Streaming 실제 연동 — 실시간 마이크 입력 + 실제 diarization
C) 하이브리드 — Transcribe Streaming 연동하되, 데모 시 사전 녹음 fallback 준비
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 3: AgentCore 서비스 사용 범위
Bedrock AgentCore의 어떤 기능들을 실제로 연동할 건지 확인합니다.

A) Memory + Policy 만 (핵심 2종)
B) Memory + Policy + Evaluations (3종)
C) Memory + Policy + Evaluations + Runtime (4종 전체)
D) Mock/Stub으로 대체 — AgentCore API 호출 없이 로컬 시뮬레이션
E) Other (please describe after [Answer]: tag below)

[Answer]: C 근데 Evaluation이랑 Runtime의미 잘모르겠어.

---

## Question 4: Orchestrator 프레임워크
LangGraph를 사용한다고 되어 있는데, 구체적으로 어떤 형태를 원하시나요?

A) LangGraph (Python) — langgraph 라이브러리 사용
B) LangGraph.js (TypeScript) — JavaScript/TypeScript 기반
C) 순수 Python state machine — 외부 프레임워크 없이 직접 구현
D) Bedrock Agent (managed) — AWS managed agent 활용
E) Other (please describe after [Answer]: tag below)

[Answer]: E Strands 쓸꺼야 

---

## Question 5: 응답 생성 (TTS) 방식
응답을 음성으로 출력할 건지, 텍스트만으로 할 건지요?

A) 텍스트 전용 — 데모 UI에 텍스트로만 표시
B) Amazon Polly TTS — 텍스트 → 음성 변환 포함
C) Nova Sonic (S2S) — Speech-to-Speech 직접 연동
D) 텍스트 기본 + Polly 옵션 — 텍스트 우선, 시간 여유 시 Polly 추가
E) Other (please describe after [Answer]: tag below)

[Answer]: D

---

## Question 6: 데모 UI 기술 스택
데모용 UI mock의 기술 스택을 확인합니다.

A) Streamlit (Python) — 빠른 프로토타이핑
B) React + TypeScript — 풀 프론트엔드
C) Gradio — ML 데모 특화
D) 터미널 CLI — UI 없이 콘솔 기반 데모
E) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 7: 데이터 저장소
STM(Short-Term Memory)과 LTM(Long-Term Memory) 구현 방식을 확인합니다.

A) AgentCore Memory만 사용 — STM/LTM 모두 AgentCore에 위임
B) Valkey(Redis) STM + AgentCore LTM — 기획 문서 그대로
C) 로컬 인메모리 STM + AgentCore LTM — 인프라 최소화
D) 전부 로컬 (JSON/SQLite) — AWS 의존 없이 로컬 시뮬레이션
E) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 8: CEDAR 정책 구현 방식
AgentCore Policy (CEDAR) 규칙을 어떻게 구현할 건지요?

A) AgentCore Policy API 실제 연동 — CEDAR 정책을 AgentCore에 등록하고 런타임 평가
B) 로컬 CEDAR 엔진 — cedar-policy 라이브러리로 로컬 평가
C) 커스텀 Python 규칙 엔진 — CEDAR 형식 참고하되 자체 구현
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 9: 배포 환경
개발/데모 실행 환경을 확인합니다.

A) 로컬 개발 환경 — 로컬에서 실행, AWS 서비스만 원격 호출
B) AWS Cloud9 / EC2 — 클라우드 개발 환경
C) 컨테이너 (Docker) — 로컬 Docker로 패키징
D) AWS Lambda + API Gateway — 서버리스 배포
E) Other (please describe after [Answer]: tag below)

[Answer]: E ECS + fargate 로 서버리스 배포 + D옵션 몇개

---

## Question 10: Bedrock 모델 선택
LLM 추론에 사용할 모델을 확인합니다.

A) Claude 3.5 Sonnet (Bedrock)
B) Claude 3 Haiku (Bedrock) — 빠른 응답, 비용 절감
C) Claude 4 Sonnet (Bedrock) — 최신 모델
D) Nova Pro / Nova Lite — AWS 자체 모델
E) Other (please describe after [Answer]: tag below)

[Answer]: E Claude Haiku4.5

---

## Question 11: 동시 발화 처리 우선순위 세부 규칙
S2 시나리오에서 동시 발화 시 우선순위 규칙을 더 구체화해야 합니다. 아래 중 어떤 정책을 적용할까요?

A) 운전자 절대 우선 — 운전자 발화가 있으면 항상 운전자 먼저 처리, 나머지는 큐잉
B) 안전 관련 우선 — 안전 관련 발화(차량제어, 내비)가 엔터테인먼트보다 우선
C) 선착순 + 운전자 보너스 — 기본 선착순이되, 운전자는 0.5초 우선권
D) 컨텍스트 기반 — 현재 상황(주행 중/정차 중)에 따라 동적 우선순위
E) Other (please describe after [Answer]: tag below)

[Answer]: D

---

## Question 12: 평가(Evaluation) 지표 구현 수준
AgentCore Evaluations 커스텀 지표를 어느 수준까지 구현할까요?

A) 정의만 — 지표 정의 문서화, 실제 측정 로직은 미구현
B) 기본 측정 — 화자 식별 정확도 + 가드레일 누락률 2개 지표 실측
C) 전체 측정 — 3개 지표(식별 정확도, 페르소나 일관성, 가드레일 누락률) 모두 실측 + 대시보드
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 13: Security Extensions
이 프로젝트에 보안 확장 규칙을 적용할까요?

A) Yes — 모든 SECURITY 규칙을 blocking constraint로 적용 (프로덕션 수준 애플리케이션에 권장)
B) No — SECURITY 규칙 스킵 (PoC, 프로토타입, 실험적 프로젝트에 적합)
C) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 14: Property-Based Testing Extension
이 프로젝트에 Property-Based Testing (PBT) 규칙을 적용할까요?

A) Yes — 모든 PBT 규칙을 blocking constraint로 적용 (비즈니스 로직, 데이터 변환, 직렬화, 상태 관리 컴포넌트가 있는 프로젝트에 권장)
B) Partial — 순수 함수와 직렬화 round-trip에만 PBT 규칙 적용
C) No — PBT 규칙 스킵 (단순 CRUD, UI 전용, 얇은 통합 레이어에 적합)
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Question 15: 페르소나 확장성
현재 5개 페르소나(아빠, 엄마, 아이, 할머니, 게스트)가 정의되어 있습니다. 향후 확장을 고려한 설계가 필요한가요?

A) 고정 5종 — 현재 정의된 페르소나만 지원, 하드코딩 OK
B) 설정 기반 확장 — 새 페르소나를 config 파일로 추가 가능하게 설계
C) 동적 등록 — 런타임에 새 페르소나 등록/수정 가능한 API 제공
D) Other (please describe after [Answer]: tag below)

[Answer]: C 로 하되 AI 판단하에 대화를 통해 유추해서 자동등록도

---
