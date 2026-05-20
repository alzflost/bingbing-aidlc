# User Stories

> Role-based Persona 기반. 페르소나를 역할 속성 조합으로 정의.
> 데모용 프리셋 5개: 운전자(성인), 동승자(성인), 어린이, 어르신, 게스트
> 데모 핵심 카드: S3(같은 말, 다른 응답) + S4(가드레일)

스토리 분류: 시나리오 기반 (S1~S7 + 시스템 스토리)
우선순위: P0(데모 필수) / P1(데모 보강) / P2(시간 여유 시)
Acceptance Criteria: Given/When/Then 표준
비기능: 응답 3초 이내, 화자 식별 90%+, 동시 발화 500ms 윈도우

---

## S3: 같은 말, 다른 추천 [데모 핵심 카드 #1]

### US-S3-01: 화자별 개인화 응답 [P0]

**As a** 등록된 탑승자
**I want** 같은 말을 해도 내 선호도에 맞는 추천을 받길
**So that** 매번 취향을 설명하지 않아도 된다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 동승자(성인, 비건 선호 LTM) | "배고프다" 발화 | AgentCore Memory 프로파일 조회 → 비건 식당 추천 (3초 이내) |
| 2 | 운전자(성인, 고기 선호 LTM) | "배고프다" 발화 | AgentCore Memory 프로파일 조회 → 고기집 추천 (3초 이내) |
| 3 | 게스트(메모리 없음) | "배고프다" 발화 | 메모리 조회 스킵 → 일반 인기 식당 추천 |
| 4 | AgentCore Memory 조회 실패 | 등록 화자 발화 | 3초 타임아웃 → 일반 추천 fallback + 에러 로깅 |
| 5 | 어린이(공룡 관심 LTM) | "심심해" 발화 | 아이 LTM 기반 공룡 퀴즈/콘텐츠 추천 |

---

## S4: 어린이 안전 모드 [데모 핵심 카드 #2]

### US-S4-01: 어린이 차량 제어 차단 [P0]

**As a** 운전자 (성인)
**I want** 어린이가 위험한 차량 제어를 요청해도 차단되길
**So that** 주행 중 안전이 보장된다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | age_group=child + 고속도로 주행 중 | "창문 열어줘" 발화 | CEDAR: `age_group=child AND driving_speed>80` → 차단 → 맞춤 거절 ("OO야, 지금 고속도로라 위험해. 도착하면 열어줄게!") |
| 2 | age_group=child | "전화 걸어줘" 발화 | CEDAR: `age_group=child AND tool=bt_call` → 차단 → 우회 ("대신 재미있는 퀴즈 할까?") |
| 3 | age_group=child | "시끄러운 음악 틀어줘" 발화 | 연령 필터 + 볼륨 60% 제한 → 적합 콘텐츠 + 적정 볼륨 |
| 4 | age_group=child + 정차 중 | "창문 열어줘" 발화 | CEDAR: `driving_speed=0` → 조건부 허용 → 운전자에게 확인 요청 |
| 5 | age_group=child | "목적지 바꿔줘" 발화 | CEDAR: `age_group=child AND tool=navigation` → 차단 → "그건 운전하시는 분한테 부탁해봐!" |

---

## S1: 시동 ON — 화자별 차등 환영

### US-S1-01: 화자 인식 및 환영 [P0]

**As a** 탑승자 (모든 프리셋)
**I want** 시동이 켜지면 나를 인식하고 맞춤 환영을 해주길
**So that** 바로 개인화된 서비스를 받을 수 있다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 운전석 채널에 등록된 성인 탑승 | 시동 ON | 좌석 채널 매핑 → driver=true 설정 → LTM 조회 → 개인화 환영 (3초 이내) |
| 2 | 뒷좌석에 어린이 탑승 | 시동 ON + 첫 발화 감지 | 어휘/말투 휴리스틱 → age_group=child 추정 → 연령 맞춤 환영 |
| 3 | 미매핑 채널에서 음성 감지 | 시동 ON | 자기소개 요청 ("안녕하세요! 이름을 말씀해주시겠어요?") |
| 4 | 자기소개 요청에 3초 내 응답 없음 | 타임아웃 | relationship=guest 자동 처리 + 기본 환영 |
| 5 | 인식 처리 지연 3초 초과 | 시스템 지연 | 기본 환영 즉시 제공 + 백그라운드 인식 계속 |

---

## S2: 동시 발화 충돌 해소

### US-S2-01: 역할 기반 동시 발화 처리 [P0]

**As a** 운전자
**I want** 여러 사람이 동시에 말해도 안전 관련 요청이 우선 처리되길
**So that** 주행 중 안전이 지연되지 않는다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 고속도로 주행 중 | child "만화 틀어줘" + driver "경로 안내해줘" (500ms 이내) | driver + 안전/내비 → 절대 우선 → child 큐잉 → 순차 처리 |
| 2 | 정차 중 | 동승자(성인) "식당 찾아줘" + child "노래 틀어줘" (500ms 이내) | driver 우선권 해제 → 선착순 처리 |
| 3 | 주행 중 | elder "에어컨 줄여줘" + driver "볼륨 올려줘" (500ms 이내) | 둘 다 비안전 → driver 약간 우선 |
| 4 | 큐잉된 요청 존재 | 우선 요청 처리 완료 | 큐잉 요청 자동 처리 + 해당 화자 스타일로 응답 (3초 이내) |

---

## S5: 어르신 응답 단순화

### US-S5-01: 어르신 맞춤 응답 [P1]

