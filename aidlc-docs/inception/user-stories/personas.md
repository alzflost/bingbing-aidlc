# Personas

> Role-based Persona 설계: 페르소나를 고정 가족 역할이 아닌 **역할 속성 조합**으로 정의.
> 데모용 프리셋 5개를 제공하되, 내부 엔진은 역할 속성 기반으로 동작.
> 7시간 타임박스 내 구현 가능한 범위로 한정.

---

## 역할 속성 모델

| 속성 | 타입 | 값 | 설명 |
|---|---|---|---|
| `driver` | boolean | true/false | 현재 운전석에 앉아있는가 (동적, 트립마다 변경 가능) |
| `age_group` | enum | adult/teen/child/elder | 연령대 (프로파일에 저장) |
| `account_owner` | boolean | true/false | 차량 계정 소유자인가 |
| `relationship` | enum | owner/family/guest | 차량과의 관계 |

### 권한 결정 규칙 (CEDAR 정책 기반)

```
IF driver = true AND age_group = adult → 운전 제어 포함 Full 권한
IF driver = false AND age_group = adult AND relationship = family → 운전 제어 제외 Full
IF driver = false AND age_group = adult AND relationship = guest → 정보 조회만
IF age_group = child → 엔터테인먼트만 + 콘텐츠 필터 + 안전 가드레일
IF age_group = elder → 본인 좌석 환경 + 재확인 패턴
IF age_group = teen → 엔터테인먼트 + 웹검색 + 콘텐츠 필터(완화)
```

### 응답 스타일 결정 규칙

```
IF age_group = child → 친근, 단순, 격려적, 짧은 문장
IF age_group = elder → 존칭, 핵심만, 느린 발화, 재확인
IF age_group = teen → 캐주얼, 자율성 존중
IF age_group = adult AND driver = true → 효율적, 정보 밀도 높음, 최소 인터랙션
IF age_group = adult AND driver = false → 협업적, 옵션 제시
IF relationship = guest → 중립, 거리감 유지
```

---

## 데모용 프리셋 5개

### Preset 1: 운전자 (성인)

| 항목 | 내용 |
|---|---|
| actor_id 예시 | actor_father, actor_mother, actor_adult_child (운전석 탑승 시) |
| 역할 속성 | `driver=true, age_group=adult, relationship=owner|family` |
| 권한 | Full (모든 도구 접근 가능, 운전 제어 포함) |
| 응답 스타일 | 효율적, 정보 밀도 높음, 옵션 2~3개 제시 |
| 핵심 니즈 | 빠른 정보 접근, 운전 중 최소 인터랙션 |
| 데모 시나리오 | 경로 안내, 차량 제어, 전화 발신, 개인화 추천 |

#### 권한 상세

| 도구 | 허용 |
|---|---|
| 내비게이션 (목적지 변경) | ✅ |
| 차량제어 (운전 관련) | ✅ |
| 차량제어 (본인 좌석 환경) | ✅ |
| 뮤직 (재생/변경) | ✅ |
| BT전화 발신 | ✅ |
| 웹검색 | ✅ |

---

### Preset 2: 동승자 (성인)

| 항목 | 내용 |
|---|---|
| actor_id 예시 | actor_mother, actor_father (조수석/뒷좌석 시) |
| 역할 속성 | `driver=false, age_group=adult, relationship=owner|family` |
| 권한 | Full (운전 제어 제외) |
| 응답 스타일 | 협업적, 옵션 제시 |
| 핵심 니즈 | 일정 조율, 추천, 전화, 콘텐츠 |
| 데모 시나리오 | 식당 추천(개인 선호 기반), 전화, 음악 |

#### 권한 상세

| 도구 | 허용 |
|---|---|
| 내비게이션 (목적지 변경) | ✅ |
| 차량제어 (운전 관련) | ❌ |
| 차량제어 (본인 좌석 환경) | ✅ |
| 뮤직 (재생/변경) | ✅ |
| BT전화 발신 | ✅ |
| 웹검색 | ✅ |

---

### Preset 3: 어린이 (child)

| 항목 | 내용 |
|---|---|
| actor_id 예시 | actor_child_1, actor_child_2 |
| 역할 속성 | `driver=false, age_group=child, relationship=family` |
| 권한 | 최소 (엔터테인먼트 일부만, 안전 최우선) |
| 응답 스타일 | 친근, 단순, 격려적, 짧은 문장 |
| 핵심 니즈 | 퀴즈, 음악, 간단한 게임, 호기심 해결 |
| 데모 시나리오 | 차량 제어 시도 → 안전 차단, 콘텐츠 추천 |

