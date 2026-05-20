# Traceability Matrix — Family Profile Co-pilot

> **Purpose**: 요구사항(FR/NFR) → 스토리 → 컴포넌트 → Task → Test 의 end-to-end 추적성 인덱스. AI 심사관이 산출물 일관성을 검증할 때 진입점으로 사용.
>
> **Last updated**: 2026-05-20T18:00:00Z (post Code Gen Phase 4~6 — API Service + Agent Service + Frontend + CI/CD + Docker 완성)
>
> **Scope**: Inception + Construction (Functional Design + Infrastructure Design + Code Gen Phase 0~6 + CI/CD) 단계 산출물 기반.
>
> **정본 정의 (source of truth)**:
>
> Inception:
> - 요구사항: `aidlc-docs/inception/requirements/requirements.md`
> - 스토리: `aidlc-docs/inception/user-stories/stories.md`
> - 페르소나: `aidlc-docs/inception/user-stories/personas.md`
> - 컴포넌트: `aidlc-docs/inception/application-design/components.md` (C1~C11)
> - 서비스: `aidlc-docs/inception/application-design/services.md` (SVC-1 API, SVC-2 Agent, SVC-3 Reflection Lambda)
> - 유닛: `aidlc-docs/inception/application-design/unit-of-work.md` (U1 Infra, U2 API, U3 Agent, U4 Lambda, U5 Frontend)
> - 유닛 의존성: `aidlc-docs/inception/application-design/unit-of-work-dependency.md`
> - 유닛-스토리 매핑: `aidlc-docs/inception/application-design/unit-of-work-story-map.md`
> - 검토: `aidlc-docs/inception/review/application-design-review.md`
> - 결정: `aidlc-docs/inception/decisions/` (ADR-001 ~ ADR-005)
>
> Construction:
> - Functional Design (shared): `aidlc-docs/construction/shared/functional-design/domain-entities.md`
> - NFR Requirements (shared): `aidlc-docs/construction/shared/nfr-requirements/nfr-requirements.md`
> - Tech Stack: `aidlc-docs/construction/shared/nfr-requirements/tech-stack-decisions.md`
> - U1 Functional Design: `aidlc-docs/construction/infrastructure/functional-design/terraform-modules.md`
> - U1 Infrastructure Design: `aidlc-docs/construction/infrastructure/infrastructure-design/infrastructure-design.md`
> - U2 Functional Design: `aidlc-docs/construction/api-service/functional-design/business-logic-model.md`
> - U3 Functional Design: `aidlc-docs/construction/agent-service/functional-design/business-logic-model.md`
> - U4 Functional Design: `aidlc-docs/construction/reflection-lambda/functional-design/business-logic-model.md`
> - U5 Functional Design: `aidlc-docs/construction/frontend/functional-design/frontend-components.md`
> - Code Generation Plan: `aidlc-docs/construction/plans/code-generation-plan.md`
> - Evaluation Metrics: `aidlc-docs/inception/evaluation/metrics.md`
> - Golden Dataset: `aidlc-docs/inception/evaluation/golden-dataset.jsonl` (30 test cases)
>
> Code (workspace root):
> - Shared models: `shared/models/` (entities.py, enums.py)
> - Shared policies: `shared/policies/permissions.cedar`
> - Shared prompts: `shared/prompts/*.yaml` (5 프리셋)
> - Terraform: `terraform/modules/` (vpc, ecs, elasticache, dynamodb, lambda, eventbridge, alb, cicd)
> - API Service: `services/api-service/` (FastAPI + WebSocket + Speaker Mapping + State Machine)
> - Agent Service: `services/agent-service/` (Strands Agent + Bedrock + Policy Enforcer + Persona Registry)
> - Reflection Lambda: `services/reflection-lambda/` (EventBridge handler + Bedrock pattern extraction)
> - Frontend: `frontend/` (React + Zustand + Tailwind + Vite + Zod validation)
> - CI/CD: `.github/workflows/deploy.yml` (GitHub Actions + OIDC + ECR + ECS)
> - Docker: `docker-compose.yml` (api-service + agent-service + valkey)
>
> 본 매트릭스는 정본을 가리키는 인덱스이며, 정본과 충돌 시 정본이 우선합니다.