**As a** 어르신 (age_group=elder)
**I want** 간단하고 천천히 답변을 받길
**So that** 쉽게 이해하고 사용할 수 있다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | age_group=elder | "에어컨 줄여줘" 발화 | 1문장 핵심 응답 + TTS 0.8x |
| 2 | age_group=elder | 전화 발신 요청 | 1회 재확인 → 확인 후 실행 |
| 3 | age_group=elder | 복잡한 질문 | 1문장 핵심 → 추가 정보는 요청 시에만 |
| 4 | age_group=elder | 내비 변경 시도 | CEDAR 차단 → 정중 거절 |

---

## S6: 운행 후 화자별 메모리 누적

### US-S6-01: 트립 종료 시 학습 [P1]

**As a** 등록된 탑승자
**I want** 운행 중 내 선호가 자동으로 학습되길
**So that** 다음 탑승 시 더 나은 개인화를 받는다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 트립 중 동승자(성인)가 비건 식당 선택 | 시동 OFF | Reflection → LTM preference "비건 선호" confidence 증가 |
| 2 | 트립 중 어린이가 공룡 퀴즈 반응 | 시동 OFF | Reflection → LTM "공룡 콘텐츠" 선호 저장 |
| 3 | 게스트 발화 존재 | 시동 OFF | STM 전량 삭제, LTM 미적재 |
| 4 | Reflection 실패 | 시동 OFF | 에러 로깅 + STM 보존 → 다음 시동 시 재시도 |

---

## S7: 미등록 화자 처리

### US-S7-01: 게스트 프라이버시 보호 [P1]

**As a** 게스트 탑승자
**I want** 내 발화가 저장되지 않길
**So that** 프라이버시가 보호된다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 3단계 매핑 모두 실패 | 발화 | relationship=guest 자동 처리, 정보 조회만 허용 |
| 2 | relationship=guest | 차량 제어 요청 | CEDAR 차단 → 중립 톤 거절 |
| 3 | relationship=guest | "오늘 날씨 어때?" | 정상 응답 (3초 이내) |
| 4 | 게스트 발화 이력 | 트립 종료 | STM 전량 삭제, LTM 미적재 |

---

## 시스템 스토리

### US-SYS-01: 화자 매핑 상태 머신 [P0]

**As a** 시스템
**I want** 3단계 매핑 전략으로 화자를 식별하고 역할 속성을 부여하길
**So that** 모든 시나리오에서 올바른 권한/스타일이 적용된다

> 매핑 전략:
> 1. Primary — 좌석 채널 기반 (운전석 = driver=true)
> 2. Secondary — 자기소개 바인딩 (spk_N ↔ actor_id)
> 3. Tertiary — 어휘/말투 휴리스틱 (age_group 추정)
>
> 핵심: 운전석 채널 탑승자에게 자동으로 driver=true 부여

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | Idle 상태 | 시동 ON | Onboarding → 좌석 점유 확인 → 운전석 채널 = driver=true |
| 2 | Onboarding + 채널 매핑 성공 | 등록 채널 발화 | Active 전환, 역할 속성 바인딩 확정 |
| 3 | Onboarding + 미매핑 채널 | 자기소개 응답 수신 | 페르소나 바인딩 → Active |
| 4 | Active + 미등록 음성 | 3단계 실패 | relationship=guest 처리 |
| 5 | Active | 시동 OFF | Trip-end → Reflection → Idle |
| 6 | 상태 전환 예외 | 에러 | 이전 상태 유지 (fail-safe) + 로깅 |

### US-SYS-02: 평가 지표 실측 [P2]

**As a** 시스템 운영자
**I want** 핵심 품질 지표를 측정하길
**So that** 시스템 품질을 모니터링할 수 있다

**Acceptance Criteria:**

| # | Given | When | Then |
|---|---|---|---|
| 1 | 화자 발화 처리 완료 | 매 응답 | 화자 식별 정확도 업데이트 (목표 90%+) |
| 2 | 페르소나 맞춤 응답 생성 | 매 응답 | 페르소나 일관성 업데이트 (목표 95%+) |
| 3 | CEDAR Policy 평가 | 도구 호출 시도 | 가드레일 누락률 업데이트 (목표 0%) |
| 4 | 대시보드 조회 | 운영자 요청 | 3개 지표 + 트립별 추이 표시 |

---

## 페르소나-스토리 매핑

| 프리셋 | 관련 스토리 | 데모 등장 |
|---|---|---|
| 운전자 (성인) | US-S1-01, US-S3-01, US-S2-01 | ✅ 핵심 |
| 동승자 (성인) | US-S1-01, US-S3-01, US-S6-01 | ✅ 핵심 |
| 어린이 | US-S1-01, US-S4-01, US-S2-01, US-S6-01 | ✅ 핵심 |
| 어르신 | US-S5-01 | ⚠️ 시간 여유 시 |
| 게스트 | US-S7-01, US-S3-01 | ⚠️ 시간 여유 시 |

---

## 비기능 요구사항 요약

| 항목 | 목표값 |
|---|---|
| 응답 지연 | 3초 이내 |
| 화자 식별 정확도 | 90%+ |
| 동시 발화 윈도우 | 500ms |
| 메모리 조회 타임아웃 | 3초 |
| 가드레일 누락률 | 0% |
| TTS 발화 속도 (elder) | 0.8x |
| 볼륨 한계 (child) | 최대 60% |
| Transcribe 최대 화자 | 5명 |
| STM 보존 | 트립 종료 후 24시간 |
