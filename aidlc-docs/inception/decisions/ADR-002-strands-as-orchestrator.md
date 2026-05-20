# ADR-002: Strands Agents SDK as Main Orchestrator

| 항목 | 내용 |
|------|------|
| **상태** | Accepted |
| **결정일** | 2026-05-20 |
| **연관 정본** | requirements.md FR-06.1, application-design.md §2, components.md C4 |
| **연관 audit** | 2026-05-20T09:10:00Z (Verification Q4:E Strands), 2026-05-20T09:15:00Z (Clarification CL2:A Strands 메인) |
| **연관 review** | application-design-review.md Issue #3 |

## Context and Problem Statement

LLM 에이전트 메인 오케스트레이터(페르소나 분기 + 도구 호출 + 대화 관리)를 어떤 프레임워크로 구현할지 결정이 필요하다.

기획 초안(`requirements/family-profile-co-pilot-idea.md` §6.1)에서는 **LangGraph**를 명시했으나, Requirements Analysis 단계 사용자 응답(Q4:E)에서 **Strands**가 선택되었고 Clarification(CL2:A)에서 "Strands를 메인 오케스트레이터, LangGraph는 미사용"으로 확정되었다. 그러나 이 변경의 명시적 근거 기록이 부재하다는 review 지적(Issue #3)이 있어, 본 ADR로 결정 근거를 정식화한다.

핵심 요구사항:

- AWS Bedrock(Claude Haiku 4.5) 호출 (FR-06.3)
- 페르소나별 프롬프트 템플릿 동적 적용 (FR-06.2, FR-02.4)
- 도구 호출 라우팅 (차량제어 / 내비 / 음악 / 전화 / 검색)
- 동시 발화 다중 처리 (FR-04.4)
- AgentCore Memory 연동 (FR-05.2)
- 7시간 타임박스 안 구현 가능

## Considered Options

1. **LangGraph (LangChain 기반 그래프 워크플로우 프레임워크)** — Python 생태계 풍부, 그래프 형태 워크플로우 명시적
2. **Strands Agents SDK (AWS 자체 에이전트 프레임워크)** — AWS 네이티브, `@tool` 데코레이터, MCP 클라이언트 내장
3. **자체 구현 (LLM SDK + 직접 라우팅)** — 최대 자유도, 7시간엔 비현실적

## Decision Outcome

**옵션 2 (Strands Agents SDK)를 채택**한다.

선정 사유:

- **AWS 네이티브 통합**: Bedrock(Claude Haiku 4.5) / AgentCore Memory / AgentCore Policy와 같은 AWS 서비스와 직접 통합되어 추가 어댑터 코드 불필요
- **`@tool` 데코레이터 단순성**: 페르소나별 도구 분기가 데코레이터 한 줄로 표현 — 7시간 타임박스 적합
- **MCP 클라이언트 내장**: 향후 차량 제어를 MCP Server로 분리할 때 추가 작업 최소
- **프로덕션 검증된 prior art**: 동일 도메인(in-vehicle AI agent) 프로덕션 시스템이 이미 Strands를 채택·운영 중 (Prior Art 섹션 참조)
- **문서·예제 풍부**: AWS 공식 추천 + 동일 도메인 기준 사례 존재

## Consequences

- ✅ **AWS 통합 비용 최소화**: Bedrock / AgentCore Memory / AgentCore Policy 호출이 SDK 안에서 자연스럽게 처리됨
- ✅ **단순한 도구 등록**: 페르소나별 도구 차등 노출이 `@tool` + 조건부 등록으로 깔끔
- ✅ **prior art 보유**: 구현 막힐 경우 동일 도메인 프로덕션 코드 패턴(`SPEC-IXICORE-AGENT-001`) 참조 가능
- ⚠️ **LangGraph 생태계 라이브러리 사용 불가**: LangChain 기반 도구 / 메모리 어댑터를 직접 쓸 수 없음 (Strands에서 동등 기능 제공으로 대체)
- ⚠️ **상대적으로 신규 프레임워크**: LangGraph 대비 커뮤니티 자료 적음. AWS 공식 문서와 prior art로 보완

## Prior Art

LG U+ **ixi-drive** (커넥티드카 AI 음성 에이전트 프로덕션 시스템)에서 동일한 결정을 채택해 운영 중이다.

| 출처 | 내용 |
|------|------|
| `SPEC-IXICORE-AGENT-001__main-agent-design__v5.12.md` | "Main Agent — Strands 기반 LLM Agent, OEM MCP Tool + Service @tool 등록" 명시 |
| `ARCH-C2-001__ixi-drive-containers__v1.0.md` ADR-001 | Agent Core 컨테이너 기술 스택을 "Python 3.13 · FastAPI · Strands Agent SDK"로 확정 |

ixi-drive는 본 프로젝트와 동일한 도메인(차량 내 AI 에이전트)에서 Strands + MCP + Valkey 조합을 프로덕션 환경에서 검증한 사례다. 본 프로젝트는 이 검증된 스택 위에 multi-speaker 페르소나 layer(ADR-001)를 추가한다.

> Note: ixi-drive는 단일 화자(주 운전자) 가정 시스템이므로 페르소나 분기 layer는 본 프로젝트가 새로 도입하는 부분이다. Strands 기반 stack은 prior art, 다중 화자 분기는 차별화.