---

## 1. ID 명명 규칙

| 카테고리 | 형식 | 출처 |
|---|---|---|
| Functional Req | `FR-XX.Y` | requirements.md §1 |
| Non-Functional Req | `NFR-XX.Y` | requirements.md §2 |
| User Story | `US-S{N}-NN` / `US-SYS-NN` | stories.md |
| Persona Preset | `PS-{N}` | personas.md (5개 프리셋) |
| Component | `C{N}` | components.md |
| Service | `SVC-{N}` | services.md |
| Unit of Work | `U{N}` | unit-of-work.md (U1~U5) |
| Task | `T-XX` | (TBD: Construction — code-generation plan) |
| Test | `TC-XX` | (TBD: Construction — functional-design / test plan) |
| Decision | `ADR-NNN` | decisions/ (ADR-001 ~ ADR-005 작성 완료) |

---

## 2. Functional Requirements → Stories → Components

| Req ID | 요약 | 스토리 | 컴포넌트 | 우선순위 | Status |
|---|---|---|---|---|---|
| FR-01.1 | 시동 ON 좌석 점유 확인 + 운전석 채널 driver=true 자동 부여 (좌석 센서는 프론트 목업, 운전자는 DDB 프로필 인증) | US-S1-01, US-SYS-01 | C1, C2, C11 | P0 | Done |
| FR-01.2 | Transcribe Streaming + spk_N 라벨 부여 | US-S1-01, US-SYS-01 | C1 | P0 | Done |
| FR-01.3 | 3단계 매핑 (좌석 채널 → 자기소개 → 어휘/말투 휴리스틱) | US-S1-01, US-S7-01, US-SYS-01 | C2 | P0 | Done |
| FR-01.4 | 미등록 음성 → relationship=guest 자동 처리 | US-S7-01, US-SYS-01 | C2 | P0 | Done |
| FR-01.5 | 하이브리드 (LIVE + FALLBACK 사전녹음) | (NFR-02.2 cross) | C1 | P0 | Done |
| FR-01.6 | 좌석 변경/신규 탑승 시 자기소개 확인 | US-SYS-01 | C2 | P1 | Done |
| FR-02.1 | 역할 속성 기반 페르소나 엔진 (driver/age_group/account_owner/relationship) | US-SYS-01, US-S1-01 | C6 | P0 | Done |
| FR-02.2 | 5개 데모 프리셋 사전 정의 (운전자/동승자/어린이/어르신/게스트) | (전 시나리오) | C6 | P0 | Done |
| FR-02.3 | 운전석 탑승자 driver=true 자동 부여 (가족 구성 무관) | US-S1-01, US-SYS-01 | C2, C6 | P0 | Done |
| FR-02.4 | 역할 속성 조합별 응답 스타일 (호칭/밀도/톤/속도) + 권한 세트 | US-S3-01, US-S4-01, US-S5-01 | C4, C6 | P0 | Done |
| FR-02.5 | CEDAR 정책은 역할 속성 기반 — 프리셋 추가 없이 새 조합 커버 | (NFR-04.1 cross) | C3, C6 | P0 | Done |
| FR-03.1 | AgentCore Policy CEDAR 등록 + 런타임 평가 | US-SYS-01 | C3 | P0 | Done |
| FR-03.2 | 권한 허용 시 도구 실행 | US-S3-01 | C3, C4, C7 | P0 | Done |
| FR-03.3 | 권한 차단 시 페르소나 맞춤 톤 거절 | US-S4-01, US-S5-01, US-S7-01 | C3, C4 | P0 | Done |
| FR-03.4 | 권한 매트릭스 페르소나별 차등 | US-S4-01, US-S5-01, US-S7-01 | C3 | P0 | Done |
| FR-03.5 | 어린이 콘텐츠 필터 (폭력/성인/공포 + 연령 재정렬) | US-S4-01 | C3 | P0 | Done |
| FR-04.1 | 동시 발화 500ms 윈도우 + 역할 속성 기반 동적 우선순위 | US-S2-01 | C2, C3, C4 | P0 | Done |
| FR-04.2 | 주행 중 우선순위: driver+안전 > driver비안전 > adult family > elder > child/teen > guest | US-S2-01 | C3 | P0 | Done |
| FR-04.3 | 정차 중: driver 우선권 해제, 전원 선착순 | US-S2-01 | C3 | P1 | Done |
| FR-04.4 | 낮은 우선순위 발화 큐잉 후 순차 처리 | US-S2-01 | C4 | P1 | Done |
| FR-05.1 | Valkey STM (트립 단위 화자별 발화 이력) | US-S3-01, US-S6-01 | C5 | P0 | Done |
| FR-05.2 | AgentCore Memory LTM (actor_id별 프로파일) | US-S1-01, US-S3-01 | C5 | P0 | Done |
| FR-05.3 | 시동 OFF Reflection → STM → LTM 승격 | US-S6-01 | C8 | P1 | Done |
| FR-05.4 | 게스트 발화 메모리 미저장 (privacy by design) | US-S7-01 | C5, C8 | P0 | Done |
| FR-05.5 | 어린이 발화는 부모 권한 하에서만 LTM 적재 | US-S6-01 | C5, C8 | P1 | Done |
| FR-06.1 | Strands Agents SDK 메인 오케스트레이터 | (전 시나리오) | C4 | P0 | Done |
| FR-06.2 | 화자 식별 결과 → 페르소나 프롬프트 동적 적용 | US-S3-01, US-S4-01, US-S5-01 | C4, C6 | P0 | Done |
| FR-06.3 | Claude Haiku 4.5 (Bedrock) 추론 | (전 시나리오) | C4 | P0 | Done |
| FR-06.4 | 텍스트 응답 + Polly TTS 옵션 | US-S5-01 (TTS 0.8x) | C4 | P1 | Skipped |
| FR-07.1 | S1 시동 환영 — 화자별 차등 + LTM 개인화 | US-S1-01 | C1, C2, C4, C5, C10, C11 | P0 | Done |
| FR-07.2 | S3 같은 말 다른 추천 — 화자별 선호도 분기 | US-S3-01 | C4, C5, C6 | P0 | Done |
| FR-07.3 | S4 어린이 안전 — 도구 차단 + 우회 응답 | US-S4-01 | C3, C4, C7 | P0 | Done |
| FR-07.4 | S2 동시 발화 충돌 해소 + 큐잉 | US-S2-01 | C2, C3, C4 | P1* | Done |
| FR-07.5 | S5 노약자 응답 단순화 + 재확인 | US-S5-01 | C4, C6 | P1 | Done |
| FR-07.6 | S6 트립 종료 화자별 메모리 누적 | US-S6-01 | C5, C8 | P1 | Done |
| FR-07.7 | S7 게스트 처리 + 메모리 미적용 | US-S7-01 | C2, C3, C5 | P0 | Done |
| FR-08.1 | AgentCore Evaluations 3개 커스텀 지표 | US-SYS-02 | C9 (Optional P2) | P1 | Done |
| FR-08.2 | 평가 결과 대시보드 실시간 표시 | US-SYS-02 | C9 (Optional P2), C11 | P2 | Skipped |

