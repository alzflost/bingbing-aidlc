# Family Profile Co-pilot — Requirements Document

## Intent Analysis

| 항목 | 내용 |
|---|---|
| **User Request** | 차량 내 다중 화자를 실시간 구분하고, 화자별 페르소나에 맞춰 응답·기능·가드레일을 차등 적용하는 AI Car Agent 구현 |
| **Request Type** | New Project (Greenfield) |
| **Scope Estimate** | System-wide — 다중 컴포넌트 (음성 입력, 화자 매핑, 정책 엔진, 오케스트레이터, 메모리, UI) |
| **Complexity Estimate** | Complex — 실시간 다중 화자 처리, AWS 서비스 4종 연동, 동적 페르소나 관리 |
| **Target Event** | AWS Summit Seoul 2026 AI-DLC Building Session (7시간 타임박스) |

---

## 1. Functional Requirements

### FR-01: 화자 식별 및 매핑 (Speaker Identification & Mapping)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-01.1 | WHEN 시동이 ON 되었을 때 THE SYSTEM SHALL 좌석 점유 센서 데이터를 확인하고 화자 자동 인식을 시작한다 | P0 |
| FR-01.2 | THE SYSTEM SHALL Amazon Transcribe Streaming을 통해 실시간 음성을 텍스트로 변환하고 화자 라벨(spk_0~spk_N)을 부여한다 | P0 |
| FR-01.3 | THE SYSTEM SHALL 4단계 자연스러운 화자 인식 전략으로 spk_N을 actor_id에 매핑한다: (1) 좌석 채널 자동 매핑 — 운전석/조수석은 채널로 자동 인식, (2) 대화형 자연 확인 — 첫 발화 시 자연스러운 대화로 확인 (예: "안녕하세요! OO 아빠시죠?"), (3) 암묵적 학습 — 말투/어휘/음성 특성으로 자동 추론, 확신도 낮을 때만 확인, (4) 명시적 확인은 옵셔널 — 추론 실패 시에만 "누구신지 말씀해주실래요?" 요청 | P0 |
| FR-01.4 | WHEN 이전 트립에서 학습된 가족 구성원이 탑승했을 때 THE SYSTEM SHALL 자동 인식하여 별도 확인 없이 매핑한다 | P0 |
| FR-01.5 | WHEN 미등록 음성이 감지되었을 때 THE SYSTEM SHALL 자연스러운 대화로 확인을 시도하고, 응답이 없거나 매핑 실패 시 게스트(actor_guest) 페르소나로 처리한다 | P0 |
| FR-01.6 | THE SYSTEM SHALL 하이브리드 방식으로 동작한다 — Transcribe Streaming 실제 연동 + 데모 시 사전 녹음 fallback | P0 |
| FR-01.7 | WHEN 좌석 변경 또는 새 탑승자가 감지되었을 때 THE SYSTEM SHALL 대화형 자연 확인으로 신규 화자를 인식한다 (강제 자기소개 없음) | P1 |

### FR-02: 페르소나 관리 (Persona Management)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-02.1 | THE SYSTEM SHALL 7개 기본 페르소나를 사전 정의하여 제공한다: 아빠(actor_father), 엄마(actor_mother), 유아(actor_toddler, 3~6세), 청소년(actor_teen, 13~18세), 성인 자녀(actor_adult_child, 19세+), 어르신(actor_elder, 성별 무관), 게스트(actor_guest) | P0 |
| FR-02.2 | THE SYSTEM SHALL 런타임에 새 페르소나를 등록/수정/삭제할 수 있는 API를 제공한다 | P1 |
| FR-02.3 | WHEN 대화 중 새 탑승자가 감지되었을 때 THE SYSTEM SHALL AI 판단으로 기본 프로파일(이름, 추정 연령대, 기본 권한)을 자동 생성한다 | P1 |
| FR-02.4 | THE SYSTEM SHALL 대화 패턴 분석을 통해 기존 페르소나 속성(선호도, 말투 등)을 점진적으로 자동 업데이트한다 | P2 |
| FR-02.5 | 각 페르소나는 고유한 응답 스타일(호칭, 정보 밀도, 톤, 발화 속도)을 가진다. 유아: 매우 단순/친근/안전 최우선, 청소년: 캐주얼/자율성 존중하되 안전 가드레일, 성인 자녀: 일반 성인 수준/독립적 | P0 |