#### 권한 상세

| 도구 | 허용 |
|---|---|
| 내비게이션 (목적지 변경) | ❌ |
| 차량제어 (운전 관련) | ❌ |
| 차량제어 (본인 좌석 환경) | ⚠️ 제한 (고속 주행 중 차단, 정차 시 부모 확인) |
| 뮤직 (재생/변경) | ⚠️ 연령 필터 + 볼륨 안전 한계(60%) |
| BT전화 발신 | ❌ |
| 웹검색 | ⚠️ 콘텐츠 필터 (폭력·성인·공포 차단) |

#### 가드레일
- 모든 차량 운전 제어 차단
- 고속도로 주행 중 좌석 환경 제어(창문 등) 차단
- 콘텐츠 연령 필터 적용
- 볼륨 안전 한계 적용 (최대 60%)
- 부적절 요청 시 "재미있는 다른 것" 우회 응답
- 전화 발신 완전 차단

---

### Preset 4: 어르신 (elder)

| 항목 | 내용 |
|---|---|
| actor_id 예시 | actor_grandma, actor_grandpa |
| 역할 속성 | `driver=false, age_group=elder, relationship=family` |
| 권한 | 제한 (본인 좌석 환경 + 정보 조회) |
| 응답 스타일 | 존칭, 핵심만, 느린 발화(0.8x), 중요 동작 시 1회 재확인 |
| 핵심 니즈 | 좌석 환경 조절, 간단한 정보 조회 |
| 데모 시나리오 | "에어컨 줄여줘", 전화 → 재확인 후 실행 |

#### 권한 상세

| 도구 | 허용 |
|---|---|
| 내비게이션 (목적지 변경) | ❌ |
| 차량제어 (운전 관련) | ❌ |
| 차량제어 (본인 좌석 환경) | ✅ |
| 뮤직 (재생/변경) | ✅ |
| BT전화 발신 | ⚠️ 확인 후 |
| 웹검색 | ✅ |

#### 가드레일
- 내비게이션/운전 제어 차단
- 전화 발신 시 1회 재확인 필수
- 응답 1문장 우선
- 발화 속도 0.8x

---

### Preset 5: 게스트 (guest)

| 항목 | 내용 |
|---|---|
| actor_id 예시 | actor_guest |
| 역할 속성 | `driver=false, age_group=adult, relationship=guest` |
| 권한 | 최소 (정보 조회만) |
| 응답 스타일 | 중립, 친절하지만 거리감 유지 |
| 핵심 니즈 | 기본 정보 조회 (날씨, 시간, 도착 예정) |
| 데모 시나리오 | 정보 질문 → 응답, 제어 시도 → 차단 |

#### 권한 상세

| 도구 | 허용 |
|---|---|
| 내비게이션 (목적지 변경) | ❌ |
| 차량제어 (운전 관련) | ❌ |
| 차량제어 (본인 좌석 환경) | ❌ |
| 뮤직 (재생/변경) | ❌ |
| BT전화 발신 | ❌ |
| 웹검색 | ✅ (정보 조회 only) |

#### 가드레일
- 메모리 미저장 (트립 종료 시 모든 발화 데이터 삭제)
- 모든 제어 기능 차단
- 정보 조회만 허용
- 개인화 메모리 미적용

---

## 동시 발화 우선순위 (역할 속성 기반)

| 우선순위 | 조건 | 비고 |
|---|---|---|
| 1순위 | driver=true + 안전 관련 요청 | 절대 우선 |
| 2순위 | driver=true + 비안전 요청 | 약간 우선 |
| 3순위 | age_group=adult, relationship=family | 선착순 |
| 4순위 | age_group=elder | 선착순 |
| 5순위 | age_group=child/teen | 큐잉 후 순차 |
| 6순위 | relationship=guest | 최후순위 |

> 정차 중에는 driver 우선권 해제, 전원 선착순.
> 동시 발화 판정: 500ms 이내 겹침.

---

## 설계 장점

1. **유연한 가족 구성**: 엄마가 운전해도, 성인 자녀가 운전해도 자연스럽게 권한 전환
2. **CEDAR 정책 단순화**: 역할 속성 기반 규칙 → 프리셋 추가 없이 새 조합 커버
3. **데모 단순성 유지**: 5개 프리셋으로 시연, 내부는 역할 엔진
4. **확장성**: 새 연령대(teen) 추가 시 age_group 값만 추가
5. **피치 어필**: "누구든 운전석에 앉으면 운전자 권한" = 차별화 포인트