> `*` FR-07.4: requirements.md FR-07.4는 P1, 그러나 In Scope §4에는 S2가 핵심 시나리오로 포함되어 있음 (P0 데모 카드). §6 D-04 참조.

**Status 범례**: Designed = Inception 산출물 존재 / Specified = Functional Design 까지 상세화 완료 / Implementing = Construction Code Generation 진행 중 / **Done = 코드+테스트 완료** / Skipped = Out of scope.

---

## 3. Non-Functional Requirements → Components/Services

| NFR ID | 요약 | 적용 컴포넌트/서비스 | 검증 방식 | Status |
|---|---|---|---|---|
| NFR-01.1 | E2E 응답 지연 P95 ≤ 3초 | SVC-1, SVC-2 (전 경로) | 통합 성능 테스트 | Done |
| NFR-01.2 | Transcribe diarization 결과 ≤ 1초 | C1 | 컴포넌트 성능 테스트 | Done |
| NFR-01.3 | AgentCore Policy 평가 ≤ 500ms | C3 | 컴포넌트 성능 테스트 | Done |
| NFR-01.4 | 동시 5명 화자 처리 | C1, C2 | 부하 테스트 | Done |
| NFR-02.1 | 데모 환경 99% 가용성 | SVC-1, SVC-2, SVC-3 | 헬스체크 + 모니터링 | Done |
| NFR-02.2 | Transcribe 실패 시 사전녹음 fallback 자동 전환 (LIVE → FALLBACK) | C1 | 장애 주입 테스트 | Done |
| NFR-03.1 | 모든 AWS 통신 TLS 1.2+ (SECURITY-01) | 전 컴포넌트 (외부 호출) | 설정 검증 | Done |
| NFR-03.2 | IAM 최소 권한 (SECURITY-06) | SVC-1, SVC-2, SVC-3 (Task Role/Lambda Role) | IAM 정책 리뷰 | Done |
| NFR-03.3 | 게스트 발화 트립 종료 시 즉시 삭제 | C5, C8 | 동작 테스트 (FR-05.4 cross) | Done |
| NFR-03.4 | 어린이 개인정보 부모 동의 하에만 저장 | C5, C8 (FR-05.5 cross) | 동작 테스트 | Done |
| NFR-03.5 | API 입력 검증 (SECURITY-05) | SVC-1 (REST + WS), SVC-2 (내부 API) | 입력 fuzzing + PBT | Done |
| NFR-03.6 | HTTP 보안 헤더 (SECURITY-04) | SVC-1 응답 미들웨어 | 헤더 검증 테스트 | Done |
| NFR-03.7* | 네트워크 격리 (SECURITY-07) — VPC/SG/Private Subnet | SVC-1, SVC-2 인프라 (Terraform) | 인프라 테스트 | Done |
| NFR-03.8* | 인증/접근제어 (SECURITY-08) — JWT + WebSocket 토큰 | C10 (WS auth), SVC-1 REST auth | 인증 테스트 | Done |
| NFR-03.9* | 보안 설계 (SECURITY-11) — Policy 분리, Rate limit | C3 + SVC-1 | 설계 리뷰 + 부하 테스트 | Done |
| NFR-03.10* | Fail-closed 예외 처리 (SECURITY-15) — 구조화 로깅 | 전 서비스 글로벌 핸들러 | 장애 주입 테스트 | Done |
| NFR-03.11† | SECURITY-03 로깅, SECURITY-09 하드닝, SECURITY-10 공급망, SECURITY-12 인증 | All units (구조화 로깅, no default creds, uv.lock, JWT 세션) | 코드 리뷰 + 의존성 스캔 | Done |
| NFR-04.1 | 역할 속성 기반 CEDAR 정책 → 프리셋 추가 없이 확장 | C3, C6 (FR-02.5 cross) | 정책 테스트 | Done |
| NFR-04.2 | ECS Fargate 수평 확장 (Terraform IaC) | SVC-1, SVC-2 | 부하 + 오토스케일 테스트 | Done |
| NFR-05.1 | Property-Based Testing 전체 적용 | C2, C3, C4, C5, C6 | PBT (Hypothesis/fast-check) | Done |
| NFR-05.2 | PBT 프레임워크: Python Hypothesis / TS fast-check | (도구 선택) | — | Done |
| NFR-05.3 | 비즈니스 로직(매핑/정책/페르소나 분기) PBT 필수. PBT-01 Testable Properties 명시: 상태 전이, 매핑 일관성, 정책 멱등성, role→prompt 결정성, round-trip 직렬화 등 (`tech-stack-decisions.md` PBT 섹션) | C2, C3, C4 | PBT | Done |

