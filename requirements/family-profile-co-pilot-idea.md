# Family Profile Co-pilot — Kiro 기획 자료

> **목적**: AWS Summit Seoul 2026 AI-DLC 빌딩 세션(7시간) 출품작 기획. 본 문서는 Kiro의 spec-driven 워크플로우(requirements → design → tasks)에 입력될 Inception 단계 산출물이자, `.kiro/steering/` 스티어링 파일 작성의 근거 자료.
>
> **버전**: v0.1 (Inception draft)
> **작성 시점**: 2026-05-20
> **세션**: AWS Summit Seoul 2026 AI-DLC Building Session (5/20, COEX)

---

## 1. 한 줄 정의

> **차량 내 다중 화자를 실시간 구분하고, 화자별 페르소나에 맞춰 응답·기능·가드레일을 차등 적용하는 AI Car Agent.**

기존 차량 음성 비서가 "한 사람을 위한 어시스턴트"였다면, 이 프로젝트는 "차 안의 모든 사람을 각자에게 맞게 응대하는 어시스턴트"로 재정의.

---

## 2. 배경 — 왜 지금 이 주제인가

### 2.1 AWS 2026 AI 트렌드 정합성

| 트렌드 | 본 프로젝트 매핑 |
|---|---|
| Bedrock AgentCore Memory (Episodic) | 화자별 `actor_id` 분리 메모리 |
| AgentCore Policy (CEDAR) | 어린이·노약자·게스트 권한 차등 |
| AgentCore Evaluations | "올바른 화자에게 올바른 응답" 평가 |
| Multi-agent / A2A | (선택) 페르소나별 sub-agent 분리 |
| Nova 2 Sonic 한계 보완 | native S2S가 다중 화자 신원 구분 미제공 → Transcribe diarization으로 빈틈 보강 |
| in-vehicle assistant 플래그십 | re:Invent 2025 차량 콕핏 데모와 정렬 |

### 2.2 차별화 포인트

기존 차량 음성 비서는 "운전자 단일 사용자" 가정. 가족 단위·B2B 카풀·렌터카·택시 등 **다중 화자 시나리오에서 작동하는 차량 에이전트는 시장에 거의 없음**.

---

## 3. 핵심 컨셉

### 3.1 처리 흐름 (개념)

```
음성 입력
   ↓
Transcribe Streaming (diarization: spk_0, spk_1, ...)
   ↓
화자→페르소나 매핑 레이어
   ↓
AgentCore Memory (actor_id별 프로파일 조회)
   ↓
AgentCore Policy (페르소나별 권한 enforce)
   ↓
Bedrock (페르소나 프롬프트 분기) + Tool 호출
   ↓
응답 생성 (Polly 또는 Nova Sonic)
```

### 3.2 기술적 정밀성 — diarization ≠ identification

- Transcribe diarization은 익명 라벨(`spk_0`~`spk_9`) 제공, 실명 매핑 미제공
- 스트리밍 시 5명까지 정확도 양호, 최대 30명
- 실명 매핑은 별도 레이어 필요

### 3.3 매핑 전략 (7시간 스코프 적합)

1. **좌석 채널 기반** (Primary) — 운전석 마이크 채널 = 주 운전자 고정
2. **트립 시작 1회 자기소개** (Secondary) — 시동 후 "탑승하신 분들 말씀해주세요" → spk_N ↔ 페르소나 바인딩
3. **콘텐츠 기반 휴리스틱** (Tertiary) — 어휘·말투로 어린이/노약자 보정

→ Voiceprint 등록 시스템은 스코프 외 (향후 확장 항목).

---

## 4. 페르소나 정의

| 페르소나 | actor_id | 역할 | 권한 | 응답 스타일 |
|---|---|---|---|---|
| **아빠** | `actor_father` | 주 운전자, 계정 소유자 | Full | 효율적, 정보 밀도 높음 |
| **엄마** | `actor_mother` | 조수석, 일정 관리 주체 | Full (운전 제어 제외) | 협업적, 옵션 제시 |
| **아이** | `actor_child` | 8세, 뒷좌석 | 제한 (콘텐츠/엔터테인먼트만) | 친근, 단순, 안전 |
| **할머니** | `actor_elder` | 뒷좌석 동승자 | 제한 (본인 좌석 환경만) | 단순, 느린 발화, 1회 재확인 |
| **게스트** | `actor_guest` | 미등록 화자 | 최소 (정보 조회만) | 중립, 메모리 미적용 |

