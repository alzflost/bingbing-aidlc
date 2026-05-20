# Requirements Clarification Questions

답변 분석 중 몇 가지 추가 확인이 필요한 부분이 있습니다.

---

## Clarification 1: AgentCore Evaluations & Runtime 의미 확인
Q3에서 "C 근데 Evaluation이랑 Runtime의미 잘모르겠어"라고 하셨습니다.

간단히 설명드리면:
- **AgentCore Evaluations**: 에이전트 응답 품질을 자동 평가하는 서비스. 커스텀 지표(화자 식별 정확도, 가드레일 누락률 등)를 정의하고 런타임에 측정.
- **AgentCore Runtime**: 에이전트 실행 환경을 관리하는 서비스. 에이전트 배포, 세션 관리, 도구 호출 라우팅 등을 처리.

이 설명을 바탕으로, 4종 전체 사용(C)을 유지할까요?

A) 4종 전체 유지 (Memory + Policy + Evaluations + Runtime)
B) 3종으로 축소 (Memory + Policy + Evaluations) — Runtime은 Strands Agent SDK가 대체
C) 2종 + Evaluations 선택적 (Memory + Policy 필수, Evaluations는 시간 여유 시)
D) Other (please describe after [Answer]: tag below)

[Answer]: B 런타임은 굳이.. ECS로 하고 strands로만 하는걸로

---

## Clarification 2: Strands Agent SDK 사용 범위
Q4에서 "Strands 쓸꺼야"라고 하셨습니다. Strands Agents SDK의 구체적 사용 범위를 확인합니다.

A) Strands를 메인 오케스트레이터로 — 페르소나 분기, 도구 호출, 대화 관리 모두 Strands로
B) Strands + Multi-agent — 페르소나별 sub-agent를 Strands로 구성
C) Strands 기본 + AgentCore Runtime 연동 — Strands 에이전트를 AgentCore Runtime에 배포
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Clarification 3: ECS + Fargate 배포 상세
Q9에서 "ECS + Fargate로 서버리스 배포 + D옵션 몇개"라고 하셨습니다. 구체적으로 어떤 구성인지 확인합니다.

A) 메인 서비스(Strands Agent + API)는 ECS Fargate, 이벤트 처리(Reflection 등)는 Lambda
B) 전체 ECS Fargate — Lambda 없이 모든 컴포넌트를 컨테이너로
C) API Gateway + Lambda(경량 엔드포인트) + ECS Fargate(에이전트 코어 로직)
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Clarification 4: 동적 페르소나 자동 등록 범위
Q15에서 "C로 하되 AI 판단하에 대화를 통해 유추해서 자동등록도"라고 하셨습니다. 자동 등록의 범위를 확인합니다.

A) 대화 중 새 탑승자 감지 시 AI가 기본 프로파일 자동 생성 (이름, 추정 연령대, 기본 권한)
B) 대화 패턴 분석으로 기존 페르소나 속성 자동 업데이트 (선호도, 말투 등)
C) A + B 모두 — 신규 등록도 하고, 기존 프로파일도 대화 기반으로 점진적 보강
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Clarification 5: React 프론트엔드 범위
Q6에서 React + TypeScript를 선택하셨습니다. 데모 UI의 구체적 범위를 확인합니다.

A) 최소 데모 — 화자 라벨 + 텍스트 응답 실시간 표시 (채팅 형태)
B) 중간 데모 — A + 좌석 배치도 시각화 + 페르소나별 색상 구분
C) 풀 데모 — B + 권한 매트릭스 대시보드 + 메모리 상태 표시 + Evaluation 지표
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---