> `*` 표시 NFR-03.7~10은 requirements.md NFR-03 본문엔 명시되지 않았으나 application-design.md §5 SECURITY-07/08/11/15 매핑에 존재 + In Scope §4에 "프로덕션 레벨 SECURITY 전체 적용" / "JWT 인증 + WebSocket 토큰" / "구조화 로깅"이 명시됨. Construction `shared/nfr-requirements/nfr-requirements.md` §4가 SECURITY 전체 매핑을 정식 등재함으로써 추적성 closure (D-03 closed).
>
> `†` 표시 NFR-03.11은 Construction NFR 산출물에서 신규 추가된 SECURITY 규칙들. requirements.md NFR-03 차후 갱신 시 흡수 권장.

---

## 4. Persona Preset ↔ Story 커버리지 (역추적)

| Preset ID | 프리셋 | 역할 속성 | 관련 스토리 | 데모 등장 | 권한 (FR-03.4 cross) |
|---|---|---|---|---|---|
| PS-1 | 운전자 (성인) | `driver=true, age_group=adult, relationship=owner|family` | US-S1-01, US-S2-01, US-S3-01 | ✅ Critical | Full (운전 제어 포함) |
| PS-2 | 동승자 (성인) | `driver=false, age_group=adult, relationship=owner|family` | US-S1-01, US-S3-01, US-S6-01 | ✅ Critical | Full (운전 제어 제외) |
| PS-3 | 어린이 | `driver=false, age_group=child, relationship=family` | US-S1-01, US-S2-01, US-S4-01, US-S6-01 | ✅ Critical | 최소 (엔터테인먼트 + 안전 가드레일) |
| PS-4 | 어르신 | `driver=false, age_group=elder, relationship=family` | US-S5-01 | ⚠️ Stretch | 제한 (본인 좌석 환경 + 정보) |
| PS-5 | 게스트 | `driver=false, age_group=adult, relationship=guest` | US-S3-01, US-S7-01 | ⚠️ Stretch | 최소 (정보 조회 only) |