---

## 5. 핵심 시나리오 (7건)

### S1. 시동 ON — 화자별 차등 환영
- **트리거**: 시동 ON + 좌석 점유 센서
- **흐름**: 아빠 운전석 탑승 → "오늘 장모님 댁 막힘 없습니다. 평소 들르시던 안성휴게소 경유 추가할까요?" / 뒷좌석 아이 발화 감지 → "OO야, 가는 길에 공룡 퀴즈 같이 할까?"
- **메모리 활용**: 아빠 휴게소 루틴 (LTM Preference), 아이 콘텐츠 선호 (LTM Preference)

### S2. 동시 발화 충돌 해소
- **트리거**: 운전자와 동승자 발화 시간 겹침
- **흐름**: 아이 "만화 틀어줘!" + 아빠 "경로 다시 안내해줘" → AgentCore Policy enforce → 운전자 우선 처리, 아이에게 페르소나 맞춤 거절
- **킬러 포인트**: governance 시연

### S3. 같은 말, 다른 추천
- **트리거**: 동일 발화를 다른 화자가 함
- **흐름**: 엄마 "배고프다" → 비건 식당 추천 / 아빠 "배고프다" → 고기집 추천
- **킬러 포인트**: 화자 구분의 직접적 가치 증명

### S4. 어린이 안전 모드
- **트리거**: 아이 발화 + 제한 권한 도구 호출 시도
- **흐름**: 아이 "창문 다 열어줘!" (고속도로 주행 중) → 차량제어 차단(Policy, 고속 주행 중 어린이의 차창 제어 금지) → "OO야, 지금 고속도로라 위험해. 도착하면 열어줄게!" 우회 / 아이 "랩 노래 시끄럽게 틀어줘" → 연령 적합 콘텐츠 + 볼륨 안전 한계 → 다른 음악 추천 + 적정 볼륨
- **킬러 포인트**: 차량 안전 가드레일

### S5. 노약자 응답 단순화
- **트리거**: 할머니 페르소나 발화
- **흐름**: "에어컨 좀 줄여줄래" → 단순 핵심만 응답 + 느린 발화 속도 + 필요 시 재확인
- **메모리 활용**: 노약자 응답 verbosity 설정 (LTM Preference)

### S6. 운행 후 화자별 메모리 누적
- **트리거**: 시동 OFF (트립 종료)
- **흐름**: Reflection agent가 화자별 에피소드를 분리해 각 `actor_id`에 저장. 엄마 비건 선택 강화, 아이 공룡 퀴즈 반응 시간 누적, 아빠 휴게소 패턴 재확인
- **킬러 포인트**: AgentCore Episodic Memory의 학습 시연

### S7. 미등록 화자 처리
- **트리거**: 매핑되지 않은 음성 감지
- **흐름**: "게스트" 처리, 기본 모드 응답, 개인화 메모리 미적용, 트립 종료 시 발화 미저장
- **킬러 포인트**: 프라이버시 by design

---

## 6. 시스템 아키텍처 초안

### 6.1 컴포넌트

| 컴포넌트 | 역할 | 구현 |
|---|---|---|
| Voice Ingestion | 마이크 입력 + 좌석 채널 라우팅 | (mock) WebRTC + 채널 메타 |
| Diarization Service | 화자 라벨링 | Amazon Transcribe Streaming |
| Speaker Mapping Layer | spk_N ↔ actor_id 매핑 | 자체 구현 (state machine) |
| Profile Resolver | actor_id로 페르소나 조회 | AgentCore Memory `getMemory` |
| Policy Enforcer | 페르소나별 도구 권한 검사 | AgentCore Policy (CEDAR) |
| Orchestrator | 페르소나 프롬프트 분기 + 도구 호출 | LangGraph |
| Response Generator | 응답 생성 | Bedrock (Claude) + Polly 또는 Nova Sonic |
| Memory Writer | 화자별 에피소드 적재 | AgentCore Memory `putEvent` |
| Reflection Agent | 트립 종료 시 패턴 추출 | AgentCore Episodic Memory |
| Evaluation | 응답 품질 모니터링 | AgentCore Evaluations |

