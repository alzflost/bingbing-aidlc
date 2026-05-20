# Functional Design Plan — All Units (병렬)

5개 유닛 동시 Functional Design. 아래 질문에 답변 후 전체 유닛의 상세 비즈니스 로직을 생성합니다.

---

## Questions

### Question 1: 운전자 프로필 인증 방식
프론트엔드에서 운전자가 프로필을 인증하는 UI 방식을 확인합니다.

A) 프로필 목록 선택 — 차량에 등록된 프로필 리스트에서 터치 선택
B) PIN 입력 — 프로필 선택 + 4자리 PIN 확인
C) 음성 인증 — "나 OO이야" 발화로 인증 (Transcribe 기반)
D) 자동 (목업) — 시동 ON 시 마지막 운전자 프로필 자동 선택 (데모 단순화)
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2: 미등록 가족 임시 프로파일 저장 위치
미등록 가족(DDB에 없지만 자기소개한 사람)의 임시 프로파일을 어디에 저장할까요?

A) DynamoDB에 바로 등록 — 자기소개 시 vehicle_profiles에 추가 (영구)
B) Valkey STM에만 — 트립 동안만 유지, 트립 종료 시 삭제
C) Valkey STM + 트립 종료 시 운전자 확인 후 DDB 등록 — "OO를 가족으로 등록할까요?"
D) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Question 3: 도구(Tool) 목록 확정
Agent Service의 Tool Registry에 등록할 도구 목록을 확인합니다. 실제 외부 API 연동 vs mock?

A) 전부 mock — 모든 도구가 하드코딩된 응답 반환 (빠른 개발)
B) 일부 실제 — 웹검색(실제) + 나머지 mock (내비, 차량제어, 뮤직, 전화)
C) 전부 실제 연동 — 각 도구별 실제 API 연동
D) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 4: 페르소나 프롬프트 관리 방식
역할 속성 조합별 프롬프트 템플릿을 어떻게 관리할까요?

A) 파일 기반 — `shared/prompts/` 디렉토리에 YAML/JSON 파일로 관리
B) DynamoDB — 프롬프트 템플릿도 DB에 저장 (런타임 수정 가능)
C) 코드 내장 — Python 코드에 직접 정의 (단순)
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 5: Frontend 상태 관리
React 앱의 상태 관리 라이브러리를 확인합니다.

A) Zustand — 경량, 간단
B) Redux Toolkit — 풀 기능, 미들웨어
C) React Context + useReducer — 라이브러리 없이
D) Jotai/Recoil — 원자적 상태
E) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 6: Reflection Agent 패턴 추출 방식
트립 종료 시 STM에서 LTM으로 승격할 때, 패턴 추출을 어떻게 할까요?

A) LLM 기반 — Claude에게 발화 이력을 주고 "이 사용자의 선호도를 요약해줘" 요청
B) 규칙 기반 — 키워드 매칭 + 빈도 분석으로 선호도 추출
C) 하이브리드 — 규칙으로 1차 필터 + LLM으로 요약/정제
D) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## Execution Plan (답변 후 실행)

- [x] Step 1: 공유 도메인 모델 정의 (shared/models)
- [x] Step 2: Unit 1 (Infrastructure) — Terraform 모듈 설계
- [x] Step 3: Unit 2 (API Service) — 비즈니스 로직 상세
- [x] Step 4: Unit 3 (Agent Service) — 비즈니스 로직 상세
- [x] Step 5: Unit 4 (Reflection Lambda) — 비즈니스 로직 상세
- [x] Step 6: Unit 5 (Frontend) — 컴포넌트 설계 + 상태 관리

---

답변 완료 후 알려주세요.