### FR-03: 권한 및 정책 (Permission & Policy)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-03.1 | THE SYSTEM SHALL AgentCore Policy API를 통해 CEDAR 정책을 등록하고 런타임에 평가한다 | P0 |
| FR-03.2 | WHEN 등록된 화자가 도구 호출을 요청했을 때 IF 해당 화자의 페르소나 권한이 도구를 허용한다면 THE SYSTEM SHALL 도구를 실행한다 | P0 |
| FR-03.3 | WHEN 등록된 화자가 도구 호출을 요청했을 때 IF 해당 화자의 페르소나 권한이 도구를 차단한다면 THE SYSTEM SHALL 거절 응답을 페르소나 맞춤 톤으로 생성한다 | P0 |
| FR-03.4 | THE SYSTEM SHALL 권한 매트릭스(내비게이션, 차량제어, 뮤직, BT전화, 웹검색, 브라우저제어)를 페르소나별로 차등 적용한다 | P0 |
| FR-03.5 | THE SYSTEM SHALL 어린이 페르소나에 대해 콘텐츠 필터(폭력·성인·공포 차단, 연령 적합도 재정렬)를 적용한다 | P0 |

### FR-04: 동시 발화 처리 (Concurrent Speech Handling)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-04.1 | WHEN 복수 화자의 발화 시간이 겹쳤을 때 THE SYSTEM SHALL 컨텍스트 기반 동적 우선순위로 처리 순서를 결정한다 | P0 |
| FR-04.2 | 주행 중: 안전 관련 발화(차량제어, 내비) > 운전자 일반 발화 > 동승자 발화 | P0 |
| FR-04.3 | 정차 중: 선착순 처리, 운전자 특별 우선권 없음 | P1 |
| FR-04.4 | 우선순위가 낮은 발화는 큐잉 후 순차 처리한다 | P1 |

### FR-05: 메모리 관리 (Memory Management)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-05.1 | THE SYSTEM SHALL Valkey(Redis)를 STM(Short-Term Memory)으로 사용하여 트립 단위 화자별 발화 이력을 저장한다 | P0 |
| FR-05.2 | THE SYSTEM SHALL AgentCore Memory를 LTM(Long-Term Memory)으로 사용하여 actor_id별 페르소나 프로파일을 저장한다 | P0 |
| FR-05.3 | WHEN 시동이 OFF 되었을 때 THE SYSTEM SHALL Reflection agent를 실행하여 화자별 에피소드를 STM에서 LTM으로 승격한다 | P1 |
| FR-05.4 | 게스트(actor_guest) 발화는 메모리에 저장하지 않는다 (프라이버시 by design) | P0 |
| FR-05.5 | 어린이 발화는 부모 권한 하에서만 LTM에 적재한다 | P1 |

### FR-06: 오케스트레이션 (Orchestration)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-06.1 | THE SYSTEM SHALL Strands Agents SDK를 메인 오케스트레이터로 사용하여 페르소나 분기, 도구 호출, 대화 관리를 처리한다 | P0 |
| FR-06.2 | THE SYSTEM SHALL 화자 식별 결과에 따라 페르소나별 프롬프트 템플릿을 동적으로 적용한다 | P0 |
| FR-06.3 | THE SYSTEM SHALL Claude Haiku 4.5 (Bedrock)를 LLM 추론 모델로 사용한다 | P0 |
| FR-06.4 | THE SYSTEM SHALL 텍스트 기본 응답을 제공하되, 시간 여유 시 Amazon Polly TTS를 추가한다 | P1 |

### FR-07: 시나리오별 요구사항 (Scenario Requirements)

| ID | 시나리오 | 요구사항 | 우선순위 |
|---|---|---|---|
| FR-07.1 | S1: 시동 ON 환영 | 화자별 차등 환영 메시지 + 메모리 기반 개인화 | P0 |
| FR-07.2 | S3: 같은 말, 다른 추천 | 동일 발화에 대해 화자별 선호도 기반 차등 응답 | P0 |
| FR-07.3 | S4: 어린이 안전 모드 | 제한 권한 도구 차단 + 페르소나 맞춤 우회 응답 | P0 |
| FR-07.4 | S2: 동시 발화 충돌 | 컨텍스트 기반 우선순위 + 큐잉 | P1 |
| FR-07.5 | S5: 노약자 응답 단순화 | 단순 핵심 응답 + 느린 발화 + 재확인 | P1 |
| FR-07.6 | S6: 운행 후 메모리 누적 | Reflection agent 화자별 에피소드 분리 저장 | P1 |
| FR-07.7 | S7: 미등록 화자 처리 | 게스트 모드 + 메모리 미적용 | P0 |

### FR-08: 평가 시스템 (Evaluation System)

| ID | 요구사항 | 우선순위 |
|---|---|---|
| FR-08.1 | THE SYSTEM SHALL AgentCore Evaluations를 통해 3개 커스텀 지표를 실측한다: 화자 식별 정확도, 페르소나 일관성, 가드레일 누락률 | P1 |
| FR-08.2 | THE SYSTEM SHALL 평가 결과를 대시보드에 실시간 표시한다 | P2 |

---

## 2. Non-Functional Requirements

### NFR-01: 성능 (Performance)