### 6.2 핵심 상태 — Speaker Mapping State Machine

```
[Idle]
   ↓ 시동 ON
[Onboarding] — 좌석 점유 확인, 자기소개 요청
   ↓ 자기소개 완료
[Active] — spk_N ↔ actor_id 바인딩 유지
   ↓ 신규 음성 감지
   ├─→ 기존 매핑 → 응답
   └─→ 미등록 → [Guest] (메모리 미적용)
   ↓ 좌석 변경 / 새 탑승
[Re-mapping] — 신규 화자 자기소개 요청
   ↓ 시동 OFF
[Trip-end] — Reflection agent 실행 → [Idle]
```

### 6.3 데이터 흐름 (트립 단위)

1. `tripId` 생성 (시동 ON 시점)
2. `tripId`별 STM (Valkey) — 화자별 발화 이력
3. `actor_id`별 LTM (Bedrock AgentCore Memory) — 페르소나 프로파일
4. Reflection 단계에서 STM → LTM 승격 (화자별 분리)

---

## 7. AI-DLC 단계별 산출물

### 7.1 Inception — Units of Work (요구사항 단위)

- [ ] UoW-01: 페르소나 4종 + 게스트 정의 (권한 매트릭스 포함)
- [ ] UoW-02: 화자→페르소나 매핑 레이어 (3 전략)
- [ ] UoW-03: 동시 발화 충돌 해소 정책
- [ ] UoW-04: 어린이 콘텐츠 가드레일
- [ ] UoW-05: 노약자 응답 스타일 변형 규칙
- [ ] UoW-06: 게스트 프라이버시 정책 (메모리 미적용 + 미저장)
- [ ] UoW-07: 화자별 메모리 분리 (`actor_id` 스코프)
- [ ] UoW-08: Reflection agent 화자별 패턴 추출
- [ ] UoW-09: AgentCore Evaluations 커스텀 지표 (화자 오인식률, 가드레일 누락률)

### 7.2 Construction — 핵심 컴포넌트 작업

- [ ] Task-01: Transcribe Streaming 통합 (다중 화자 라벨)
- [ ] Task-02: Speaker Mapping State Machine 구현
- [ ] Task-03: 페르소나 프롬프트 템플릿 5종
- [ ] Task-04: AgentCore Policy 규칙 작성 (CEDAR)
- [ ] Task-05: LangGraph 페르소나 분기 노드 추가
- [ ] Task-06: AgentCore Memory `actor_id` 스코프 적용
- [ ] Task-07: Reflection agent 화자별 분리 로직
- [ ] Task-08: 데모용 UI mock (화자 라벨 + 응답 실시간 표시)

### 7.3 Operations — 운영·평가

- [ ] Ops-01: AgentCore Evaluations 지표 정의
  - 화자 식별 정확도 (mapping accuracy)
  - 페르소나 일관성 (correct persona response rate)
  - 가드레일 누락률 (policy violation rate)
- [ ] Ops-02: 운행 후 reflection 품질 점검
- [ ] Ops-03: CloudWatch 대시보드 (실시간 화자별 응답 흐름)

---

## 8. 가드레일 & 정책

### 8.1 권한 매트릭스

| 도구 | 아빠 | 엄마 | 아이 | 할머니 | 게스트 |
|---|---|---|---|---|---|
| 내비게이션 (목적지 변경) | ✅ | ✅ | ❌ | ❌ | ❌ |
| 차량제어 (운전 관련) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 차량제어 (본인 좌석 환경) | ✅ | ✅ | ⚠️ 제한 | ✅ | ❌ |
| 뮤직 (재생/변경) | ✅ | ✅ | ⚠️ 연령 필터 | ✅ | ❌ |
| BT전화 발신 | ✅ | ✅ | ❌ | ⚠️ 확인 후 | ❌ |
| 웹검색 | ✅ | ✅ | ⚠️ 콘텐츠 필터 | ✅ | ✅ (정보 only) |
| 브라우저제어 | ✅ | ✅ | ⚠️ 연령 필터 | ✅ | ❌ |