> **핵심 차별점**: 페르소나는 고정 가족 역할이 아닌 역할 속성 조합. "누구든 운전석에 앉으면 driver=true" → 가족 구성 무관 자연스러운 권한 전환.

---

## 5. Component ↔ Service ↔ Unit ↔ FR 역추적

| Comp | Service | Unit | 핵심 책임 | 직접 매핑 FR | 간접 매핑 FR |
|---|---|---|---|---|---|
| C1 Voice Ingestion | SVC-1 API | U2 | 오디오 수신 + Transcribe 연동 (LIVE/FALLBACK 전환) | FR-01.2, FR-01.5 | FR-07.1 |
| C2 Speaker Mapping | SVC-1 API | U2 | spk_N → actor_id 매핑 (3단계) + 500ms 동시 발화 버퍼링 + driver 자동 부여 + DDB `vehicle_profiles` 조회 | FR-01.1, FR-01.3, FR-01.4, FR-01.6, FR-02.3, FR-04.1 | FR-07.1, FR-07.4, FR-07.7 |
| C3 Policy Enforcer | SVC-2 Agent | U3 | CEDAR 평가 (역할 속성 기반) + 우선순위 결정 + 콘텐츠 필터 | FR-02.5, FR-03.1~5, FR-04.1~3 | FR-07.3, FR-07.4, FR-07.7 |
| C4 Orchestrator | SVC-2 Agent | U3 | Strands 메인 루프 + 페르소나 분기 + 동시 발화 처리 | FR-02.4, FR-04.4, FR-06.1~4 | 전 시나리오 (FR-07.*) |
| C5 Memory Manager | SVC-2 Agent | U3 | STM/LTM 읽기/쓰기 (actor_id 스코프) | FR-05.1, FR-05.2, FR-05.4, FR-05.5 | FR-07.1, FR-07.2, FR-07.6, FR-07.7 |
| C6 Persona Registry | SVC-2 Agent | U3 | 역할 속성 페르소나 엔진 + 5 프리셋 + 프롬프트 템플릿 조회 | FR-02.1, FR-02.2, FR-02.4, FR-02.5 | FR-07.5 |
| C7 Tool Registry | SVC-2 Agent | U3 | 도구 정의/실행 | (FR-03.2, FR-06 cross) | FR-07.3 |
| C8 Reflection Agent | SVC-3 Lambda | U4 | 트립 종료 패턴 추출 + STM→LTM 승격 | FR-05.3, FR-05.4, FR-05.5 | FR-07.6 |
| C9 Eval Collector (Optional P2) | SVC-2 Agent | U3 | 3개 지표 측정 (데모 시 mock actual) | FR-08.1, FR-08.2 | NFR-05.x cross |
| C10 WebSocket Gateway | SVC-1 API | U2 | WS 연결 관리 + 인증 | (모든 외부 통신 진입점) | FR-07.1, NFR-03.8 |
| C11 Demo UI | Client | U5 | 좌석/권한/메모리/지표 시각화 + 좌석 센서 목업 + 운전자 프로필 인증 UI | FR-08.2 | FR-07.1 |

