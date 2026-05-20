# Family Profile Co-pilot

> 차량 내 다중 화자를 실시간 구분하고, 화자별 페르소나에 맞춰 응답·기능·가드레일을 차등 적용하는 AI Car Agent

## 시연

http://family-copilot-prod-521479254.us-east-1.elb.amazonaws.com/

## 핵심 기능

- **화자별 차등 응답**: 같은 "배고프다"에 아빠는 고기집, 엄마는 비건 식당 추천
- **역할 기반 가드레일**: 어린이가 고속도로에서 "창문 열어줘" → CEDAR 정책으로 차단 + 맞춤 거절
- **3단계 화자 매핑**: 좌석 채널 → 자기소개 이름 매칭 → 어휘 휴리스틱 (fallback: 게스트)
- **5개 페르소나 프리셋**: 운전자(성인), 동승자(성인), 어린이, 어르신, 게스트
- **동시 발화 처리**: 500ms 윈도우 버퍼링 + 우선순위 기반 순차 처리
- **프라이버시 by design**: 미등록 화자는 게스트 처리, 메모리 미저장

## 기술 스택

| 영역 | 기술 |
|------|------|
| LLM | Bedrock Claude Haiku 4.5 (Strands Agents SDK) |
| 음성 인식 | Amazon Transcribe Streaming (화자 분리) |
| 정책 엔진 | AgentCore Policy (CEDAR) |
| 상태 저장 | Valkey (Redis 호환) |
| 백엔드 | FastAPI + Python 3.12 |
| 프론트엔드 | React + TypeScript + Zustand + Tailwind |
| 인프라 | ECS Fargate + ALB + Terraform |
| 패키지 관리 | uv workspace |

## 프로젝트 구조

```
bingbing-aidlc/
├── aidlc-docs/              # AI-DLC 산출물 (inception, construction)
│   ├── inception/           # 요구사항, 유저스토리, 설계 문서
│   └── construction/        # 기능설계, 프론트엔드 컴포넌트 설계
├── frontend/                # React + TypeScript 데모 UI
│   └── src/
│       ├── components/      # SeatMap, ConversationStream, ChatInput 등
│       ├── hooks/           # useWebSocket (실시간 통신)
│       ├── stores/          # Zustand (trip, conversation, profile)
│       └── types/           # 도메인 타입 + Zod 스키마
├── services/
│   ├── api-service/         # WebSocket Gateway + Voice Ingestion + Speaker Mapping
│   │   └── src/
│   │       ├── mapping/     # SpeakerMapper (3단계), StateMachine
│   │       └── voice/       # Transcribe Streaming 연동
│   ├── agent-service/       # Orchestrator + Policy + Persona
│   │   └── src/
│   │       ├── orchestrator/  # Strands Agent + Bedrock 호출
│   │       ├── policy/        # CEDAR 정책 평가
│   │       └── persona/       # 페르소나 레지스트리 + 프롬프트
│   └── reflection-lambda/   # 트립 종료 후 화자별 메모리 적재
├── shared/                  # 공유 도메인 모델
│   ├── models/              # entities.py, enums.py (Pydantic)
│   ├── policies/            # permissions.cedar
│   └── prompts/             # 페르소나별 프롬프트 YAML (5종)
├── terraform/               # IaC (VPC, ECS, ALB, ElastiCache, DynamoDB, Lambda)
│   └── modules/
├── idea/                    # 기획 원본 문서
├── scripts/                 # DynamoDB 시드 스크립트
├── docker-compose.yml       # 로컬 개발 환경 (api + agent + valkey)
└── pyproject.toml           # uv workspace 루트 설정
```

## 로컬 실행

### 사전 요구사항

- Docker & Docker Compose
- Node.js 18+
- AWS 자격증명 (Bedrock 접근 권한)

### 백엔드

```bash
docker compose up --build
```

- API Service: http://localhost:8080
- Agent Service: http://localhost:8081
- Valkey: localhost:6379

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

http://localhost:5173 에서 접속

### 테스트

```bash
# 프로젝트 루트에서
uv sync --dev
uv run pytest -c pyproject.toml -v
```

## 시연 시나리오

1. **시동 ON** → 운전자 프로필 선택 (아빠)
2. **S3: 같은 말, 다른 추천** → 좌석 변경하며 "배고프다" 입력 → 화자별 다른 응답 확인
3. **S4: 어린이 안전 모드** → 민수(어린이) 좌석에서 "창문 열어줘" → 가드레일 차단 확인
4. **시동 OFF** → 트립 종료

## 아키텍처

```
┌─────────────┐     WebSocket      ┌──────────────────┐
│  React UI   │◄──────────────────►│   API Service    │
│  (Browser)  │                    │  (ECS Fargate)   │
└─────────────┘                    │                  │
                                   │  - WS Gateway    │
                                   │  - Voice Ingest  │──► Transcribe Streaming
                                   │  - Speaker Map   │──► Valkey (상태)
                                   └────────┬─────────┘
                                            │ HTTP
                                            ▼
                                   ┌──────────────────┐
                                   │  Agent Service   │
                                   │  (ECS Fargate)   │
                                   │                  │
                                   │  - Orchestrator  │──► Bedrock (Claude Haiku 4.5)
                                   │  - Policy        │──► CEDAR 정책 평가
                                   │  - Persona Reg   │──► 프롬프트 분기
                                   └──────────────────┘
```

## 팀

AWS Summit Seoul 2026 AI-DLC Building Session 출품작