| ID | 요구사항 |
|---|---|
| NFR-01.1 | 화자 식별 → 응답 생성까지 end-to-end 지연시간 3초 이내 (P95) |
| NFR-01.2 | Transcribe Streaming diarization 결과 수신 1초 이내 |
| NFR-01.3 | AgentCore Policy 평가 응답 500ms 이내 |
| NFR-01.4 | 동시 5명 화자 처리 가능 |

### NFR-02: 가용성 (Availability)

| ID | 요구사항 |
|---|---|
| NFR-02.1 | 데모 환경 기준 99% 가용성 (7시간 세션 내 다운타임 최소화) |
| NFR-02.2 | Transcribe 연결 실패 시 사전 녹음 fallback 자동 전환 |

### NFR-03: 보안 (Security)

| ID | 요구사항 |
|---|---|
| NFR-03.1 | 모든 AWS 서비스 통신은 TLS 1.2+ 암호화 (SECURITY-01) |
| NFR-03.2 | IAM 역할은 최소 권한 원칙 적용 (SECURITY-06) |
| NFR-03.3 | 게스트 발화 데이터는 트립 종료 시 즉시 삭제 |
| NFR-03.4 | 어린이 개인정보는 부모 동의 하에만 저장 |
| NFR-03.5 | API 입력 검증 필수 (SECURITY-05) |
| NFR-03.6 | HTTP 보안 헤더 적용 (SECURITY-04) |

### NFR-04: 확장성 (Scalability)

| ID | 요구사항 |
|---|---|
| NFR-04.1 | 페르소나 동적 등록/수정 API로 무제한 페르소나 확장 가능 |
| NFR-04.2 | ECS Fargate 기반 수평 확장 가능한 아키텍처 |

### NFR-05: 테스트 (Testing)

| ID | 요구사항 |
|---|---|
| NFR-05.1 | Property-Based Testing 적용 (PBT 전체 규칙 적용) |
| NFR-05.2 | PBT 프레임워크: Python — Hypothesis, TypeScript — fast-check |
| NFR-05.3 | 비즈니스 로직(화자 매핑, 정책 평가, 페르소나 분기)에 PBT 필수 |

---

## 3. Technical Decisions

| 결정 항목 | 선택 | 근거 |
|---|---|---|
| Orchestrator | Strands Agents SDK (Python) | 메인 오케스트레이터, 페르소나 분기/도구 호출/대화 관리 |
| LLM | Claude Haiku 4.5 (Bedrock) | 빠른 응답 + 비용 효율 |
| STM | Valkey (Redis) | 트립 단위 발화 이력, 고속 읽기/쓰기 |
| LTM | AgentCore Memory | actor_id별 페르소나 프로파일 |
| Policy Engine | AgentCore Policy (CEDAR) | 실제 API 연동, CEDAR 정책 등록/평가 |
| Evaluation | AgentCore Evaluations | 3개 커스텀 지표 실측 |
| TTS | 텍스트 기본 + Polly 옵션 | 시간 여유 시 추가 |
| Frontend | React + TypeScript | 풀 데모 UI (좌석 배치도, 권한 대시보드, 메모리 상태, Evaluation 지표) |
| Deployment | ECS Fargate (메인) + Lambda (이벤트) | 서버리스, 메인 서비스는 컨테이너, Reflection 등은 Lambda |
| Speech-to-Text | Amazon Transcribe Streaming | 하이브리드 (실시간 + fallback) |
| Security | SECURITY 전체 규칙 적용 | 프로덕션 수준 보안 |
| Testing | PBT 전체 규칙 적용 | Hypothesis + fast-check |

---

## 4. Scope Definition (이번 세션)

### In Scope (Critical Path + 데모 UI)
- Speaker Mapping State Machine 구현
- AgentCore Memory actor_id 스코프 적용
- AgentCore Policy CEDAR 정책 작성 및 연동
- 페르소나 프롬프트 템플릿 5종
- Strands Agent 오케스트레이터
- 핵심 시나리오 시연: S1(환영), S3(같은 말 다른 추천), S4(어린이 안전), S7(게스트)
- React 풀 데모 UI (좌석 배치도, 권한 대시보드, 메모리 상태, Evaluation 지표)
- Transcribe Streaming 하이브리드 연동

### Stretch Goals (시간 여유 시)
- S2(동시 발화), S5(노약자), S6(Reflection)
- Amazon Polly TTS 연동
- 동적 페르소나 자동 등록
- AgentCore Evaluations 실측 대시보드

### Out of Scope
- Voiceprint 등록 시스템
- 프로덕션 배포 (CI/CD 파이프라인)
- 다국어 지원
- OTA 업데이트

---

## 5. Extension Configuration

| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | Yes | Requirements Analysis |
| Property-Based Testing | Yes (Full) | Requirements Analysis |