### 5.1 Unit ↔ Story 매핑 (요약 인덱스)

> 정본: `aidlc-docs/inception/application-design/unit-of-work-story-map.md`

| Unit | 직접 책임 스토리 (P0/P1 위주) |
|---|---|
| U1 Infrastructure (Terraform) | 모든 스토리의 배포 전제 |
| U2 API Service | US-SYS-01, US-S1-01, US-S2-01, US-S7-01 |
| U3 Agent Service | US-S1-01, US-S2-01, US-S3-01, US-S4-01, US-S5-01, US-S7-01, US-SYS-02 |
| U4 Reflection Lambda | US-S6-01, US-S7-01 |
| U5 Frontend | US-S1-01, US-S2-01, US-S3-01, US-S4-01, US-SYS-01, US-SYS-02 |

### 5.2 데이터 저장소 (확정)

| 저장소 | Unit | 용도 | 키 스킴 / 데이터 |
|---|---|---|---|
| Valkey (ElastiCache, IAM 인증) | U1 → U2/U3/U4 | STM + 트립 상태 + 동시 발화 버퍼 | `trip:{trip_id}:*` (ADR-004) |
| AgentCore Memory | U1 → U3/U4 | LTM (페르소나 프로파일, 선호도, 에피소드) | `actor_id` 스코프 (ADR-003) |
| AgentCore Policy | U1 → U3 | CEDAR 정책 (역할 속성 기반) | `aws_verifiedpermissions_policy_store` |
| AgentCore Evaluations | U1 → U3 (Optional P2) | 3개 지표 (식별/일관성/누락률) | FR-08.1 |
| **DynamoDB `vehicle_profiles`** | U1 → U2 | 차량별 등록 가족 프로파일 (회원가입 대체) | PK=vehicle_id, SK=actor_id, attrs=name/age_group/relationship/account_owner/default_seat_channel/preferences_summary |

---

## 6. Known Discrepancies (산출물 간 차이 — 정합성 추적)