### 8.2 콘텐츠 필터 (어린이)

- 폭력·성인·공포 콘텐츠 차단
- 검색 결과 연령 적합도 재정렬
- 부적절 요청 시 "재미있는 다른 것" 우회 응답

### 8.3 프라이버시

- 게스트 발화: 메모리 미저장
- 어린이 발화: 부모 권한 하에서만 LTM 적재
- 트립 단위 STM은 일정 기간 후 자동 삭제

---

## 9. 평가 기준 매핑

| 평가 축 | 본 프로젝트 어필 전략 |
|---|---|
| AI-DLC 충실도 | `aidlc-docs/` 구조 유지 + Mob Elaboration 시연 (페르소나 엣지 케이스 토론 풍부) |
| Technical Implementation | AgentCore 4종(Memory/Policy/Evaluations/Runtime) 활용, LangGraph 자산 재활용 |
| Business Value | 가족·B2B 카풀·렌터카·택시·OEM PoC 확장 시나리오 |
| Innovation | "차량 내 다중 화자 페르소나 분기"는 시장 빈 영역 |
| Presentation | S3(같은 말, 다른 응답) + S4(가드레일) 두 장면이 핵심 카드 |

---

## 10. 7시간 타임박스 계획

| 시간 | 단계 | 작업 |
|---|---|---|
| 0:00–0:30 | Setup | Kiro 워크스페이스 + steering files 로드, AWS 자격증명 확인 |
| 0:30–1:30 | Inception | Mob Elaboration: UoW 9건 검토·확정, 페르소나 권한 매트릭스 최종화 |
| 1:30–2:00 | Architecture | Kiro에 design.md 생성 요청, 컴포넌트 확정 |
| 2:00–4:00 | Construction (Core) | Speaker Mapping + AgentCore Memory + Policy 결선 작업 |
| 4:00–5:30 | Construction (Demo) | S1·S3·S4·S6 시연 가능한 흐름 통합 |
| 5:30–6:30 | Polish | 데모 UI mock, 페르소나별 응답 톤 다듬기 |
| 6:30–7:00 | Pitch prep | 5분 피치 리허설, 백업 영상 녹화 |

**Critical path**: Speaker Mapping → AgentCore Memory `actor_id` 스코프 → 페르소나 프롬프트. 이 3개가 안 되면 나머지는 의미 없음. 2시 이전 작동 확인 필수.

---

## 11. 데모 시나리오 (5분 피치)

1. **0:00–0:30** 문제 제기 — "차에 가족 4명이 탔습니다. 누구의 비서입니까?"
2. **0:30–1:30** S3 시연 — 같은 "배고프다"에 다른 응답 (가장 강한 카드)
3. **1:30–2:30** S4 시연 — 아이가 차량제어/전화 시도 → 가드레일 차단
4. **2:30–3:30** 아키텍처 1슬라이드 — Transcribe + Speaker Mapping + AgentCore 4종
5. **3:30–4:30** S6 시연 — 운행 후 화자별 메모리 대시보드
6. **4:30–5:00** AI-DLC 충실도 — Kiro 산출물(`aidlc-docs/`) 보여주기, 7시간 안에 어떻게 가능했는지

---

## 12. 리스크 및 대응

| 리스크 | 영향 | 대응 |
|---|---|---|
| Transcribe 다중 화자 정확도 부족 | 데모 실패 | 사전 녹음 + 좌석 채널 시뮬레이션으로 우회 |
| AgentCore Memory `actor_id` 응답 지연 | 시연 끊김 | LTM 핵심 항목 사전 로드 + 캐싱 |
| 7시간 안 통합 실패 | 데모 미완성 | Critical path 우선, S1·S3·S4 최소 시연 가능 시점에 freeze |
| 화자→실명 매핑 정확도 | UX 손상 | 좌석 채널 1차, 자기소개 2차로 이중화 |
| 페르소나 응답 품질 | 데모 임팩트 약화 | 페르소나 프롬프트 사전 작성·검증 |
| Nova Sonic 통합 시간 부족 | TTS 품질 저하 | Polly fallback 준비 |

---

## 13. Kiro 스티어링 파일 제안

`.kiro/steering/` 하위에 작성할 파일들:

### 13.1 `product.md`
- 프로젝트 정의 (§1)
- 핵심 가치 제안 (§2)
- 페르소나 정의 (§4)

### 13.2 `tech.md`
- 사용 AWS 서비스 목록 + 버전
- LangGraph 노드 명명 규칙
- Bedrock 모델 선택 기준
- AgentCore Memory `actor_id` 명명 규칙 (`actor_{role}`)

### 13.3 `structure.md`
- 리포 구조 (제안):
  ```
  family-copilot/
  ├── aidlc-docs/
  │   ├── inception/
  │   ├── construction/
  │   └── operations/
  ├── src/
  │   ├── ingestion/        # Transcribe 통합
  │   ├── mapping/          # Speaker Mapping
  │   ├── personas/         # 프롬프트 + 권한
  │   ├── orchestrator/     # LangGraph
  │   └── reflection/       # 트립 종료 처리
  ├── policies/             # CEDAR 정책
  └── demo/                 # 데모 UI mock
  ```

### 13.4 `safety.md` (도메인 특화)
- 어린이 콘텐츠 필터 규칙
- 운전자 우선순위 정책
- 게스트 프라이버시 규칙
- 응답 길이·속도 페르소나별 임계값

### 13.5 `evaluation.md`
- AgentCore Evaluations 커스텀 지표 정의
- "올바른 화자에게 올바른 응답" 판정 기준

---

## 14. 다음 단계 — Kiro 시동 절차

1. 본 문서를 `.kiro/steering/product.md`의 기반 자료로 import
2. Kiro에 `requirements.md` 생성 요청 — §5 시나리오 + §7.1 UoW 기반, EARS 표기로 자동 변환
3. Kiro에 `design.md` 생성 요청 — §6 아키텍처 + §3.1 흐름 기반
4. Kiro에 `tasks.md` 생성 요청 — §7.2 + §10 타임박스 기반
5. §13의 스티어링 파일 5종 작성
6. 빌딩 세션 당일: Mob Elaboration으로 §7.1 UoW 검토·확정 → Construction 진입

---

## 부록 A. 요구사항 EARS 표기 예시 (Kiro 변환용)

```
WHEN 시동이 ON 되었을 때
THE SYSTEM SHALL 좌석 점유 센서를 확인하고 자기소개 프롬프트를 시작한다.

WHEN 등록된 화자가 도구 호출을 요청했을 때
IF 해당 화자의 페르소나 권한이 도구를 허용한다면
THE SYSTEM SHALL 도구를 실행한다.

WHEN 등록된 화자가 도구 호출을 요청했을 때
IF 해당 화자의 페르소나 권한이 도구를 차단한다면
THE SYSTEM SHALL 거절 응답을 페르소나 맞춤 톤으로 생성한다.

WHEN 미등록 음성이 감지되었을 때
THE SYSTEM SHALL 게스트 페르소나로 처리하고 메모리에 저장하지 않는다.

WHEN 시동이 OFF 되었을 때
THE SYSTEM SHALL Reflection agent를 실행하여 화자별 에피소드를 LTM에 적재한다.
```

## 부록 B. 페르소나 프롬프트 스켈레톤 예시

```
[페르소나: 아빠]
- 호칭: 일상적, 짧게
- 정보 밀도: 높음 (옵션 2-3개 제시)
- 차량제어·내비: 즉시 실행
- 톤: 효율적, 동료적

[페르소나: 아이]
- 호칭: 이름 + 친근체
- 정보 밀도: 낮음 (1개씩)
- 차량제어·통신: 차단 + 우회 제안
- 콘텐츠 필터: 연령 적합
- 톤: 따뜻, 격려적

[페르소나: 할머니]
- 호칭: 존칭, 천천히
- 정보 밀도: 핵심만
- 응답 길이: 1문장 우선
- 재확인: 중요 동작 시 1회
- 톤: 정중, 안정적

[페르소나: 게스트]
- 호칭: 중립
- 정보 밀도: 표준
- 기능: 정보 조회만
- 메모리: 저장하지 않음
- 톤: 친절하지만 거리감 유지
```

---

**문서 끝.** 이 자료를 Kiro에 입력해 `requirements.md`, `design.md`, `tasks.md` 생성을 시작.