| # | 항목 | 현황 | 영향 | 해결 방향 |
|---|---|---|---|---|
| D-01 | application-design.md §3 컴포넌트 요약 표의 stale 표현 | C2 description "spk_N → actor_id 매핑 (4단계 전략)" — 실제 components.md C2는 3단계로 정정됨. 또 C6 description "페르소나 CRUD + 자동 생성" — 실제 components.md C6는 역할 속성 엔진으로 변경됨 | 문서 내부 일관성 결함, 구현자 혼란 가능 | application-design.md §3 표를 components.md 최신 정의로 동기화 |
| D-02 | audit.md "10 stories" 표기 | 실제 stories.md = 9 (US-S1~S7 + US-SYS-01, US-SYS-02). audit.md 09:35 entry "Generated stories.md (10 stories ...)"는 부정확 | 외부 표기 정확성 (낮은 영향) | audit.md는 raw input 보존 원칙상 사후 수정 비권장. 본 매트릭스 §4 / stories.md를 정본으로 인용 |
| ~~D-03~~ | ~~NFR-03 추가 SECURITY 규칙~~ | **CLOSED** — Construction `shared/nfr-requirements/nfr-requirements.md` §4가 SECURITY-01/03/04/05/06/07/08/09/10/11/12/15 전체 매핑을 정식 등재함. 매트릭스 §3에서도 NFR-03.11(†) 신규 행으로 흡수 | — | requirements.md NFR-03 차후 갱신 시 동일 흡수 권장 (낮은 우선도) |
| D-04 | FR-07.4 (S2 동시 발화) 우선순위 | requirements.md FR-07.4 = P1, In Scope §4는 S2를 핵심 시나리오로 포함, US-S2-01 = P0 | 우선순위 혼선 가능 | requirements.md FR-07.4 우선순위를 P0로 정정 또는 In Scope §4에서 "P1이지만 데모 시연 포함" 명시 |
| D-05 | FR-01.3 매핑 "단계 수" | requirements.md FR-01.3 = "3단계 매핑 전략", components.md C2 = "3단계 인식 전략" — 일치. application-design-review.md Issue #1에서 지적된 "4단계" 잔재는 D-01에 한정 (application-design.md §3 표) | 정본 일치, application-design.md §3만 갱신 필요 | D-01과 동일 처리 |
| ~~D-06~~ | ~~ADR 부재~~ | **CLOSED** — 2026-05-20T14:25Z `aidlc-docs/inception/decisions/` 하위 5개 ADR 작성으로 해결 (ADR-001~005, MADR 형식, ixi-drive prior art 인용) | — | §8 참조 |
| D-07 | DDB `vehicle_profiles` 테이블 정본 누락 | unit-of-work.md / Construction `terraform-modules.md` / `tech-stack-decisions.md`에 등재 + Code Gen Phase 3에서 `terraform/modules/dynamodb/` 실제 모듈 작성됨. **Construction에서 closure**, requirements.md "Technical Decisions" 정본만 미반영 | 데이터 저장소 추적성은 매트릭스 §5.2로 보강 완료 | requirements.md "Technical Decisions" 차후 갱신 시 DDB 항목 추가 (낮은 우선도) |
| D-08 | US-S1-01 AC와 FR-01.1 본문 표현 차이 | stories.md US-S1-01 AC는 좌석 센서 목업 + DDB 프로필 인증 명시, requirements.md FR-01.1은 일반 표현. Construction `terraform-modules.md` DDB 모듈 + `business-logic-model.md` (API)에서 디테일 구체화 + Code Gen Phase 2에서 `shared/prompts/*.yaml` 5종 생성으로 페르소나 디테일이 코드에 정착됨 | 정본 표현이 추상적, 구현은 상세 — Construction에서 사실상 closure | requirements.md FR-01에 "좌석 센서는 프론트 목업, 운전자는 DDB 프로필 인증" 명시 추가 권장 (낮은 우선도) |
| D-09 | Functional Design 신규 결정 사항 (audit 미기재) | `all-units-functional-design-plan.md` Q1~Q6 답변(A/C/B/A/A/A)이 Construction 산출물에 반영되었으나 audit.md에는 별도 entry가 없음. 결정: Q1=A 프로필 목록 선택, Q2=C 트립 종료 시 운전자 확인 후 DDB 등록, Q3=B 웹검색만 실제, Q4=A 파일 기반 프롬프트, Q5=A Zustand, Q6=A LLM 기반 패턴 추출 | 결정 근거 추적성 약함 | 본 매트릭스 D-09에 기록함으로써 인덱스 보강. audit.md는 raw input 보존 원칙상 사후 수정 비권장 |
| D-10 | aidlc-state.md 진행 상태 stale | **CLOSED** — 2026-05-20T18:00Z 전체 Construction Phase 완료 반영. 모든 유닛 코드 생성 + CI/CD 파이프라인 + Docker 완성. aidlc-state.md 갱신 완료 | — | — |

---

## 7. 갱신 정책 (해커톤 7시간 컨텍스트)

본 매트릭스는 **인덱스**이지 **정본**이 아닙니다. 정본(requirements/stories/components/units 등)이 진화함에 따라 다음 시점에서만 동기화합니다.

| 시점 | 갱신 항목 | 예상 시간 |
|---|---|---|
| Inception 끝 | §2, §3, §4, §5 시드 채움 | 5~10분 |
| Units Generation 후 | Unit 컬럼 + 데이터 저장소 §5.2 | 5분 |
| Functional Design 후 | Status: Designed → Specified, NFR 추적 보강 | 5분 |
| Code Generation 끝 | Task ID, Test ID 컬럼 일괄 채움 + Status: Specified → Implementing/Done | 10분 |
| 마감 전 30분 | Status 컬럼 최종 정리 (Done/WIP/Skipped) + Last updated 시각 갱신 | 5분 |
| 정본 메이저 변경 시 (out-of-band) | 영향 받은 행 동기화 | 5~10분 |

워크플로우 진행 상태(어떤 stage가 끝났는지)는 본 매트릭스가 아닌 `aidlc-docs/aidlc-state.md`가 정본입니다. 매트릭스는 진행 상태를 추적하지 않습니다.

---

## 8. ADR (작성 완료)

`aidlc-docs/inception/decisions/` 하위에 MADR 간소화 형식(LG U+ ixi-drive 표준 차용)으로 5건 작성. application-design-review.md Issue #3 응답 포함.

| ADR | 제목 | 우선도 | prior art |
|---|---|---|---|
| [ADR-001](inception/decisions/ADR-001-role-based-persona-model.md) | Role-based Persona Model | ⭐⭐⭐ | 없음 (차별화 신규) |
| [ADR-002](inception/decisions/ADR-002-strands-as-orchestrator.md) | Strands Agents SDK | ⭐⭐⭐ | ixi-drive `SPEC-IXICORE-AGENT-001` v5.12, `ARCH-C2-001` ADR-001 |
| [ADR-003](inception/decisions/ADR-003-two-tier-memory.md) | Two-tier Memory (Valkey + AgentCore) | ⭐⭐⭐ | ixi-drive `SPEC-IXICORE-MEMORY-001` v1.2 |
| [ADR-004](inception/decisions/ADR-004-trip-scoped-state-machine.md) | Trip-scoped State Machine & Identifier Lifecycle | ⭐⭐ | ixi-drive `SPEC-IXICORE-AUTH-002` v1.0 |
| [ADR-005](inception/decisions/ADR-005-natural-speaker-recognition.md) | Natural Speaker Recognition (3-step) | ⭐⭐ | 없음 (UX 신규, Human-in-the-Loop 증거) |

> 인덱스: [decisions/README.md](inception/decisions/README.md)
>
> §6 D-06 (ADR 부재) 이슈는 본 작성으로 closure.
